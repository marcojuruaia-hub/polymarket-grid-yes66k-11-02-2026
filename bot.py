import os
import time
import requests
import re
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OpenOrderParams
from py_clob_client.order_builder.constants import BUY, SELL

# ==========================================================
# 🎮 CONFIGURAÇÃO RÁPIDA (Dica: Use termos simples como "70,000" e "Feb")
# ==========================================================
BTC_PRECO = "70,000"      
BTC_DATA  = "February 11"  
# ==========================================================

PROXY_ADDRESS = "0x658293eF9454A2DD555eb4afcE6436aDE78ab20B"

def extrair_id_limpo(dado):
    if not dado: return None
    if isinstance(dado, list) and len(dado) > 0: dado = dado[0]
    match = re.search(r'\d{30,}', str(dado))
    return match.group(0) if match else None

def buscar_id_btc_inteligente(preco, data):
    """Busca o ID e lista sugestões se não encontrar"""
    try:
        url = "https://gamma-api.polymarket.com/markets?active=true&closed=false&limit=50&query=Bitcoin"
        markets = requests.get(url).json()
        sugestoes = []
        
        for m in markets:
            q = m.get("question", "")
            sugestoes.append(q)
            # Busca ignorando maiúsculas/minúsculas
            if preco.lower() in q.lower() and data.lower() in q.lower():
                return extrair_id_limpo(m.get("clobTokenIds")), q
        
        # Se não achou, mostra o que tem disponível no Log para ajudar o usuário
        print(f"🔎 Não achei '{preco}' '{data}'. Mercados disponíveis no site agora:")
        for s in sugestoes[:5]: # Mostra os 5 principais
            print(f"   -> {s}")
            
    except Exception as e:
        print(f"⚠️ Erro na busca: {e}")
    return None, None

def buscar_id_lula():
    # Lógica da V34 que já sabemos que funciona
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
    print(f">>> 🚀 ROBÔ V38: BUSCANDO BTC {BTC_PRECO} EM {BTC_DATA} <<<")
    key = os.getenv("PRIVATE_KEY")
    client = ClobClient("https://clob.polymarket.com/", key=key, chain_id=137, signature_type=2, funder=PROXY_ADDRESS)
    client.set_api_creds(client.create_or_derive_api_creds())

    while True:
        try:
            id_btc, nome_btc = buscar_id_btc_inteligente(BTC_PRECO, BTC_DATA)
            id_lula = buscar_id_lula()
            ordens = client.get_orders(OpenOrderParams())
            
            # --- OPERAÇÃO BITCOIN ---
            if id_btc:
                print(f"✅ OPERANDO BTC: {nome_btc}")
                # (Lógica de compra/venda simplificada aqui...)
                ativos = [round(float(o.get('price')), 2) for o in ordens if o.get('asset_id') == id_btc]
                for p in [0.50, 0.40, 0.30, 0.20, 0.10, 0.05, 0.01]:
                    if p not in ativos:
                        try:
                            client.create_and_post_order(OrderArgs(price=p, size=5.0 if p > 0.20 else round(1.0/p, 2), side=BUY, token_id=id_btc))
                        except: pass
            
            # --- OPERAÇÃO LULA ---
            if id_lula:
                print("✅ OPERANDO LULA")
                # (Lógica do Lula da V34...)
                # ... [mesmo código de grid do Lula que já funciona] ...

        except Exception as e:
            print(f"⚠️ Erro no ciclo: {e}")

        time.sleep(120)

if __name__ == "__main__":
    main()
