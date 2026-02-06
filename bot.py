import os
import time
import requests
import json
import re
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OpenOrderParams
from py_clob_client.order_builder.constants import BUY, SELL

# --- CONFIGURAÇÕES ---
PROXY_ADDRESS = "0x658293eF9454A2DD555eb4afcE6436aDE78ab20B"
BTC_TOKEN_ID = "21639768904545427220464585903669395149753104733036853605098419574581993897148"

# --- GRIDS ---
BTC_GRID = [round(x * 0.01, 2) for x in range(37, 20, -1)]
LULA_GRID = [round(x * 0.01, 2) for x in range(52, 39, -1)]

def extrair_id_limpo(dado):
    """Extrai apenas os números do ID, ignorando colchetes e aspas"""
    if not dado: return None
    # Se for uma lista, pega o primeiro item
    if isinstance(dado, list) and len(dado) > 0:
        dado = dado[0]
    # Usa Regex para pegar apenas a sequência de números longos
    match = re.search(r'\d{30,}', str(dado))
    return match.group(0) if match else None

def buscar_id_lula_v34():
    """Busca o ID do Lula com varredura em múltiplos slugs"""
    slugs = ["brazil-presidential-election-2026", "brazil-presidential-election"]
    for slug in slugs:
        try:
            url = f"https://gamma-api.polymarket.com/events?slug={slug}"
            resp = requests.get(url).json()
            for event in resp:
                for m in event.get("markets", []):
                    if "Lula" in m.get("question", ""):
                        raw_id = m.get("clobTokenIds")
                        clean_id = extrair_id_limpo(raw_id)
                        if clean_id:
                            return clean_id
        except: continue
    return None

def calcular_qtd(preco):
    return 5.0 if preco > 0.20 else round(1.0 / preco, 2)

def main():
    print(">>> 🚀 ROBÔ V34: MODO BLINDADO ATIVADO <<<")
    key = os.getenv("PRIVATE_KEY")
    client = ClobClient("https://clob.polymarket.com/", key=key, chain_id=137, signature_type=2, funder=PROXY_ADDRESS)
    client.set_api_creds(client.create_or_derive_api_creds())

    while True:
        try:
            lula_id = buscar_id_lula_v34()
            ordens = client.get_orders(OpenOrderParams())
            
            # --- BITCOIN ---
            print("\n--- [BITCOIN] ---")
            ativos_btc = [round(float(o.get('price')), 2) for o in ordens if o.get('asset_id') == BTC_TOKEN_ID]
            for p in BTC_GRID:
                if p not in ativos_btc:
                    try:
                        client.create_and_post_order(OrderArgs(price=p, size=calcular_qtd(p), side=BUY, token_id=BTC_TOKEN_ID))
                        print(f"✅ BTC: Compra a ${p}")
                    except: pass

            # --- LULA ---
            if lula_id:
                print(f"--- [LULA - ID: {lula_id[:15]}...] ---")
                ativos_lula = [round(float(o.get('price')), 2) for o in ordens if o.get('asset_id') == lula_id]
                for p in LULA_GRID:
                    if p not in ativos_lula:
                        try:
                            qtd = calcular_qtd(p)
                            client.create_and_post_order(OrderArgs(price=p, size=qtd, side=BUY, token_id=lula_id))
                            print(f"✅ LULA: Compra a ${p}")
                        except Exception as e:
                            if "balance" not in str(e).lower(): print(f"❌ Erro Lula: {e}")
                    
                    # VENDA LULA
                    preco_v = round(p + 0.01, 2)
                    if preco_v not in ativos_lula:
                        try:
                            client.create_and_post_order(OrderArgs(price=preco_v, size=calcular_qtd(p), side=SELL, token_id=lula_id))
                        except: pass
            else:
                print("❌ LULA: Mercado não encontrado. Verifique o Slug.")

        except Exception as e:
            print(f"⚠️ Erro no ciclo: {e}")

        print("\n--- 😴 Aguardando 30s ---")
        time.sleep(30)

if __name__ == "__main__":
    main()
