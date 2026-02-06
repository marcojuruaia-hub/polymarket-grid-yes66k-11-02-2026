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
    print(">>> ROBÔ GRID V7 (FINAL) <<<")
    
    key = os.getenv("PRIVATE_KEY")
    if not key:
        print("ERRO: Sem PRIVATE_KEY.")
        sys.exit(1)

    try:
        client = ClobClient("https://clob.polymarket.com/", key=key, chain_id=137)
        try:
            client.create_api_key()
        except:
            pass 
        print(">>> Conectado!")
    except Exception as e:
        print(f"Erro Conexão: {e}")
        sys.exit(1)

    # Cria lista de preços
    grid_compras = []
    p = GRID_COMPRA_INICIO
    while p >= GRID_COMPRA_FIM:
        grid_compras.append(round(p, 2))
        p -= PASSO_COMPRA
    
    while True:
        print("\n--- Tentando Operar ---")
        
        # --- COMPRA ---
        for preco in grid_compras:
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
                print(f"✅ SUCESSO! Compra colocada a ${preco}. ID: {resp.get('orderID')}")
            except Exception as e:
                msg = str(e)
                if "balance" in msg.lower():
                     print(f"⚠️ Saldo insuficiente para comprar a ${preco}")
                else:
                     print(f"❌ Erro ao comprar a ${preco}: {msg}")

        # --- VENDA ---
        for preco_compra in grid_compras:
            preco_venda = round(preco_compra + LUCRO, 2)
            try:
                qtd = round(VALOR_ORDEM_USD / preco_compra, 2)
                if preco_venda < 1.0:
                    resp = client.create_and_post_order(
                        OrderArgs(
                            price=preco_venda,
                            size=qtd,
                            side="SELL",
                            token_id=TOKEN_ID
                        )
                    )
                    print(f"💰 VENDA colocada a ${preco_venda}. ID: {resp.get('orderID')}")
            except Exception as e:
                pass 

        print("Aguardando 30 segundos...")
        time.sleep(30)

if __name__ == "__main__":
    main()
    
