import requests
import time

def raio_x_polymarket():
    print("\n" + "="*50)
    print("🔎 INICIANDO RAIO-X DAS ELEIÇÕES BRASIL 2026")
    print("="*50)
    
    # Tentamos os dois formatos de slug possíveis
    slugs = ["brazil-presidential-election-2026", "brazil-presidential-election"]
    
    for slug in slugs:
        url = f"https://gamma-api.polymarket.com/events?slug={slug}"
        try:
            resp = requests.get(url).json()
            for event in resp:
                for market in event.get("markets", []):
                    # Aqui pegamos a pergunta e os IDs
                    question = market.get("question", "Sem nome")
                    # No sistema novo, os IDs ficam em clobTokenIds
                    ids = market.get("clobTokenIds", [])
                    
                    print(f"\n📌 MERCADO: {question}")
                    if ids:
                        print(f"✅ ID YES: {ids[0]}")
                        if len(ids) > 1:
                            print(f"❌ ID NO:  {ids[1]}")
                    else:
                        print("⚠️  Nenhum ID encontrado para este mercado.")
        except Exception as e:
            print(f"❌ Erro ao acessar slug {slug}: {e}")

    print("\n" + "="*50)
    print("FIM DA VARREDURA. PROCURE O LULA NA LISTA ACIMA!")
    print("="*50)

if __name__ == "__main__":
    while True:
        raio_x_polymarket()
        time.sleep(300)
