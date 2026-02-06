import os
import time
import sys
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs
from py_clob_client.order_builder.constants import BUY, SELL

# --- CONFIGURAÇÕES FIXAS ---
TOKEN_ID = "21639768904545427220464585903669395149753104733036853605098419574581993896843"
VALOR_ORDEM_USD = 1.00
LUCRO = 0.01

GRID_COMPRA_INICIO = 0.20
GRID_COMPRA_FIM = 0.01
PASSO_COMPRA = 0.01

def main():
    print(">>> 🚀 ROBÔ V13: OPERAÇÃO TOTAL ATIVADA <<<")
    
    key = os.getenv("PRIVATE_KEY")
    if not key:
        print("❌ ERRO: PRIVATE_KEY não configurada no Railway.")
        sys.exit(1)

    try:
        # 1. Inicializa o cliente
        client = ClobClient("https://clob.polymarket.com/", key=key, chain_id=137)
        
        # 2. AUTENTICAÇÃO DUPLA (O segredo da V13)
        print(">>> 🔐 Autenticando na API da Polymarket...")
        creds = client.create_or_derive_api_creds()
        client.set_api_creds(creds) # <--- Fixa as credenciais no robô
        
        print(">>> ✅ Conectado e Autenticado com sucesso!")
    except Exception as e:
        print(f"❌ Erro crítico na autenticação: {e}")
        sys.exit(1)

    # 3. Prepara o Grid
    grid_compras = []
    p = GRID_COMPRA_INICIO
    while p >= GRID_COMPRA_FIM:
        grid_compras.append(round(p, 2))
        p -= PASSO_COMPRA
    
    print(f">>> 📊 Grid configurado: {grid_compras}")

    while True:
        print("\n--- ⏳ Verificando Oportunidades ---")
        
        for preco in grid_compras:
            # --- TENTATIVA DE COMPRA (BUY) ---
            try:
                qtd = round(VALOR_ORDEM_USD / preco, 2)
                
                # Ordem limpa, sem 'order_type' para evitar conflitos
                resp = client.create_and_post_order(
                    OrderArgs(
                        price=preco,
                        size=qtd,
                        side=BUY, 
                        token_id=TOKEN_ID
                    )
                )
                print(f"✅ COMPRA: {qtd} cotas a ${preco}. ID: {resp.get('orderID')}")
            except Exception as e:
                msg = str(e).lower()
                if "balance" in msg:
                     print(f"⚠️ Saldo insuficiente para comprar a ${preco}")
                elif "under" in msg:
                     print(f"⚠️ Ordem abaixo do mínimo permitido pela Polymarket.")
                else:
                     print(f"❌ Erro na compra a ${preco}: {e}")

            # --- TENTATIVA DE VENDA (SELL) ---
            preco_venda = round(preco + LUCRO, 2)
            try:
                if preco_venda < 1.0:
                    qtd_v = round(VALOR_ORDEM_USD / preco, 2)
                    resp_v = client.create_and_post_order(
                        OrderArgs(
                            price=preco_venda,
                            size=qtd_v,
                            side=SELL,
                            token_id=TOKEN_ID
                        )
                    )
                    print(f"💰 VENDA: {qtd_v} cotas a ${preco_venda}. ID: {resp_v.get('orderID')}")
            except:
                pass # Ignora erros de saldo na venda (ainda não comprou)

        print("--- 😴 Pausa de 30 segundos ---")
        time.sleep(30)

if __name__ == "__main__":
    main()
