import os
import time
import requests
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OpenOrderParams
from py_clob_client.order_builder.constants import BUY, SELL

# ==========================================================
# 🛠️ ÁREA DE MUDANÇA SIMPLES (SÓ MEXA AQUI)
# ==========================================================
DATA_BTC  = "February 11"  # Mude para "February 12" quando quiser
PRECO_BTC = "70,000"      # Mude para "66,000", "75,000", etc.
# ==========================================================

PROXY_ADDRESS = "0x658293eF9454A2DD555eb4afcE6436aDE78ab20B"

def buscar_id_btc_automatico(data_alvo, preco_alvo):
    """Acha o ID do Bitcoin baseado na data e preço que você escolheu"""
    try:
        # Busca mercados de Bitcoin ativos
        url = "https://gamma-api.polymarket.com/markets?active=true&closed=false&limit=100&query=Bitcoin"
        markets = requests.get(url).json()
        
        for m in markets:
            q = m.get("question", "")
            # Verifica se a pergunta tem o preço e a data que você quer
            if preco_alvo in q and data_alvo in q:
                ids = m.get("clobTokenIds")
                if ids:
                    import json
                    # Limpa o ID se ele vier como texto
                    clean_id = json.loads(ids.replace("'", '"'))[0] if isinstance(ids, str) else ids[0]
                    print(f"🎯 MERCADO ENCONTRADO: {q}")
                    return clean_id
    except: pass
    return None

def calcular_qtd(preco):
    return 5.0 if preco > 0.20 else round(1.0 / preco, 2)

def main():
    print(f">>> 🚀 ROBÔ V36: BUSCANDO {PRECO_BTC} PARA {DATA_BTC} <<<")
    key = os.getenv("PRIVATE_KEY")
    client = ClobClient("https://clob.polymarket.com/", key=key, chain_id=137, signature_type=2, funder=PROXY_ADDRESS)
    client.set_api_creds(client.create_or_derive_api_creds())

    while True:
        try:
            # Acha o ID do Bitcoin que você configurou no topo
            id_atual = buscar_id_btc_automatico(DATA_BTC, PRECO_BTC)
            
            if not id_atual:
                print(f"⚠️ Não achei o mercado de {PRECO_BTC} para {DATA_BTC}. Verifique se escreveu igual ao site.")
                time.sleep(60)
                continue

            print(f">>> Operando no ID: {id_atual[:10]}...")
            ordens = client.get_orders(OpenOrderParams())
            ativos = [round(float(o.get('price')), 2) for o in ordens if o.get('asset_id') == id_atual]
            
            # Grid Simples (0.50 até 0.01)
            for p in [0.50, 0.40, 0.30, 0.20, 0.10, 0.05, 0.01]:
                if p not in ativos:
                    try:
                        client.create_and_post_order(OrderArgs(price=p, size=calcular_qtd(p), side=BUY, token_id=id_atual))
                        print(f"✅ Compra enviada a ${p}")
                    except: pass
                
                # Venda com lucro de 0.01
                pv = round(p + 0.01, 2)
                if pv not in ativos:
                    try:
                        client.create_and_post_order(OrderArgs(price=pv, size=calcular_qtd(p), side=SELL, token_id=id_atual))
                    except: pass

        except Exception as e:
            print(f"⚠️ Erro: {e}")
        
        print(f"--- 😴 Ciclo finalizado. Próximo em 2 min ---")
        time.sleep(120)

if __name__ == "__main__":
    main()
