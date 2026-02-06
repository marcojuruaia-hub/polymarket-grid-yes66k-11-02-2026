import os
import time
import sys
import requests
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OpenOrderParams
from py_clob_client.order_builder.constants import BUY, SELL

# --- CONFIGURAÇÕES ---
PROXY_ADDRESS = "0x658293eF9454A2DD555eb4afcE6436aDE78ab20B"

# ID BITCOIN
BTC_TOKEN_ID = "21639768904545427220464585903669395149753104733036853605098419574581993896843"
BTC_GRID = [0.50, 0.45, 0.40, 0.35, 0.30, 0.25, 0.20, 0.15, 0.10, 0.05, 0.01]

# ID LULA YES (Confirmado para o mercado 2026)
LULA_TOKEN_ID = "7060424505324548455115201948842183204938647007786196231016629983411456578033"
LULA_GRID = [round(x * 0.01, 2) for x in range(52, 39, -1)]

def calcular_qtd(preco):
    return 5.0 if preco > 0.20 else round(1.0 / preco, 2)

def main():
    print(">>> 🚀 ROBÔ V28: CORREÇÃO DE COMANDOS <<<")
    
    key = os.getenv("PRIVATE_KEY")
    if not key:
        print("❌ ERRO: Adicione a PRIVATE_KEY no Railway!")
        return

    # Inicialização (Signature Type 2 para MetaMask/Gnosis Safe)
    client = ClobClient("https://clob.polymarket.com/", key=key, chain_id=137, signature_type=2, funder=PROXY_ADDRESS)
    client.set_api_creds(client.create_or_derive_api_creds())
    
    print(f">>> ✅ Conectado ao Cofre: {PROXY_ADDRESS}")

    while True:
        try:
            # CORREÇÃO: O método correto é get_orders(OpenOrderParams())
            print(">>> Lendo ordens abertas...")
            ordens_abertas = client.get_orders(OpenOrderParams())
            
            # --- 📊 MERCADO 1: BITCOIN ---
            print("\n--- [BITCOIN] ---")
            ativos_btc = [round(float(o.get('price')), 2) for o in ordens_abertas if o.get('asset_id') == BTC_TOKEN_ID]
            for p in BTC_GRID:
                if p not in ativos_btc:
                    try:
                        client.create_and_post_order(OrderArgs(price=p, size=calcular_qtd(p), side=BUY, token_id=BTC_TOKEN_ID))
                        print(f"✅ Compra BTC a ${p}")
                    except: pass

            # --- 🇧🇷 MERCADO 2: LULA ---
            print("\n--- [LULA] ---")
            ativos_lula = [round(float(o.get('price')), 2) for o in ordens_abertas if o.get('asset_id') == LULA_TOKEN_ID]
            print(f"ℹ️ Ordens ativas no Lula: {ativos_lula}")
            
            for p in LULA_GRID:
                if p not in ativos_lula:
                    try:
                        qtd = calcular_qtd(p)
                        client.create_and_post_order(OrderArgs(price=p, size=qtd, side=BUY, token_id=LULA_TOKEN_ID))
                        print(f"✅ Compra LULA a ${p}")
                    except Exception as e:
                        if "balance" not in str(e).lower():
                            print(f"❌ Erro Lula a ${p}: {e}")
                
                # VENDA LULA
                preco_v = round(p + 0.01, 2)
                if preco_v not in ativos_lula:
                    try:
                        client.create_and_post_order(OrderArgs(price=preco_v, size=calcular_qtd(p), side=SELL, token_id=LULA_TOKEN_ID))
                    except: pass

        except Exception as e:
            print(f"⚠️ Erro no ciclo: {e}")

        print("\n--- 😴 Aguardando 120s ---")
        time.sleep(120)

if __name__ == "__main__":
    main()
