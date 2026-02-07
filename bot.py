import sys
# Destrava o log para aparecer na hora
sys.stdout.reconfigure(line_buffering=True)

import os
import time
import requests
import json
import re
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OpenOrderParams
from py_clob_client.order_builder.constants import BUY, SELL

# ==========================================================
# 🎯 MUDANÇA MANUAL
# ==========================================================
BTC_TOKEN_ID = "COLE_O_ID_AQUI" 
# ==========================================================

PROXY_ADDRESS = "0x658293eF9454A2DD555eb4afcE6436aDE78ab20B"

def extrair_id_limpo(dado):
    if not dado: return None
    if isinstance(dado, list) and len(dado) > 0: dado = dado[0]
    match = re.search(r'\d{30,}', str(dado))
    return match.group(0) if match else None

def scanner_bruto_definitivo():
    print("\n" + "═"*60)
    print("🔎 LISTA COMPLETA: BITCOIN UP/DOWN FEB 8")
    print("═"*60)
    try:
        # Busca o evento pelo slug exato que você mandou
        slug = "bitcoin-up-or-down-on-february-8"
        url = f"https://gamma-api.polymarket.com/events?slug={slug}"
        resp = requests.get(url).json()
        
        encontrou = False
        for event in resp:
            print(f"📂 Evento: {event.get('title')}")
            for m in event.get("markets", []):
                q = m.get("question", "")
                ids = m.get("clobTokenIds")
                if ids:
                    clean_id = extrair_id_limpo(ids)
                    print(f"📌 Pergunta: {q}")
                    print(f"👉 ID: {clean_id}")
                    print("-" * 20)
                    encontrou = True
        
        if not encontrou:
            print("⚠️ A API retornou vazio. Verifique se o mercado já não encerrou.")

    except Exception as e:
        print(f"⚠️ Erro no scanner: {e}")
    print("═"*60 + "\n")

def main():
    print(">>> 🚀 ROBÔ V35.3: MODO SCANNER BRUTO <<<")
    key = os.getenv("PRIVATE_KEY")
    client = ClobClient("https://clob.polymarket.com/", key=key, chain_id=137, signature_type=2, funder=PROXY_ADDRESS)
    client.set_api_creds(client.create_or_derive_api_creds())

    # Roda o scanner uma vez
    scanner_bruto_definitivo()

    while True:
        if BTC_TOKEN_ID == "COLE_O_ID_AQUI":
            print("⚠️  Aguardando você copiar o ID do log acima...")
        else:
            print(f">>> Operando no ID: {BTC_TOKEN_ID[:15]}...")
            
        time.sleep(30)

if __name__ == "__main__":
    main()
