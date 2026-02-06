import requests
import json
import time

# O Link do seu mercado
MARKET_SLUG = "bitcoin-above-66k-on-february-11"

def main():
    print("--- INICIANDO MODO DETETIVE ---")
    print(f"Investigando: {MARKET_SLUG}...")
    
    try:
        url = f"https://gamma-api.polymarket.com/markets?slug={MARKET_SLUG}"
        resp = requests.get(url).json()
        
        if not resp:
            print("ERRO: API retornou vazio.")
            return

        market = resp[0]
        
        # AQUI ESTÁ O SEGREDO: Vamos imprimir TUDO para achar o ID
        print("\n=== DADOS DO MERCADO (Copie isso) ===")
        print(json.dumps(market, indent=2))
        print("=====================================\n")

        print("Tentei achar clobTokenIds e veio:", market.get('clobTokenIds'))
        
    except Exception as e:
        print(f"Erro no detetive: {e}")

    print("--- FIM DA INVESTIGAÇÃO (Pode parar o robô) ---")
    time.sleep(600) # Fica parado para dar tempo de ler

if __name__ == "__main__":
    main()
