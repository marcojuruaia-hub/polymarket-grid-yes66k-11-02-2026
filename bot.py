import os
import time
import sys
import requests
from py_clob_client.client import ClobClient

# --- CONFIGURAÇÕES ---
# Slug do Mercado (Parte final do seu link)
MARKET_SLUG = "bitcoin-above-66k-on-february-11" 

# Seus valores:
VALOR_ORDEM_USD = 5.00  # $5 por ordem
LUCRO = 0.01            # Ganho por grid
GRID_INICIAL = 0.50     # Começa a comprar em 50 centavos
GRID_FINAL = 0.10       # Para em 10 centavos
PASSO = 0.05            # Desce de 5 em 5 centavos

def get_token_id():
    """Busca o ID do token YES automaticamente"""
    try:
        url = f"https://gamma-api.polymarket.com/events?slug={MARKET_SLUG}"
        r = requests.get(url).json()
        # Procura o mercado exato dentro do evento
        for market in r[0]['markets']:
            if market['slug'] == MARKET_SLUG:
                print(f"Mercado encontrado: {market['question']}")
                return market['clobTokenIds'][0] # ID do YES
    except Exception as e:
        print(f"Erro ao buscar ID: {e}")
        return None

def main():
    print(">>> Iniciando Robô Grid Polymarket (Auto-ID)...")

    # 1. Busca o ID do YES
    token_id = get_token_id()
    if not token_id:
        print("ERRO CRÍTICO: Não foi possível achar o ID do mercado.")
        sys.exit(1)
    print(f"ID do Mercado (YES): {token_id}")

    # 2. Conexão
    key = os.getenv("PRIVATE_KEY")
    if not key:
        print("ERRO: Configure a PRIVATE_KEY no Railway.")
        sys.exit(1)

    try:
        # Usa a Polygon (Chain ID 137)
        client = ClobClient("https://clob.polymarket.com/", key=key, chain_id=137)
        client.create_api_key()
        print(">>> Conectado com sucesso!")
    except Exception as e:
        print(f"Aviso de conexão: {e}")

    # 3. Estratégia
    precos_compra = []
    p = GRID_INICIAL
    while p >= GRID_FINAL:
        precos_compra.append(round(p, 2))
        p -= PASSO
    
    print(f"Níveis de compra configurados: {precos_compra}")

    while True:
        print("\n--- Analisando Mercado ---")
        # Por segurança, apenas simula
        for preco in precos_compra:
            qtd = round(VALOR_ORDEM_USD / preco, 2)
            print(f"Grid {preco}: Compraria {qtd} cotas do ID {token_id} (Simulação)")
        
        time.sleep(60)

if __name__ == "__main__":
    main()
