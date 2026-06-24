import sys

LARGURA = 50
ESTOQUE_BAIXO = 5  # limiar de alerta: 0 = esgotado, 1..5 = estoque baixo


class Cancelado(Exception):
    """Levantada quando o usuário deixa um prompt vazio para cancelar a operação."""


def limpar_tela():
    """Limpa a tela do terminal, apenas quando a saída é um terminal real."""
    if sys.stdout.isatty():  # só emite escapes ANSI em terminal real
        print("\033[2J\033[H", end="")


def imprimir_cabecalho(titulo):
    """Imprime o cabeçalho da caixa de menu com o título dado."""
    print("═" * LARGURA)
    print(f" {titulo} ".center(LARGURA, "═"))
    print("═" * LARGURA)


def imprimir_linha(texto):
    """Imprime uma linha de texto dentro da caixa de menu."""
    print(f"║ {texto:<{LARGURA - 4}} ║")


def imprimir_rodape():
    """Imprime o rodapé que fecha a caixa de menu."""
    print("╚" + "═" * (LARGURA - 2) + "╝")


def formatar_produto(id_produto, dados):
    """Formata um produto numa linha padrão: ID .. | nome | R$ preco | Qtd: estoque."""
    return (
        f"ID {id_produto} | {dados['nome']} | "
        f"R$ {dados['preco']:.2f} | Qtd: {dados['estoque']}"
    )


def ler_int(mensagem, minimo=None, cancelavel=False):
    """Lê um número inteiro do usuário, validando o tipo e o valor mínimo. Se a operação for cancelável (True), um espaço vazio termina a operação"""

    while True:
        # Pede a entrada para o usuário.
        entrada = input(mensagem)

        # Se a operação for cancelável e a entrda for vazia, cancela a operação
        if cancelavel and entrada.strip() == "":
            raise Cancelado()

        # caso contrário, checa se o valor é >= que o mínimo e se é inteiro
        try:
            valor = int(entrada)
            if minimo is not None and valor < minimo:
                print(f"[Erro]: valor deve ser maior ou igual a {minimo}.")
                continue
            return valor
        except ValueError:
            print("[Erro]: digite um número inteiro válido.")


def ler_float(mensagem, minimo=None, cancelavel=False):
    """A mesma ideia do ler_int"""

    while True:
        # PEde entrada para o usuário.
        entrada = input(mensagem)

        # Checa se é cancelável e está vazia.
        if cancelavel and entrada.strip() == "":
            raise Cancelado()

        # Se passar, troca vírugla por ponto (se for o caso). Checa se é >= mínimo e se é float.
        try:
            valor = float(entrada.replace(",", "."))  # aceita vírgula decimal
            if minimo is not None and valor < minimo:
                print(f"[Erro]: valor deve ser maior ou igual a {minimo}.")
                continue
            return valor
        except ValueError:
            print("[Erro]: digite um número válido.")


def ler_sim_nao(mensagem):
    """Lê s/n. Retorna True só para 's'/'sim' (case-insensitive). Loop até resposta válida."""
    while True:
        # pede a resposta do usuário
        resp = input(mensagem).strip().lower()

        # Se sim sim se não não :D
        if resp in ("s", "sim"):
            return True
        if resp in ("n", "nao", "não"):
            return False

        # se nem não nem sim então tenta de novo
        print("[Erro]: digite 's' para sim ou 'n' para não.")


def printmenu():
    """Imprime o menu principal do sistema."""
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


# Inserir
def inserir(dicionario, seq):
    """Cadastra um novo produto com ID automático, preço e estoque zero."""

    imprimir_cabecalho("INSERIR PRODUTO NO SISTEMA")

    # Começamos atribuindo o ID automaticamente de acordo com o ID disponível no momento
    id_produto = seq[0]
    print(f"ID atribuído automaticamente: {id_produto}")

    # depois pedimos o Input de string do usuário e validamos se há realmente algo escrito.
    nome = input("Digite o nome do produto: ").strip()
    if not nome:
        print("\n[Erro]: nome não pode ser vazio.")
        return False

    nome_lower = nome.lower()
    duplicado = None

    # Percorremos pelos nomes do dicionario para checar se há repetido. Se houver, exclama ao usuário e oferece a opção de cadastrar mesmo assim.
    for pid, dados in dicionario.items():
        if dados["nome"].lower() == nome_lower:
            duplicado = pid
            break
    if duplicado is not None:
        print(f'\n[Aviso]: já existe um produto com o nome "{nome}" (ID {duplicado}).')
        if not ler_sim_nao("Deseja cadastrar mesmo assim? (s/n): "):
            print("\nInserção cancelada.")
            return False

    # Se o usuário escolheu cadastrar mesmo assim ou não havia nome repetido, prossegue com a atribuição de preço, adicionar no dicionario de produtos;
    # incrementar em 1 o ID disponível atual e exibir uma mensagem de exito.
    preco = ler_float("Digite o preço do produto: ", minimo=0.01, cancelavel=True)
    dicionario[id_produto] = {"nome": nome, "preco": preco, "estoque": 0}
    seq[0] = id_produto + 1  # só incrementa após criar com sucesso
    print("\nProduto cadastrado com sucesso!")
    return True


# Remover
def remover(dicionario, seq):
    """Remove um produto pelo ID, após confirmação do usuário."""

    imprimir_cabecalho("REMOVER PRODUTO DO SISTEMA")

    # Pedimos o ID do produtoe buscamos com a função .get.
    id_produto = ler_int(
        "Digite o ID do produto que deseja remover: ", minimo=0, cancelavel=True
    )
    produto = dicionario.get(id_produto)

    # Se este ID não estiver cadastrado, exclama ao usuário e sai da operação.
    if produto is None:
        print("\n[Erro]: ID não encontrado.")
        return False

    # Caso contrário, exibimos a informação do produto marcado pelo ID e pedimos uma confirmação do usuário.
    print(f"\nProduto: {formatar_produto(id_produto, produto)}")
    if not ler_sim_nao("\nConfirma remoção? (s/n): "):
        print("\nRemoção cancelada.")
        return False

    # Se escolhermos remover, utilizamos a função .pop no ID do produto e exibimos uma mensagem de éxito.
    dicionario.pop(id_produto)
    print(f"\nProduto com ID {id_produto} removido com sucesso!")
    return True


# Buscar
def buscar_menu(dicionario, seq):
    """Menu de busca: escolhe buscar por nome ou por ID e propaga possível mutação."""
    imprimir_cabecalho("BUSCAR NO SISTEMA")
    imprimir_linha("1. Buscar por nome")
    imprimir_linha("2. Buscar por ID")
    imprimir_rodape()

    # Pedimos ao usuário uma das opções disponível
    opcao = ler_int("\nDigite uma das opções acima: ", cancelavel=True)
    print("-" * LARGURA)

    opcoes = {
        1: _buscar_por_nome,
        2: _buscar_por_id,
    }

    # Se a opção for válida, simplemento buscamos e exectuamos ela. Caso contrário, excalamamos para o usuário e saimos da operação.
    acao = opcoes.get(opcao)
    if acao:
        return acao(dicionario)
    print("\n[Erro]: Opção inválida!")
    return False


def _buscar_por_nome(dicionario):
    """Busca produtos por trecho de nome e permite agir sobre um dos resultados."""

    # Pede um nome para o usuário
    nome = input("Digite o nome do produto: ")

    # Busca o(s) produtos com aquele nome (ou trcho) e armazena o resultado... em resultado.
    resultados = _buscar_nome(dicionario, nome)

    # Se  não tiver exito, exclama ao usuário
    if not resultados:
        print("\nNenhum produto encontrado.")
        return False

    # Mostra quais foram os resultados encontrados e formata eles de tal modo a ficar agradável visualmente.
    print(f"\n{len(resultados)} resultado(s) encontrado(s):")
    for pid, dados in resultados:
        print(f"  {formatar_produto(pid, dados)}")

    # Se a quantidade de resultador for somente 1, ativa imediatamente a opção de agir sobre aque produto
    if len(resultados) == 1:
        return _agir_sobre(dicionario, resultados[0][0])

    # Caso contráriom checa os IDS válidos do resultado. Pede ao usuário para que escolha um para agir sobre.
    ids_validos = {pid for pid, _ in resultados}
    id_alvo = ler_int(
        "\nID do produto para agir (0 = voltar): ", minimo=0, cancelavel=True
    )

    # Se o usuário digitar '0', sai da operação.
    if id_alvo == 0:
        return False

    # Se o ID digitado for inválido, sai da operação
    if id_alvo not in ids_validos:
        print("\n[Erro]: ID não está entre os resultados da busca.")
        return False

    # Caso contrário abre o menu de agir sobre em relação ao ID digitado válido.
    return _agir_sobre(dicionario, id_alvo)


def _buscar_por_id(dicionario):
    """Busca um produto pelo ID e permite agir diretamente sobre ele."""

    # Pega o ID
    id_produto = ler_int("Digite o ID do produto: ", minimo=0, cancelavel=True)

    # Se o ID for inválido, exclama para o usuário
    if id_produto not in dicionario:
        print("\n[Erro]: ID não encontrado.")
        return False

    # Se não abre o menu de agir sobre
    return _agir_sobre(dicionario, id_produto)


def _agir_sobre(dicionario, id_produto):
    """Após exibir um produto encontrado, oferece ações diretas sobre ele (sem redigitar o ID).
    Retorna True se mutou o dicionário."""

    # Nosso dicionario de produtos se estrutura da seguinte forma:
    #
    # {ID: {"nome":nome, "preço":preço, "estoque":estoque}}
    #
    # O que isto faz é pegar os dados, da nossa lista de produtos, ou seja o que vem depois de "ID:"
    dados = dicionario[id_produto]

    # Exibe a estrutura do produto formatada e pede ao usuário que escolha uma das opcoes de operação
    print(f"\nProduto: {formatar_produto(id_produto, dados)}")
    print(
        "\n1. Alterar nome\n2. Alterar preço\n3. Adicionar ao estoque\n4. Subtrair do estoque\n0. Voltar"
    )

    # Pega a ação do usuário (observe que esta é uma operação cancelavel)
    opcao = ler_int("\nAção: ", minimo=0, cancelavel=True)
    if opcao == 0:
        return False

    # A depender da escolha do usuário, executa uma dessas coisa ai de baixo
    # A função _agir_sobre é executada após todo o processamento da função buscar.
    # Isso significa, basicamentente, que não precisamos validar os dados que chegam a ela pois
    # eles já passarm por este processo antes.
    # Então as funções "_cores" servem simplemente para executar a tarefa necessária,
    # sem precisar validar ou tratar nada antes.
    acoes = {
        1: _alterar_nome_core,
        2: _alterar_preco_core,
        3: _controle_inserir_core,
        4: _controle_subtrair_core,
    }
    acao = acoes.get(opcao)
    if acao:
        return acao(dicionario, id_produto)

    # Se a escolha for inválida, ele avisa e encerra a operação
    print("\n[Erro]: Opção inválida!")
    return False


def _buscar_nome(dicionario, nome_busca):
    """Lista (id, dados) dos produtos cujo nome contém o trecho buscado (ignora caixa)."""

    nome_busca = nome_busca.lower()
    return [
        (id_produto, dados)
        for id_produto, dados in dicionario.items()
        if nome_busca in dados["nome"].lower()
    ]


# Irei estar pulanddo esta parte porque são simplemente as operações de _agir_sobre


# Funções _cores assumem que os valores já estão validades e agem diretamente sobre eles, mutando dicionario (e qualquer outra oisa que atuem sobre).
# Neste caso, funções cores são apenas para não repetir a lógica dentro de uma função.


# Tudo o que tiver "_core" no nome, saiba que ta mudando algo e não validando, qualquer coisa que chamar ou retornar uma "_core"
def _alterar_nome_core(dicionario, id_produto):
    """Núcleo de alteração de nome: recebe o ID direto, sem ler do usuário."""
    print(f"\nProduto atual: {dicionario[id_produto]}")
    novo_nome = input("Digite um novo nome para o produto: ").strip()
    if not novo_nome:
        print("\n[Erro]: nome não pode ser vazio.")
        return False
    dicionario[id_produto]["nome"] = novo_nome
    print("\nNome atualizado com sucesso!")
    return True


def alterar_nome(dicionario):
    """Lê o ID do usuário e altera o nome do produto correspondente."""
    id_produto = ler_int(
        "Digite o ID do produto a ser alterado: ", minimo=0, cancelavel=True
    )
    if id_produto not in dicionario:
        print("\n[Erro]: ID não encontrado.")
        return False
    return _alterar_nome_core(dicionario, id_produto)


def _alterar_preco_core(dicionario, id_produto):
    """Núcleo de alteração de preço: recebe o ID direto, sem ler do usuário."""
    print(f"\nProduto atual: {dicionario[id_produto]}")
    novo_preco = ler_float(
        "Digite um novo preço para o produto: ", minimo=0.01, cancelavel=True
    )
    dicionario[id_produto]["preco"] = novo_preco
    print("\nPreço atualizado com sucesso!")
    return True


def alterar_preco(dicionario):
    """Lê o ID do usuário e altera o preço do produto correspondente."""
    id_produto = ler_int(
        "Digite o ID do produto a ser alterado: ", minimo=0, cancelavel=True
    )
    if id_produto not in dicionario:
        print("\n[Erro]: ID não encontrado.")
        return False
    return _alterar_preco_core(dicionario, id_produto)


# Atualizar produto:
def alterar(dicionario, seq):
    """Menu de atualização: escolhe alterar nome ou preço do produto."""
    imprimir_cabecalho("ATUALIZAR PRODUTO")
    imprimir_linha("1. Alterar Nome")
    imprimir_linha("2. Alterar Preço")
    imprimir_rodape()

    # Recebee um input do usuário
    opcao = ler_int("\nO que deseja alterar? ", cancelavel=True)
    print("-" * LARGURA)

    opcoes = {
        1: alterar_nome,
        2: alterar_preco,
    }

    # Executa a opção
    acao = opcoes.get(opcao)

    # Se a ação foi executada com sucesso e não está vazia, simplemente retorna o o resultado dela
    if acao:
        return acao(dicionario)

    # Se não, a única razão plausível é que não foi escolhido uma opção válida.
    print("\n[Erro]: Opção inválida!")
    return False


# Controle de Estoque
def controle_menu(dicionario, seq):
    """Menu de controle de estoque: inserir, subtrair, checar ou definir estoque."""
    # Basicamente a mesma ideia da função anterior
    imprimir_cabecalho("CONTROLE DE ESTOQUE")
    imprimir_linha("1. Inserir no estoque")
    imprimir_linha("2. Subtrair do estoque")
    imprimir_linha("3. Checar estoque")
    imprimir_linha("4. Definir estoque")
    imprimir_rodape()

    # Recebe a escolha do usuário
    opcao = ler_int("\nDigite a opção desejada: ", cancelavel=True)
    print("-" * LARGURA)

    opcoes = {
        1: controle_inserir,
        2: controle_subtrair,
        3: controle_exibir,
        4: controle_definir,
    }

    # Executa e retonar o resultado da ação
    acao = opcoes.get(opcao)
    if acao:
        return acao(dicionario)

    # Se a ação for invpalida encerra a operação
    print("\n[Erro]: Opção inválida!")
    return False


# Uma observação que não coloquei lá em cima, as funções "_cores" não validam nada, tem que receber pronto e mastigado.
# (eu do futuro): coloquei sim.
def _controle_inserir_core(dicionario, id_produto):
    """Núcleo de adição ao estoque: soma uma quantidade ao estoque do produto."""
    quantidade = ler_int(
        "Digite quantidade a ser adicionada: ", minimo=1, cancelavel=True
    )
    dicionario[id_produto]["estoque"] += quantidade
    print("\nEstoque adicionado com sucesso!")
    return True


def controle_inserir(dicionario):
    """Lê o ID do usuário e adiciona uma quantidade ao estoque do produto."""
    id_produto = ler_int("Digite o ID do produto: ", minimo=0, cancelavel=True)
    if id_produto not in dicionario:
        print("\n[Erro]: ID não encontrado.")
        return False
    return _controle_inserir_core(dicionario, id_produto)


def _controle_subtrair_core(dicionario, id_produto):
    """Núcleo de subtração do estoque: remove uma quantidade, bloqueando se exceder o total."""
    quantidade = ler_int(
        "Digite quantidade a ser removida: ", minimo=1, cancelavel=True
    )

    if quantidade > dicionario[id_produto]["estoque"]:
        print(
            f"\n[Erro]: Qtd informada é maior que o estoque atual ({dicionario[id_produto]['estoque']})."
        )
        return False

    dicionario[id_produto]["estoque"] -= quantidade
    print("\nEstoque reduzido com sucesso!")
    return True


def controle_subtrair(dicionario):
    """Lê o ID do usuário e subtrai uma quantidade do estoque do produto."""
    id_produto = ler_int("Digite o ID do produto: ", minimo=0, cancelavel=True)
    if id_produto not in dicionario:
        print("\n[Erro]: ID não encontrado.")
        return False
    return _controle_subtrair_core(dicionario, id_produto)


def _controle_definir_core(dicionario, id_produto):
    """Núcleo de definição de estoque: define um valor absoluto, recebendo o ID direto."""
    quantidade = ler_int("Digite o novo estoque: ", minimo=0, cancelavel=True)
    dicionario[id_produto]["estoque"] = quantidade
    print("\nEstoque definido com sucesso!")
    return True


def controle_definir(dicionario):
    """Lê o ID do usuário e define um valor absoluto para o estoque do produto."""
    id_produto = ler_int("Digite o ID do produto: ", minimo=0, cancelavel=True)
    if id_produto not in dicionario:
        print("\n[Erro]: ID não encontrado.")
        return False
    return _controle_definir_core(dicionario, id_produto)


def controle_exibir(dicionario):
    """Exibe um relatório com o estoque atual de todos os produtos. Apenas leitura."""
    listar_todos(dicionario, titulo="RELATÓRIO DE ESTOQUE ATUAL")
    return False  # exibição é só leitura


# Lista todos os produtos (de acordo com a sua escolha)
def listar_todos(dicionario, seq=None, titulo="LISTA DE PRODUTOS", ordenar_por=None):
    """Lista todos os produtos em uma caixa, ordenados conforme ordenar_por.

    Mostra ao final a contagem de itens em estoque baixo e esgotados.
    Retorna False, pois é apenas leitura."""

    imprimir_cabecalho(titulo)

    # Se não tiver nenhum produto cadastrado ainda, avisa e sai.
    if not dicionario:
        imprimir_linha("Nenhum produto cadastrado no sistema.")
        imprimir_rodape()
        return False

    # Pega os produtos como uma tupla de (id, dados) pra podermos ordenar do jeito
    # que o usuário pediu (por nome, preço, estoque...).
    itens = list(dicionario.items())
    if ordenar_por == "nome":
        itens.sort(key=lambda kv: kv[1]["nome"].lower())
    elif ordenar_por == "preco":
        itens.sort(key=lambda kv: kv[1]["preco"])
    elif ordenar_por == "estoque":
        itens.sort(key=lambda kv: kv[1]["estoque"])
    # ordenar_por None (ou "id"): mantém a ordem de cadastro

    # conta quantos estão com estoque baixo e quantos estão esgotados,
    # pra poder avisar o usuário lá no final.
    baixos = 0
    zerados = 0
    for id_produto, dados in itens:
        # Monta a linha de cada produto e joga dentro da caixa.
        info = (
            f"ID: {id_produto} | {dados['nome']} | "
            f"R$ {dados['preco']:.2f} | Qtd: {dados['estoque']}"
        )
        imprimir_linha(info)
        # 0 = esgotado; de 1 até ESTOQUE_BAIXO = estoque baixo. O resto tá ok.
        if dados["estoque"] == 0:
            zerados += 1
        elif dados["estoque"] <= ESTOQUE_BAIXO:
            baixos += 1

    imprimir_rodape()

    # Depois da lista, junta os avisos (se tiver algum) e mostra tudo numa linha só.
    avisos = []
    if baixos:
        avisos.append(f"{baixos} com estoque baixo (≤{ESTOQUE_BAIXO})")
    if zerados:
        avisos.append(f"{zerados} esgotado(s)")
    if avisos:
        print(f"[Aviso]: {', '.join(avisos)}.")

    return False  # listagem é só leitura


def listar_menu(dicionario, seq):
    """Menu de listagem: escolhe o critério de ordenação e lista os produtos."""
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


# Função de estatísticas
def estatisticas(dicionario, seq):
    """Exibe um quadro com totais: produtos, valor em estoque, baixos e esgotados."""

    imprimir_cabecalho("ESTATÍSTICAS")

    # Se não tiver produto cadastrado, avisa e sai cedo.
    if not dicionario:
        imprimir_linha("Nenhum produto cadastrado.")
        imprimir_rodape()
        return False

    # Soma tudo: quantos produtos existem, quanto de dinheiro tá -
    # parado no estoque, e quantos precisam de atenção.
    total = len(dicionario)
    valor_estoque = sum(d["preco"] * d["estoque"] for d in dicionario.values())
    baixos = sum(1 for d in dicionario.values() if 0 < d["estoque"] <= ESTOQUE_BAIXO)
    zerados = sum(1 for d in dicionario.values() if d["estoque"] == 0)

    # Mostra cada total numa linha da caixa.
    imprimir_linha(f"Produtos cadastrados: {total}")
    imprimir_linha(f"Valor total em estoque: R$ {valor_estoque:.2f}")
    imprimir_linha(f"Estoque baixo (≤{ESTOQUE_BAIXO}): {baixos}")
    imprimir_linha(f"Esgotados: {zerados}")
    imprimir_rodape()
    return False
