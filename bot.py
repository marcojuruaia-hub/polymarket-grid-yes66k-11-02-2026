import os
import time
import requests
import json
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OpenOrderParams
from py_clob_client.order_builder.constants import BUY, SELL

# --- CONFIGURAÇÕES FIXAS ---
PROXY_ADDRESS = "0x658293eF9454A2DD555eb4afcE6436aDE78ab20B"
BTC_TOKEN_ID = "21639768904545427220464585903669395149753104733036853605098419574581993896843"

# --- CONFIGURAÇÕES DE GRID ---
BTC_GRID = [0.50, 0.45, 0.40, 0.35, 0.30, 0.25, 0.20, 0.15, 0.10, 0.05, 0.01]
LULA_GRID = [round(x * 0.01, 2) for x in range(52, 39, -1)]

def buscar_id_lula():
    """Busca o ID do Lula e limpa caracteres extras se necessário"""
    try:
        url = "https://gamma-api.polymarket.com/events?slug=brazil-presidential-election-2026"
        resp = requests.get(url).json()
        for event in resp:
            for m in event.get("markets", []):
                if "Lula" in m.get("question", ""):
                    ids = m.get("clobTokenIds")
                    # Se vier como string ["123"], transformamos em lista real
                    if isinstance(ids, str):
                        ids = json.loads(ids.replace("'", '"'))
                    return ids[0] if ids else None
    except Exception as e:
        print(f"⚠️ Erro ao buscar ID do Lula: {e}")
    return None

def calcular_qtd(preco):
    """Regra: 5 shares se > 0.20, senão $1.00 de valor total"""
    return 5.0 if preco > 0.20 else round(1.0 / preco, 2)

def main():
    print(">>> 🚀 ROBÔ V33: BITCOIN + LULA (ID AUTO) <<<")
    key = os.getenv("PRIVATE_KEY")
    client = ClobClient("https://clob.polymarket.com/", key=key, chain_id=137, signature_type=2, funder=PROXY_ADDRESS)
    client.set_api_creds(client.create_or_derive_api_creds())

    while True:
        try:
            # 1. Busca ID do Lula dinamicamente
            lula_id = buscar_id_lula()
            
            print("\n>>> Lendo ordens abertas...")
            ordens = client.get_orders(OpenOrderParams())
            
            # --- LOOP BITCOIN ---
            print("--- [BITCOIN] ---")
            ativos_btc = [round(float(o.get('price')), 2) for o in ordens if o.get('asset_id') == BTC_TOKEN_ID]
            for p in BTC_GRID:
                if p not in ativos_btc:
                    try:
                        client.create_and_post_order(OrderArgs(price=p, size=calcular_qtd(p), side=BUY, token_id=BTC_TOKEN_ID))
                        print(f"✅ BTC: Compra a ${p}")
                    except: pass

            # --- LOOP LULA ---
            if lula_id:
                print(f"--- [LULA - ID: {lula_id[:10]}...] ---")
                ativos_lula = [round(float(o.get('price')), 2) for o in ordens if o.get('asset_id') == lula_id]
                for p in LULA_GRID:
                    if p not in ativos_lula:
                        try:
                            qtd = calcular_qtd(p)
                            client.create_and_post_order(OrderArgs(price=p, size=qtd, side=BUY, token_id=lula_id))
                            print(f"✅ LULA: Compra a ${p}")
                        except Exception as e:
                            if "balance" in str(e).lower(): print(f"⚠️ Sem saldo para Lula a ${p}")
                    
                    # VENDA LULA (Lucro 0.01)
                    preco_v = round(p + 0.01, 2)
                    if preco_v not in ativos_lula:
                        try:
                            client.create_and_post_order(OrderArgs(price=preco_v, size=calcular_qtd(p), side=SELL, token_id=lula_id))
                        except: pass
            else:
                print("❌ LULA: ID não encontrado neste ciclo.")

        except Exception as e:
            print(f"⚠️ Erro no ciclo: {e}")

        print("\n--- 😴 Aguardando 2 minutos ---")
        time.sleep(120)

if __name__ == "__main__":
    main()
