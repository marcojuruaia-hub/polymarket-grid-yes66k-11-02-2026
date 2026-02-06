import os
import time
import sys
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OrderType

# --- CONFIGURAÇÕES FINAIS ---
# O ID Gigante que descobrimos nos logs (YES - Bitcoin > 66k)
TOKEN_ID = "21639768904545427220464585903669395149753104733036853605098419574581993896843"

VALOR_ORDEM_USD = 5.00  # Valor da aposta
LUCRO = 0.01            # Lucro por ordem

# Grid de Compra (Do jeito que você pediu)
# Começa comprando a 0.50, 0.45, 0.40... até 0.10
GRID_COMPRA_INICIO = 0.50
GRID_COMPRA_FIM = 0.10
PASSO_COMPRA = 0.05

def main():
    print(">>> ROBÔ GRID DE OPERAÇÃO - START <<<")
    print(f"ID do Ativo: {TOKEN_ID[:10]}...") # Mostra só o começo pra não poluir

    # 1. Conexão Segura
    key = os.getenv("PRIVATE_KEY")
    if not key:
        print("ERRO: PRIVATE_KEY não encontrada.")
        sys.exit(1)

    try:
        client = ClobClient("https://clob.polymarket.com/", key=key, chain_id=137)
        try:
            client.create_api_key()
        except Exception:
            pass 
        print(">>> Conectado! Iniciando operações...")
    except Exception as e:
        print(f"Erro de conexão: {e}")
        sys.exit(1)

    # 2. Gera a lista de preços do Grid
    grid_compras = []
    p = GRID_COMPRA_INICIO
    while p >= GRID_COMPRA_FIM:
        grid_compras.append(round(p, 2))
        p -= PASSO_COMPRA
    
    print(f"Grid Ativo: {grid_compras}")

    # 3. Loop Infinito (Compra e Vende)
    while True:
        print("\n--- Ciclo de Mercado ---")
        
        # --- PARTE 1: TENTAR COMPRAR (BID) ---
        for preco in grid_compras:
            try:
                qtd = round(VALOR_ORDEM_USD / preco, 2)
                
                # Envia ordem de COMPRA
                resp = client.create_and_post_order(
                    OrderArgs(
                        price=preco,
                        size=qtd,
                        side="BUY", 
                        token_id=TOKEN_ID,
                        order_type=OrderType.LIMIT
                    )
                )
                print(f"✅ COMPRA enviada: {qtd} cotas a ${preco} (ID: {resp.get('orderID')})")
            except Exception as e:
                # Ignora erro de saldo insuficiente pra não travar
                if "balance" not in str(e).lower():
                    pass 

        # --- PARTE 2: TENTAR VENDER (ASK) ---
        # Se comprou a 0.50, tenta vender a 0.51
        for preco_compra in grid_compras:
            preco_venda = round(preco_compra + LUCRO, 2)
            try:
                qtd = round(VALOR_ORDEM_USD / preco_compra, 2)
                
                if preco_venda < 1.0:
                    # Envia ordem de VENDA
                    resp = client.create_and_post_order(
                        OrderArgs(
                            price=preco_venda,
                            size=qtd,
                            side="SELL",
                            token_id=TOKEN_ID,
                            order_type=OrderType.LIMIT
                        )
                    )
                    print(f"💰 VENDA enviada: {qtd} cotas a ${preco_venda} (ID: {resp.get('orderID')})")
            except Exception as e:
                pass 

        print("Aguardando 30 segundos...")
        time.sleep(30)

if __name__ == "__main__":
    main()
