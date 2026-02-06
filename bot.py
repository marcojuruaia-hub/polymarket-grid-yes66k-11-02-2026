import os
import time
import requests
import json
import re
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OpenOrderParams
from py_clob_client.order_builder.constants import BUY, SELL

# ==========================================================
# 🎮 CONFIGURAÇÃO RÁPIDA (Mude aqui igual está no site)
# ==========================================================
BTC_PRECO = "70,000"      # Ex: "66,000", "70,000", "75,000"
BTC_DATA  = "February 11"  # Ex: "February 11", "February 12"
# ==========================================================

PROXY_ADDRESS = "0x658293eF9454A2DD555eb4afcE6436aDE78ab20B"

def extrair_id_limpo(dado):
    """Lógica da V34 para limpar colchetes e aspas do ID"""
    if not dado: return None
    if isinstance(dado, list) and len(dado) > 0: dado = dado[0]
    match = re.search(r'\d{30,}', str(dado))
    return match.group(0) if match else None

def buscar_id_btc_dinamico(preco, data):
    """Procura o ID do BTC baseado no texto do site"""
    try:
        url = "https://gamma-api.polymarket.com/markets?active=true&closed=false&limit=100&query=Bitcoin"
        markets = requests.get(url).json()
        for m in markets:
            pergunta = m.get("question", "")
            # Se a pergunta tiver o preço E a data que você escolheu
            if preco in pergunta and data in pergunta:
                return extrair_id_limpo(m.get("clobTokenIds"))
    except: return None

def buscar_id_lula_v34():
    """Lógica da V34 que você já validou"""
    for slug in ["brazil-presidential-election-2026", "brazil-presidential-election"]:
        try:
            url = f"https://gamma-api.polymarket.com/events?slug={slug}"
            resp = requests.get(url).json()
            for event in resp:
                for m in event.get("markets", []):
                    if "Lula" in m.get("question", ""):
                        return extrair_id_limpo(m.get("clobTokenIds"))
        except: continue
    return None

def calcular_qtd(preco):
    return 5.0 if preco > 0.20 else round(1.0 / preco, 2)

def main():
    print(f">>> 🚀 ROBÔ V37: BUSCANDO BTC {BTC_PRECO} EM {BTC_DATA} <<<")
    key = os.getenv("PRIVATE_KEY")
    client = ClobClient("https://clob.polymarket.com/", key=key, chain_id=137, signature_type=2, funder=PROXY_ADDRESS)
    client.set_api_creds(client.create_or_derive_api_creds())

    while True:
        try:
            # Acha os IDs dinamicamente
            id_btc = buscar_id_btc_dinamico(BTC_PRECO, BTC_DATA)
            id_lula = buscar_id_lula_v34()
            
            ordens = client.get_orders(OpenOrderParams())
            
            # --- OPERAÇÃO BITCOIN ---
            if id_btc:
                print(f"₿ BTC ATIVO: {BTC_PRECO} ({BTC_DATA})")
                ativos_btc = [round(float(o.get('price')), 2) for o in ordens if o.get('asset_id') == id_btc]
                for p in [0.50, 0.45, 0.40, 0.35, 0.30, 0.25, 0.20, 0.15, 0.10, 0.05, 0.01]:
                    if p not in ativos_btc:
                        try:
                            client.create_and_post_order(OrderArgs(price=p, size=calcular_qtd(p), side=BUY, token_id=id_btc))
                            print(f"✅ BTC: Compra a ${p}")
                        except: pass
            else:
                print(f"⚠️ BTC: Não achei o mercado {BTC_PRECO} {BTC_DATA} no site.")

            # --- OPERAÇÃO LULA ---
            if id_lula:
                print(f"🇧🇷 LULA ATIVO")
                ativos_lula = [round(float(o.get('price')), 2) for o in ordens if o.get('asset_id') == id_lula]
                for p in [round(x * 0.01, 2) for x in range(52, 39, -1)]:
                    if p not in ativos_lula:
                        try:
                            client.create_and_post_order(OrderArgs(price=p, size=calcular_qtd(p), side=BUY, token_id=id_lula))
                            print(f"✅ LULA: Compra a ${p}")
                        except: pass
            
        except Exception as e:
            print(f"⚠️ Erro no ciclo: {e}")

        print(f"\n--- 😴 Aguardando 30s ---")
        time.sleep(30)

if __name__ == "__main__":
    main()
