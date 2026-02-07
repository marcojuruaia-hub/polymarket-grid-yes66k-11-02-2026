import os
import time
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OpenOrderParams
from py_clob_client.order_builder.constants import SELL

# --- CONFIGURAÇÕES ---
TOKEN_ID = "21639768904545427220464585903669395149753104733036853605098419574581993896843"
PROXY_ADDRESS = "0x658293eF9454A2DD555eb4afcE6436aDE78ab20B"
SHARES_POR_ORDEM = 5  # Quantidade de shares por ordem de venda
INTERVALO_SEGUNDOS = 60  # Intervalo entre ciclos

# Grid de vendas (da mais alta para a mais baixa)
GRID_VENDAS = [0.83, 0.82, 0.81, 0.80, 0.79, 0.78, 0.76, 0.74, 0.72, 0.70, 0.65, 0.60, 0.55, 0.50, 0.40]

def obter_saldo_disponivel(client, token_id):
    """Obtém o saldo disponível de shares"""
    try:
        balances = client.get_balances()
        for balance in balances:
            if balance.get("tokenId") == token_id:
                saldo = float(balance.get("available", 0))
                print(f"💰 Saldo disponível: {saldo:.2f} shares")
                return saldo
        
        print("⚠️ Nenhum saldo encontrado para este token")
        return 0
    except Exception as e:
        print(f"❌ Erro ao obter saldo: {e}")
        return 0

def obter_ordens_venda_ativas(client, token_id):
    """Obtém todas as ordens de venda ativas"""
    try:
        todas_ordens = client.get_orders(OpenOrderParams())
        ordens_venda = []
        
        for ordem in todas_ordens:
            if (ordem.get('asset_id') == token_id and 
                ordem.get('status') == 'open' and
                ordem.get('side') == 'SELL'):
                
                ordens_venda.append({
                    'price': round(float(ordem.get('price', 0)), 2),
                    'size': float(ordem.get('size', 0))
                })
        
        print(f"📊 Ordens de venda ativas: {len(ordens_venda)}")
        return ordens_venda
    except Exception as e:
        print(f"❌ Erro ao obter ordens: {e}")
        return []

def calcular_ordens_possiveis(saldo_shares):
    """Calcula quantas ordens podem ser criadas com base no saldo"""
    if saldo_shares < SHARES_POR_ORDEM:
        return []
    
    # Quantas ordens completas podemos criar
    num_ordens = int(saldo_shares // SHARES_POR_ORDEM)
    
    # Pega os N preços mais altos da grid
    return GRID_VENDAS[:num_ordens]

def criar_ordem_venda(client, preco, quantidade, token_id):
    """Cria uma ordem de venda"""
    try:
        # Cria nova ordem
        ordem = OrderArgs(
            price=preco,
            size=quantidade,
            side=SELL,
            token_id=token_id
        )
        
        resultado = client.create_and_post_order(ordem)
        print(f"✅ VENDA criada: {quantidade} shares a ${preco:.2f}")
        return True
        
    except Exception as e:
        erro_msg = str(e).lower()
        
        if "balance" in erro_msg or "insufficient" in erro_msg:
            print(f"❌ Saldo insuficiente para venda a ${preco:.2f}")
        elif "already" in erro_msg or "duplicate" in erro_msg:
            print(f"⏭️ Ordem já existe a ${preco:.2f}")
        else:
            print(f"❌ Erro ao criar ordem: {e}")
        
        return False

def main():
    print(">>> 🤖 ROBÔ DE VENDAS SIMPLES - BITCOIN $100K <<<")
    print(f">>> Mercado: Bitcoin superará $100k até 31/12/2025")
    print(f">>> ⚙️ Configuração: {SHARES_POR_ORDEM} shares por ordem")
    print(f">>> 🎯 Preços de venda: {GRID_VENDAS}")
    print(f">>> ⏱️ Verificação a cada: {INTERVALO_SEGUNDOS}s")
    print("="*60)
    
    # Verifica chave privada
    key = os.getenv("PRIVATE_KEY")
    if not key:
        print("❌ ERRO: PRIVATE_KEY não configurada!")
        print("   Execute: export PRIVATE_KEY=sua_chave_privada")
        return
    
    # Inicializa cliente
    try:
        client = ClobClient(
            "https://clob.polymarket.com/", 
            key=key, 
            chain_id=137, 
            signature_type=2, 
            funder=PROXY_ADDRESS
        )
        client.set_api_creds(client.create_or_derive_api_creds())
        print("✅ Conectado ao Polymarket")
    except Exception as e:
        print(f"❌ Falha na conexão: {e}")
        return
    
    print(f"🔍 Monitorando mercado Bitcoin...\n")
    
    ciclo = 0
    
    while True:
        ciclo += 1
        print(f"\n{'='*60}")
        print(f"🔁 CICLO {ciclo} - {time.strftime('%H:%M:%S')}")
        print(f"{'='*60}")
        
        try:
            # 1. Verifica saldo
            saldo_shares = obter_saldo_disponivel(client, TOKEN_ID)
            
            # 2. Verifica ordens ativas
            ordens_ativas = obter_ordens_venda_ativas(client, TOKEN_ID)
            precos_ativos = [o['price'] for o in ordens_ativas]
            
            # 3. Calcula quantas ordens podemos ter
            precos_possiveis = calcular_ordens_possiveis(saldo_shares)
            
            if not precos_possiveis:
                print(f"\n⏭️ Saldo insuficiente: {saldo_shares:.2f} shares")
                print(f"   Mínimo necessário: {SHARES_POR_ORDEM} shares")
            else:
                print(f"\n🎯 Com {saldo_shares:.2f} shares podemos ter {len(precos_possiveis)} ordens:")
                
                # 4. Para cada preço possível, verifica se já existe ordem
                for preco in precos_possiveis:
                    if preco in precos_ativos:
                        print(f"   ✅ Já tem ordem a ${preco:.2f}")
                    else:
                        print(f"   ➕ Criando ordem a ${preco:.2f}...")
                        if criar_ordem_venda(client, preco, SHARES_POR_ORDEM, TOKEN_ID):
                            time.sleep(1)  # Pequeno delay entre ordens
            
            # 5. Mostra resumo
            print(f"\n📋 RESUMO FINAL:")
            print(f"   Saldo livre: {saldo_shares:.2f} shares")
            print(f"   Ordens ativas: {len(ordens_ativas)}")
            
            if ordens_ativas:
                print(f"   Detalhes das ordens:")
                # Ordena do maior para menor preço
                for ordem in sorted(ordens_ativas, key=lambda x: x['price'], reverse=True):
                    print(f"     • ${ordem['price']:.2f}: {ordem['size']:.2f} shares")
            
            # Calcula quanto ainda pode ser vendido
            shares_em_ordens = sum(o['size'] for o in ordens_ativas)
            saldo_livre = saldo_shares - shares_em_ordens
            ordens_adicionais = int(saldo_livre // SHARES_POR_ORDEM)
            
            if ordens_adicionais > 0:
                print(f"\n💡 Ainda pode criar {ordens_adicionais} ordens adicionais")
                print(f"   Saldo disponível: {saldo_livre:.2f} shares")
            
        except Exception as e:
            print(f"\n⚠️ ERRO: {e}")
        
        # 6. Aguarda próximo ciclo
        print(f"\n⏳ Próxima verificação em {INTERVALO_SEGUNDOS} segundos...")
        time.sleep(INTERVALO_SEGUNDOS)

if __name__ == "__main__":
    main()
