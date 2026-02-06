import os
import time
import sys
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs

# --- CONFIGURAÇÕES ---
TOKEN_ID = "21639768904545427220464585903669395149753104733036853605098419574581993896843"
VALOR_ORDEM_USD = 1.00
LUCRO = 0.01

GRID_COMPRA_INICIO = 0.40
GRID_COMPRA_FIM = 0.10
PASSO_COMPRA = 0.02

def main():
    print(">>> ROBÔ V12: O CAMINHO DA VITÓRIA! 🚀 <<<")
    
    key = os.getenv("PRIVATE_KEY")
    if not key:
        print("ERRO: Configure a PRIVATE_KEY no Railway.")
        sys.exit(1)

    try:
        client = ClobClient("https://clob.polymarket.com/", key=key, chain_id=137)
        # Tenta recuperar ou criar a chave (como é conta nova, ele vai achar rápido)
        try:
            client.derive_api_key()
        except:
            client.create_api_key()
        print(">>> ✅ Conectado e Autenticado!")
    except Exception as e:
        print(f"Erro na conexão: {e}")
        sys.exit(1)

    # Gera lista de preços do grid
    grid_compras = []
    p = GRID_COMPRA_INICIO
    while p >= GRID_COMPRA_FIM:
        grid_compras.append(round(p, 2))
        p -= PASSO_COMPRA
    
    while True:
        print("\n--- Ciclo de Mercado ---")
        
        for preco in grid_compras:
            # 1. TENTATIVA DE COMPRA
            try:
                qtd = round(VALOR_ORDEM_USD / preco, 2)
                resp = client.create_and_post_order(
                    OrderArgs(
                        price=preco,
                        size=qtd,
                        side="BUY", 
                        token_id=TOKEN_ID
                    )
                )
                print(f"✅ COMPRA enviada: {qtd} cotas a ${preco}. ID: {resp.get('orderID')}")
            except Exception as e:
                msg = str(e)
                if "balance" in msg.lower():
                     print(f"⚠️ Saldo insuficiente para comprar a ${preco}")
                else:
                     print(f"❌ Erro na compra (${preco}): {msg}")

            # 2. TENTATIVA DE VENDA (Grid Real)
            preco_venda = round(preco + LUCRO, 2)
            try:
                if preco_venda < 1.0:
                    qtd_v = round(VALOR_ORDEM_USD / preco, 2)
                    resp_v = client.create_and_post_order(
                        OrderArgs(
                            price=preco_venda,
                            size=qtd_v,
                            side="SELL",
                            token_id=TOKEN_ID
                        )
                    )
                    print(f"💰 VENDA enviada: {qtd_v} cotas a ${preco_venda}")
            except:
                pass # Ignora erros de saldo na venda

        print("Aguardando 30 segundos...")
        time.sleep(30)

if __name__ == "__main__":
    main()
