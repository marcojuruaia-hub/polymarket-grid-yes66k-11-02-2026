import sys
# --- COMANDO PARA DESTRAVAR LOGS NO RAILWAY ---
sys.stdout.reconfigure(line_buffering=True)
# ----------------------------------------------

import os
import time
import requests
import json
import re
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OpenOrderParams
from py_clob_client.order_builder.constants import BUY, SELL

# ==========================================================
# 🎯 MUDANÇA MANUAL (Cole aqui o ID quando o log mostrar)
# ==========================================================
BTC_TOKEN_ID = "COLE_O_ID_AQUI" 
# ==========================================================

PROXY_ADDRESS = "0x658293eF9454A2DD555eb4afcE6436aDE78ab20B"

def extrair_id_limpo(dado):
    if not dado: return None
    if isinstance(dado, list) and len(dado) > 0: dado = dado[0]
    match = re.search(r'\d{30,}', str(dado))
    return match.group(0) if match else None

def scanner_up_down_730():
    """Escaneia especificamente o horário das 7:30-7:45"""
    print("\n" + "═"*60)
    print("🔎 BUSCANDO ID: BITCOIN 7:30AM - 7:45AM ET (FEB 7)")
    print("═"*60)
    try:
        # Tenta buscar pelo evento geral do dia 7
        url = "https://gamma-api.polymarket.com/events?slug=bitcoin-up-or-down-on-february-7"
        resp = requests.get(url).json()
        
        encontrou = False
        for event in resp:
            for m in event.get("markets", []):
                q = m.get("question", "")
                # Filtra pelo horário específico
                if "7:30" in q and "7:45" in q:
                    ids = m.get("clobTokenIds")
                    if ids:
                        clean_id = extrair_id_limpo(ids)
                        print(f"📌 MERCADO ENCONTRADO: {q}")
                        print(f"👉 ID 'YES' PARA COPIAR: {clean_id}\n")
                        encontrou = True
        
        if not encontrou:
            print("⚠️ Não achei esse horário específico na lista geral.")
            print("Tentando busca ampla por '7:30'...")
            # Busca alternativa
            url_alt = "https://gamma-api.polymarket.com/markets?active=true&query=Bitcoin%207:30&limit=20"
            resp_alt = requests.get(url_alt).json()
            for m in resp_alt:
                q = m.get("question", "")
                if "7:45" in q and "Feb" in q:
                     print(f"📌 {q}")
                     print(f"👉 ID 'YES' PARA COPIAR: {extrair_id_limpo(m.get('clobTokenIds'))}\n")

    except Exception as e:
        print(f"⚠️ Erro no scanner: {e}")
    print("═"*60 + "\n")

def main():
    print(">>> 🚀 ROBÔ V35.2: SCANNER DE EMERGÊNCIA (7:30-7:45) <<<")
    key = os.getenv("PRIVATE_KEY")
    client = ClobClient("https://clob.polymarket.com/", key=key, chain_id=137, signature_type=2, funder=PROXY_ADDRESS)
    client.set_api_creds(client.create_or_derive_api_creds())

    # Roda o scanner focado no horário
    scanner_up_down_730()

    while True:
        if BTC_TOKEN_ID == "COLE_O_ID_AQUI":
            print("⚠️  Aguardando ID... (Copie do log acima)")
        else:
            print(f">>> Operando no ID: {BTC_TOKEN_ID[:15]}...")
            # (Sua lógica de operação aqui...)
            
        time.sleep(30)

if __name__ == "__main__":
    main()
