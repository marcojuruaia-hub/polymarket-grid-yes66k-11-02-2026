import os
import time
import sys
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs
from py_clob_client.order_builder.constants import BUY, SELL

# --- CONFIGURAÇÕES LULA ---
# TODO: Substitua pelo ID que você encontrar
TOKEN_ID = "7060424505324548455115201948842183204938647007786196231016629983411456578033" 
PROXY_ADDRESS = "0x658293eF9454A2DD555eb4afcE6436aDE78ab20B"
LUCRO = 0.01

# Grid: 0.52 até 0.40 (0.01 em 0.01)
GRID_COMPRA = [round(x * 0.01, 2) for x in range(52, 39, -1)]

def get_precos_abertos(client):
    try:
        ordens = client.get_open_orders()
        return [round(float(o.get('price')), 2) for o in ordens if o.get('token_id') == TOKEN_ID]
    except: return []

def calcular_quantidade_minima(preco):
    return 5.0 if preco > 0.20 else round(1.0 / preco, 2)

def main():
    print(">>> 🇧🇷 ROBÔ LULA ATIVADO (SEPARADO) <<<")
    key = os.getenv("PRIVATE_KEY")
    client = ClobClient("https://clob.polymarket.com/", key=key, chain_id=137, signature_type=2, funder=PROXY_ADDRESS)
    client.set_api_creds(client.create_or_derive_api_creds())
    
    print(f">>> ✅ Operando no Cofre: {PROXY_ADDRESS}")

    while True:
        print("\n--- ⏳ Ciclo Eleitoral ---")
        precos_ativos = get_precos_abertos(client)
        
        for preco in GRID_COMPRA:
            if preco not in precos_ativos:
                try:
                    qtd = calcular_quantidade_minima(preco)
                    client.create_and_post_order(OrderArgs(price=preco, size=qtd, side=BUY, token_id=TOKEN_ID))
                    print(f"✅ COMPRA: {qtd} cotas a ${preco}")
                except Exception as e:
                    if "balance" not in str(e).lower(): print(f"❌ Erro: {e}")
            
            preco_venda = round(preco + LUCRO, 2)
            if preco_venda not in precos_ativos:
                try:
                    qtd_v = calcular_quantidade_minima(preco)
                    client.create_and_post_order(OrderArgs(price=preco_venda, size=qtd_v, side=SELL, token_id=TOKEN_ID))
                    print(f"💰 VENDA: ${preco_venda}")
                except: pass 
        time.sleep(120)

if __name__ == "__main__":
    main()
