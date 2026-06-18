import json
import os
import re
import shutil
import tempfile

CAMINHO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "banco_dados.json")
CAMINHO_BAK = CAMINHO + ".bak"

# Casa o campo "preco" no JSON serializado para formatá-lo com 2 casas decimais.
# Seguro no schema controlado: só `preco` é float (nome é str, estoque e proximo_id são int).
_PRECO = re.compile(r'("preco":\s*)(-?[0-9eE.+-]+)')


def salvar_dados(dicionario, proximo_id):
    """Grava o banco em schema aninhado: {"proximo_id": n, "produtos": {id: prod}}.

    `preco` é gravado com 2 casas decimais (ex.: 15.00). Escrita atômica: serializa em
    arquivo temporário no mesmo diretório e troca via os.replace. Antes de trocar,
    copia o arquivo atual para `.bak` (mantém CAMINHO intacto até o novo estar pronto,
    sem janela sem arquivo). Round-trip preservado: json.loads lê 15.00 -> float 15.0."""
    dados = {
        "proximo_id": proximo_id,
        "produtos": {str(chave): valor for chave, valor in dicionario.items()},
    }
    texto = json.dumps(dados, ensure_ascii=False, indent=2)
    texto = _PRECO.sub(lambda m: f"{m.group(1)}{float(m.group(2)):.2f}", texto)

    diretorio = os.path.dirname(CAMINHO) or "."
    fd, tmp = tempfile.mkstemp(dir=diretorio, prefix="banco_", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as arquivo:
            arquivo.write(texto)
        # backup do arquivo atual (se existir) antes da troca — não há janela sem CAMINHO
        if os.path.exists(CAMINHO):
            try:
                shutil.copy2(CAMINHO, CAMINHO_BAK)
            except OSError:
                pass  # sem backup, mas segue gravando
        os.replace(tmp, CAMINHO)  # atômico
    except OSError:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def _parse_pipe(texto):
    """Legado: converte arquivo pipe-delimitado, pulando linhas inválidas."""
    dicionario = {}
    for linha in texto.splitlines():
        linha = linha.strip()
        if not linha:
            continue

        partes = linha.split("|")
        if len(partes) != 4:
            continue  # pula só a linha ruim, não o arquivo inteiro

        try:
            id_produto = int(partes[0])
            dicionario[id_produto] = {
                "nome": partes[1],
                "preco": float(partes[2]),
                "estoque": int(partes[3]),
            }
        except ValueError:
            continue

    return dicionario


def _parse_texto(texto):
    """Converte texto (JSON aninhado/flat legado ou pipe-delimitado) em (produtos, proximo_id).
    Não grava nada — a migração de formato acontece no próximo salvar_dados. None se irrecuperável."""
    try:
        dados = json.loads(texto)
    except json.JSONDecodeError:
        dicionario = _parse_pipe(texto)
        if not dicionario:
            return None
        return dicionario, max(dicionario, default=0) + 1

    if not isinstance(dados, dict):
        return None

    # Formato novo aninhado: {"proximo_id": n, "produtos": {...}}
    if "produtos" in dados:
        produtos = {int(chave): valor for chave, valor in dados["produtos"].items()}
        proximo_id = dados.get("proximo_id", max(produtos, default=0) + 1)
        return produtos, proximo_id

    # Formato JSON legado flat: {"1": {...}, "2": {...}}
    produtos = {int(chave): valor for chave, valor in dados.items()}
    return produtos, max(produtos, default=0) + 1


def _carregar_arquivo(caminho):
    """Lê e converte um arquivo em (produtos, proximo_id). None se ausente/ilegível/corrompido."""
    if not os.path.exists(caminho):
        return None
    try:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            texto = arquivo.read()
    except OSError:
        return None
    return _parse_texto(texto)


def carregar_dados():
    """Retorna (produtos, proximo_id). Primeiro uso (sem CAMINHO nem .bak) -> ({}, 1).
    Falha crítica (CAMINHO corrompido e sem .bak utilizável) -> None (preserva o arquivo,
    não migra, não sobrescreve). Se CAMINHO está corrompido/ausente mas `.bak` é utilizável,
    recupera do backup (restaura CAMINHO) com um [Aviso]."""
    parsed = _carregar_arquivo(CAMINHO)
    if parsed is not None:
        return parsed

    # CAMINHO ausente ou corrompido: tentar o backup
    if os.path.exists(CAMINHO_BAK):
        parsed_bak = _carregar_arquivo(CAMINHO_BAK)
        if parsed_bak is not None:
            print(f"[Aviso]: arquivo principal corrompido ou ausente — usando backup ({os.path.basename(CAMINHO_BAK)}).")
            try:
                shutil.copy2(CAMINHO_BAK, CAMINHO)  # restaura CAMINHO a partir do backup
            except OSError:
                pass  # ainda assim retorna os dados em memória
            return parsed_bak

    # Nem CAMINHO nem .bak existem: primeiro uso
    if not os.path.exists(CAMINHO) and not os.path.exists(CAMINHO_BAK):
        return {}, 1

    # CAMINHO existe mas está corrompido e não há .bak: falha crítica (T2)
    return None