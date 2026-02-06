import os
import time
import sys
import threading
import requests
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs
from py_clob_client.order_builder.constants import BUY, SELL

# --- CONFIGURAÇÕES ---
PROXY_ADDRESS = "0x658293eF9454A2DD555eb4afcE6436aDE78ab20B"
USDC_E = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174" # Endereço do USDC.e na Polygon

# Configuração Bitcoin (Mercado 1)
BTC_TOKEN_ID = "21639768904545427220464585903669395149753104733036853605098419574581993896843"
BTC_GRID = [0.50, 0.45, 0.40, 0.35, 0.30, 0.25, 0.20, 0.15, 0.10, 0.05, 0.01]

# Configuração Lula (Mercado 2)
LULA_SLUG = "brazil-presidential-election-2026"
LULA_GRID = [round(x * 0.01, 2) for x in range(52, 39, -1)]

def get_lula_token_id():
    """Tenta buscar o ID do Lula automaticamente via API"""
    try:
        url = f"https://gamma-api.polymarket.com/markets?slug={LULA_SLUG}"
        resp = requests.get(url).json()
        for market in resp:
            if "Luiz Inácio Lula da Silva" in market.get("question", ""):
                # O ID costuma vir como uma string longa no campo clobTokenId
                return market.get("clobTokenId")
    except:
        return None
    return None

def calcular_qtd(preco):
    return 5.0 if preco > 0.20 else round(1.0 / preco, 2)

def executar_grid(client, nome, token_id, grid, lucro=0.01):
    """Função que gerencia o grid de um mercado específico"""
    print(f"\n--- 📊 Verificando {nome} ---")
    try:
        ordens = client.get_open_orders()
        ativos = [round(float(o.get('price')), 2) for o in ordens if o.get('token_id') == token_id]
        
        for preco in grid:
            # COMPRA
            if preco not in ativos:
                try:
                    qtd = calcular_qtd(preco)
                    client.create_and_post_order(OrderArgs(price=preco, size=qtd, side=BUY, token_id=token_id))
                    print(f"✅ {nome} COMPRA: {qtd} a ${preco}")
                except Exception as e:
                    if "balance" not in str(e).lower(): print(f"❌ Erro {nome}: {e}")
            
            # VENDA
            preco_venda = round(preco + lucro, 2)
            if preco_venda not in ativos:
                try:
                    qtd_v = calcular_qtd(preco)
                    client.create_and_post_order(OrderArgs(price=preco_venda, size=qtd_v, side=SELL, token_id=token_id))
                    print(f"💰 {nome} VENDA: ${preco_venda}")
                except: pass
    except Exception as e:
        print(f"⚠️ Erro no loop de {nome}: {e}")

def main():
    print(">>> 🚀 ROBÔ V26: SISTEMA UNIFICADO (MULTI-MERCADO) <<<")
    key = os.getenv("PRIVATE_KEY")
    if not key:
        print("❌ ERRO: Adicione a PRIVATE_KEY no Railway!")
        return

    client = ClobClient("https://clob.polymarket.com/", key=key, chain_id=137, signature_type=2, funder=PROXY_ADDRESS)
    client.set_api_creds(client.create_or_derive_api_creds())
    
    # Busca o ID do Lula (Se não achar, usa um padrão ou avisa)
    lula_id = get_lula_token_id()
    if not lula_id:
        print("⚠️ Não achei o ID do Lula automaticamente. Usando ID padrão...")
        lula_id = "7060424505324548455115201948842183204938647007786196231016629983411456578033"

    while True:
        # Roda o Bitcoin
        executar_grid(client, "BITCOIN", BTC_TOKEN_ID, BTC_GRID)
        
        # Roda o Lula
        executar_grid(client, "LULA", lula_id, LULA_GRID)
        
        print("\n--- 😴 Fim do ciclo. Aguardando 120s ---")
        time.sleep(120)

if __name__ == "__main__":
    main()
