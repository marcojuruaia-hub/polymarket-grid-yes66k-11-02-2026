import os
import time
import sys
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs
from py_clob_client.order_builder.constants import BUY, SELL

# --- CONFIGURAÇÕES DO USUÁRIO ---
TOKEN_ID = "21639768904545427220464585903669395149753104733036853605098419574581993896843"
PROXY_ADDRESS = "0x658293eF9454A2DD555eb4afcE6436aDE78ab20B"
LUCRO = 0.01

# Grid de 0.50 até 0.01 (Passo de 0.05 para não sobrecarregar, ajuste se quiser)
GRID_COMPRA = [0.84, 0.83, 0.82, 0.81, 0.80, 0.78, 0.76, 0.74, 0.72, 0.70, 0.65, 0.60, 0.05, 0.40]

def get_precos_abertos(client):
    try:
        ordens = client.get_open_orders()
        return [round(float(o.get('price')), 2) for o in ordens if o.get('token_id') == TOKEN_ID]
    except Exception as e:
        print(f"⚠️ Erro ao ler ordens abertas: {e}")
        return []

def calcular_quantidade_minima(preco):
    """Calcula o mínimo de shares baseado na regra de $1 vs 5 shares"""
    if preco > 0.20:
        # Acima de 0.20: Mínimo de 5 shares
        return 5.0
    else:
        # 0.20 ou menos: Mínimo de $1.00 convertido em shares
        # Ex: a 0.10, compra 10 shares ($1.00)
        return round(1.0 / preco, 2)

def main():
    print(">>> 🚀 ROBÔ V24: MÍNIMOS DINÂMICOS ATIVADOS <<<")
    
    key = os.getenv("PRIVATE_KEY")
    client = ClobClient("https://clob.polymarket.com/", key=key, chain_id=137, signature_type=2, funder=PROXY_ADDRESS)
    client.set_api_creds(client.create_or_derive_api_creds())
    
    print(f">>> ✅ Operando no Cofre: {PROXY_ADDRESS}")

    while True:
        print("\n--- ⏳ Verificando Status das Ordens ---")
        precos_ativos = get_precos_abertos(client)
        
        for preco in GRID_COMPRA:
            # 1. LÓGICA DE COMPRA (MÍNIMO DINÂMICO)
            if preco not in precos_ativos:
                try:
                    qtd_compra = calcular_quantidade_minima(preco)
                    client.create_and_post_order(
                        OrderArgs(price=preco, size=qtd_compra, side=BUY, token_id=TOKEN_ID)
                    )
                    print(f"✅ COMPRA: {qtd_compra} cotas a ${preco}")
                except Exception as e:
                    if "balance" in str(e).lower():
                        print(f"⚠️ Sem saldo para ${preco}")
                    else:
                        print(f"❌ Erro em ${preco}: {e}")
            else:
                print(f"ℹ️ Já existe ordem a ${preco}")

            # 2. LÓGICA DE VENDA
            preco_venda = round(preco + LUCRO, 2)
            if preco_venda not in precos_ativos:
                try:
                    # Tenta vender a mesma quantidade que seria comprada nesse nível
                    qtd_venda = calcular_quantidade_minima(preco)
                    client.create_and_post_order(
                        OrderArgs(price=preco_venda, size=qtd_venda, side=SELL, token_id=TOKEN_ID)
                    )
                    print(f"💰 VENDA: Colocada a ${preco_venda}")
                except:
                    pass 

        print(f"--- Ciclo Finalizado. Aguardando 120s ---")
        time.sleep(120)

if __name__ == "__main__":
    main()
