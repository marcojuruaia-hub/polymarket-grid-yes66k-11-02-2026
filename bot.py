import os
import time
import sys
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs
from py_clob_client.order_builder.constants import BUY, SELL

# --- CONFIGURAÇÕES ---
TOKEN_ID = "21639768904545427220464585903669395149753104733036853605098419574581993896843"
VALOR_ORDEM_USD = 5.00  
LUCRO = 0.01
GRID_COMPRA_INICIO = 0.50
GRID_COMPRA_FIM = 0.30
PASSO_COMPRA = 0.05

def main():
    print(">>> 🚀 ROBÔ V19: MODO DETETIVE <<<")
    
    key = os.getenv("PRIVATE_KEY")
    if not key:
        print("❌ ERRO: PRIVATE_KEY não encontrada.")
        sys.exit(1)

    try:
        # Inicializa o cliente
        client = ClobClient("https://clob.polymarket.com/", key=key, chain_id=137, signature_type=0)
        
        print(">>> 🔐 Autenticando...")
        creds = client.create_or_derive_api_creds()
        client.set_api_creds(creds)
        
        # --- VERIFICAÇÃO DE SALDO REAL ---
        print(">>> 🕵️ Verificando carteiras...")
        try:
            proxy = client.get_proxy_address()
            print(f">>> 🏦 Endereço do Cofre (Proxy): {proxy}")
        except:
            print(">>> ⚠️ Não foi possível localizar o endereço do Proxy.")

    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        sys.exit(1)

    grid_compras = [0.50, 0.45, 0.40, 0.35, 0.30]

    while True:
        print("\n--- ⏳ Iniciando Ciclo de Ordens ---")
        
        for preco in grid_compras:
            try:
                qtd = round(VALOR_ORDEM_USD / preco, 2)
                
                # Criando a ordem
                resp = client.create_and_post_order(
                    OrderArgs(
                        price=preco,
                        size=qtd,
                        side=BUY, 
                        token_id=TOKEN_ID
                    )
                )
                
                if resp.get("success") or resp.get("orderID"):
                    print(f"✅ SUCESSO! Compra a ${preco} enviada.")
                else:
                    print(f"❌ Resposta estranha da API: {resp}")
                    
            except Exception as e:
                msg = str(e).lower()
                if "balance" in msg:
                    print(f"⚠️ Saldo insuficiente para ${preco}. O robô não está vendo o Cash.")
                elif "minimum" in msg or "size" in msg:
                    print(f"❌ Ordem negada: Valor ${VALOR_ORDEM_USD} é muito baixo para este mercado.")
                else:
                    print(f"❌ Erro técnico em ${preco}: {e}")

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

        print(f"--- Fim do Ciclo. Dormindo 60s ---")
        time.sleep(60)

if __name__ == "__main__":
    main()
