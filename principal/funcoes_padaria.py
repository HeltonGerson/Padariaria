LARGURA = 50


def limpar_tela():
    print("\033[2J\033[H", end="")


def imprimir_cabecalho(titulo):
    print("═" * LARGURA)
    print(f" {titulo} ".center(LARGURA, "═"))
    print("═" * LARGURA)


def imprimir_linha(texto):
    print(f"║ {texto:<{LARGURA - 4}} ║")


def imprimir_rodape():
    print("╚" + "═" * (LARGURA - 2) + "╝")


def ler_int(mensagem, minimo=None):
    while True:
        try:
            valor = int(input(mensagem))
            if minimo is not None and valor < minimo:
                print(f"[Erro]: valor deve ser maior ou igual a {minimo}.")
                continue
            return valor
        except ValueError:
            print("[Erro]: digite um número inteiro válido.")


def ler_float(mensagem, minimo=None):
    while True:
        try:
            valor = float(input(mensagem))
            if minimo is not None and valor < minimo:
                print(f"[Erro]: valor deve ser maior ou igual a {minimo}.")
                continue
            return valor
        except ValueError:
            print("[Erro]: digite um número válido.")


def proximo_id(dicionario):
    return max(dicionario.keys(), default=0) + 1


def printmenu():
    imprimir_cabecalho("SISTEMA GERENCIADOR DE PADARIA")
    imprimir_linha("1. Inserir produto")
    imprimir_linha("2. Remover produto")
    imprimir_linha("3. Buscar produto")
    imprimir_linha("4. Atualizar produto")
    imprimir_linha("5. Controle de estoque")
    imprimir_linha("6. Listar todos os produtos")
    imprimir_linha("0. Sair")
    imprimir_rodape()
    print("\nEscolha uma operação: ", end="")


def inserir(dicionario):
    imprimir_cabecalho("INSERIR PRODUTO NO SISTEMA")

    id_produto = proximo_id(dicionario)
    print(f"ID atribuído automaticamente: {id_produto}")

    nome = input("Digite o nome do produto: ").strip()
    if not nome:
        print("\n[Erro]: nome não pode ser vazio.")
        return

    preco = ler_float("Digite o preço do produto: ", minimo=0.01)
    dicionario[id_produto] = {"nome": nome, "preco": preco, "estoque": 0}
    print("\nProduto cadastrado com sucesso!")


def remover(dicionario):
    imprimir_cabecalho("REMOVER PRODUTO DO SISTEMA")

    id_produto = ler_int("Digite o ID do produto que deseja remover: ")
    removido = dicionario.pop(id_produto, None)

    if removido:
        print(f"\nProduto com ID {id_produto} removido com sucesso!")
    else:
        print("\n[Erro]: ID não encontrado.")


def buscar_ID(dicionario, id_produto):
    return dicionario.get(id_produto, "[Erro]: ID não encontrado!")


def buscar_nome(dicionario, nome_busca):
    nome_busca = nome_busca.lower()
    return [
        {"ID": id_produto, **dados}
        for id_produto, dados in dicionario.items()
        if nome_busca in dados["nome"].lower()
    ]


def _buscar_por_nome(dicionario):
    nome = input("Digite o nome do produto: ")
    resultados = buscar_nome(dicionario, nome)
    if not resultados:
        print("\nNenhum produto encontrado.")
    else:
        print(f"\n{len(resultados)} resultado(s) encontrado(s):")
        for item in resultados:
            print(
                f"  ID {item['ID']} | {item['nome']} | "
                f"R$ {item['preco']:.2f} | Qtd: {item['estoque']}"
            )


def _buscar_por_id(dicionario):
    id_produto = ler_int("Digite o ID do produto: ")
    resultado = buscar_ID(dicionario, id_produto)
    if isinstance(resultado, dict):
        print(
            f"\nResultado: ID {id_produto} | {resultado['nome']} | "
            f"R$ {resultado['preco']:.2f} | Qtd: {resultado['estoque']}"
        )
    else:
        print(f"\n{resultado}")


# ok
def buscar_menu(dicionario):
    imprimir_cabecalho("BUSCAR NO SISTEMA")
    imprimir_linha("1. Buscar por nome")
    imprimir_linha("2. Buscar por ID")
    imprimir_rodape()

    opcao = ler_int("\nDigite uma das opções acima: ")
    print("-" * LARGURA)

    opcoes = {
        1: _buscar_por_nome,
        2: _buscar_por_id,
    }

    acao = opcoes.get(opcao)
    if acao:
        acao(dicionario)
    else:
        print("\n[Erro]: Opção inválida!")


# ok
def alterar_nome(dicionario):
    id_produto = ler_int("Digite o ID do produto a ser alterado: ")

    if id_produto not in dicionario:
        print("\n[Erro]: ID não encontrado.")
        return

    print(f"\nProduto atual: {dicionario[id_produto]}")
    novo_nome = input("Digite um novo nome para o produto: ").strip()
    if not novo_nome:
        print("\n[Erro]: nome não pode ser vazio.")
        return
    dicionario[id_produto]["nome"] = novo_nome
    print("\nNome atualizado com sucesso!")


# ok
def alterar_preco(dicionario):
    id_produto = ler_int("Digite o ID do produto a ser alterado: ")

    if id_produto not in dicionario:
        print("\n[Erro]: ID não encontrado.")
        return

    print(f"\nProduto atual: {dicionario[id_produto]}")
    novo_preco = ler_float("Digite um novo preço para o produto: ", minimo=0.01)
    dicionario[id_produto]["preco"] = novo_preco
    print("\nPreço atualizado com sucesso!")


# ok
def alterar(dicionario):
    imprimir_cabecalho("ATUALIZAR PRODUTO")
    imprimir_linha("1. Alterar Nome")
    imprimir_linha("2. Alterar Preço")
    imprimir_rodape()

    opcao = ler_int("\nO que deseja alterar? ")
    print("-" * LARGURA)

    opcoes = {
        1: alterar_nome,
        2: alterar_preco,
    }

    acao = opcoes.get(opcao)
    if acao:
        acao(dicionario)
    else:
        print("\n[Erro]: Opção inválida!")


def controle_inserir(dicionario):
    id_produto = ler_int("Digite o ID do produto: ")

    if id_produto not in dicionario:
        print("\n[Erro]: ID não encontrado!")
        return

    quantidade = ler_int("Digite quantidade a ser adicionada: ", minimo=1)
    dicionario[id_produto]["estoque"] += quantidade
    print("\nEstoque adicionado com sucesso!")


def controle_subtrair(dicionario):
    id_produto = ler_int("Digite o ID do produto: ")

    if id_produto not in dicionario:
        print("\n[Erro]: ID não encontrado!")
        return

    quantidade = ler_int("Digite quantidade a ser removida: ", minimo=1)

    if quantidade > dicionario[id_produto]["estoque"]:
        print(
            f"\n[Erro]: Qtd informada é maior que o estoque atual ({dicionario[id_produto]['estoque']})."
        )
        return

    dicionario[id_produto]["estoque"] -= quantidade
    print("\nEstoque reduzido com sucesso!")


def listar_todos(dicionario, titulo="LISTA DE PRODUTOS"):
    imprimir_cabecalho(titulo)

    if not dicionario:
        imprimir_linha("Nenhum produto cadastrado no sistema.")
        imprimir_rodape()
        return

    for id_produto, dados in dicionario.items():
        info = (
            f"ID: {id_produto} | {dados['nome']} | "
            f"R$ {dados['preco']:.2f} | Qtd: {dados['estoque']}"
        )
        imprimir_linha(info)

    imprimir_rodape()


def controle_exibir(dicionario):
    listar_todos(dicionario, titulo="RELATÓRIO DE ESTOQUE ATUAL")


def controle_menu(dicionario):
    imprimir_cabecalho("CONTROLE DE ESTOQUE")
    imprimir_linha("1. Inserir no estoque")
    imprimir_linha("2. Subtrair do estoque")
    imprimir_linha("3. Checar estoque")
    imprimir_rodape()

    opcao = ler_int("\nDigite a opção desejada: ")
    print("-" * LARGURA)

    opcoes = {
        1: controle_inserir,
        2: controle_subtrair,
        3: controle_exibir,
    }

    acao = opcoes.get(opcao)
    if acao:
        acao(dicionario)
    else:
        print("\n[Erro]: Opção inválida!")
