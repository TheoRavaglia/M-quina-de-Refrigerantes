"""
Máquina de refrigerantes em python

Esta é uma simulação de uma máquina de refrigerantes em Python.
A máquina oferece produtos como Coca-Cola, Pepsi, Guaraná Antarctica e Fanta.
Os consumidores podem escolher produtos, efetuar pagamentos com cartão, dinheiro ou Pix,
e a máquina processa as transações, fornecendo troco quando necessário.

Funcionalidades:
- Escolha de produtos e métodos de pagamento (cartão, dinheiro ou Pix) para os consumidores.
- Processamento seguro de pagamentos, incluindo validação de senha para pagamentos com cartão.
- Controle de estoque de produtos e atualização automática após cada venda.
- Controle de moedas e cédulas disponíveis na máquina.
- Registro de histórico de compras associado aos números de telefone para pagamentos Pix.

Como Usar:
1. Execute a função choose_user() para iniciar a interação com a máquina.
2. Escolha entre as opções de Consumidor ou Administrador.
3. Consumidores podem escolher produtos e métodos de pagamento.
4. Administradores têm acesso a opções como visualizar estoque e adicionar dinheiro.
"""
# Código #

import re  # Importar o módulo de expressões regulares

# Lista de produtos
produtos = [
    {"nome": "Coca-Cola[1]", "preco": 4.00, "estoque": 5},
    {"nome": "Pepsi[2]", "preco": 3.50, "estoque": 5},
    {"nome": "Guaraná[3] Antarctica", "preco": 3.00, "estoque": 5},
    {"nome": "Fanta[4]", "preco": 2.50, "estoque": 5},
]

# Dicionário para armazenar o histórico de compras associado ao número de telefone
historico_compras_pix = {}

# Dicionário para armazenar a quantidade de cédulas e moedas disponíveis
quantidade_dinheiro = {
    0.05: 5,  # Moeda de 5 centavos
    0.10: 5,  # Moeda de 10 centavos
    0.25: 5,  # Moeda de 25 centavos
    0.50: 5,  # Moeda de 50 centavos
    1: 5,  # Moeda de 1 real
    2: 5,  # Cédula de 2 reais
    5: 5,  # Cédula de 5 reais
    10: 5,  # Cédula de 10 reais
    20: 5,  # Cédula de 20 reais
}

# Dicionário para mapear os valores das cédulas e moedas
valores_cedulas_moedas = {
    0.05: "Moeda de 5 centavos",
    0.10: "Moeda de 10 centavos",
    0.25: "Moeda de 25 centavos",
    0.50: "Moeda de 50 centavos",
    1: "Moeda de 1 real",
    2: "Cédula de 2 reais",
    5: "Cédula de 5 reais",
    10: "Cédula de 10 reais",
    20: "Cédula de 20 reais",
}

# Funções #

def mostrar_produtos(produtos):
    print("Produtos disponíveis:")
    for produto in produtos:
        print(f"{produto['nome']} - R${produto['preco']:.2f} | Estoque: {produto['estoque']} unidades")

def escolher_produto(produtos):
    mostrar_produtos(produtos)

    opcao_produto = int(input("Escolha um produto digitando o número correspondente: "))

    if 1 <= opcao_produto <= len(produtos):
        produto_escolhido = produtos[opcao_produto - 1]

        if produto_escolhido['estoque'] > 0:
            print(f"Produto escolhido: {produto_escolhido['nome']}. Valor: R${produto_escolhido['preco']:.2f}")
            return produto_escolhido
        else:
            print("Produto fora de estoque. Por favor, escolha outro produto.")
    else:
        print("Opção de produto inválida. Tente novamente.")
    return None

def processar_pagamento_cartao(produto_escolhido):
    confirmacao = input("(Digite a senha do cartão): ")
    print("Pagamento processado. Aguarde seu produto.")
    produto_escolhido['estoque'] -= 1
    return True

def processar_pagamento_dinheiro(produto_escolhido):
    valor_produto = produto_escolhido['preco']
    valor_faltante = 0  # Inicializa o total inserido como zero

    # Variáveis para controlar o troco
    troco_disponivel = quantidade_dinheiro.copy()
    troco = {valor: 0 for valor in troco_disponivel}

    while valor_faltante < valor_produto:
        dinheiro_inserido = float(input(f"Insira o valor em dinheiro (faltam R${valor_produto - valor_faltante:.2f}): R$"))

        if dinheiro_inserido <= 0:
            print("Valor inválido. Insira um valor positivo.")
            continue  # Continuar o loop se o valor for negativo

        if dinheiro_inserido not in valores_cedulas_moedas:
            print("Cédula ou moeda inválida. Insira um valor existente.")
            continue

        # Atualiza o troco e o estoque de moedas e cédulas
        troco_a_devolver = dinheiro_inserido
        troco_adicionado = calcular_troco(troco_a_devolver, troco_disponivel, atualizar_estoque=True)

        incrementar_estoque_dinheiro(troco_adicionado) # Atualiza o estoque antes de subtrair o dinheiro inserido
        valor_faltante += dinheiro_inserido  # Acumula os valores inseridos

        # Atualiza a contagem de notas e moedas no troco
        for valor, quantidade in troco_adicionado.items():
            troco[valor] += quantidade

    troco_a_devolver = valor_faltante - valor_produto
    troco_adicionado = calcular_troco(troco_a_devolver, troco_disponivel, atualizar_estoque=True)

    if tem_troco_suficiente(troco_adicionado, troco_disponivel):
        # Atualiza o estoque antes de subtrair o dinheiro inserido
        atualizar_estoque_dinheiro(troco_adicionado)

        # Exibe o valor do troco
        print(f"Pagamento em dinheiro processado. Troco: R${troco_a_devolver:.2f}. Aguarde seu produto.")
    else:
        # Se não houver troco suficiente, devolve o valor total inserido
        print("Não há troco suficiente na máquina. Insira um valor exato.")

    # Atualiza o estoque
    produto_escolhido['estoque'] -= 1

    # Adiciona detalhes ao histórico de compras
    compra = {
        "produto": produto_escolhido['nome'],
        "valor": produto_escolhido['preco'],
        "metodo_pagamento": "Dinheiro",
        "troco": troco
    }
    adicionar_historico_compras(compra)
    return True

def calcular_troco(valor_troco, troco_disponivel, atualizar_estoque=True):
    troco = {}

    for valor, quantidade in sorted(troco_disponivel.items(), key=lambda x: x[0], reverse=True):
        if valor_troco >= valor:
            max_qtd = min(valor_troco // valor, quantidade)
            valor_troco -= max_qtd * valor
            troco[valor] = max_qtd
            if atualizar_estoque:
                troco_disponivel[valor] -= max_qtd

    return troco if valor_troco == 0 else None

def tem_troco_suficiente(troco, troco_disponivel):
    for valor, quantidade in troco.items():
        if quantidade > troco_disponivel[valor]:
            return False
    return True

def incrementar_estoque_dinheiro(troco):
    for valor, quantidade in troco.items():
        quantidade_dinheiro[valor] += quantidade

#
def atualizar_estoque_dinheiro(troco):
    for valor, quantidade in troco.items():
        quantidade_dinheiro[valor] -= quantidade

def processar_pagamento_pix(produto_escolhido):
    telefone_pix = None
    while telefone_pix is None or not re.match(r'^\d{11}$', telefone_pix):
        telefone_pix = input("Insira o número de telefone para pagamento via Pix: ")

        # Verifica se o número de telefone Pix é válido usando regex
        if not re.match(r'^\d{11}$', telefone_pix):
            print("Número de telefone Pix inválido. Insira um número de telefone válido.")

    compra = {
        "produto": produto_escolhido['nome'],
        "valor": produto_escolhido['preco'],
        "metodo_pagamento": "Pix"
    }

    # Adiciona a contagem de notas e moedas ao histórico
    compra["troco"] = {}  # Certifica-se de que o campo "troco" existe, mesmo que seja vazio
    adicionar_historico_compras(compra, telefone_pix)

    produto_escolhido['estoque'] -= 1
    print("Pagamento via Pix processado. Aguarde seu produto.")
    return True

def processar_pagamento(metodo_pagamento, produto_escolhido):
    if metodo_pagamento == 1:
        return processar_pagamento_cartao(produto_escolhido)
    elif metodo_pagamento == 2:
        return processar_pagamento_dinheiro(produto_escolhido)
    elif metodo_pagamento == 3:
        return processar_pagamento_pix(produto_escolhido)
    else:
        print("Opção de pagamento inválida. Tente novamente.")
    return False

def adicionar_historico_compras(compra, telefone=None):
    # Adiciona a compra ao histórico associado ao número de telefone (ou None se não for Pix)
    if telefone in historico_compras_pix:
        historico_compras_pix[telefone].append(compra)
    else:
        historico_compras_pix[telefone] = [compra]

    # Adiciona a contagem de notas e moedas ao histórico
    if "troco" in compra:
        compra["troco_contagem"] = {valores_cedulas_moedas[valor]: quantidade for valor, quantidade in compra["troco"].items()}
    else:
        compra["troco_contagem"] = {}

def ver_historico_compras():
    print("\nHistórico de Compras por Número de Telefone (Pix):")
    for telefone, compras in historico_compras_pix.items():
        print(f"Telefone: {telefone}")
        for compra in compras:
            print(f"Produto: {compra['produto']}, Valor: R${compra['valor']:.2f}, Método de Pagamento: {compra['metodo_pagamento']}")
        print()

def login_administrador():
    senha_administrador = "1234"
    senha_input = input("Digite a senha do administrador: ")

    if senha_input == senha_administrador:
        menu_administrador()
    else:
        print("Senha incorreta. Tente novamente.")
        login_administrador()

def menu_administrador():
    while True:
        print("\nMenu Administrador:")
        print("Digite 1 para visualizar o estoque de produtos.")
        print("Digite 2 para visualizar a quantidade de cédulas e moedas.")
        print("Digite 3 para adicionar cédulas e moedas.")
        print("Digite 4 para adicionar refrigerantes ao estoque.")
        print("Digite 5 para visualizar o histórico de compras")
        print("Digite 6 para sair do modo administrador.")

        opcao_administrador = int(input("Digite sua opção: "))

        if opcao_administrador == 1:
            visualizar_estoque()
        elif opcao_administrador == 2:
            visualizar_quantidade_dinheiro()
        elif opcao_administrador == 3:
            adicionar_dinheiro()
        elif opcao_administrador == 4:
            adicionar_refrigerante()
        elif opcao_administrador == 5:
             visualizar_historico_compras()
        elif opcao_administrador == 6:
            escolher_usuario()
        else:
            print("Opção inválida. Tente novamente.")

def visualizar_estoque():
    print("\nEstoque de Produtos:")
    for produto in produtos:
        print(f"{produto['nome']} - Estoque: {produto['estoque']} unidades")

def visualizar_quantidade_dinheiro():
    print("\nQuantidade de Cédulas e Moedas:")
    for valor, quantidade in quantidade_dinheiro.items():
        print(f"{valores_cedulas_moedas[valor]} - Quantidade: {quantidade}")

def adicionar_dinheiro():
    while True:
        print("\nAdicionar Cédulas e Moedas:")
        print("Digite 0 para sair.")

        for valor, descricao in valores_cedulas_moedas.items():
            print(f"Digite {valor} para adicionar {descricao}.")

        opcao_adicionar_dinheiro = float(input("Digite sua opção: "))

        if opcao_adicionar_dinheiro == 0:
            break
        elif opcao_adicionar_dinheiro in valores_cedulas_moedas:
            # Verifica se é uma cédula (valor maior que 1) ou uma moeda (valor menor ou igual a 1)
            if opcao_adicionar_dinheiro > 1:
                if opcao_adicionar_dinheiro.is_integer():
                    opcao_adicionar_dinheiro = int(opcao_adicionar_dinheiro)

                quantidade_adicionar = int(input(f"Quantidade de {valores_cedulas_moedas[opcao_adicionar_dinheiro]}: "))
                if quantidade_adicionar < 0:
                    print("Quantidade inválida. Insira um valor positivo.")
                    continue

                quantidade_disponivel = quantidade_dinheiro[opcao_adicionar_dinheiro]
                if quantidade_adicionar > 0:
                    print(f"{quantidade_adicionar} {valores_cedulas_moedas[opcao_adicionar_dinheiro]} adicionadas.")
                    quantidade_dinheiro[opcao_adicionar_dinheiro] += quantidade_adicionar
                else:
                    print("Nenhuma cédula adicionada. Quantidade deve ser maior que zero.")
            else:
                # Moedas aceitam apenas quantidade inteira
                if opcao_adicionar_dinheiro.is_integer():
                    quantidade_adicionar = int(
                        input(f"Quantidade de {valores_cedulas_moedas[opcao_adicionar_dinheiro]}: "))
                    if quantidade_adicionar < 0:
                        print("Quantidade inválida. Insira um valor positivo.")
                        continue

                    quantidade_disponivel = quantidade_dinheiro[opcao_adicionar_dinheiro]
                    if quantidade_adicionar > 0:
                        print(f"{quantidade_adicionar} {valores_cedulas_moedas[opcao_adicionar_dinheiro]} adicionadas.")
                        quantidade_dinheiro[opcao_adicionar_dinheiro] += quantidade_adicionar
                    else:
                        print("Nenhuma moeda adicionada. Quantidade deve ser maior que zero.")
                else:
                    print("Opção inválida. Insira um valor existente para moeda.")
        else:
            print("Opção inválida. Insira um valor existente.")

def adicionar_refrigerante():
    print("\nAdicionar Refrigerantes:")
    mostrar_produtos(produtos)

    escolha_refrigerante = int(input("Escolha o refrigerante para adicionar (digite o número correspondente): "))

    if 1 <= escolha_refrigerante <= len(produtos):
        quantidade_adicionar = int(input("Quantidade de refrigerantes para adicionar (limite máximo: 5): "))

        if 1 <= quantidade_adicionar <= 5:
            # Atualiza o estoque
            produtos[escolha_refrigerante - 1]['estoque'] += quantidade_adicionar
            print(f"{quantidade_adicionar} refrigerante(s) adicionado(s) ao estoque.")
        else:
            print("Quantidade inválida. O limite máximo é 5 refrigerantes.")
    else:
        print("Escolha de refrigerante inválida. Tente novamente.")

def visualizar_historico_compras():
    print("\nHistórico de Compras:")
    for telefone, compras in historico_compras_pix.items():
        print(f"\nTelefone: {telefone}")
        for compra in compras:
            print(f"Produto: {compra['produto']}, Valor: R${compra['valor']:.2f}, "
                  f"Método de Pagamento: {compra['metodo_pagamento']}")
            if 'troco' in compra:
                print("Troco:")
                for cedula_moeda, quantidade in compra['troco_contagem'].items():
                    print(f"{cedula_moeda}: {quantidade}")
        print()

def escolher_usuario():
    while True:
        print('Escolha uma opção')
        print('Digite 1 para consumidor. Digite 2 para Administrador.')

        opcao_usuario = int(input("Digite sua opção: "))

        if opcao_usuario == 1:
            print("Bem-vindo, Consumidor!")
            while True:
                produto_escolhido = escolher_produto(produtos)
                if produto_escolhido:
                    opcao_pagamento = int(input("Escolha um método de pagamento (1 para cartao, 2 para dinheiro, 3 para pix): "))
                    processar_pagamento(opcao_pagamento, produto_escolhido)
                    break
        elif opcao_usuario == 2:
            print("Bem-vindo, Administrador!")
            login_administrador()
            break
        else:
            print("Opção inválida. Por favor, escolha 1 para consumidor ou 2 para administrador.")

escolher_usuario()