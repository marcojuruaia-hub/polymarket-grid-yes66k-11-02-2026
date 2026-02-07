import os
import time
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs
from py_clob_client.order_builder.constants import BUY, SELL

# --- CONFIGURAÇÕES DO USUÁRIO ---
TOKEN_ID = "21639768904545427220464585903669395149753104733036853605098419574581993896843"
PROXY_ADDRESS = "0x658293eF9454A2DD555eb4afcE6436aDE78ab20B"
LUCRO = 0.01  # 1 centavo de lucro

# Grid de compra
GRID_COMPRA = [0.83, 0.82, 0.81, 0.80, 0.79, 0.78, 0.76, 0.74, 0.72, 0.70, 0.65, 0.60, 0.55, 0.50, 0.40]

# Rastrear ordens para evitar duplicatas
ordens_compra_abertas = set()
ordens_venda_criadas = set()
compras_executadas_processadas = set()  # IDs de compras que já viraram venda

def get_ordens_por_status(client):
    """Busca ordens abertas (LIVE) e executadas recentes"""
    try:
        # Ordens abertas (ainda não executadas)
        ordens_live = client.get_orders(token_id=TOKEN_ID, status="LIVE")
        
        # Ordens executadas recentemente (para criar vendas)
        ordens_matched = client.get_orders(token_id=TOKEN_ID, status="MATCHED")
        
        compras_abertas = set()
        vendas_abertas = set()
        compras_executadas = []
        
        # Processar ordens abertas
        for ordem in ordens_live:
            preco = round(float(ordem.get('price')), 2)
            if ordem.get('side') == 'BUY':
                compras_abertas.add(preco)
            elif ordem.get('side') == 'SELL':
                vendas_abertas.add(preco)
        
        # Processar ordens executadas (compras que viraram posição)
        for ordem in ordens_matched:
            if ordem.get('side') == 'BUY':
                ordem_id = ordem.get('id')
                preco = round(float(ordem.get('price')), 2)
                size = float(ordem.get('size_matched', ordem.get('size', 0)))
                
                compras_executadas.append({
                    'id': ordem_id,
                    'preco': preco,
                    'quantidade': size
                })
        
        return compras_abertas, vendas_abertas, compras_executadas
        
    except Exception as e:
        print(f"⚠️ Erro ao buscar ordens: {e}")
        return set(), set(), []

def calcular_quantidade_minima(preco):
    """Calcula o mínimo de shares"""
    if preco > 0.20:
        return 5.0
    else:
        return round(1.0 / preco, 2)

def main():
    print(">>> 🚀 ROBÔ V3: SÓ VENDE DEPOIS DE COMPRAR <<<")
    
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
    print(f">>> 💰 Lucro: +${LUCRO} por share\n")
    
    while True:
        print("\n" + "="*70)
        print("--- ⏳ VERIFICANDO ORDENS ---")
        
        compras_abertas, vendas_abertas, compras_executadas = get_ordens_por_status(client)
        
        print(f"📊 Compras abertas (aguardando): {sorted(compras_abertas)}")
        print(f"📊 Vendas abertas: {sorted(vendas_abertas)}")
        print(f"📊 Compras executadas: {len(compras_executadas)}")
        
        # ==============================================================
        # ETAPA 1: CRIAR ORDENS DE COMPRA (nos preços do grid)
        # ==============================================================
        print("\n🔵 ETAPA 1: Verificando ordens de COMPRA...")
        
        for preco_compra in GRID_COMPRA:
            # Só cria se NÃO existe ordem aberta nesse preço
            if preco_compra in compras_abertas or preco_compra in ordens_compra_abertas:
                print(f"  ℹ️ Já existe compra a ${preco_compra:.2f}")
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
                
                ordens_compra_abertas.add(preco_compra)
                print(f"  ✅ COMPRA criada: {qtd} shares a ${preco_compra:.2f}")
                
            except Exception as e:
                if "balance" in str(e).lower() or "insufficient" in str(e).lower():
                    print(f"  ⚠️ Sem saldo para ${preco_compra:.2f}")
                else:
                    print(f"  ❌ Erro: {e}")
        
        # ==============================================================
        # ETAPA 2: CRIAR VENDAS PARA COMPRAS QUE FORAM EXECUTADAS
        # ==============================================================
        print("\n🟢 ETAPA 2: Criando VENDAS para compras executadas...")
        
        for compra in compras_executadas:
            ordem_id = compra['id']
            preco_comprado = compra['preco']
            qtd_comprada = compra['quantidade']
            
            # Já processamos essa compra antes?
            if ordem_id in compras_executadas_processadas:
                continue
            
            # Calcular preço de venda (1 centavo acima)
            preco_venda = round(preco_comprado + LUCRO, 2)
            
            # Já existe venda nesse preço?
            if preco_venda in vendas_abertas or preco_venda in ordens_venda_criadas:
                print(f"  ℹ️ Já existe venda a ${preco_venda:.2f}")
                compras_executadas_processadas.add(ordem_id)
                continue
            
            try:
                client.create_and_post_order(
                    OrderArgs(
                        price=preco_venda,
                        size=qtd_comprada,
                        side=SELL,
                        token_id=TOKEN_ID
                    )
                )
                
                ordens_venda_criadas.add(preco_venda)
                compras_executadas_processadas.add(ordem_id)
                
                print(f"  ✅ VENDA criada: {qtd_comprada} shares a ${preco_venda:.2f}")
                print(f"     (compra foi a ${preco_comprado:.2f}, lucro de ${LUCRO:.2f}/share)")
                
            except Exception as e:
                if "balance" in str(e).lower() or "insufficient" in str(e).lower():
                    print(f"  ⚠️ Sem shares para vender")
                else:
                    print(f"  ❌ Erro ao vender: {e}")
        
        # Atualizar cache de ordens abertas
        ordens_compra_abertas = compras_abertas
        
        print("\n" + "="*70)
        print("⏰ Aguardando 30s...\n")
        time.sleep(30)

if __name__ == "__main__":
    main()
