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
BTC_TOKEN_ID = "35318893558430035110899642976572154099643885812628890621430761251325731975007" 

# BTC: Gera de 0.36 até 0.30 (diminuindo de 0.01 em 0.01)
BTC_GRID = [round(x * 0.01, 2) for x in range(36, 29, -1)]

# LULA: Gera de 0.52 até 0.40
LULA_GRID = [round(x * 0.01, 2) for x in range(52, 39, -1)]

PROXY_ADDRESS = "0x658293eF9454A2DD555eb4afcE6436aDE78ab20B"
# ==========================================================

def extrair_id_limpo(dado):
    if not dado: return None
    if isinstance(dado, list) and len(dado) > 0: dado = dado[0]
    match = re.search(r'\d{30,}', str(dado))
    return match.group(0) if match else None

def calcular_qtd(preco):
    return 5.0 if preco > 0.20 else round(1.0 / preco, 2)

def buscar_id_lula_robusto():
    slugs = ["brazil-presidential-election-2026", "brazil-presidential-election"]
    for slug in slugs:
        try:
            url = f"https://gamma-api.polymarket.com/events?slug={slug}"
            resp = requests.get(url).json()
            for event in resp:
                for m in event.get("markets", []):
                    if "Lula" in m.get("question", ""):
                        return extrair_id_limpo(m.get("clobTokenIds"))
        except: continue
    return None

def main():
    print(f">>> 🚀 ROBÔ V34.7: GRIDS INTELIGENTES <<<")
    print(f"GRID BTC: {BTC_GRID}")
    
    key = os.getenv("PRIVATE_KEY")
    client = ClobClient("https://clob.polymarket.com/", key=key, chain_id=137, signature_type=2, funder=PROXY_ADDRESS)
    client.set_api_creds(client.create_or_derive_api_creds())

    while True:
        try:
            lula_id = buscar_id_lula_robusto()
            todas_ordens = client.get_orders(OpenOrderParams())
            
            # --- BITCOIN ---
            print("\n--- [BITCOIN] ---")
            compras_btc = [round(float(o.get('price')), 2) for o in todas_ordens if o.get('asset_id') == BTC_TOKEN_ID and o.get('side') == BUY]
            vendas_btc  = [round(float(o.get('price')), 2) for o in todas_ordens if o.get('asset_id') == BTC_TOKEN_ID and o.get('side') == SELL]
            
            for p in BTC_GRID:
                if p not in compras_btc:
                    try:
                        client.create_and_post_order(OrderArgs(price=p, size=calcular_qtd(p), side=BUY, token_id=BTC_TOKEN_ID))
                        print(f"✅ BTC: Compra a ${p}")
                    except: pass
                
                pv = round(p + 0.01, 2)
                if pv not in vendas_btc:
                    try:
                        client.create_and_post_order(OrderArgs(price=pv, size=calcular_qtd(p), side=SELL, token_id=BTC_TOKEN_ID))
                        print(f"💰 BTC: Venda a ${pv}")
                    except: pass

            # --- LULA ---
            if lula_id:
                print(f"--- [LULA] ---")
                compras_lula = [round(float(o.get('price')), 2) for o in todas_ordens if o.get('asset_id') == lula_id and o.get('side') == BUY]
                vendas_lula  = [round(float(o.get('price')), 2) for o in todas_ordens if o.get('asset_id') == lula_id and o.get('side') == SELL]
                
                for p in LULA_GRID:
                    if p not in compras_lula:
                        try:
                            client.create_and_post_order(OrderArgs(price=p, size=calcular_qtd(p), side=BUY, token_id=lula_id))
                            print(f"✅ LULA: Compra a ${p}")
                        except: pass
                    
                    pv_lula = round(p + 0.01, 2)
                    if pv_lula not in vendas_lula:
                        try:
                            client.create_and_post_order(OrderArgs(price=pv_lula, size=calcular_qtd(p), side=SELL, token_id=lula_id))
                            print(f"💰 LULA: Venda a ${pv_lula}")
                        except: pass
            else:
                print("⚠️ Lula não encontrado (tentando novamente...)")

        except Exception as e:
            print(f"⚠️ Erro no ciclo: {e}")

        time.sleep(30)

if __name__ == "__main__":
    main()
