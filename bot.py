import os
import time
import requests
import json
import re
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OpenOrderParams
from py_clob_client.order_builder.constants import BUY, SELL

# ==========================================================
# 🎯 CONFIGURAÇÃO MANUAL
# ==========================================================
BTC_TOKEN_ID = "57958928795031811527482965981097791872407665107252816912824758700091189524826" 

# Grid solicitado: 0.37 até 0.30
BTC_GRID = [0.37, 0.36, 0.35, 0.34, 0.33, 0.32, 0.31, 0.30]
LULA_GRID = [round(x * 0.01, 2) for x in range(52, 39, -1)]
# ==========================================================

PROXY_ADDRESS = "0x658293eF9454A2DD555eb4afcE6436aDE78ab20B"

def extrair_id_limpo(dado):
    if not dado: return None
    if isinstance(dado, list) and len(dado) > 0: dado = dado[0]
    match = re.search(r'\d{30,}', str(dado))
    return match.group(0) if match else None

def calcular_qtd(preco):
    return 5.0 if preco > 0.20 else round(1.0 / preco, 2)

def buscar_id_lula_v34():
    url = "https://gamma-api.polymarket.com/events?slug=brazil-presidential-election-2026"
    try:
        resp = requests.get(url).json()
        for event in resp:
            for m in event.get("markets", []):
                if "Lula" in m.get("question", ""):
                    return extrair_id_limpo(m.get("clobTokenIds"))
    except: pass
    return None

def main():
    print(">>> 🚀 ROBÔ V34.4: CORREÇÃO DE VENDAS ATIVADA <<<")
    key = os.getenv("PRIVATE_KEY")
    client = ClobClient("https://clob.polymarket.com/", key=key, chain_id=137, signature_type=2, funder=PROXY_ADDRESS)
    client.set_api_creds(client.create_or_derive_api_creds())

    while True:
        try:
            lula_id = buscar_id_lula_v34()
            ordens = client.get_orders(OpenOrderParams())
            
            # --- BITCOIN (COMPRA E VENDA) ---
            print("\n--- [BITCOIN] ---")
            ativos_btc = [round(float(o.get('price')), 2) for o in ordens if o.get('asset_id') == BTC_TOKEN_ID]
            
            for p in BTC_GRID:
                # 1. Tenta colocar a COMPRA
                if p not in ativos_btc:
                    try:
                        client.create_and_post_order(OrderArgs(price=p, size=calcular_qtd(p), side=BUY, token_id=BTC_TOKEN_ID))
                        print(f"✅ BTC: Compra a ${p}")
                    except: pass
                
                # 2. Tenta colocar a VENDA (sempre +0.01 do preço de compra)
                preco_v = round(p + 0.01, 2)
                if preco_v not in ativos_btc:
                    try:
                        client.create_and_post_order(OrderArgs(price=preco_v, size=calcular_qtd(p), side=SELL, token_id=BTC_TOKEN_ID))
                        print(f"💰 BTC: Venda a ${preco_v}")
                    except: pass

            # --- LULA (COMPRA E VENDA) ---
            if lula_id:
                print(f"--- [LULA] ---")
                ativos_lula = [round(float(o.get('price')), 2) for o in ordens if o.get('asset_id') == lula_id]
                for p in LULA_GRID:
                    if p not in ativos_lula:
                        try:
                            client.create_and_post_order(OrderArgs(price=p, size=calcular_qtd(p), side=BUY, token_id=lula_id))
                            print(f"✅ LULA: Compra a ${p}")
                        except: pass
                    
                    preco_v_lula = round(p + 0.01, 2)
                    if preco_v_lula not in ativos_lula:
                        try:
                            client.create_and_post_order(OrderArgs(price=preco_v_lula, size=calcular_qtd(p), side=SELL, token_id=lula_id))
                        except: pass
        
        except Exception as e:
            print(f"⚠️ Erro no ciclo: {e}")

        time.sleep(30)

if __name__ == "__main__":
    main()
