import os
import time
import sys
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs
from py_clob_client.order_builder.constants import BUY, SELL

# --- PARÂMETROS ---
TOKEN_ID = "21639768904545427220464585903669395149753104733036853605098419574581993896843"
VALOR_ORDEM_USD = 5.00  
LUCRO = 0.01

GRID_COMPRA_INICIO = 0.50
GRID_COMPRA_FIM = 0.30
PASSO_COMPRA = 0.05

def main():
    print(">>> 🚀 ROBÔ V18: AGUARDANDO DEPÓSITO <<<")
    
    key = os.getenv("PRIVATE_KEY")
    if not key:
        print("❌ ERRO: Configure a PRIVATE_KEY no Railway.")
        sys.exit(1)

    try:
        # Inicialização simples e direta
        client = ClobClient("https://clob.polymarket.com/", key=key, chain_id=137, signature_type=0)
        
        print(">>> 🔐 Autenticando...")
        creds = client.create_or_derive_api_creds()
        client.set_api_creds(creds)
        print(">>> ✅ Login efetuado com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        sys.exit(1)

    grid_compras = [0.50, 0.45, 0.40, 0.35, 0.30]

    while True:
        print("\n--- ⏳ Ciclo de Operação ---")
        for preco in grid_compras:
            # COMPRA
            try:
                qtd = round(VALOR_ORDEM_USD / preco, 2)
                resp = client.create_and_post_order(
                    OrderArgs(price=preco, size=qtd, side=BUY, token_id=TOKEN_ID)
                )
                print(f"✅ COMPRA: {qtd} cotas a ${preco}. ID: {resp.get('orderID')}")
            except Exception as e:
                msg = str(e).lower()
                if "balance" in msg:
                    print(f"⚠️ Saldo zero no Cash da Polymarket. Faça o 'Deposit' no site!")
                else:
                    print(f"❌ Erro em ${preco}: {e}")

            # VENDA
            preco_venda = round(preco + LUCRO, 2)
            try:
                qtd_v = round(VALOR_ORDEM_USD / preco, 2)
                client.create_and_post_order(
                    OrderArgs(price=preco_venda, size=qtd_v, side=SELL, token_id=TOKEN_ID)
                )
                print(f"💰 VENDA colocada a ${preco_venda}")
            except:
                pass 

        print(f"--- Aguardando 60 segundos ---")
        time.sleep(60)

if __name__ == "__main__":
    main()
