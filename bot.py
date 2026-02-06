import os
import time
import sys
import requests
from py_clob_client.client import ClobClient

# --- CONFIGURAÇÕES DE MERCADO (CORRIGIDO) ---
# Link original: polymarket.com/event/bitcoin-above-on-february-11/bitcoin-above-66k-on-february-11
# O sistema precisa separar o "Evento" do "Mercado" para achar o ID.

EVENT_SLUG = "bitcoin-above-on-february-11"       # O Grupo de apostas
MARKET_SLUG = "bitcoin-above-66k-on-february-11"  # A sua aposta específica

# --- SEUS VALORES ---
VALOR_ORDEM_USD = 5.00  # $5 por ordem
GRID_INICIAL = 0.50     # Começa a comprar em 50 centavos
GRID_FINAL = 0.10       # Para em 10 centavos
PASSO = 0.05            # Desce de 5 em 5 centavos

def get_token_id():
    """Busca o ID do token YES automaticamente usando o Event Slug correto"""
    try:
        # Busca pelo EVENTO primeiro (que contém vários mercados)
        url = f"https://gamma-api.polymarket.com/events?slug={EVENT_SLUG}"
        resp = requests.get(url).json()
        
        if not resp:
            print("ERRO: API retornou lista vazia. Verifique o EVENT_SLUG.")
            return None

        # Procura o MERCADO exato dentro do evento
        for market in resp[0]['markets']:
            if market['slug'] == MARKET_SLUG:
                print(f"Mercado encontrado: {market['question']}")
                # O ID do 'YES' é geralmente o primeiro da lista [0] ou [1]. 
                # Na Polymarket CLOB, IDs são strings longas.
                return market['clobTokenIds'][0] 
                
        print("Mercado não encontrado dentro do evento.")
        return None
    except Exception as e:
        print(f"Erro ao buscar ID: {e}")
        return None

def main():
    print(">>> Iniciando Robô Grid Polymarket v2 (Fix ID)...")

    # 1. Busca o ID
    token_id = get_token_id()
    if not token_id:
        print("ERRO CRÍTICO: ID não encontrado. O robô vai parar.")
        sys.exit(1)
    print(f"ID do Mercado (YES): {token_id}")

    # 2. Conexão
    key = os.getenv("PRIVATE_KEY")
    if not key:
        print("ERRO: Configure a PRIVATE_KEY no Railway.")
        sys.exit(1)

    try:
        client = ClobClient("https://clob.polymarket.com/", key=key, chain_id=137)
        client.create_api_key()
        print(">>> Conectado com sucesso!")
    except Exception as e:
        print(f"Aviso de conexão: {e}")

    # 3. Definição do Grid
    precos_compra = []
    p = GRID_INICIAL
    while p >= GRID_FINAL:
        precos_compra.append(round(p, 2))
        p -= PASSO
    
    print(f"Níveis de compra: {precos_compra}")

    while True:
        print("\n--- Analisando Mercado ---")
        # Simulação de segurança
        for preco in precos_compra:
            qtd = round(VALOR_ORDEM_USD / preco, 2)
            print(f"Grid {preco}: Compraria {qtd} cotas (ID: {token_id})")
        
        print("Aguardando 60 segundos...")
        time.sleep(60)

if __name__ == "__main__":
    main()
