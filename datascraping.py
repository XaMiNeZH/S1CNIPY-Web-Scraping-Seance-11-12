import sys
try:
    import requests
    from bs4 import BeautifulSoup
    import pandas as pd
except ImportError as e:
    print("Missing required Python package:", e)
    print("Install dependencies with:")
    print("    pip install -r requirements.txt")
    sys.exit(1)

import time
import random

# URL de l'équipe nationale du Maroc sur Transfermarkt
URL = "https://www.transfermarkt.com/morocco/kader/verein/3575/saison_id/2024/plus/1"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

response = requests.get(URL, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

players = []
table = soup.find("table", {"class": "items"})

rows = table.find_all("tr", {"class": ["odd", "even"]})

for row in rows:
    name = row.find("td", {"class": "hauptlink"}).get_text(strip=True)
    
    position_tag = row.find("td", {"class": "zentriert"}).find("table")
    position = ""
    if position_tag:
        position = position_tag.get_text(strip=True)
    
    market_value_tag = row.find("td", {"class": "rechts hauptlink"})
    market_value = market_value_tag.get_text(strip=True) if market_value_tag else "N/A"

    age_tag = row.find_all("td", {"class": "zentriert"})
    try:
        age = age_tag[1].get_text(strip=True)
    except:
        age = "N/A"

    players.append({
        "name": name,
        "age": age,
        "position": position,
        "market_value": market_value
    })

    time.sleep(random.uniform(0.5, 1.2))  # éviter d’être bloqué

df = pd.DataFrame(players)
print(df)

df.to_csv("equipe_maroc.csv", index=False)
print("Données enregistrées dans equipe_maroc.csv")