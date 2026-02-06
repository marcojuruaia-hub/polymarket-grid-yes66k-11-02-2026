import os
import time
import requests
import re
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OpenOrderParams
from py_clob_client.order_builder.constants import BUY, SELL

# ==========================================================
# 🎯 CONFIGURAÇÃO
# ==========================================================
BTC_TOKEN_ID = "35318893558430035110899642976572154099643885812628890621430761251325731975007"

BTC_GRID  = [round(x * 0.01, 2) for x in range(36, 29, -1)]
LULA_GRID = [round(x * 0.01, 2) for x in range(52, 39, -1)]

PROXY_ADDRESS = "0x658293eF9454A2DD555eb4afcE6436aDE78ab20B"
STEP_LUCRO = 0.01
SLEEP = 30
# ==========================================================


def extrair_id_limpo(dado):
    if not dado:
        retur
