import os
import time
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OpenOrderParams
from py_clob_client.order_builder.constants import SELL

# --- CONFIGURAÇÕES ---
TOKEN_ID = "21639768904545427220464585903669395149753104733036853605098419574581993896843"
PROXY_ADDRESS = "0x658293eF9454A2DD555eb4afcE6436aDE78ab20B"
SHARES_POR_ORDEM = 5
INTERVALO_SEGUNDOS = 10

# Grid de vendas (da mais alta para a mais baixa)
GRID_VENDAS = [0.30, 0.29, 0.28 0.27, 0.26, 0.25, 0.24, 0.23, 0.22, 0.21, 0.20]

def obter_ordens_ativas(client):
    """Obtém todas as ordens ativas"""
    try:
        return client.get_orders(OpenOrderParams())
    except Exception as e:
        print(f"❌ Erro ao buscar ordens: {e}")
        return []

def main():
    print(">>> 🤖 ROBÔ DE VENDAS BITCOIN - MODO SIMPLES <<<")
    print(">>> Estratégia: Criar ordens até acabar o saldo")
    
    # Configuração
    key = os.getenv("PRIVATE_KEY")
    if not key:
        print("❌ ERRO: PRIVATE_KEY não configurada!")
        print("   Adicione no GitHub Secrets ou variável de ambiente")
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
    
    ciclo = 0
    ordens_criadas = []
    
    while True:
        ciclo += 1
        print(f"\n{'='*50}")
        print(f"🔁 CICLO {ciclo} - {time.strftime('%H:%M:%S')}")
        print(f"{'='*50}")
        
        try:
            # 1. Ver ordens atuais
            ordens = obter_ordens_ativas(client)
            ordens_venda = []
            
            for ordem in ordens:
                if (ordem.get('asset_id') == TOKEN_ID and 
                    ordem.get('status') == 'open' and
                    ordem.get('side') == 'SELL'):
                    
                    preco = round(float(ordem.get('price', 0)), 2)
                    tamanho = float(ordem.get('size', 0))
                    ordens_venda.append(preco)
                    print(f"   ✅ Ordem ativa: {tamanho} shares a ${preco:.2f}")
            
            print(f"\n📊 Total de ordens ativas: {len(ordens_venda)}")
            
            # 2. Tentar criar próxima ordem na sequência
            ordem_criada_neste_ciclo = False
            
            for preco in GRID_VENDAS:
                if preco not in ordens_venda and preco not in ordens_criadas:
                    print(f"\n🔄 Tentando criar ordem a ${preco:.2f}...")
                    
                    try:
                        # Cria ordem
                        ordem = OrderArgs(
                            price=preco,
                            size=SHARES_POR_ORDEM,
                            side=SELL,
                            token_id=TOKEN_ID
                        )
                        
                        client.create_and_post_order(ordem)
                        ordens_criadas.append(preco)
                        print(f"✅ SUCESSO! Ordem criada: {SHARES_POR_ORDEM} shares a ${preco:.2f}")
                        ordem_criada_neste_ciclo = True
                        break  # Para após criar uma ordem
                        
                    except Exception as e:
                        erro_msg = str(e).lower()
                        
                        if "balance" in erro_msg or "insufficient" in erro_msg:
                            print(f"❌ SEM SALDO para ordem a ${preco:.2f}")
                            print(f"   ⏹️ Parando criação de novas ordens")
                            # Remove da lista para não tentar de novo
                            if preco in ordens_criadas:
                                ordens_criadas.remove(preco)
                            break
                        elif "already" in erro_msg or "duplicate" in erro_msg:
                            print(f"⏭️ Ordem já existe a ${preco:.2f}")
                            ordens_criadas.append(preco)
                        else:
                            print(f"⚠️ Erro desconhecido: {e}")
            
            # 3. Mostrar resumo
            print(f"\n📋 RESUMO:")
            print(f"   Preços com ordem: {sorted(ordens_criadas, reverse=True)}")
            print(f"   Total de ordens criadas: {len(ordens_criadas)}")
            
            if not ordem_criada_neste_ciclo:
                print(f"   ✅ Todas ordens possíveis já foram criadas")
            
        except Exception as e:
            print(f"\n⚠️ ERRO GERAL: {e}")
        
        # 4. Esperar próximo ciclo
        print(f"\n⏳ Próximo ciclo em {INTERVALO_SEGUNDOS} segundos...")
        time.sleep(INTERVALO_SEGUNDOS)

if __name__ == "__main__":
    main()
