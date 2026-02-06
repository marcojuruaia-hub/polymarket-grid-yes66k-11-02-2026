import os
import time
import requests
import re
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OpenOrderParams
from py_clob_client.order_builder.constants import BUY, SELL

# ==========================================================
# ⚙️ CONFIGURAÇÃO
# ==========================================================
BTC_TOKEN_ID = "35318893558430035110899642976572154099643885812628890621430761251325731975007"

PROXY_ADDRESS = "0x658293eF9454A2DD555eb4afcE6436aDE78ab20B"

STEP = 0.01          # distância entre compra e venda
NIVEIS = 5           # quantos níveis abaixo do book
SLEEP = 30
# ==========================================================


def extrair_id_limpo(dado):
    if not dado:
        return None
    if isinstance(dado, list) and dado:
        dado = dado[0]
    match = re.search(r"\d{30,}", str(dado))
    return match
