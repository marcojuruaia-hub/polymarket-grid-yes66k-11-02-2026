import os
import time
import sys
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs

# --- CONFIGURAÇÕES ---
TOKEN_ID = "21639768904545427220464585903669395149753104733036853605098419574581993896843"
VALOR_ORDEM_USD = 5.00
LUCRO = 0.01

GRID_COMPRA_INICIO = 0.50
GRID_COMPRA_FIM = 0.10
PASSO_COMPRA = 0.05

def main():
    print(">>> ROBÔ GRID V9 (FORÇA BRUTA AUTH) <<<")
    
    key = os.getenv("PRIVATE_KEY")
    if not key:
        print("ERRO: Sem PRIVATE_KEY.")
        sys.exit(1)

    try:
        # Conecta na rede Polygon
        client = ClobClient("https://clob.polymarket.com/", key=key, chain_id=137)
        
        # TENTATIVA DE LOGIN MULTIPLO
        print(">>> Tentando autenticação...")
        auth_sucesso = False
        
        # 1. Tenta derivar (se a chave já existir)
        try:
            client.derive_api_key()
            print(">>> ✅ Chave recuperada (Derivada)!")
            auth_sucesso = True
        except:
            # 2. Se falhar, tenta criar uma nova
            try:
                client.create_api_key()
                print(">>> ✅ Chave nova criada!")
                auth_sucesso = True
            except Exception as e:
                print(f">>> Aviso: Erro ao criar/derivar: {e}")

        # Verifica se funcionou
        if not auth_sucesso:
            print("❌ FALHA CRÍTICA: O robô não conseguiu permissão da API.")
            print("DICA: Verifique se sua conta tem saldo em MATIC para taxas de rede.")
            sys.exit(1)

    except Exception as e:
        print(f"Erro Conexão Geral: {e}")
        sys.exit(1)

    # Lista de preços
    grid_compras = []
    p = GRID_COMPRA_INICIO
    while p >= GRID_COMPRA_FIM:
        grid_compras.append(round(p, 2))
        p -= PASSO_COMPRA
    
    while True:
        print("\n--- Ciclo de Operação ---")
        
        for preco in grid_compras:
            try:
                qtd = round(VALOR_ORDEM_USD / preco, 2)
                resp = client.create_and_post_order(
                    OrderArgs(
                        price=preco,
                        size=qtd,
                        side="BUY", 
                        token_id=TOKEN_ID
                    )
                )
                print(f"✅ SUCESSO! Compra a ${preco}. ID: {resp.get('orderID')}")
            except Exception as e:
                msg = str(e)
                if "balance" in msg.lower():
                     print(f"⚠️ Saldo insuficiente para ${preco}")
                else:
                     print(f"❌ Erro em ${preco}: {msg}")

        print("Aguardando 30 segundos...")
        time.sleep(30)

if __name__ == "__main__":
    main()
