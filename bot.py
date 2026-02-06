import os
import time
import sys
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OrderType

# --- CONFIGURAÇÕES ---
TOKEN_ID = "21639768904545427220464585903669395149753104733036853605098419574581993896843"
VALOR_ORDEM_USD = 1.00
LUCRO = 0.01

GRID_COMPRA_INICIO = 0.40
GRID_COMPRA_FIM = 0.10
PASSO_COMPRA = 0.02

def main():
    print(">>> ROBÔ GRID - MODO DEBUG <<<")
    
    key = os.getenv("PRIVATE_KEY")
    if not key:
        print("ERRO: Sem PRIVATE_KEY.")
        sys.exit(1)

    try:
        client = ClobClient("https://clob.polymarket.com/", key=key, chain_id=137)
        try:
            client.create_api_key()
        except:
            pass 
        print(">>> Conectado!")
    except Exception as e:
        print(f"Erro Conexão: {e}")
        sys.exit(1)

    grid_compras = []
    p = GRID_COMPRA_INICIO
    while p >= GRID_COMPRA_FIM:
        grid_compras.append(round(p, 2))
        p -= PASSO_COMPRA
    
    while True:
        print("\n--- Tentando Operar ---")
        
        # TENTA COMPRAR (E MOSTRA O ERRO SE FALHAR)
        for preco in grid_compras:
            try:
                qtd = round(VALOR_ORDEM_USD / preco, 2)
                print(f"Tentando comprar {qtd} a ${preco}...")
                
                resp = client.create_and_post_order(
                    OrderArgs(
                        price=preco,
                        size=qtd,
                        side="BUY", 
                        token_id=TOKEN_ID,
                        order_type=OrderType.LIMIT
                    )
                )
                print(f"✅ SUCESSO! ID da Ordem: {resp.get('orderID')}")
            except Exception as e:
                # AQUI ESTÁ A MUDANÇA: Vamos ver o erro!
                print(f"❌ FALHA ao comprar a ${preco}: {e}")

        print("Aguardando 30 segundos...")
        time.sleep(30)

if __name__ == "__main__":
    main()
