import os
import time
import sys
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs
from py_clob_client.order_builder.constants import BUY, SELL

# --- CONFIGURAÇÕES DO USUÁRIO ---
TOKEN_ID = "21639768904545427220464585903669395149753104733036853605098419574581993896843"
PROXY_ADDRESS = "0x658293eF9454A2DD555eb4afcE6436aDE78ab20B"
LUCRO = 0.01  # 1 centavo de lucro

# Grid de compra (preços onde você QUER COMPRAR)
GRID_COMPRA = [0.83, 0.82, 0.81, 0.80, 0.79, 0.78, 0.76, 0.74, 0.72, 0.70, 0.65, 0.60, 0.55, 0.50, 0.40]

def get_ordens_abertas(client):
    """Retorna todas as ordens abertas separadas por tipo"""
    try:
        ordens = client.get_open_orders()
        ordens_token = [o for o in ordens if o.get('token_id') == TOKEN_ID]
        
        compras_abertas = {}
        vendas_abertas = {}
        
        for ordem in ordens_token:
            preco = round(float(ordem.get('price')), 2)
            lado = ordem.get('side')
            
            if lado == 'BUY':
                compras_abertas[preco] = ordem
            elif lado == 'SELL':
                vendas_abertas[preco] = ordem
        
        return compras_abertas, vendas_abertas
    except Exception as e:
        print(f"⚠️ Erro ao ler ordens abertas: {e}")
        return {}, {}

def get_posicao_atual(client):
    """Verifica quantas shares você tem compradas"""
    try:
        # Aqui você precisaria verificar seu saldo de tokens
        # Por enquanto, vamos assumir baseado nas ordens executadas
        return 0  # Placeholder - ajustar conforme API do Polymarket
    except:
        return 0

def calcular_quantidade_minima(preco):
    """Calcula o mínimo de shares baseado na regra de $1 vs 5 shares"""
    if preco > 0.20:
        return 5.0
    else:
        return round(1.0 / preco, 2)

def main():
    print(">>> 🚀 ROBÔ CORRIGIDO: COMPRA BARATO, VENDE CARO <<<")
    
    key = os.getenv("PRIVATE_KEY")
    client = ClobClient(
        "https://clob.polymarket.com/", 
        key=key, 
        chain_id=137, 
        signature_type=2, 
        funder=PROXY_ADDRESS
    )
    client.set_api_creds(client.create_or_derive_api_creds())
    
    print(f">>> ✅ Operando no Cofre: {PROXY_ADDRESS}")
    print(f">>> 💰 Lucro configurado: ${LUCRO} por share\n")
    
    while True:
        print("\n" + "="*60)
        print("--- ⏳ Verificando Status das Ordens ---")
        
        compras_abertas, vendas_abertas = get_ordens_abertas(client)
        
        print(f"📊 Compras abertas: {list(compras_abertas.keys())}")
        print(f"📊 Vendas abertas: {list(vendas_abertas.keys())}")
        
        # PARTE 1: COLOCAR ORDENS DE COMPRA
        print("\n🔵 Verificando ordens de COMPRA...")
        for preco_compra in GRID_COMPRA:
            if preco_compra not in compras_abertas:
                try:
                    qtd_compra = calcular_quantidade_minima(preco_compra)
                    
                    client.create_and_post_order(
                        OrderArgs(
                            price=preco_compra, 
                            size=qtd_compra, 
                            side=BUY, 
                            token_id=TOKEN_ID
                        )
                    )
                    print(f"  ✅ COMPRA criada: {qtd_compra} shares a ${preco_compra:.2f}")
                    
                except Exception as e:
                    if "balance" in str(e).lower():
                        print(f"  ⚠️ Sem saldo para comprar a ${preco_compra:.2f}")
                    else:
                        print(f"  ❌ Erro ao comprar a ${preco_compra:.2f}: {e}")
            else:
                print(f"  ℹ️ Já existe ordem de compra a ${preco_compra:.2f}")
        
        # PARTE 2: COLOCAR ORDENS DE VENDA (somente para compras que já existem)
        print("\n🟢 Verificando ordens de VENDA...")
        for preco_compra in compras_abertas.keys():
            # Calcular preço de venda com lucro
            preco_venda = round(preco_compra + LUCRO, 2)
            
            # Só coloca venda se ainda não existe
            if preco_venda not in vendas_abertas:
                try:
                    # Vende a mesma quantidade que foi comprada
                    qtd_venda = calcular_quantidade_minima(preco_compra)
                    
                    client.create_and_post_order(
                        OrderArgs(
                            price=preco_venda, 
                            size=qtd_venda, 
                            side=SELL, 
                            token_id=TOKEN_ID
                        )
                    )
                    print(f"  ✅ VENDA criada: {qtd_venda} shares a ${preco_venda:.2f} (lucro de ${LUCRO:.2f})")
                    
                except Exception as e:
                    if "balance" in str(e).lower() or "insufficient" in str(e).lower():
                        print(f"  ⚠️ Sem shares para vender a ${preco_venda:.2f}")
                    else:
                        print(f"  ❌ Erro ao vender a ${preco_venda:.2f}: {e}")
            else:
                print(f"  ℹ️ Já existe ordem de venda a ${preco_venda:.2f}")
        
        print("\n" + "="*60)
        print(f"⏰ Ciclo finalizado. Aguardando 30s...")
        time.sleep(30)

if __name__ == "__main__":
    main()
