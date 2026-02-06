import os
import time
import requests
import re
import json
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OpenOrderParams
from py_clob_client.order_builder.constants import BUY, SELL

# ==========================================================
# 🎯 CONFIGURAÇÃO RÁPIDA
# ==========================================================
BTC_PRECO_ALVO = "70,000"      # O robô vai limpar o "$" e a "," sozinho
BTC_DATA_ALVO  = "February 12" # Escreva o mês e o dia
INTERVALO      = 30            # Tempo de espera em segundos
# ==========================================================

PROXY_ADDRESS = "0x658293eF9454A2DD555eb4afcE6436aDE78ab20B"

def extrair_id_limpo(dado):
    if not dado: return None
    if isinstance(dado, list) and len(dado) > 0: dado = dado[0]
    match = re.search(r'\d{30,}', str(dado))
    return match.group(0) if match else None

def limpar_texto(texto):
    """Remove $, vírgulas e espaços para comparação segura"""
    return re.sub(r'[$,\s]', '', str(texto)).lower()

def buscar_id_btc_flexivel(preco, data):
    """Busca o ID com tolerância a erros de digitação/formatação"""
    try:
        url = "https://gamma-api.polymarket.com/events?slug=bitcoin-above-on-february-6"
        resp = requests.get(url).json()
        
        preco_limpo = limpar_texto(preco)
        data_limpa = limpar_texto(data)
        
        print(f"🔎 Analisando opções para {preco} em {data}...")
        
        for event in resp:
            for m in event.get("markets", []):
                q = m.get("question", "")
                q_limpa = limpar_texto(q)
                
                # Verifica se o preço e a data estão na pergunta de forma flexível
                if preco_limpo in q_limpa and data_limpa in q_limpa:
                    print(f"✅ MERCADO BTC ENCONTRADO: {q}")
                    return extrair_id_limpo(m.get("clobTokenIds"))
        
        print("❌ BTC: Não encontrei esse mercado. Verifique a lista no log acima.")
    except Exception as e:
        print(f"⚠️ Erro ao acessar API: {e}")
    return None

def buscar_id_lula():
    """Lógica da V34 que varre os mercados do Lula"""
    try:
        url = "https://gamma-api.polymarket.com/events?slug=brazil-presidential-election-2026"
        resp = requests.get(url).json()
        for event in resp:
            for m in event.get("markets", []):
                if "Lula" in m.get("question", ""):
                    return extrair_id_limpo(m.get("clobTokenIds"))
    except: pass
    return None

def calcular_qtd(preco):
    return 5.0 if preco > 0.20 else round(1.0/preco, 2)

def main():
    print(f">>> 🚀 ROBÔ V41: BTC ({BTC_PRECO_ALVO}) + LULA ATIVADOS <<<")
    key = os.getenv("PRIVATE_KEY")
    client = ClobClient("https://clob.polymarket.com/", key=key, chain_id=137, signature_type=2, funder=PROXY_ADDRESS)
    client.set_api_creds(client.create_or_derive_api_creds())

    while True:
        try:
            # 1. Localiza os IDs
            id_btc = buscar_id_btc_flexivel(BTC_PRECO_ALVO, BTC_DATA_ALVO)
            id_lula = buscar_id_lula()
            
            ordens = client.get_orders(OpenOrderParams())
            
            # --- OPERAÇÃO BITCOIN ---
            if id_btc:
                ativos_btc = [round(float(o.get('price')), 2) for o in ordens if o.get('asset_id') == id_btc]
                for p in [0.50, 0.40, 0.30, 0.20, 0.10, 0.05, 0.01]:
                    if p not in ativos_btc:
                        try:
                            client.create_and_post_order(OrderArgs(price=p, size=calcular_qtd(p), side=BUY, token_id=id_btc))
                            print(f"✅ BTC: Compra a ${p}")
                        except: pass
            
            # --- OPERAÇÃO LULA ---
            if id_lula:
                print("--- [LULA ATIVO] ---")
                ativos_lula = [round(float(o.get('price')), 2) for o in ordens if o.get('asset_id') == id_lula]
                # Grid Lula: 0.52 até 0.40
                for p in [round(x * 0.01, 2) for x in range(52, 39, -1)]:
                    if p not in ativos_lula:
                        try:
                            client.create_and_post_order(OrderArgs(price=p, size=calcular_qtd(p), side=BUY, token_id=id_lula))
                            print(f"✅ LULA: Compra a ${p}")
                        except: pass

        except Exception as e:
            print(f"⚠️ Erro no ciclo: {e}")
        
        print(f"--- 😴 Aguardando {INTERVALO}s ---")
        time.sleep(INTERVALO)

if __name__ == "__main__":
    main()
