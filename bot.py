import os
import time
import sys
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs
from py_clob_client.order_builder.constants import BUY, SELL

# --- PARÂMETROS OTIMIZADOS ---
TOKEN_ID = "21639768904545427220464585903669395149753104733036853605098419574581993896843"
VALOR_ORDEM_USD = 5.00  
LUCRO = 0.01

GRID_COMPRA_INICIO = 0.50
GRID_COMPRA_FIM = 0.30
PASSO_COMPRA = 0.05

def main():
    print(">>> 🚀 ROBÔ V17: OPERAÇÃO LIMPA <<<")
    
    key = os.getenv("PRIVATE_KEY")
    if not key:
        print("❌ ERRO: Configure a PRIVATE_KEY no Railway.")
        sys.exit(1)

    try:
        # Inicialização estável
        client = ClobClient("https://clob.polymarket.com/", key=key, chain_id=137, signature_type=0)
        
        print(">>> 🔐 Autenticando...")
        creds = client.create_or_derive_api_creds()
        client.set_api_creds(creds)
        print(">>> ✅ Autenticação concluída.")
        
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        sys.exit(1)

    # Criando o grid: 0.50, 0.45, 0.40, 0.35, 0.30
    grid_compras = []
    p = GRID_COMPRA_INICIO
    while p >= GRID_COMPRA_FIM:
        grid_compras.append(round(p, 2))
        p -= PASSO_COMPRA

    while True:
        print("\n--- ⏳ Ciclo de Operação ---")
        
        for preco in grid_compras:
            # 1. TENTATIVA DE COMPRA
            try:
                qtd = round(VALOR_ORDEM_USD / preco, 2)
                resp = client.create_and_post_order(
                    OrderArgs(
                        price=preco,
                        size=qtd,
                        side=BUY, 
                        token_id=TOKEN_ID
                    )
                )
                print(f"✅ COMPRA: {qtd} cotas a ${preco}. ID: {resp.get('orderID')}")
            except Exception as e:
                msg = str(e).lower()
                if "balance" in msg:
                    print(f"⚠️ Saldo insuficiente para ${preco}. Verifique se você tem USDC.e (bridged) e não o USDC nativo.")
                elif "allowance" in msg:
                    print(f"⚠️ Erro de Allowance: Você precisa aprovar o USDC no site da Polymarket uma vez.")
                else:
                    print(f"❌ Erro na compra a ${preco}: {e}")

            # 2. TENTATIVA DE VENDA
            preco_venda = round(preco + LUCRO, 2)
            try:
                qtd_v = round(VALOR_ORDEM_USD / preco, 2)
                client.create_and_post_order(
                    OrderArgs(
                        price=preco_venda,
                        size=qtd_v,
                        side=SELL,
                        token_id=TOKEN_ID
                    )
                )
                print(f"💰 VENDA colocada a ${preco_venda}")
            except:
                pass 

        print(f"--- Aguardando 60 segundos ---")
        time.sleep(60)

if __name__ == "__main__":
    main()
