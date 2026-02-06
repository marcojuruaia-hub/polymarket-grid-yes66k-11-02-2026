import os
import time
import sys
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs
from py_clob_client.order_builder.constants import BUY, SELL

# --- NOVOS PARÂMETROS SOLICITADOS ---
TOKEN_ID = "21639768904545427220464585903669395149753104733036853605098419574581993896843"
VALOR_ORDEM_USD = 5.00  # Mínimo obrigatório da Polymarket
LUCRO = 0.01            # Vender $0,01 acima da compra

GRID_COMPRA_INICIO = 0.50
GRID_COMPRA_FIM = 0.30
PASSO_COMPRA = 0.05

# Endereço do USDC.e (Polygon)
USDC_ADDRESS = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"

def main():
    print(">>> 🚀 ROBÔ V16: GRID OTIMIZADO ATIVADO <<<")
    
    key = os.getenv("PRIVATE_KEY")
    if not key:
        print("❌ ERRO: Configure a PRIVATE_KEY no Railway.")
        sys.exit(1)

    try:
        # Inicialização com Signature Type 0 (MetaMask)
        client = ClobClient("https://clob.polymarket.com/", key=key, chain_id=137, signature_type=0)
        
        print(">>> 🔐 Autenticando...")
        creds = client.create_or_derive_api_creds()
        client.set_api_creds(creds)
        
        print(">>> 🛡️ Verificando Allowance (Permissão de USDC)...")
        client.update_allowance(USDC_ADDRESS)
        print(">>> ✅ Tudo pronto para operar!")
        
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        sys.exit(1)

    # Criando o grid: 0.50, 0.45, 0.40, 0.35, 0.30
    grid_compras = []
    p = GRID_COMPRA_INICIO
    while p >= GRID_COMPRA_FIM:
        grid_compras.append(round(p, 2))
        p -= PASSO_COMPRA
    
    print(f">>> 📊 Níveis de preço: {grid_compras}")

    while True:
        print("\n--- ⏳ Ciclo de Operação ---")
        
        for preco in grid_compras:
            # 1. TENTATIVA DE COMPRA (BUY)
            try:
                qtd = round(VALOR_ORDEM_USD / preco, 2)
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
                    print(f"⚠️ Saldo insuficiente para ${preco}. Verifique se é USDC.e")
                else:
                    print(f"❌ Erro na compra a ${preco}: {e}")

            # 2. TENTATIVA DE VENDA (SELL)
            preco_venda = round(preco + LUCRO, 2)
            try:
                # Tenta vender a mesma quantidade comprada
                qtd_v = round(VALOR_ORDEM_USD / preco, 2)
                client.create_and_post_order(
                    OrderArgs(
                        price=preco_venda,
                        size=qtd_v,
                        side=SELL,
                        token_id=TOKEN_ID
                    )
                )
                print(f"💰 VENDA colocada a ${preco_venda}")
            except:
                # Erro aqui é normal se você ainda não tiver as cotas para vender
                pass 

        print(f"--- Aguardando 60 segundos ---")
        time.sleep(60)

if __name__ == "__main__":
    main()
