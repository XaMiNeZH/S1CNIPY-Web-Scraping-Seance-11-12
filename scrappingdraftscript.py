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
import re

# URL de l'équipe nationale du Maroc sur Transfermarkt
URL = "https://www.transfermarkt.com/morocco/kader/verein/3575/saison_id/2024/plus/1"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_player_details(player_url):
    """Scrape detailed player information from their profile page"""
    try:
        time.sleep(random.uniform(1, 2))  # Be respectful with requests
        response = requests.get(player_url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        
        details = {
            "height": "N/A",
            "foot": "N/A",
            "debut": "N/A"
        }
        
        # Method 1: Look for info-table with different possible structures
        info_sections = soup.find_all("span", class_=re.compile(r"info-table__content"))
        
        for i, span in enumerate(info_sections):
            text = span.get_text(strip=True)
            
            # Height detection - look for pattern like "1,85 m" or "185 cm"
            if re.search(r'\d[,\.]\d{2}\s*m', text) or re.search(r'\d{3}\s*cm', text):
                details["height"] = text
            
            # Foot detection - look for common foot values
            if text.lower() in ["right", "left", "both", "right foot", "left foot", "both feet"]:
                details["foot"] = text
        
        # Method 2: Try to find data in the player's header section
        if details["height"] == "N/A":
            # Look for all text containing height patterns
            all_spans = soup.find_all("span")
            for span in all_spans:
                text = span.get_text(strip=True)
                if re.search(r'\d[,\.]\d{2}\s*m', text):
                    details["height"] = text
                    break
        
        # Method 3: Look for foot in labels
        if details["foot"] == "N/A":
            labels = soup.find_all(string=re.compile(r"Foot", re.IGNORECASE))
            for label in labels:
                parent = label.find_parent()
                if parent:
                    next_elem = parent.find_next_sibling()
                    if next_elem:
                        foot_text = next_elem.get_text(strip=True)
                        if foot_text.lower() in ["right", "left", "both"]:
                            details["foot"] = foot_text
                            break
        
        # Get national team debut
        # Look for tables with national team data
        tables = soup.find_all("table", {"class": "items"})
        for table in tables:
            rows = table.find_all("tr", class_=re.compile(r"(odd|even)"))
            for row in rows:
                # Check if this row mentions Morocco
                row_text = row.get_text()
                if "Morocco" in row_text or "Maroc" in row_text:
                    # Try to find date cells
                    date_cells = row.find_all("td", {"class": "zentriert"})
                    for cell in date_cells:
                        cell_text = cell.get_text(strip=True)
                        # Look for date patterns like "Nov 15, 2019" or "15.11.2019"
                        if re.search(r'\d{2}[./]\d{2}[./]\d{4}|\w{3}\s+\d{1,2},\s+\d{4}', cell_text):
                            details["debut"] = cell_text
                            break
                    if details["debut"] != "N/A":
                        break
            if details["debut"] != "N/A":
                break
        
        return details
    
    except Exception as e:
        print(f"  ⚠ Error scraping details: {e}")
        return {
            "height": "N/A",
            "foot": "N/A",
            "debut": "N/A"
        }

print("Fetching Morocco team data...")
response = requests.get(URL, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

players = []
table = soup.find("table", {"class": "items"})

if not table:
    print("Could not find player table. Page structure may have changed.")
    sys.exit(1)

rows = table.find_all("tr", {"class": ["odd", "even"]})
total_players = len(rows)

print(f"Found {total_players} players. Scraping details...")
print("This may take 1-2 minutes...")
print()

for idx, row in enumerate(rows, 1):
    try:
        # Basic info from main table
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
        
        # Get player profile URL
        player_link = row.find("td", {"class": "hauptlink"}).find("a")
        if player_link and player_link.get("href"):
            player_url = "https://www.transfermarkt.com" + player_link.get("href")
            print(f"[{idx}/{total_players}] Scraping {name}...", end="")
            player_details = get_player_details(player_url)
            
            # Show what was found
            status = []
            if player_details["height"] != "N/A":
                status.append(f"H:{player_details['height']}")
            if player_details["foot"] != "N/A":
                status.append(f"F:{player_details['foot']}")
            if player_details["debut"] != "N/A":
                status.append(f"D:✓")
            
            if status:
                print(f" [{', '.join(status)}]")
            else:
                print(" [No extra data found]")
        else:
            print(f"[{idx}/{total_players}] {name} - No profile URL")
            player_details = {
                "height": "N/A",
                "foot": "N/A",
                "debut": "N/A"
            }
        
        players.append({
            "name": name,
            "age": age,
            "position": position,
            "height": player_details["height"],
            "foot": player_details["foot"],
            "debut": player_details["debut"],
            "market_value": market_value
        })
        
    except Exception as e:
        print(f"  ✗ Error processing player in row {idx}: {e}")
        continue

df = pd.DataFrame(players)
print("\n" + "="*80)
print("Scraping completed!")
print("="*80)
print(df.to_string())

df.to_csv("equipe_maroc.csv", index=False, encoding='utf-8-sig')
print("\n✓ Data saved to equipe_maroc.csv")
print(f"Total players scraped: {len(players)}")

# Show summary statistics
height_found = sum(1 for p in players if p["height"] != "N/A")
foot_found = sum(1 for p in players if p["foot"] != "N/A")
debut_found = sum(1 for p in players if p["debut"] != "N/A")

print(f"\nData collection summary:")
print(f"  - Height: {height_found}/{len(players)} players")
print(f"  - Foot: {foot_found}/{len(players)} players")
print(f"  - Debut: {debut_found}/{len(players)} players")