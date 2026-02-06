import os
import time
import sys
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs
from py_clob_client.order_builder.constants import BUY, SELL

# --- CONFIGURAÇÕES DO MERCADO LULA ---
# TODO: Substitua pelo Token ID do "Yes" no mercado do Lula
TOKEN_ID = "COLE_AQUI_O_TOKEN_ID" 
PROXY_ADDRESS = "0x658293eF9454A2DD555eb4afcE6436aDE78ab20B"
LUCRO = 0.01

# Grid: 0.52 até 0.40 (de 0.01 em 0.01)
GRID_COMPRA = [round(x * 0.01, 2) for x in range(52, 39, -1)]

def get_precos_abertos(client):
    try:
        ordens = client.get_open_orders()
        return [round(float(o.get('price')), 2) for o in ordens if o.get('token_id') == TOKEN_ID]
    except Exception as e:
        print(f"⚠️ Erro ao ler ordens abertas: {e}")
        return []

def calcular_quantidade_minima(preco):
    """Regra: 5 shares se > 0.20, senão $1.00 de valor total"""
    if preco > 0.20:
        return 5.0
    else:
        return round(1.0 / preco, 2)

def main():
    print(">>> 🇧🇷 ROBÔ ELEIÇÕES: LULA YES ATIVADO <<<")
    
    key = os.getenv("PRIVATE_KEY")
    if not key:
        print("❌ ERRO: PRIVATE_KEY não configurada.")
        sys.exit(1)

    client = ClobClient("https://clob.polymarket.com/", key=key, chain_id=137, signature_type=2, funder=PROXY_ADDRESS)
    client.set_api_creds(client.create_or_derive_api_creds())
    
    print(f">>> ✅ Operando no Cofre: {PROXY_ADDRESS}")
    print(f">>> 📊 Grid configurado de {GRID_COMPRA[0]} até {GRID_COMPRA[-1]}")

    while True:
        print("\n--- ⏳ Verificando Status Eleitoral ---")
        precos_ativos = get_precos_abertos(client)
        
        for preco in GRID_COMPRA:
            # 1. LÓGICA DE COMPRA
            if preco not in precos_ativos:
                try:
                    qtd = calcular_quantidade_minima(preco)
                    client.create_and_post_order(
                        OrderArgs(price=preco, size=qtd, side=BUY, token_id=TOKEN_ID)
                    )
                    print(f"✅ COMPRA: {qtd} cotas a ${preco}")
                except Exception as e:
                    if "balance" not in str(e).lower():
                        print(f"❌ Erro em ${preco}: {e}")
            
            # 2. LÓGICA DE VENDA
            preco_venda = round(preco + LUCRO, 2)
            if preco_venda not in precos_ativos:
                try:
                    qtd_v = calcular_quantidade_minima(preco)
                    client.create_and_post_order(
                        OrderArgs(price=preco_venda, size=qtd_v, side=SELL, token_id=TOKEN_ID)
                    )
                    print(f"💰 VENDA: Colocada a ${preco_venda}")
                except:
                    pass 

        print(f"--- Fim do ciclo. Aguardando 120s ---")
        time.sleep(120)

if __name__ == "__main__":
    main()
