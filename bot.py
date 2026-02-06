import os
import time
import sys
import requests
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OrderType
# Removi o 'Side' daqui de cima pois ele estava causando o erro

# --- CONFIGURAÇÕES ---
MARKET_SLUG = "bitcoin-above-66k-on-february-11"
VALOR_ORDEM_USD = 5.00
LUCRO = 0.01

# Grid de Compra
GRID_COMPRA_INICIO = 0.50
GRID_COMPRA_FIM = 0.10
PASSO_COMPRA = 0.05

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
        try:
            idx = market['outcomes'].index("Yes")
        except:
            idx = 0 

        token_id = market['clobTokenIds'][idx]
        print(f"ID Bruto encontrado: {token_id}")
        return token_id

    except Exception as e:
        print(f"Erro na busca do ID: {e}")
        return None

def main():
    print(">>> ROBÔ GRID REAL MONEY V5 (FIX IMPORT) <<<")

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
            pass # Chave ja existe
            
        print(">>> Conectado e pronto para negociar!")
    except Exception as e:
        print(f"Erro crítico de conexão: {e}")
        sys.exit(1)

    # 3. Define os preços
    grid_compras = []
    p = GRID_COMPRA_INICIO
    while p >= GRID_COMPRA_FIM:
        grid_compras.append(round(p, 2))
        p -= PASSO_COMPRA
    
    # 4. Loop Infinito
    while True:
        print("\n--- Ciclo de Operação (REAL) ---")
        
        # COMPRA (BID)
        for preco in grid_compras:
            try:
                qtd = round(VALOR_ORDEM_USD / preco, 2)
                #print(f"Tentando colocar COMPRA: {qtd} cotas a ${preco}...")
                
                resp = client.create_and_post_order(
                    OrderArgs(
                        price=preco,
                        size=qtd,
                        side="BUY",  # <--- MUDANÇA AQUI (Texto simples)
                        token_id=token_id,
                        order_type=OrderType.LIMIT
                    )
                )
                print(f"-> Ordem de COMPRA enviada! ID: {resp.get('orderID')}")
            except Exception as e:
                if "balance" not in str(e).lower():
                    pass # Ignora erros menores para não sujar o log

        # VENDA (ASK)
        for preco_compra in grid_compras:
            preco_venda = round(preco_compra + LUCRO, 2)
            try:
                qtd = round(VALOR_ORDEM_USD / preco_compra, 2)
                
                if preco_venda < 1.0:
                    #print(f"Verificando VENDA: {qtd} cotas a ${preco_venda}...")
                    resp = client.create_and_post_order(
                        OrderArgs(
                            price=preco_venda,
                            size=qtd,
                            side="SELL", # <--- MUDANÇA AQUI (Texto simples)
                            token_id=token_id,
                            order_type=OrderType.LIMIT
                        )
                    )
                    print(f"-> Ordem de VENDA enviada! ID: {resp.get('orderID')}")
            except Exception as e:
                pass 

        print("Ciclo finalizado. Pausa de 30 segundos...")
        time.sleep(30)

if __name__ == "__main__":
    main()
