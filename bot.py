import os
import time
import requests
import re
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OpenOrderParams
from py_clob_client.order_builder.constants import BUY, SELL

# ==========================================================
# 🎯 MUDANÇA SIMPLES (Mude aqui para trocar o alvo)
# ==========================================================
BTC_PRECO_ALVO = "70,000"      # O valor (Ex: 66,000 ou 70,000)
BTC_DATA_ALVO  = "February 12" # A data (Ex: February 11 ou February 12)
# ==========================================================

PROXY_ADDRESS = "0x658293eF9454A2DD555eb4afcE6436aDE78ab20B"

def extrair_id_limpo(dado):
    """Lógica da V34 para IDs numéricos"""
    if not dado: return None
    if isinstance(dado, list) and len(dado) > 0: dado = dado[0]
    match = re.search(r'\d{30,}', str(dado))
    return match.group(0) if match else None

def buscar_id_btc_especifico(preco, data):
    """Busca o ID dentro da 'pasta' de Bitcoin correta"""
    try:
        # Acessamos diretamente o 'Event' que você mandou no link
        url = "https://gamma-api.polymarket.com/events?slug=bitcoin-above-on-february-6"
        resp = requests.get(url).json()
        
        print(f"🔎 Procurando BTC ${preco} para o dia {data}...")
        
        for event in resp:
            for m in event.get("markets", []):
                q = m.get("question", "")
                # Se a pergunta contém o preço (70,000) e a data (February 12)
                if preco in q and data in q:
                    print(f"✅ MERCADO LOCALIZADO: {q}")
                    return extrair_id_limpo(m.get("clobTokenIds"))
        
        print("❌ Não achei essa combinação. Verifique se escreveu igual ao site.")
    except Exception as e:
        print(f"⚠️ Erro ao acessar API: {e}")
    return None

def main():
    print(f">>> 🚀 ROBÔ V40: MODO NAVEGADOR ATIVADO <<<")
    key = os.getenv("PRIVATE_KEY")
    client = ClobClient("https://clob.polymarket.com/", key=key, chain_id=137, signature_type=2, funder=PROXY_ADDRESS)
    client.set_api_creds(client.create_or_derive_api_creds())

    while True:
        try:
            # 1. Localiza o ID do novo alvo
            id_btc = buscar_id_btc_especifico(BTC_PRECO_ALVO, BTC_DATA_ALVO)
            
            if id_btc:
                ordens = client.get_orders(OpenOrderParams())
                ativos = [round(float(o.get('price')), 2) for o in ordens if o.get('asset_id') == id_btc]
                
                # 2. Executa o Grid (0.50 até 0.01)
                for p in [0.50, 0.40, 0.30, 0.20, 0.10, 0.05, 0.01]:
                    if p not in ativos:
                        try:
                            # 5 cotas se > 0.20, senão valor de $1.00
                            qtd = 5.0 if p > 0.20 else round(1.0/p, 2)
                            client.create_and_post_order(OrderArgs(price=p, size=qtd, side=BUY, token_id=id_btc))
                            print(f"✅ Ordem enviada: ${p}")
                        except: pass
            
        except Exception as e:
            print(f"⚠️ Erro no ciclo: {e}")
        
        print("--- 😴 Aguardando 30s ---")
        time.sleep(30)

if __name__ == "__main__":
    main()
