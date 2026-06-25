"""Ponto de entrada do sistema: carrega os dados e executa o laço de menu principal.

Cada operação devolve True se alterou os dados (para que sejam salvos) e False caso
contrário. Em Ctrl+C, Ctrl+D ou saída normal, o estado atual sempre é salvo."""

import sys

import funcoes_padaria
import banco

resultado = banco.carregar_dados()  # (produtos, proximo_id) ou None (falha crítica)

# Checagem de integridade de arquivos de dados
if resultado is None:
    funcoes_padaria.limpar_tela()
    print("[Aviso]: arquivo de dados corrompido (banco_dados.json).")
    print(
        "Os dados existentes NÃO foram sobrescritos. Restaure um backup ou repare o arquivo."
    )
    input("\nPressione [Enter] para sair sem salvar...")
    sys.exit(1)

produtos, proximo_id = resultado
seq = [proximo_id]

opcoes = {
    "1": funcoes_padaria.inserir,
    "2": funcoes_padaria.remover,
    "3": funcoes_padaria.buscar_menu,
    "4": funcoes_padaria.alterar,
    "5": funcoes_padaria.controle_menu,
    "6": funcoes_padaria.listar_menu,
    "7": funcoes_padaria.estatisticas,
}

# Looping onde basicamente roda todo o programa
while True:
    funcoes_padaria.limpar_tela()
    funcoes_padaria.printmenu()

    # Pega o input do usuário
    try:
        opcao = input("").strip()

        # se for 0 sai Cancelado
        if opcao == "0":
            break

        # Executa a ação da opção escolhida
        acao = opcoes.get(opcao)

        # Checa se o dicionário foi mutado, se for ele salva
        if acao:
            if acao(produtos, seq):
                banco.salvar_dados(produtos, seq[0])
            input("\nPressione [Enter] para voltar ao menu principal...")

        # Se não foi mutado, a única possibilidade é que uma opção inválida foi escolhida
        else:
            print("\n[Erro]: opção inválida!")
            input("\nPressione [Enter] para continuar...")
            continue

    # basicamente trata inputs ilegais do usuário
    except (
        EOFError,
        KeyboardInterrupt,
    ):
        print()
        break

    # Caso uma operação seja cancelavel, cancela
    except funcoes_padaria.Cancelado:
        print("\n[Aviso]: operação cancelada.")
        input("\nPressione [Enter] para voltar ao menu principal...")
        continue


# Limpa a tela e atualiza o banco de dados.
funcoes_padaria.limpar_tela()
banco.salvar_dados(produtos, seq[0])
print("Dados salvos. Encerrando. Até a próxima.")
