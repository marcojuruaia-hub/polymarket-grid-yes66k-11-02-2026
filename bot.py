import os
import time
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OpenOrderParams
from py_clob_client.order_builder.constants import SELL

# --- CONFIGURAÇÕES ---
TOKEN_ID = "21639768904545427220464585903669395149753104733036853605098419574581993896843"
PROXY_ADDRESS = "0x658293eF9454A2DD555eb4afcE6436aDE78ab20B"
SHARES_POR_ORDEM = 5
INTERVALO_SEGUNDOS = 10  # REDUZIDO PARA 10 SEGUNDOS

# Grid de vendas (da mais alta para a mais baixa)
GRID_VENDAS = [0.80, 0.79, 0.78, 0.77, 0.76, 0.75, 0.74, 0.73, 0.72, 0.71, 0.70]

def obter_ordens_ativas(client):
    """Obtém todas as ordens ativas"""
    try:
        return client.get_orders(OpenOrderParams())
    except Exception as e:
        print(f"❌ Erro ao buscar ordens: {e}")
        return []

def main():
    print(">>> 🤖 ROBÔ DE VENDAS BITCOIN - MODO RÁPIDO <<<")
    print(f">>> Intervalo: {INTERVALO_SEGUNDOS} segundos")
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
            "https://clob.polymarket.com
