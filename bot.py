import os
import time
import sys
import requests
from py_clob_client.client import ClobClient

# --- CONFIGURAÇÕES ---
# Slug exato da aposta (copiado do seu link)
MARKET_SLUG = "bitcoin-above-66k-on-february-11"

# Seus valores:
VALOR_ORDEM_USD = 5.00
GRID_INICIAL = 0.40
GRID_FINAL = 0.10
PASSO = 0.05

def get_yes_token_id():
    """Busca o ID do YES direto no mercado"""
    print(f"Buscando ID para: {MARKET_SLUG}...")
    try:
        # Usa o endpoint de Markets (mais preciso que Events)
        url = f"https://gamma-api.polymarket.com/markets?slug={MARKET_SLUG}"
        resp = requests.get(url).json()

        if not resp:
            print("ERRO: A API não encontrou esse mercado. Verifique o link.")
            return None
        
        market = resp[0] # Pega o primeiro resultado
        
        # Lógica inteligente para achar o 'YES'
        # A API retorna outcomes tipo ["No", "Yes"] ou ["Yes", "No"]
        try:
            index_yes = market['outcomes'].index("Yes") # Descobre em qual posição está o Yes
        except ValueError:
            # Caso esteja escrito de forma diferente (ex: YES, Sim)
            index_yes = 1 if "Yes" in str(market['outcomes']) else 0

        token_id = market['clobTokenIds'][index_yes]
        print(f"SUCESSO! Mercado: {market['question']}")
        print(f"ID do YES encontrado: {token_id}")
        return token_id

    except Exception as e:
        print(f"Erro na busca: {e}")
        return None

def main():
    print(">>> Iniciando Robô Grid v3 (Busca Direta)...")

    # 1. Pega o ID
    token_id = get_yes_token_id()
    if not token_id:
        print("FALHA FATAL: Não temos o ID para negociar.")
        sys.exit(1)

    # 2. Conecta
    key = os.getenv("PRIVATE_KEY")
    if not key:
        print("ERRO: PRIVATE_KEY não configurada no Railway.")
        sys.exit(1)

    try:
        client = ClobClient("https://clob.polymarket.com/", key=key, chain_id=137)
        client.create_api_key()
        print(">>> Conectado ao Polymarket!")
    except Exception as e:
        print(f"Aviso de conexão: {e}")

    # 3. Cria o Grid
    precos_compra = []
    p = GRID_INICIAL
    while p >= GRID_FINAL:
        precos_compra.append(round(p, 2))
        p -= PASSO
    
    print(f"Grid configurado: {precos_compra}")

    # 4. Loop
    while True:
        print("\n--- Ciclo de Verificação ---")
        for preco in precos_compra:
            qtd = round(VALOR_ORDEM_USD / preco, 2)
            print(f"Compraria {qtd} cotas a ${preco} (ID: {token_id})")
        
        print("Dormindo 60s...")
        time.sleep(60)

if __name__ == "__main__":
    main()
