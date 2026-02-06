import os
import time
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs
from py_clob_client.order_builder.constants import BUY, SELL

# --- CONFIGURAÇÕES DO USUÁRIO ---
TOKEN_ID = "21639768904545427220464585903669395149753104733036853605098419574581993896843"
PROXY_ADDRESS = "0x658293eF9454A2DD555eb4afcE6436aDE78ab20B"
LUCRO = 0.01  # 1 centavo de lucro

# Grid de compra (preços onde você QUER COMPRAR)
GRID_COMPRA = [0.83, 0.82, 0.81, 0.80, 0.79, 0.78, 0.76, 0.74, 0.72, 0.70, 0.65, 0.60, 0.55, 0.50, 0.40]

# Dicionário para rastrear ordens criadas nesta sessão
ordens_criadas = {
    'compra': set(),
    'venda': set()
}

def get_ordens_abertas(client):
    """Retorna ordens abertas usando o método correto da API"""
    try:
        # Método correto: get_orders com status LIVE
        response = client.get_orders(
            token_id=TOKEN_ID,
            status="LIVE"  # Apenas ordens ativas
        )
        
        compras_abertas = {}
        vendas_abertas = {}
        
        for ordem in response:
            preco = round(float(ordem.get('price')), 2)
            lado = ordem.get('side')
            
            if lado == 'BUY':
                compras_abertas[preco] = ordem
            elif lado == 'SELL':
                vendas_abertas[preco] = ordem
        
        return compras_abertas, vendas_abertas
        
    except Exception as e:
        print(f"⚠️ Erro ao ler ordens: {e}")
        # Retorna as que já criamos nesta sessão como fallback
        compras_fallback = {p: None for p in ordens_criadas['compra']}
        vendas_fallback = {p: None for p in ordens_criadas['venda']}
        return compras_fallback, vendas_fallback

def calcular_quantidade_minima(preco):
    """Calcula o mínimo de shares baseado na regra de $1 vs 5 shares"""
    if preco > 0.20:
        return 5.0
    else:
        return round(1.0 / preco, 2)

def main():
    print(">>> 🚀 ROBÔ V2: SEM DUPLICATAS <<<")
    
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
        
        print(f"📊 Compras abertas: {sorted(compras_abertas.keys())}")
        print(f"📊 Vendas abertas: {sorted(vendas_abertas.keys())}")
        
        # PARTE 1: COLOCAR ORDENS DE COMPRA (sem duplicar)
        print("\n🔵 Verificando ordens de COMPRA...")
        for preco_compra in GRID_COMPRA:
            # Verifica se já existe (na API ou nas que criamos)
            if preco_compra in compras_abertas or preco_compra in ordens_criadas['compra']:
                print(f"  ℹ️ Já existe ordem de compra a ${preco_compra:.2f}")
                continue
            
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
                
                # Marca como criada para não duplicar
                ordens_criadas['compra'].add(preco_compra)
                print(f"  ✅ COMPRA criada: {qtd_compra} shares a ${preco_compra:.2f}")
                
            except Exception as e:
                if "balance" in str(e).lower() or "insufficient" in str(e).lower():
                    print(f"  ⚠️ Sem saldo para comprar a ${preco_compra:.2f}")
                else:
                    print(f"  ❌ Erro ao comprar a ${preco_compra:.2f}: {e}")
        
        # PARTE 2: COLOCAR ORDENS DE VENDA (para as compras que existem)
        print("\n🟢 Verificando ordens de VENDA...")
        
        # Unir compras da API com as que criamos
        todos_precos_compra = set(compras_abertas.keys()) | ordens_criadas['compra']
        
        for preco_compra in todos_precos_compra:
            # Calcular preço de venda com lucro
            preco_venda = round(preco_compra + LUCRO, 2)
            
            # Verifica se já existe venda
            if preco_venda in vendas_abertas or preco_venda in ordens_criadas['venda']:
                print(f"  ℹ️ Já existe ordem de venda a ${preco_venda:.2f}")
                continue
            
            try:
                qtd_venda = calcular_quantidade_minima(preco_compra)
                
                client.create_and_post_order(
                    OrderArgs(
                        price=preco_venda, 
                        size=qtd_venda, 
                        side=SELL, 
                        token_id=TOKEN_ID
                    )
                )
                
                # Marca como criada
                ordens_criadas['venda'].add(preco_venda)
                print(f"  ✅ VENDA criada: {qtd_venda} shares a ${preco_venda:.2f} (compra foi a ${preco_compra:.2f})")
                
            except Exception as e:
                if "balance" in str(e).lower() or "insufficient" in str(e).lower():
                    print(f"  ⚠️ Sem shares para vender a ${preco_venda:.2f}")
                else:
                    print(f"  ❌ Erro ao vender a ${preco_venda:.2f}: {e}")
        
        print("\n📋 Resumo desta sessão:")
        print(f"   Compras criadas: {len(ordens_criadas['compra'])}")
        print(f"   Vendas criadas: {len(ordens_criadas['venda'])}")
        
        print("\n" + "="*60)
        print(f"⏰ Ciclo finalizado. Aguardando 30s...")
        time.sleep(30)

if __name__ == "__main__":
    main()
