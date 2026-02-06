import os
import time
import sys
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs

# --- CONFIGURAÇÕES ---
TOKEN_ID = "21639768904545427220464585903669395149753104733036853605098419574581993896843"
VALOR_ORDEM_USD = 1.00
LUCRO = 0.01
GRID_COMPRA_INICIO = 0.40
GRID_COMPRA_FIM = 0.10
PASSO_COMPRA = 0.02

def main():
    print(">>> ROBÔ V10: O EXTERMINADOR DE CHAVES <<<")
    
    key = os.getenv("PRIVATE_KEY")
    if not key:
        print("ERRO: Sem PRIVATE_KEY.")
        sys.exit(1)

    try:
        # Inicializa conexão
        client = ClobClient("https://clob.polymarket.com/", key=key, chain_id=137)
        print(">>> Conectado. Tentando resolver o conflito de API...")

        # --- ESTRATÉGIA DE LIMPEZA E CRIAÇÃO ---
        try:
            # Tenta criar a chave normalmente
            client.create_api_key()
            print(">>> ✅ Chave criada de primeira!")
        except Exception as e:
            msg = str(e).lower()
            # Se der erro dizendo que já existe...
            if "exists" in msg or "already" in msg or "400" in msg:
                print(">>> ⚠️ Chave antiga detectada. Forçando remoção...")
                try:
                    # Tenta DELETAR a chave antiga usando a assinatura da carteira
                    client.delete_api_key()
                    print(">>> 🗑️ Chave antiga DELETADA com sucesso! (Adeus conflito)")
                    time.sleep(3) # Dá um tempo pro sistema processar
                    
                    # Cria a nova chave limpa
                    client.create_api_key()
                    print(">>> ✅ Nova Chave criada com sucesso! Agora vai!")
                except Exception as e2:
                    print(f">>> ❌ Falha ao deletar chave via código: {e2}")
                    # Tenta derivar como última esperança (se for compatível)
                    try:
                        client.derive_api_key()
                        print(">>> ✅ Chave derivada (recuperada)!")
                    except:
                        pass
            else:
                print(f">>> Erro estranho na criação: {e}")

    except Exception as e:
        print(f"Erro Geral de Conexão: {e}")
        # Segue o baile para tentar operar

    # --- INÍCIO DAS OPERAÇÕES ---
    grid_compras = []
    p = GRID_COMPRA_INICIO
    while p >= GRID_COMPRA_FIM:
        grid_compras.append(round(p, 2))
        p -= PASSO_COMPRA
    
    while True:
        print("\n--- Ciclo de Operação ---")
        
        # COMPRA
        for preco in grid_compras:
            try:
                qtd = round(VALOR_ORDEM_USD / preco, 2)
                resp = client.create_and_post_order(
                    OrderArgs(
                        price=preco,
                        size=qtd,
                        side="BUY", 
                        token_id=TOKEN_ID
                    )
                )
                print(f"✅ SUCESSO! Compra colocada a ${preco}. ID: {resp.get('orderID')}")
            except Exception as e:
                msg = str(e)
                if "balance" in msg.lower():
                     print(f"⚠️ Saldo insuficiente para comprar a ${preco}")
                elif "credentials" in msg.lower():
                     print("❌ ERRO: O robô ainda está sem permissão.")
                else:
                     print(f"❌ Erro ao comprar a ${preco}: {msg}")

        # VENDA
        for preco_compra in grid_compras:
            preco_venda = round(preco_compra + LUCRO, 2)
            try:
                qtd = round(VALOR_ORDEM_USD / preco_compra, 2)
                if preco_venda < 1.0:
                    client.create_and_post_order(
                        OrderArgs(
                            price=preco_venda,
                            size=qtd,
                            side="SELL",
                            token_id=TOKEN_ID
                        )
                    )
                    print(f"💰 VENDA colocada a ${preco_venda}")
            except:
                pass 

        print("Aguardando 30 segundos...")
        time.sleep(30)

if __name__ == "__main__":
    main()
