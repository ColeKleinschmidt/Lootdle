import requests
from bs4 import BeautifulSoup
import json
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

url = "https://stardewvalleywiki.com/Weapons"

print(f"🔍 Fetching page: {url}")

response = requests.get(url)
if response.status_code != 200:
    print(f"❌ Failed to fetch page. Status code: {response.status_code}")
    sys.exit(1)

soup = BeautifulSoup(response.text, "html.parser")

tables = soup.find_all("table", class_=lambda x: x and "sortable" in x and "roundedborder" in x)

if not tables:
    print("❌ No weapon tables found. Printing all tables detected:")
    all_tables = soup.find_all("table")
    for index, tbl in enumerate(all_tables):
        print(f"🔹 Table {index + 1} - Classes: {tbl.get('class')}")
    sys.exit(1)

print(f"✅ Found {len(tables)} weapon tables. Extracting data...")

weapons_data = []

for table_index, table in enumerate(tables):
    print(f"📌 Processing Table {table_index + 1}...")

    tbody = table.find("tbody")
    rows = tbody.find_all("tr")[1:]

    for row_index, row in enumerate(rows):
        columns = row.find_all("td")

        if len(columns) < 6:
            print(f"⚠️ Skipping row {row_index + 1} in Table {table_index + 1}: Not enough columns.")
            continue

        try:
            image_tag = columns[0].find("img")
            image_url = f"https://stardewvalleywiki.com{image_tag['src']}" if image_tag else "None"

            name_tag = columns[1].find("a")
            name = name_tag.text.strip() if name_tag else columns[1].text.strip()

            level = columns[2].text.strip() if len(columns) > 2 else "N/A"
            description = columns[3].text.strip() if len(columns) > 3 else "N/A"
            damage = columns[4].text.strip() if len(columns) > 4 else "N/A"
            crit_chance = columns[5].text.strip() if len(columns) > 5 else "N/A"

            # Extract Stats as an Array
            raw_stats = columns[6].text.strip() if len(columns) > 6 else "None"
            stats = [s.strip() for s in raw_stats.split("\n") if s.strip()] if raw_stats != "None" else ["None"]

            # Extract Location as an Array
            raw_location = columns[7].text.strip() if len(columns) > 7 else "None"
            location = [loc.strip() for loc in raw_location.split("\n") if loc.strip()] if raw_location != "None" else ["None"]

            # Extract Buy and Sell Prices (removing commas)
            def extract_gold(text):
                match = re.search(r"(\d{1,3}(?:,\d{3})*)g", text)
                return match.group(1).replace(",", "") + "g" if match else "None"

            buy_price = extract_gold(columns[8].text) if len(columns) > 8 else "None"
            sell_price = extract_gold(columns[9].text) if len(columns) > 9 else "None"

            # Improved weapon type detection for Range
            weapon_type = name.lower()
            if any(keyword in weapon_type for keyword in ["dagger", "shiv", "stiletto", "dirk"]):
                weapon_range = "Short"
            elif any(keyword in weapon_type for keyword in ["sword", "katana", "falchion", "cutlass", "blade", "saber"]):
                weapon_range = "Medium"
            elif any(keyword in weapon_type for keyword in ["club", "mallet", "hammer", "glaive", "broadsword", "slingshot"]):
                weapon_range = "Long"
            else:
                weapon_range = "Unknown"

            weapon = {
                "Image URL": image_url,
                "Name": name,
                "Level": level,
                "Description": description,
                "Damage": damage,
                "Crit Chance": crit_chance,
                "Stats": stats,
                "Location": location,
                "Buy Price": buy_price,
                "Sell Price": sell_price,
                "Range": weapon_range
            }

            weapons_data.append(weapon)
            print(f"✅ Extracted: {name} | Damage: {damage} | Buy: {buy_price} | Sell: {sell_price} | Range: {weapon_range}")

        except Exception as e:
            print(f"❌ Error processing row {row_index + 1} in Table {table_index + 1}: {e}")

output_file = "stardew_weapons.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(weapons_data, f, indent=4, ensure_ascii=False)

print(f"🎯 Scraped {len(weapons_data)} weapons and saved to {output_file}")
