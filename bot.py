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
                    'id': ordem.get('id'),
                    'price': round(float(ordem.get('price', 0)), 2),
                    'size': float(ordem.get('size', 0)),
                    'size_matched': float(ordem.get('size_matched', 0))
                })
        
        print(f"📊 Ordens de venda ativas: {len(ordens_venda)}")
        return ordens_venda
    except Exception as e:
        print(f"❌ Erro ao obter ordens: {e}")
        return []

def calcular_precos_para_venda(saldo_shares):
    """Calcula em quais preços colocar ordens de venda baseado no saldo"""
    if saldo_shares < SHARES_POR_ORDEM:
        print(f"⏭️ Saldo insuficiente: {saldo_shares:.2f} < {SHARES_POR_ORDEM}")
        return []
    
    # Quantas ordens completas podemos criar
    num_ordens_possiveis = int(saldo_shares // SHARES_POR_ORDEM)
    
    # Pega os N preços mais altos da grid
    precos_selecionados = GRID_VENDAS[:num_ordens_possiveis]
    
    return precos_selecionados

def criar_ordem_venda(client, preco, quantidade, token_id, max_tentativas=3):
    """Tenta criar uma ordem de venda com tratamento de erros"""
    for tentativa in range(max_tentativas):
        try:
            # Verifica se já existe ordem no mesmo preço
            ordens_ativas = obter_ordens_venda_ativas(client, token_id)
            for ordem in ordens_ativas:
                if ordem['price'] == preco and ordem['size_matched'] == 0:
                    print(f"⏭️ Ordem já existe a ${preco:.2f}")
                    return False
            
            # Cria nova ordem
            ordem_args = OrderArgs(
                price=preco,
                size=quantidade,
                side=SELL,
                token_id=token_id
            )
            
            resultado = client.create_and_post_order(ordem_args)
            print(f"✅ VENDA criada: {quantidade} shares a ${preco:.2f}")
            return True
            
        except Exception as e:
            erro_msg = str(e).lower()
            
            if "balance" in erro_msg or "insufficient" in erro_msg:
                print(f"❌ Saldo insuficiente para venda a ${preco:.2f}")
                return False
            elif "already" in erro_msg or "duplicate" in erro_msg:
                print(f"⏭️ Ordem duplicada detectada a ${preco:.2f}")
                return False
            elif "nonce" in erro_msg:
                print(f"⚠️ Erro de nonce, tentando novamente... ({tentativa + 1}/{max_tentativas})")
                time.sleep(1)
            else:
                print(f"⚠️ Erro na tentativa {tentativa + 1}: {e}")
                if tentativa < max_tentativas - 1:
                    time.sleep(2)
    
    print(f"❌ Falha após {max_tentativas} tentativas para venda a ${preco:.2f}")
    return False

def cancelar_ordens_antigas(client, token_id, precos_desejados):
    """Cancela ordens que não estão mais nos preços desejados"""
    try:
        ordens_ativas = obter_ordens_venda_ativas(client, token_id)
        
        for ordem in ordens_ativas:
            # Cancela se:
            # 1. O preço não está na lista desejada
            # 2. A ordem ainda não foi executada (size_matched == 0)
            if ordem['price'] not in precos_desejados and ordem['size_matched'] == 0:
                try:
                    # Método correto para cancelar ordem
                    client.cancel_order(ordem['id'])
                    print(f"♻️ Cancelada ordem obsoleta a ${ordem['price']:.2f}")
                except Exception as e:
                    print(f"⚠️ Erro ao cancelar ordem: {e}")
    except Exception as e:
        print(f"⚠️ Erro ao cancelar ordens antigas: {e}")

def mostrar_resumo(client, token_id):
    """Mostra um resumo detalhado da situação"""
    saldo = obter_saldo_disponivel(client, token_id)
    ordens_venda = obter_ordens_venda_ativas(client, token_id)
    precos_desejados = calcular_precos_para_venda(saldo)
    
    print(f"\n📋 RESUMO DA SITUAÇÃO:")
    print(f"   Saldo disponível: {saldo:.2f} shares")
    print(f"   Ordens de venda ativas: {len(ordens_venda)}")
    print(f"   Ordens possíveis: {len(precos_desejados)}")
    
    if ordens_venda:
        print(f"\n   📊 ORDENS ATIVAS:")
        # Ordena do maior para o menor preço
        for ordem in sorted(ordens_venda, key=lambda x: x['price'], reverse=True):
            status = "⏳" if ordem['size_matched'] == 0 else "✅"
            print(f"     {status} ${ordem['price']:.2f}: {ordem['size']:.2f} shares")
    
    if precos_desejados:
        print(f"\n   🎯 PREÇOS DESEJADOS:")
        for preco in precos_desejados:
            ja_existe = any(o['price'] == preco for o in ordens_venda)
            status = "✅" if ja_existe else "⏳"
            print(f"     {status} ${preco:.2f}")
    
    # Calcula totais
    total_em_ordens = sum(o['size'] - o['size_matched'] for o in ordens_venda)
    saldo_livre = saldo - total_em_ordens
    
    print(f"\n   💰 TOTAIS:")
    print(f"     Em ordens: {total_em_ordens:.2f} shares")
    print(f"     Livre: {saldo_livre:.2f} shares")

def main():
    print(">>> 🤖 ROBÔ DE VENDAS AUTOMÁTICAS - BITCOIN <<<")
    print(f">>> ⚙️ Configuração: {SHARES_POR_ORDEM} shares por ordem")
    print(f">>> 🎯 Grid de vendas: {GRID_VENDAS}")
    print(f">>> ⏱️ Intervalo: {INTERVALO_SEGUNDOS}s\n")
    
    # Verifica chave privada
    key = os.getenv("PRIVATE_KEY")
    if not key:
        print("❌ PRIVATE_KEY não encontrada nas variáveis de ambiente!")
        print("   Configure: export PRIVATE_KEY=sua_chave_privada")
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
        print("✅ Cliente CLOB inicializado com sucesso!")
        print(f"   Token ID: {TOKEN_ID[:15]}...")
    except Exception as e:
        print(f"❌ Erro ao inicializar cliente CLOB: {e}")
        return
    
    ciclo = 0
    
    while True:
        ciclo += 1
        print(f"\n{'='*60}")
        print(f"🔄 CICLO {ciclo} - {time.strftime('%H:%M:%S')}")
        print(f"{'='*60}")
        
        try:
            # 1. Obtém saldo atual
            saldo_shares = obter_saldo_disponivel(client, TOKEN_ID)
            
            # 2. Obtém ordens de venda ativas
            ordens_venda_ativas = obter_ordens_venda_ativas(client, TOKEN_ID)
            precos_ativos = [o['price'] for o in ordens_venda_ativas]
            
            # 3. Calcula onde deveríamos ter ordens
            precos_desejados = calcular_precos_para_venda(saldo_shares)
            
            # 4. Se temos saldo suficiente para pelo menos uma ordem
            if precos_desejados:
                print(f"\n🎯 Estratégia para {saldo_shares:.2f} shares:")
                print(f"   Preços desejados: {precos_desejados}")
                
                # 5. Cancela ordens que não deveriam mais existir
                if ordens_venda_ativas:
                    cancelar_ordens_antigas(client, TOKEN_ID, precos_desejados)
                    # Atualiza lista após cancelamentos
                    ordens_venda_ativas = obter_ordens_venda_ativas(client, TOKEN_ID)
                    precos_ativos = [o['price'] for o in ordens_venda_ativas]
                
                # 6. Cria ordens faltantes
                print(f"\n📈 Criando ordens faltantes...")
                ordens_criadas = 0
                
                for preco in precos_desejados:
                    if preco in precos_ativos:
                        print(f"   ⏭️ Já existe ordem a ${preco:.2f}")
                        continue
                    
                    # Calcula quantas ordens já temos nos preços mais altos
                    # Isso garante que sempre priorizamos os preços mais altos
                    ordens_acima = sum(1 for p in precos_ativos if p > preco)
                    shares_comprometidas = ordens_acima * SHARES_POR_ORDEM
                    
                    # Verifica se ainda temos saldo livre para esta ordem
                    if saldo_shares - shares_comprometidas >= SHARES_POR_ORDEM:
                        if criar_ordem_venda(client, preco, SHARES_POR_ORDEM, TOKEN_ID):
                            ordens_criadas += 1
                            time.sleep(1)  # Delay para evitar rate limit
                    else:
                        print(f"   ⚠️ Saldo insuficiente para ordem a ${preco:.2f}")
            
            else:
                print(f"\n⏭️ Saldo insuficiente para criar ordens")
                print(f"   Mínimo necessário: {SHARES_POR_ORDEM} shares")
            
            # 7. Mostra resumo final
            mostrar_resumo(client, TOKEN_ID)
            
        except Exception as e:
            print(f"\n⚠️ ERRO NO CICLO: {e}")
            import traceback
            traceback.print_exc()
        
        # 8. Aguarda próximo ciclo
        print(f"\n⏳ Próximo ciclo em {INTERVALO_SEGUNDOS} segundos...")
        for i in range(INTERVALO_SEGUNDOS, 0, -10):
            if i <= 10:
                print(f"   Reiniciando em {i}s...")
            time.sleep(10 if i > 10 else i)

if __name__ == "__main__":
    main()
