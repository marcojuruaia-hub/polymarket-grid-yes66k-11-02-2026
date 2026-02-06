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

# O ENDEREÇO QUE VOCÊ ACHOU NO SEU PERFIL DA POLYMARKET
PROXY_ADDRESS = "0x658293eF9454A2DD555eb4afcE6436aDE78ab20B"

def main():
    print(">>> 🚀 ROBÔ V22: CONEXÃO VIA COFRE (GNOSIS SAFE) <<<")
    
    key = os.getenv("PRIVATE_KEY")
    if not key:
        print("❌ ERRO: PRIVATE_KEY não configurada no Railway.")
        sys.exit(1)

    try:
        # INICIALIZAÇÃO CORRETA: Signature Type 2 e Funder explicitado
        client = ClobClient(
            "https://clob.polymarket.com/", 
            key=key, 
            chain_id=137, 
            signature_type=2, 
            funder=PROXY_ADDRESS
        )
        
        print(f">>> 🔗 Conectado! Usando Cofre: {PROXY_ADDRESS}")

        # Autenticação L2 (Cria ou recupera as chaves de API)
        print(">>> 🔐 Configurando credenciais API...")
        client.set_api_creds(client.create_or_derive_api_creds())
        
        print(">>> ✅ TUDO PRONTO! O robô agora tem acesso ao seu saldo.")

    except Exception as e:
        print(f"❌ Erro na inicialização: {e}")
        sys.exit(1)

    # Grid entre 0.50 e 0.30
    grid_compras = [0.50, 0.45, 0.40, 0.35, 0.30]

    while True:
        print("\n--- ⏳ Ciclo de Operação ---")
        
        for preco in grid_compras:
            try:
                qtd = round(VALOR_ORDEM_USD / preco, 2)
                
                # Envia a ordem para o CLOB
                resp = client.create_and_post_order(
                    OrderArgs(
                        price=preco,
                        size=qtd,
                        side=BUY, 
                        token_id=TOKEN_ID
                    )
                )
                
                if resp.get("success") or resp.get("orderID"):
                    print(f"✅ SUCESSO! Compra a ${preco} enviada para o Cofre.")
                else:
                    print(f"❌ Resposta da API: {resp}")
                    
            except Exception as e:
                msg = str(e).lower()
                if "balance" in msg:
                    print(f"⚠️ Saldo insuficiente para ${preco}. Verifique o Cash no site.")
                else:
                    print(f"❌ Erro em ${preco}: {e}")

            # TENTATIVA DE VENDA
            preco_venda = round(preco + LUCRO, 2)
            try:
                qtd_v = round(VALOR_ORDEM_USD / preco, 2)
                client.create_and_post_order(
                    OrderArgs(price=preco_venda, size=qtd_v, side=SELL, token_id=TOKEN_ID)
                )
                print(f"💰 VENDA colocada a ${preco_venda}")
            except:
                pass 

        print(f"--- Fim do ciclo. Aguardando 60s ---")
        time.sleep(60)

if __name__ == "__main__":
    main()
