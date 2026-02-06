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
        return None
    if isinstance(dado, list) and dado:
        dado = dado[0]
    match = re.search(r"\d{30,}", str(dado))
    return match.group(0) if match else None


def calcular_qtd(preco):
    return 5.0 if preco > 0.20 else round(1.0 / preco, 2)


def buscar_id_lula():
    slugs = ["brazil-presidential-election-2026", "brazil-presidential-election"]
    for slug in slugs:
        try:
            url = f"https://gamma-api.polymarket.com/events?slug={slug}"
            resp = requests.get(url, timeout=10).json()
            for event in resp:
                for m in event.get("markets", []):
                    if "Lula" in m.get("question", ""):
                        return extrair_id_limpo(m.get("clobTokenIds"))
        except:
            continue
    return None


def atualizar_ordens(client):
    return client.get_orders(OpenOrderParams())


def separar_ordens(ordens, token_id):
    compras = [round(float(o["price"]), 2) for o in ordens if o["asset_id"] == token_id and o["side"] == BUY]
    vendas  = [round(float(o["price"]), 2) for o in ordens if o["asset_id"] == token_id and o["side"] == SELL]
    return compras, vendas


def processar_ativo(client, token_id, nome, grid):
    print(f"\n--- [{nome}] ---")

    for p_compra in grid:
        ordens = atualizar_ordens(client)
        compras, vendas = separar_ordens(ordens, token_id)

        # 🟢 COMPRA
        if p_compra not in compras:
            try:
                client.create_and_post_order(
                    OrderArgs(
                        price=p_compra,
                        size=calcular_qtd(p_compra),
                        side=BUY,
                        token_id=token_id
                    )
                )
                print(f"✅ {nome}: Compra criada a ${p_compra}")
            except Exception as e:
                print(f"❌ {nome}: Falha na compra {p_compra} → {e}")
                continue

        # ⏳ ainda não executou compra → não vende
        if p_compra not in compras:
            print(f"⏳ {nome}: Aguardando execução d
