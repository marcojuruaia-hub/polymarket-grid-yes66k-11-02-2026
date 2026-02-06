import os
import time
import requests
import json
import re
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OpenOrderParams, BalanceAllowanceParams
from py_clob_client.order_builder.constants import BUY, SELL

# --- CONFIGURAÇÕES ---
PROXY_ADDRESS = "0x658293eF9454A2DD555eb4afcE6436aDE78ab20B"
USDC_E = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
BTC_TOKEN_ID = "21639768904545427220464585903669395149753104733036853605098419574581993896843"

# --- GRIDS ---
BTC_GRID = [0.50, 0.45, 0.40, 0.35, 0.30, 0.25, 0.20, 0.15, 0.10, 0.05, 0.01]
LULA_GRID = [round(x * 0.01, 2) for x in range(52, 39, -1)]

def extrair_id_limpo(dado):
    if not dado: return None
    if isinstance(dado, list) and len(dado) > 0: dado = dado[0]
    match = re.search(r'\d{30,}', str(dado))
    return match.group(0) if match else None

def buscar_id_lula():
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

def exibir_painel(client, ordens, lula_id):
    """Imprime um resumo do estado atual da banca"""
    try:
        # Pega o saldo de USDC.e no Cofre
        bal_resp = client.get_balance_allowance(BalanceAllowanceParams(asset_id=USDC_E))
        saldo = bal_resp.get("balance", "0.00")
        
        # Conta ordens de cada mercado
        btc_ordens = [o for o in ordens if o.get('asset_id') == BTC_TOKEN_ID]
        lula_ordens = [o for o in ordens if o.get('asset_id') == lula_id] if lula_id else []
        
        print("\n" + "═"*40)
        print(f"📊 PAINEL DE CONTROLE - {time.strftime('%H:%M:%S')}")
        print(f"💰 SALDO NO COFRE: ${float(saldo):.2f} USDC")
        print(f"₿ BITCOIN: {len(btc_ordens)} ordens abertas")
        print(f"🇧🇷 LULA: {len(lula_ordens)} ordens abertas")
        print("═"*40)
    except Exception as e:
        print(f"⚠️ Erro ao gerar painel: {e}")

def calcular_qtd(preco):
    return 5.0 if preco > 0.20 else round(1.0 / preco, 2)

def main():
    print(">>> 🚀 ROBÔ V35: MODO ANALÍTICO ATIVADO <<<")
    key = os.getenv("PRIVATE_KEY")
    client = ClobClient("https://clob.polymarket.com/", key=key, chain_id=137, signature_type=2, funder=PROXY_ADDRESS)
    client.set_api_creds(client.create_or_derive_api_creds())

    while True:
        try:
            lula_id = buscar_id_lula()
            ordens = client.get_orders(OpenOrderParams())
            
            # Exibe o Painel Financeiro
            exibir_painel(client, ordens, lula_id)
            
            # --- LOOP BITCOIN ---
            ativos_btc = [round(float(o.get('price')), 2) for o in ordens if o.get('asset_id') == BTC_TOKEN_ID]
            for p in BTC_GRID:
                if p not in ativos_btc:
                    try:
                        client.create_and_post_order(OrderArgs(price=p, size=calcular_qtd(p), side=BUY, token_id=BTC_TOKEN_ID))
                    except: pass

            # --- LOOP LULA ---
            if lula_id:
                ativos_lula = [round(float(o.get('price')), 2) for o in ordens if o.get('asset_id') == lula_id]
                for p in LULA_GRID:
                    if p not in ativos_lula:
                        try:
                            client.create_and_post_order(OrderArgs(price=p, size=calcular_qtd(p), side=BUY, token_id=lula_id))
                        except: pass
                    
                    preco_v = round(p + 0.01, 2)
                    if preco_v not in ativos_lula:
                        try:
                            client.create_and_post_order(OrderArgs(price=preco_
