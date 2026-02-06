import os
import time
import requests
import json
import re
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OpenOrderParams
from py_clob_client.order_builder.constants import BUY, SELL

# ==========================================================
# 🎯 MUDANÇA MANUAL (Cole aqui o ID que você escolher do log)
# ==========================================================
BTC_TOKEN_ID = "21639768904545427220464585903669395149753104733036853605098419574581993897148"
# ==========================================================

PROXY_ADDRESS = "0x658293eF9454A2DD555eb4afcE6436aDE78ab20B"
BTC_GRID = [0.50, 0.45, 0.40, 0.35, 0.30, 0.25, 0.20, 0.15, 0.10, 0.05, 0.01]
LULA_GRID = [round(x * 0.01, 2) for x in range(52, 39, -1)]

def extrair_id_limpo(dado):
    if not dado: return None
    if isinstance(dado, list) and len(dado) > 0: dado = dado[0]
    match = re.search(r'\d{30,}', str(dado))
    return match.group(0) if match else None

def scanner_futuro():
    """Escaneia mercados de Bitcoin para os dias 11 e 12"""
    print("\n" + "═"*60)
    print("🔎 BUSCANDO MERCADOS PARA 11 E 12 DE FEVEREIRO...")
    print("═"*60)
    try:
        # Busca ampla por Bitcoin
        url = "https://gamma-api.polymarket.com/markets?active=true&query=Bitcoin&limit=100"
        resp = requests.get(url).json()
        encontrados = 0
        for m in resp:
            q = m.get("question", "")
            # Filtra apenas dias 11 e 12
            if ("February 11" in q or "February 12" in q) and "Bitcoin" in q:
                ids = m.get("clobTokenIds")
                if ids:
                    clean_id = extrair_id_limpo(ids)
                    print(f"📌 {q}")
                    print(f"👉 ID PARA COPIAR: {clean_id}\n")
                    encontrados += 1
        if encontrados == 0:
            print("⚠️ Nenhum mercado para dia 11 ou 12 encontrado na busca rápida.")
            print("Tentando busca por evento...")
            # Tentativa alternativa via Slug de evento
            url_alt = "https://gamma-api.polymarket.com/events?slug=bitcoin-above-on-february-11"
            resp_alt = requests.get(url_alt).json()
            for e in resp_alt:
                for m in e.get("markets", []):
                    print(f"📌 {m.get('question')}")
                    print(f"👉 ID PARA COPIAR: {extrair_id_limpo(m.get('clobTokenIds'))}\n")
    except Exception as e:
        print(f"⚠️ Erro no scanner: {e}")
    print("═"*60 + "\n")

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

def calcular_qtd(preco):
    return 5.0 if preco > 0.20 else round(1.0 / preco, 2)

def main():
    print(">>> 🚀 ROBÔ V34.2: SCANNER 11/12 FEV ATIVADO <<<")
    key = os.getenv("PRIVATE_KEY")
    client = ClobClient("https://clob.polymarket.com/", key=key, chain_id=137, signature_type=2, funder=PROXY_ADDRESS)
    client.set_api_creds(client.create_or_derive_api_creds())

    # Roda o scanner focado no futuro
    scanner_futuro()

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
                        print(f"✅ BTC: Ordem a ${p}")
                    except: pass

            # --- LULA ---
            if lula_id:
                print(f"--- [LULA] ---")
                ativos_lula = [round(float(o.get('price')), 2) for o in ordens if o.get('asset_id') == lula_id]
                for p in LULA_GRID:
                    if p not in ativos_lula:
                        try:
                            client.create_and_post_order(OrderArgs(price=p, size=calcular_qtd(p), side=BUY, token_id=lula_id))
                        except: pass
        except Exception as e:
            print(f"⚠️ Erro: {e}")
        time.sleep(30)

if __name__ == "__main__":
    main()
