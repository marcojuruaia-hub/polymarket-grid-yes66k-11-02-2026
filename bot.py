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
PROXY_ADDRESS = "0x658293eF9454A2DD555eb4afcE6436aDE78ab20B"

GRID_COMPRA = [0.20, 0.15, 0.10, 0.05, 0.01]

def get_precos_abertos(client):
    """Verifica quais preços já têm ordens abertas para evitar duplicidade"""
    try:
        ordens = client.get_open_orders()
        # Filtra apenas as ordens do nosso token específico
        precos = [round(float(o.get('price')), 2) for o in ordens if o.get('token_id') == TOKEN_ID]
        return precos
    except Exception as e:
        print(f"⚠️ Erro ao ler ordens abertas: {e}")
        return []

def main():
    print(">>> 🚀 ROBÔ V23: GRID COM MEMÓRIA ATIVADA <<<")
    
    key = os.getenv("PRIVATE_KEY")
    client = ClobClient("https://clob.polymarket.com/", key=key, chain_id=137, signature_type=2, funder=PROXY_ADDRESS)
    client.set_api_creds(client.create_or_derive_api_creds())
    
    print(f">>> ✅ Operando no Cofre: {PROXY_ADDRESS}")

    while True:
        print("\n--- ⏳ Verificando Status das Ordens ---")
        precos_ativos = get_precos_abertos(client)
        print(f">>> Preços já listados no site: {precos_ativos}")
        
        for preco in GRID_COMPRA:
            # --- LÓGICA DE COMPRA ---
            if preco not in precos_ativos:
                try:
                    qtd = round(VALOR_ORDEM_USD / preco, 2)
                    client.create_and_post_order(
                        OrderArgs(price=preco, size=qtd, side=BUY, token_id=TOKEN_ID)
                    )
                    print(f"✅ NOVA COMPRA: Enviada a ${preco}")
                except Exception as e:
                    if "balance" in str(e).lower():
                        print(f"⚠️ Saldo insuficiente para ${preco} (Ordens abertas ocupam saldo)")
                    else:
                        print(f"❌ Erro em ${preco}: {e}")
            else:
                print(f"ℹ️ Pulando ${preco}: Já existe uma ordem aberta.")

            # --- LÓGICA DE VENDA (Só coloca se a compra sumir e a venda não existir) ---
            preco_venda = round(preco + LUCRO, 2)
            if preco_venda not in precos_ativos:
                try:
                    # O robô tentará vender. Se você não tiver as cotas, a API negará automaticamente.
                    client.create_and_post_order(
                        OrderArgs(price=preco_venda, size=round(VALOR_ORDEM_USD/preco, 2), side=SELL, token_id=TOKEN_ID)
                    )
                    print(f"💰 NOVA VENDA: Colocada a ${preco_venda}")
                except:
                    pass 

        print(f"--- Fim do ciclo. Aguardando 2 minutos ---")
        time.sleep(120) # Aumentei para 2 min para evitar excesso de requisições

if __name__ == "__main__":
    main()
