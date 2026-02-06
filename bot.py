import os
import time
import sys
import requests
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OrderType, Side

# --- CONFIGURAÇÕES ---
MARKET_SLUG = "bitcoin-above-66k-on-february-11"
VALOR_ORDEM_USD = 1.00
LUCRO = 0.01

# Grid de Compra (Acumulação)
GRID_COMPRA_INICIO = 0.40
GRID_COMPRA_FIM = 0.2
PASSO_COMPRA = 0.02

def get_yes_token_id():
    """Busca o ID Hexadecimal do YES"""
    print(f"Buscando ID Real para: {MARKET_SLUG}...")
    try:
        url = f"https://gamma-api.polymarket.com/markets?slug={MARKET_SLUG}"
        resp = requests.get(url).json()
        
        if not resp:
            print("ERRO: Mercado não encontrado na API.")
            return None
        
        market = resp[0]
        # Tenta achar o YES
        try:
            # Procura a posição do "Yes"
            idx = market['outcomes'].index("Yes")
        except:
            idx = 0 # Chute se der erro

        token_id = market['clobTokenIds'][idx]
        
        # Correção de segurança: O ID tem que ser longo (Hex)
        print(f"ID Bruto encontrado: {token_id}")
        return token_id

    except Exception as e:
        print(f"Erro na busca do ID: {e}")
        return None

def main():
    print(">>> ROBÔ GRID REAL MONEY V4 INICIADO <<<")

    # 1. Pega o ID
    token_id = get_yes_token_id()
    if not token_id:
        print("FALHA: Sem ID do mercado.")
        sys.exit(1)

    # 2. Conecta
    key = os.getenv("PRIVATE_KEY")
    if not key:
        print("ERRO: Configure a PRIVATE_KEY no Railway.")
        sys.exit(1)

    try:
        client = ClobClient("https://clob.polymarket.com/", key=key, chain_id=137)
        try:
            client.create_api_key()
        except Exception:
            print("Aviso: Chave de API já existe (Isso é normal). Prosseguindo...")
            
        print(">>> Conectado e pronto para negociar!")
    except Exception as e:
        print(f"Erro crítico de conexão: {e}")
        sys.exit(1)

    # 3. Define os preços
    # Lista de Compras: 0.50, 0.45, 0.40...
    grid_compras = []
    p = GRID_COMPRA_INICIO
    while p >= GRID_COMPRA_FIM:
        grid_compras.append(round(p, 2))
        p -= PASSO_COMPRA
    
    # 4. Loop Infinito de Negociação
    while True:
        print("\n--- Ciclo de Operação (REAL) ---")
        
        # TENTATIVA DE COMPRA (BID)
        for preco in grid_compras:
            try:
                qtd = round(VALOR_ORDEM_USD / preco, 2)
                print(f"Tentando colocar COMPRA: {qtd} cotas a ${preco}...")
                
                resp = client.create_and_post_order(
                    OrderArgs(
                        price=preco,
                        size=qtd,
                        side=Side.BUY,
                        token_id=token_id,
                        order_type=OrderType.LIMIT
                    )
                )
                print(f"-> Ordem de COMPRA enviada! ID: {resp.get('orderID')}")
            except Exception as e:
                # Se der erro (ex: saldo insuficiente), ele avisa mas não para
                print(f"x Falha na compra a ${preco}: {e}")

        # TENTATIVA DE VENDA (ASK) - Lógica Grid Simples
        # Tenta vender um pouco acima de cada nível de compra
        for preco_compra in grid_compras:
            preco_venda = round(preco_compra + LUCRO, 2)
            try:
                # Tenta vender a mesma quantidade (se tiver saldo)
                qtd = round(VALOR_ORDEM_USD / preco_compra, 2)
                
                # Só tenta se o preço fizer sentido (abaixo de 1.00)
                if preco_venda < 1.0:
                    print(f"Verificando VENDA: {qtd} cotas a ${preco_venda}...")
                    resp = client.create_and_post_order(
                        OrderArgs(
                            price=preco_venda,
                            size=qtd,
                            side=Side.SELL,
                            token_id=token_id,
                            order_type=OrderType.LIMIT
                        )
                    )
                    print(f"-> Ordem de VENDA enviada! ID: {resp.get('orderID')}")
            except Exception as e:
                # Erro comum aqui: "Insufficient Balance" (Você ainda não comprou)
                # Vamos silenciar erros de saldo para não sujar o log
                if "balance" not in str(e).lower():
                    print(f"x Falha na venda a ${preco_venda}: {e}")

        print("Ciclo finalizado. Pausa de 30 segundos...")
        time.sleep(30)

if __name__ == "__main__":
    main()
