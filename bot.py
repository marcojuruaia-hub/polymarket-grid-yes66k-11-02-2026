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
    print(">>> 🚀 ROBÔ V20: LOCALIZADOR DE COFRE <<<")
    
    key = os.getenv("PRIVATE_KEY")
    if not key:
        print("❌ ERRO: PRIVATE_KEY não configurada.")
        sys.exit(1)

    try:
        # Inicializa o cliente (Chain 137 = Polygon)
        client = ClobClient("https://clob.polymarket.com/", key=key, chain_id=137, signature_type=0)
        
        print(">>> 🔐 Autenticando...")
        creds = client.create_or_derive_api_creds()
        client.set_api_creds(creds)
        
        # --- BUSCA FORÇADA DO PROXY ---
        print(">>> 🕵️ Localizando endereço do Proxy (Cofre)...")
        proxy_address = None
        
        try:
            proxy_address = client.get_proxy_address()
            if proxy_address:
                print(f">>> ✅ COFRE LOCALIZADO: {proxy_address}")
            else:
                print(">>> ⚠️ Proxy retornou vazio. Tentando inicializar...")
        except:
            print(">>> ⚠️ Erro ao buscar Proxy. Sua conta pode precisar de uma ação manual no site.")

    except Exception as e:
        print(f"❌ Erro na conexão inicial: {e}")
        sys.exit(1)

    grid_compras = [0.50, 0.45, 0.40, 0.35, 0.30]

    while True:
        print(f"\n--- ⏳ Ciclo de Operação (Proxy: {proxy_address}) ---")
        
        for preco in grid_compras:
            try:
                # O valor mínimo na API costuma ser mais rigoroso que no site
                qtd = round(VALOR_ORDEM_USD / preco, 2)
                
                resp = client.create_and_post_order(
                    OrderArgs(
                        price=preco,
                        size=qtd,
                        side=BUY, 
                        token_id=TOKEN_ID
                    )
                )
                
                if resp.get("success"):
                    print(f"✅ SUCESSO! Compra a ${preco} enviada.")
                else:
                    print(f"❌ Resposta da API: {resp}")
                    
            except Exception as e:
                msg = str(e).lower()
                if "balance" in msg:
                    print(f"⚠️ Saldo insuficiente para ${preco}. Verifique se o depósito caiu no site.")
                elif "allowance" in msg:
                    print(f"⚠️ Erro de permissão: USDC não aprovado.")
                else:
                    print(f"❌ Erro em ${preco}: {e}")

        print(f"--- Fim do ciclo. Aguardando 60s ---")
        time.sleep(60)

if __name__ == "__main__":
    main()
