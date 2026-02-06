import os
import time
import sys
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs
from py_clob_client.order_builder.constants import BUY, SELL
from eth_account import Account

# --- CONFIGURAÇÕES ---
TOKEN_ID = "21639768904545427220464585903669395149753104733036853605098419574581993896843"
VALOR_ORDEM_USD = 5.00  
LUCRO = 0.01

GRID_COMPRA_INICIO = 0.50
GRID_COMPRA_FIM = 0.30
PASSO_COMPRA = 0.05

def main():
    print(">>> 🚀 ROBÔ V21: FORÇANDO ONBOARDING <<<")
    
    key = os.getenv("PRIVATE_KEY")
    if not key:
        print("❌ ERRO: PRIVATE_KEY não configurada.")
        sys.exit(1)

    # Verifica qual endereço estamos usando
    try:
        acct = Account.from_key(key)
        print(f">>> 🏠 Endereço da Carteira: {acct.address}")
    except:
        pass

    try:
        # Inicializa o cliente
        client = ClobClient("https://clob.polymarket.com/", key=key, chain_id=137, signature_type=0)
        
        # 1. TENTATIVA DE ONBOARDING (A "Chave" que falta)
        print(">>> 📑 Tentando Onboarding oficial...")
        try:
            client.onboard_user()
            print(">>> ✅ Onboarding concluído!")
        except Exception as e:
            print(f">>> ⚠️ Onboarding já feito ou erro: {e}")

        # 2. AUTENTICAÇÃO
        print(">>> 🔐 Gerando credenciais de API...")
        creds = client.create_or_derive_api_creds()
        client.set_api_creds(creds)
        
        # 3. BUSCA DO PROXY
        proxy_address = client.get_proxy_address()
        if proxy_address:
            print(f">>> ✅ COFRE LOCALIZADO: {proxy_address}")
        else:
            print(">>> ❌ Proxy continua None. Tentando prosseguir...")

    except Exception as e:
        print(f"❌ Erro fatal na conexão: {e}")
        sys.exit(1)

    grid_compras = [0.50, 0.45, 0.40, 0.35, 0.30]

    while True:
        print(f"\n--- ⏳ Ciclo de Operação (Cofre: {proxy_address}) ---")
        
        for preco in grid_compras:
            try:
                qtd = round(VALOR_ORDEM_USD / preco, 2)
                resp = client.create_and_post_order(
                    OrderArgs(price=preco, size=qtd, side=BUY, token_id=TOKEN_ID)
                )
                
                if resp.get("success") or resp.get("orderID"):
                    print(f"✅ SUCESSO! Compra a ${preco} enviada.")
                else:
                    print(f"❌ Erro na ordem: {resp}")
                    
            except Exception as e:
                msg = str(e).lower()
                if "balance" in msg:
                    print(f"⚠️ Saldo ainda não reconhecido para ${preco}.")
                else:
                    print(f"❌ Erro em ${preco}: {e}")

        print(f"--- Fim do ciclo. Aguardando 60s ---")
        time.sleep(60)

if __name__ == "__main__":
    main()
