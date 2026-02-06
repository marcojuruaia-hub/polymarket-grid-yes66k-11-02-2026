import os
import time
import sys
import requests
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs
from py_clob_client.order_builder.constants import BUY, SELL

# --- CONFIGURAÇÕES ---
PROXY_ADDRESS = "0x658293eF9454A2DD555eb4afcE6436aDE78ab20B"

# BITCOIN
BTC_TOKEN_ID = "21639768904545427220464585903669395149753104733036853605098419574581993896843"
BTC_GRID = [0.50, 0.45, 0.40, 0.35, 0.30, 0.25, 0.20, 0.15, 0.10, 0.05, 0.01]

# LULA (0.52 até 0.40)
LULA_GRID = [round(x * 0.01, 2) for x in range(52, 39, -1)]

def buscar_id_lula_real():
    """Busca o ID atualizado do Lula diretamente na API da Polymarket"""
    try:
        # Slug oficial do mercado de eleições 2026
        url = "https://gamma-api.polymarket.com/events?slug=brazil-presidential-election-2026"
        resp = requests.get(url).json()
        
        # Percorre os mercados dentro do evento para achar o do Lula
        for event in resp:
            for market in event.get("markets", []):
                # Procuramos o nome do Lula e a opção "Yes"
                if "Lula" in market.get("group_name", "") or "Lula" in market.get("question", ""):
                    # Nas eleições, o ID costuma estar em clobTokenId ou nos outcomes
                    outcomes = market.get("clobTokenIds", [])
                    if outcomes:
                        # O primeiro ID costuma ser o 'Yes'
                        return outcomes[0]
        return None
    except Exception as e:
        print(f"⚠️ Erro na busca do ID: {e}")
        return "7060424505324548455115201948842183204938647007786196231016629983411456578033"

def calcular_qtd(preco):
    return 5.0 if preco > 0.20 else round(1.0 / preco, 2)

def main():
    print(">>> 🚀 ROBÔ V27: DIAGNÓSTICO ATIVADO <<<")
    key = os.getenv("PRIVATE_KEY")
    client = ClobClient("https://clob.polymarket.com/", key=key, chain_id=137, signature_type=2, funder=PROXY_ADDRESS)
    client.set_api_creds(client.create_or_derive_api_creds())
    
    lula_id = buscar_id_lula_real()
    print(f">>> 🔎 ID Identificado para o Lula: {lula_id}")

    while True:
        try:
            ordens_abertas = client.get_open_orders()
            
            # --- 📊 MERCADO 1: BITCOIN ---
            print("\n--- [BITCOIN] ---")
            ativos_btc = [round(float(o.get('price')), 2) for o in ordens_abertas if o.get('token_id') == BTC_TOKEN_ID]
            for p in BTC_GRID:
                if p not in ativos_btc:
                    try:
                        client.create_and_post_order(OrderArgs(price=p, size=calcular_qtd(p), side=BUY, token_id=BTC_TOKEN_ID))
                        print(f"✅ Compra BTC a ${p}")
                    except: pass

            # --- 🇧🇷 MERCADO 2: LULA ---
            print("\n--- [LULA] ---")
            if not lula_id:
                print("❌ Não consegui achar o ID do Lula. Pulando...")
            else:
                ativos_lula = [round(float(o.get('price')), 2) for o in ordens_abertas if o.get('token_id') == lula_id]
                print(f"ℹ️ Ordens já abertas no Lula: {ativos_lula}")
                
                for p in LULA_GRID:
                    if p not in ativos_lula:
                        try:
                            qtd = calcular_qtd(p)
                            client.create_and_post_order(OrderArgs(price=p, size=qtd, side=BUY, token_id=lula_id))
                            print(f"✅ Compra LULA a ${p}")
                        except Exception as e:
                            if "balance" not in str(e).lower():
                                print(f"❌ Erro Lula a ${p}: {e}")
                    
                    # VENDA
                    preco_v = round(p + 0.01, 2)
                    if preco_v not in ativos_lula:
                        try:
                            client.create_and_post_order(OrderArgs(price=preco_v, size=calcular_qtd(p), side=SELL, token_id=lula_id))
                        except: pass

        except Exception as e:
            print(f"⚠️ Erro geral: {e}")

        print("\n--- 😴 Aguardando 2 min ---")
        time.sleep(120)

if __name__ == "__main__":
    main()
