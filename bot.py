import os
import time
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs
from py_clob_client.order_builder.constants import BUY, SELL

# --- CONFIGURAÇÕES ---
TOKEN_ID = "21639768904545427220464585903669395149753104733036853605098419574581993896843"
PROXY_ADDRESS = "0x658293eF9454A2DD555eb4afcE6436aDE78ab20B"
LUCRO = 0.01

# Grid de compra
GRID_COMPRA = [0.83, 0.82, 0.81, 0.80, 0.79, 0.78, 0.76, 0.74, 0.72, 0.70, 0.65, 0.60, 0.55, 0.50, 0.40]

def get_ordens_abertas(client):
    """Busca ordens abertas e filtra por token"""
    try:
        # Busca TODAS as ordens abertas
        todas_ordens = client.get_orders()
        
        compras_abertas = {}
        vendas_abertas = {}
        
        # Filtra apenas as do nosso token
        for ordem in todas_ordens:
            if ordem.get('asset_id') != TOKEN_ID:
                continue
            
            preco = round(float(ordem.get('price')), 2)
            lado = ordem.get('side')
            status = ordem.get('status')
            
            # Apenas ordens ativas (LIVE)
            if status != 'LIVE':
                continue
            
            if lado == 'BUY':
                compras_abertas[preco] = ordem
            elif lado == 'SELL':
                vendas_abertas[preco] = ordem
        
        return compras_abertas, vendas_abertas
        
    except Exception as e:
        print(f"⚠️ Erro ao buscar ordens: {e}")
        return {}, {}

def calcular_quantidade_minima(preco):
    """Calcula quantidade mínima de shares"""
    if preco > 0.20:
        return 5.0
    else:
        return round(1.0 / preco, 2)

def main():
    print(">>> 🚀 ROBÔ GRID TRADING - POLYMARKET <<<")
    
    key = os.getenv("PRIVATE_KEY")
    client = ClobClient(
        "https://clob.polymarket.com/", 
        key=key, 
        chain_id=137, 
        signature_type=2, 
        funder=PROXY_ADDRESS
    )
    client.set_api_creds(client.create_or_derive_api_creds())
    
    print(f">>> ✅ Cofre: {PROXY_ADDRESS}")
    print(f">>> 💰 Lucro por operação: ${LUCRO}\n")
    
    # Rastrear ordens que já criamos
    compras_ja_criadas = set()
    vendas_ja_criadas = set()
    
    while True:
        print("\n" + "="*70)
        print("--- ⏳ VERIFICANDO ORDENS ---")
        
        compras_abertas, vendas_abertas = get_ordens_abertas(client)
        
        print(f"📊 Compras abertas: {sorted(compras_abertas.keys())}")
        print(f"📊 Vendas abertas: {sorted(vendas_abertas.keys())}")
        
        # ============================================================
        # PARTE 1: CRIAR ORDENS DE COMPRA
        # ============================================================
        print("\n🔵 CRIANDO ORDENS DE COMPRA...")
        
        for preco_compra in GRID_COMPRA:
            # Já existe ordem aberta nesse preço?
            if preco_compra in compras_abertas:
                print(f"  ℹ️ Já existe compra a ${preco_compra:.2f}")
                compras_ja_criadas.add(preco_compra)
                continue
            
            # Já tentamos criar antes?
            if preco_compra in compras_ja_criadas:
                continue
            
            try:
                qtd = calcular_quantidade_minima(preco_compra)
                
                client.create_and_post_order(
                    OrderArgs(
                        price=preco_compra, 
                        size=qtd, 
                        side=BUY, 
                        token_id=TOKEN_ID
                    )
                )
                
                compras_ja_criadas.add(preco_compra)
                print(f"  ✅ COMPRA: {qtd} shares a ${preco_compra:.2f}")
                
            except Exception as e:
                erro_str = str(e).lower()
                if "balance" in erro_str or "insufficient" in erro_str:
                    print(f"  ⚠️ Sem saldo para ${preco_compra:.2f}")
                else:
                    print(f"  ❌ Erro: {e}")
        
        # ============================================================
        # PARTE 2: CRIAR VENDAS PARA COMPRAS ABERTAS
        # ============================================================
        print("\n🟢 CRIANDO ORDENS DE VENDA...")
        
        for preco_compra in compras_abertas.keys():
            preco_venda = round(preco_compra + LUCRO, 2)
            
            # Já existe venda nesse preço?
            if preco_venda in vendas_abertas:
                print(f"  ℹ️ Já existe venda a ${preco_venda:.2f}")
                vendas_ja_criadas.add(preco_venda)
                continue
            
            # Já tentamos criar antes?
            if preco_venda in vendas_ja_criadas:
                continue
            
            try:
                qtd = calcular_quantidade_minima(preco_compra)
                
                client.create_and_post_order(
                    OrderArgs(
                        price=preco_venda,
                        size=qtd,
                        side=SELL,
                        token_id=TOKEN_ID
                    )
                )
                
                vendas_ja_criadas.add(preco_venda)
                print(f"  ✅ VENDA: {qtd} shares a ${preco_venda:.2f}")
                print(f"     → Compra foi a ${preco_compra:.2f}, lucro ${LUCRO:.2f}/share")
                
            except Exception as e:
                erro_str = str(e).lower()
                if "balance" in erro_str or "insufficient" in erro_str:
                    print(f"  ⚠️ Sem shares para vender a ${preco_venda:.2f}")
                else:
                    print(f"  ❌ Erro: {e}")
        
        # Limpar cache de ordens antigas que não existem mais
        compras_ja_criadas = set(compras_abertas.keys())
        vendas_ja_criadas = set(vendas_abertas.keys())
        
        print("\n" + "="*70)
        print("⏰ Aguardando 60 segundos...\n")
        time.sleep(60)

if __name__ == "__main__":
    main()
