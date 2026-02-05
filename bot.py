import os
import time
import sys
from py_clob_client.client import ClobClient

# --- CONFIGURAÇÕES ---
# Vamos preencher o ID do mercado no Railway depois.
# Por enquanto, o código pegará das "Variáveis de Ambiente"
TOKEN_ID = os.getenv("TOKEN_ID") 

# Seus valores definidos:
VALOR_ORDEM_USD = 5.00  # $5 por ordem
LUCRO = 0.01            # Compra a X, vende a X + 0.01
GRID_INICIAL = 0.40     # Começa a comprar aqui
GRID_FINAL = 0.10       # Para de comprar aqui
PASSO = 0.05            # Desce de 0.05 em 0.05

def main():
    print(">>> Iniciando Robô Grid Polymarket...")

    # Pega a chave secreta que vamos configurar no Railway
    key = os.getenv("PRIVATE_KEY")
    if not key:
        print("ERRO: Chave Privada não encontrada.")
        sys.exit(1)

    # Conecta na Polymarket (Polygon)
    try:
        client = ClobClient("https://clob.polymarket.com/", key=key, chain_id=137)
        client.create_api_key() # Cria credenciais se precisar
        print(">>> Conexão com Polymarket: OK!")
    except Exception as e:
        print(f"Aviso de conexão (pode ignorar se rodar): {e}")

    # Cria a lista de preços: 0.40, 0.35, 0.30 ... 0.10
    precos_compra = []
    p = GRID_INICIAL
    while p >= GRID_FINAL:
        precos_compra.append(round(p, 2))
        p -= PASSO
    
    print(f"seus níveis de compra serão: {precos_compra}")

    # Loop principal (Roda para sempre)
    while True:
        try:
            print("\n--- Analisando Mercado ---")
            
            # ATENÇÃO: Esta versão é de SEGURANÇA.
            # Ela apenas IMPRIME o que faria, não gasta dinheiro ainda.
            # Quando estiver tudo rodando no Railway, eu te ensino a tirar o bloqueio.
            
            for preco in precos_compra:
                qtd = round(VALOR_ORDEM_USD / preco, 2)
                print(f"Verificando nível {preco}: O robô compraria {qtd} cotas (Se ativo).")
            
            print("Aguardando 60 segundos...")
            time.sleep(60)

        except Exception as e:
            print(f"Erro: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
