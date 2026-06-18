def salvar_dados(dicionario):
    with open("banco_dados.json", "w", encoding="utf-8") as arquivo:
        for id_produto, dados in dicionario.items():
            linha = f"{id_produto}|{dados['nome']}|{dados['preco']}|{dados['estoque']}\n"
            arquivo.write(linha)


def carregar_dados():
    try:
        with open("banco_dados.json", "r", encoding="utf-8") as arquivo:
            linhas = arquivo.readlines()
    except FileNotFoundError:
        return {}

    dicionario = {}
    for linha in linhas:
        linha = linha.strip()
        if not linha:
            continue

        partes = linha.split("|")
        if len(partes) != 4:
            continue

        try:
            id_produto = int(partes[0])
            nome = partes[1]
            preco = float(partes[2])
            estoque = int(partes[3])
        except (ValueError, IndexError):
            print("[Aviso]: arquivo de dados corrompido. Iniciando com banco vazio.")
            return {}

        dicionario[id_produto] = {"nome": nome, "preco": preco, "estoque": estoque}

    return dicionario
