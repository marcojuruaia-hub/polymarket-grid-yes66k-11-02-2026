import os
import time
import requests
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OpenOrderParams
from py_clob_client.order_builder.constants import BUY, SELL

# --- CONFIGURAÇÕES ---
PROXY_ADDRESS = "0x658293eF9454A2DD555eb4afcE6436aDE78ab20B"
BTC_TOKEN_ID = "21639768904545427220464585903669395149753104733036853605098419574581993896843"

# --- COLE O ID QUE VOCÊ ACHAR NA URL AQUI ---
LULA_TOKEN_ID = "COLE_O_ID_DA_URL_AQUI" 

def main():
    print(">>> 🕵️ ROBÔ V31: MODO DETETIVE ATIVADO <<<")
    key = os.getenv("PRIVATE_KEY")
    client = ClobClient("https://clob.polymarket.com/", key=key, chain_id=137, signature_type=2, funder=PROXY_ADDRESS)
    client.set_api_creds(client.create_or_derive_api_creds())

    while True:
        try:
            # TENTA BUSCAR O ID AUTOMATICAMENTE SE VOCÊ NÃO COLOU
            if LULA_TOKEN_ID == "COLE_O_ID_DA_URL_AQUI":
                print("🔎 Buscando IDs de eleição na API...")
                url = "https://gamma-api.polymarket.com/events?slug=brazil-presidential-election-2026"
                data = requests.get(url).json()
                for event in data:
                    for m in event.get("markets", []):
                        q = m.get("question", "")
                        ids = m.get("clobTokenIds", [])
                        print(f"📌 Mercado: {q} | IDs: {ids}")
            
            print("\n>>> Lendo ordens...")
            ordens = client.get_orders(OpenOrderParams())
            
            # (O resto do código de Bitcoin continua igual aqui...)
            # ... mas foque no log acima para achar o ID correto!

        except Exception as e:
            print(f"⚠️ Erro: {e}")
        
        time.sleep(60)

if __name__ == "__main__":
    main()
