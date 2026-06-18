import funcoes_padaria
import banco

produtos = banco.carregar_dados()

opcoes = {
    "1": funcoes_padaria.inserir,
    "2": funcoes_padaria.remover,
    "3": funcoes_padaria.buscar_menu,
    "4": funcoes_padaria.alterar,
    "5": funcoes_padaria.controle_menu,
    "6": funcoes_padaria.listar_todos,
}

while True:
    funcoes_padaria.limpar_tela()
    funcoes_padaria.printmenu()
    opcao = input("").strip()

    if opcao == "0":
        break

    acao = opcoes.get(opcao)
    if acao:
        acao(produtos)
    else:
        print("\n[Erro]: opção inválida!")
        input("\nPressione [Enter] para continuar...")
        continue

    banco.salvar_dados(produtos)
    input("\nPressione [Enter] para voltar ao menu principal...")

funcoes_padaria.limpar_tela()
banco.salvar_dados(produtos)
print("Dados salvos. Encerrando. Até a próxima.")
