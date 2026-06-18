import sys

LARGURA = 50
ESTOQUE_BAIXO = 5  # limiar de alerta: 0 = esgotado, 1..5 = estoque baixo


class Cancelado(Exception):
    """Levantada quando o usuário deixa um prompt vazio para cancelar a operação."""


def limpar_tela():
    if sys.stdout.isatty():  # só emite escapes ANSI em terminal real (pipe/script fica limpo)
        print("\033[2J\033[H", end="")


def imprimir_cabecalho(titulo):
    print("═" * LARGURA)
    print(f" {titulo} ".center(LARGURA, "═"))
    print("═" * LARGURA)


def imprimir_linha(texto):
    print(f"║ {texto:<{LARGURA - 4}} ║")


def imprimir_rodape():
    print("╚" + "═" * (LARGURA - 2) + "╝")


def ler_int(mensagem, minimo=None, cancelavel=False):
    while True:
        entrada = input(mensagem)
        if cancelavel and entrada.strip() == "":
            raise Cancelado()
        try:
            valor = int(entrada)
            if minimo is not None and valor < minimo:
                print(f"[Erro]: valor deve ser maior ou igual a {minimo}.")
                continue
            return valor
        except ValueError:
            print("[Erro]: digite um número inteiro válido.")


def ler_float(mensagem, minimo=None, cancelavel=False):
    while True:
        entrada = input(mensagem)
        if cancelavel and entrada.strip() == "":
            raise Cancelado()
        try:
            valor = float(entrada.replace(",", "."))  # aceita vírgula decimal (BR)
            if minimo is not None and valor < minimo:
                print(f"[Erro]: valor deve ser maior ou igual a {minimo}.")
                continue
            return valor
        except ValueError:
            print("[Erro]: digite um número válido.")


def ler_sim_nao(mensagem):
    """Lê s/n. Retorna True só para 's'/'sim' (case-insensitive). Loop até resposta válida."""
    while True:
        resp = input(mensagem).strip().lower()
        if resp in ("s", "sim"):
            return True
        if resp in ("n", "nao", "não"):
            return False
        print("[Erro]: digite 's' para sim ou 'n' para não.")


def proximo_id(seq):
    """Lê o próximo ID do contador mutável threadado (seq = [proximo_id])."""
    return seq[0]


def printmenu():
    imprimir_cabecalho("SISTEMA GERENCIADOR DE PADARIA")
    imprimir_linha("1. Inserir produto")
    imprimir_linha("2. Remover produto")
    imprimir_linha("3. Buscar produto")
    imprimir_linha("4. Atualizar produto")
    imprimir_linha("5. Controle de estoque")
    imprimir_linha("6. Listar todos os produtos")
    imprimir_linha("7. Estatísticas")
    imprimir_linha("0. Sair")
    imprimir_rodape()
    print("\nEscolha uma operação: ", end="")


def inserir(dicionario, seq):
    imprimir_cabecalho("INSERIR PRODUTO NO SISTEMA")

    id_produto = proximo_id(seq)
    print(f"ID atribuído automaticamente: {id_produto}")

    nome = input("Digite o nome do produto: ").strip()
    if not nome:
        print("\n[Erro]: nome não pode ser vazio.")
        return False  # nome vazio: não consome o ID (contador não avança)

    nome_lower = nome.lower()
    duplicado = next(
        (pid for pid, dados in dicionario.items() if dados["nome"].lower() == nome_lower),
        None,
    )
    if duplicado is not None:
        print(f'\n[Aviso]: já existe um produto com o nome "{nome}" (ID {duplicado}).')
        if not ler_sim_nao("Deseja cadastrar mesmo assim? (s/n): "):
            print("\nInserção cancelada.")
            return False  # não consome o ID

    preco = ler_float("Digite o preço do produto: ", minimo=0.01, cancelavel=True)
    dicionario[id_produto] = {"nome": nome, "preco": preco, "estoque": 0}
    seq[0] = id_produto + 1  # só incrementa após criar com sucesso
    print("\nProduto cadastrado com sucesso!")
    return True


def remover(dicionario, seq):
    imprimir_cabecalho("REMOVER PRODUTO DO SISTEMA")

    id_produto = ler_int("Digite o ID do produto que deseja remover: ", minimo=0, cancelavel=True)
    produto = dicionario.get(id_produto)

    if produto is None:
        print("\n[Erro]: ID não encontrado.")
        return False

    print(
        f"\nProduto: ID {id_produto} | {produto['nome']} | "
        f"R$ {produto['preco']:.2f} | Qtd: {produto['estoque']}"
    )
    if not ler_sim_nao("\nConfirma remoção? (s/n): "):
        print("\nRemoção cancelada.")
        return False

    dicionario.pop(id_produto)
    print(f"\nProduto com ID {id_produto} removido com sucesso!")
    return True


def buscar_ID(dicionario, id_produto):
    return dicionario.get(id_produto, "[Erro]: ID não encontrado!")


def buscar_nome(dicionario, nome_busca):
    nome_busca = nome_busca.lower()
    return [
        {"ID": id_produto, **dados}
        for id_produto, dados in dicionario.items()
        if nome_busca in dados["nome"].lower()
    ]


def _agir_sobre(dicionario, id_produto):
    """Após exibir um produto encontrado, oferece ações diretas sobre ele (sem redigitar o ID).
    Retorna True se mutou o dicionário (para o contrato de save do T6)."""
    if id_produto not in dicionario:
        print("\n[Erro]: ID não encontrado.")
        return False
    dados = dicionario[id_produto]
    print(
        f"\nProduto: ID {id_produto} | {dados['nome']} | "
        f"R$ {dados['preco']:.2f} | Qtd: {dados['estoque']}"
    )
    print("\n1. Alterar nome\n2. Alterar preço\n3. Adicionar ao estoque\n4. Subtrair do estoque\n0. Voltar")
    opcao = ler_int("\nAção: ", minimo=0, cancelavel=True)
    if opcao == 0:
        return False
    acoes = {
        1: _alterar_nome_core,
        2: _alterar_preco_core,
        3: _controle_inserir_core,
        4: _controle_subtrair_core,
    }
    acao = acoes.get(opcao)
    if acao:
        return acao(dicionario, id_produto)
    print("\n[Erro]: Opção inválida!")
    return False


def _buscar_por_nome(dicionario):
    nome = input("Digite o nome do produto: ")
    resultados = buscar_nome(dicionario, nome)
    if not resultados:
        print("\nNenhum produto encontrado.")
        return False

    print(f"\n{len(resultados)} resultado(s) encontrado(s):")
    for item in resultados:
        print(
            f"  ID {item['ID']} | {item['nome']} | "
            f"R$ {item['preco']:.2f} | Qtd: {item['estoque']}"
        )

    if len(resultados) == 1:
        return _agir_sobre(dicionario, resultados[0]["ID"])

    ids_validos = {item["ID"] for item in resultados}
    id_alvo = ler_int("\nID do produto para agir (0 = voltar): ", minimo=0, cancelavel=True)
    if id_alvo == 0:
        return False
    if id_alvo not in ids_validos:
        print("\n[Erro]: ID não está entre os resultados da busca.")
        return False
    return _agir_sobre(dicionario, id_alvo)


def _buscar_por_id(dicionario):
    id_produto = ler_int("Digite o ID do produto: ", minimo=0, cancelavel=True)
    resultado = buscar_ID(dicionario, id_produto)
    if not isinstance(resultado, dict):
        print(f"\n{resultado}")
        return False
    return _agir_sobre(dicionario, id_produto)


# ok
def buscar_menu(dicionario, seq):
    imprimir_cabecalho("BUSCAR NO SISTEMA")
    imprimir_linha("1. Buscar por nome")
    imprimir_linha("2. Buscar por ID")
    imprimir_rodape()

    opcao = ler_int("\nDigite uma das opções acima: ", cancelavel=True)
    print("-" * LARGURA)

    opcoes = {
        1: _buscar_por_nome,
        2: _buscar_por_id,
    }

    acao = opcoes.get(opcao)
    if acao:
        return acao(dicionario)  # propaga mutação: buscar pode agir sobre o produto
    print("\n[Erro]: Opção inválida!")
    return False


# ok
def _alterar_nome_core(dicionario, id_produto):
    if id_produto not in dicionario:
        print("\n[Erro]: ID não encontrado.")
        return False

    print(f"\nProduto atual: {dicionario[id_produto]}")
    novo_nome = input("Digite um novo nome para o produto: ").strip()
    if not novo_nome:
        print("\n[Erro]: nome não pode ser vazio.")
        return False
    dicionario[id_produto]["nome"] = novo_nome
    print("\nNome atualizado com sucesso!")
    return True


# ok
def alterar_nome(dicionario):
    id_produto = ler_int("Digite o ID do produto a ser alterado: ", minimo=0, cancelavel=True)
    return _alterar_nome_core(dicionario, id_produto)


# ok
def _alterar_preco_core(dicionario, id_produto):
    if id_produto not in dicionario:
        print("\n[Erro]: ID não encontrado.")
        return False

    print(f"\nProduto atual: {dicionario[id_produto]}")
    novo_preco = ler_float("Digite um novo preço para o produto: ", minimo=0.01, cancelavel=True)
    dicionario[id_produto]["preco"] = novo_preco
    print("\nPreço atualizado com sucesso!")
    return True


# ok
def alterar_preco(dicionario):
    id_produto = ler_int("Digite o ID do produto a ser alterado: ", minimo=0, cancelavel=True)
    return _alterar_preco_core(dicionario, id_produto)


# ok
def alterar(dicionario, seq):
    imprimir_cabecalho("ATUALIZAR PRODUTO")
    imprimir_linha("1. Alterar Nome")
    imprimir_linha("2. Alterar Preço")
    imprimir_rodape()

    opcao = ler_int("\nO que deseja alterar? ", cancelavel=True)
    print("-" * LARGURA)

    opcoes = {
        1: alterar_nome,
        2: alterar_preco,
    }

    acao = opcoes.get(opcao)
    if acao:
        return acao(dicionario)
    print("\n[Erro]: Opção inválida!")
    return False


def _controle_inserir_core(dicionario, id_produto):
    if id_produto not in dicionario:
        print("\n[Erro]: ID não encontrado!")
        return False

    quantidade = ler_int("Digite quantidade a ser adicionada: ", minimo=1, cancelavel=True)
    dicionario[id_produto]["estoque"] += quantidade
    print("\nEstoque adicionado com sucesso!")
    return True


def controle_inserir(dicionario):
    id_produto = ler_int("Digite o ID do produto: ", minimo=0, cancelavel=True)
    return _controle_inserir_core(dicionario, id_produto)


def _controle_subtrair_core(dicionario, id_produto):
    if id_produto not in dicionario:
        print("\n[Erro]: ID não encontrado!")
        return False

    quantidade = ler_int("Digite quantidade a ser removida: ", minimo=1, cancelavel=True)

    if quantidade > dicionario[id_produto]["estoque"]:
        print(
            f"\n[Erro]: Qtd informada é maior que o estoque atual ({dicionario[id_produto]['estoque']})."
        )
        return False

    dicionario[id_produto]["estoque"] -= quantidade
    print("\nEstoque reduzido com sucesso!")
    return True


def controle_subtrair(dicionario):
    id_produto = ler_int("Digite o ID do produto: ", minimo=0, cancelavel=True)
    return _controle_subtrair_core(dicionario, id_produto)


def controle_definir(dicionario):
    id_produto = ler_int("Digite o ID do produto: ", minimo=0, cancelavel=True)

    if id_produto not in dicionario:
        print("\n[Erro]: ID não encontrado!")
        return False

    quantidade = ler_int("Digite o novo estoque: ", minimo=0, cancelavel=True)
    dicionario[id_produto]["estoque"] = quantidade
    print("\nEstoque definido com sucesso!")
    return True


def listar_todos(dicionario, seq=None, titulo="LISTA DE PRODUTOS", ordenar_por=None):
    imprimir_cabecalho(titulo)

    if not dicionario:
        imprimir_linha("Nenhum produto cadastrado no sistema.")
        imprimir_rodape()
        return False

    itens = list(dicionario.items())
    if ordenar_por == "nome":
        itens.sort(key=lambda kv: kv[1]["nome"].lower())
    elif ordenar_por == "preco":
        itens.sort(key=lambda kv: kv[1]["preco"])
    elif ordenar_por == "estoque":
        itens.sort(key=lambda kv: kv[1]["estoque"])
    # ordenar_por None (ou "id"): mantém a ordem de cadastro (inserção no dict)

    baixos = 0
    zerados = 0
    for id_produto, dados in itens:
        info = (
            f"ID: {id_produto} | {dados['nome']} | "
            f"R$ {dados['preco']:.2f} | Qtd: {dados['estoque']}"
        )
        imprimir_linha(info)
        if dados["estoque"] == 0:
            zerados += 1
        elif dados["estoque"] <= ESTOQUE_BAIXO:
            baixos += 1

    imprimir_rodape()

    avisos = []
    if baixos:
        avisos.append(f"{baixos} com estoque baixo (≤{ESTOQUE_BAIXO})")
    if zerados:
        avisos.append(f"{zerados} esgotado(s)")
    if avisos:
        print(f"[Aviso]: {', '.join(avisos)}.")

    return False  # listagem é só leitura — nunca persiste


def controle_exibir(dicionario):
    listar_todos(dicionario, titulo="RELATÓRIO DE ESTOQUE ATUAL")
    return False  # exibição é só leitura — nunca persiste


def controle_menu(dicionario, seq):
    imprimir_cabecalho("CONTROLE DE ESTOQUE")
    imprimir_linha("1. Inserir no estoque")
    imprimir_linha("2. Subtrair do estoque")
    imprimir_linha("3. Checar estoque")
    imprimir_linha("4. Definir estoque")
    imprimir_rodape()

    opcao = ler_int("\nDigite a opção desejada: ", cancelavel=True)
    print("-" * LARGURA)

    opcoes = {
        1: controle_inserir,
        2: controle_subtrair,
        3: controle_exibir,
        4: controle_definir,
    }

    acao = opcoes.get(opcao)
    if acao:
        return acao(dicionario)
    print("\n[Erro]: Opção inválida!")
    return False


def listar_menu(dicionario, seq):
    imprimir_cabecalho("LISTAR PRODUTOS")
    imprimir_linha("1. Por ordem de cadastro (ID)")
    imprimir_linha("2. Por nome")
    imprimir_linha("3. Por preço (menor primeiro)")
    imprimir_linha("4. Por estoque (menor primeiro)")
    imprimir_rodape()

    opcao = ler_int("\nOrdenar por: ", minimo=1, cancelavel=True)
    print("-" * LARGURA)

    mapa = {1: None, 2: "nome", 3: "preco", 4: "estoque"}
    if opcao not in mapa:
        print("\n[Erro]: Opção inválida!")
        return False

    listar_todos(dicionario, ordenar_por=mapa[opcao])
    return False


def estatisticas(dicionario, seq):
    imprimir_cabecalho("ESTATÍSTICAS")

    if not dicionario:
        imprimir_linha("Nenhum produto cadastrado.")
        imprimir_rodape()
        return False

    total = len(dicionario)
    valor_estoque = sum(d["preco"] * d["estoque"] for d in dicionario.values())
    baixos = sum(1 for d in dicionario.values() if 0 < d["estoque"] <= ESTOQUE_BAIXO)
    zerados = sum(1 for d in dicionario.values() if d["estoque"] == 0)

    imprimir_linha(f"Produtos cadastrados: {total}")
    imprimir_linha(f"Valor total em estoque: R$ {valor_estoque:.2f}")
    imprimir_linha(f"Estoque baixo (≤{ESTOQUE_BAIXO}): {baixos}")
    imprimir_linha(f"Esgotados: {zerados}")
    imprimir_rodape()
    return False
