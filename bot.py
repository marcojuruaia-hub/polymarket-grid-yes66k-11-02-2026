import os
import time
import requests

POLYMARKET_API = "https://api.polymarket.com"

MARKET_SLUG = "bitcoin-above-66k-on-february-11"

GRID_BUY_PRICES = [0.40, 0.35, 0.30, 0.25, 0.20, 0.15, 0.10]
TAKE_PROFIT = 0.01
ORDER_SIZE_USD = 5


API_KEY = os.getenv("POLYMARKET_API_KEY")
WALLET = os.getenv("POLYMARKET_WALLET")

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def get_yes_price():
    r = requests.get(f"{POLYMARKET_API}/markets/{MARKET_SLUG}")
    data = r.json()
    return float(data["outcomes"]["YES"]["price"])

def place_order(side, price):
    payload = {
        "market": MARKET_SLUG,
        "side": side,
        "outcome": "YES",
        "price": price,
        "amount": ORDER_SIZE_USD
    }
    r = requests.post(
        f"{POLYMARKET_API}/orders",
        json=payload,
        headers=HEADERS
    )
    return r.json()

print("🤖 Bot Polymarket Grid iniciado")
print("Rodando na nuvem...")

while True:
    try:
        price = get_yes_price()
        print(f"Preço YES atual: {price}")

        if price <= BUY_PRICE:
            print("Comprando YES...")
            place_order("buy", BUY_PRICE)

        if price >= SELL_PRICE:
            print("Vendendo YES...")
            place_order("sell", SELL_PRICE)

        time.sleep(30)

    except Exception as e:
        print("Erro:", e)
        time.sleep(60)
