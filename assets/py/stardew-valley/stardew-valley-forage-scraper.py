import requests
from bs4 import BeautifulSoup
import json
import sys
import re
import time

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "https://stardewvalleywiki.com"
FORAGING_URL = f"{BASE_URL}/Foraging"

print(f"🔍 Fetching page: {FORAGING_URL}")

response = requests.get(FORAGING_URL)
if response.status_code != 200:
    print(f"❌ Failed to fetch page. Status code: {response.status_code}")
    sys.exit(1)

soup = BeautifulSoup(response.text, "html.parser")

# Find all relevant tables (skip the first one)
tables = soup.find_all("table", class_=lambda x: x and "sortable" in x and "roundedborder" in x)[1:]

if not tables:
    print("❌ No relevant foraging tables found.")
    sys.exit(1)

print(f"✅ Found {len(tables)} foraging tables. Extracting data...")

foraging_data = []

# Function to extract gold values without commas
def extract_gold(text):
    match = re.search(r"(\d{1,3}(?:,\d{3})*)g", text)
    return match.group(1).replace(",", "") + "g" if match else "None"

# Function to extract energy and health from the table row
def extract_energy_health(text):
    numbers = re.findall(r"\d+", text)
    if len(numbers) >= 2:
        return numbers[0], numbers[1]  # Energy, Health
    return "None", "None"

# Function to clean up the Source field
def clean_source(text):
    return re.sub(r"\([^)]*\)|%", "", text).strip()

# Function to extract "Used In" correctly from specific valid sections
def extract_used_in(soup):
    valid_sections = ["Recipes", "Bundles", "Tailoring", "Quests"]
    used_in = []
    
    for section in valid_sections:
        section_header = soup.find("span", {"id": section})
        if section_header:
            section_table = section_header.find_next("table", class_="wikitable")
            if section_table:
                for row in section_table.find_all("tr")[1:]:  # Skip header row
                    first_column = row.find("td")
                    if first_column:
                        link = first_column.find("a")
                        if link and link.text.strip():
                            used_in.append(link.text.strip())

    return list(set(used_in)) if used_in else ["None"]

# Loop through every item in every table
for table_index, table in enumerate(tables):
    print(f"📌 Processing Table {table_index + 1}...")

    tbody = table.find("tbody")
    rows = tbody.find_all("tr")[1:]  # Skip the header row

    for row_index, row in enumerate(rows):
        columns = row.find_all("td")

        if len(columns) < 6:
            continue  # Skip invalid rows

        try:
            # Image
            image_tag = columns[0].find("img")
            image_url = f"{BASE_URL}{image_tag['src']}" if image_tag else "None"

            # Name
            name_tag = columns[1].find("a")
            name = name_tag.text.strip() if name_tag else columns[1].text.strip()

            # Item URL for "Used In"
            item_url = name_tag["href"] if name_tag else None

            # Found (Source)
            raw_found = columns[2].text.strip()
            source = [clean_source(f.strip()) for f in raw_found.split("\n") if f.strip()]

            # Base Sell Price
            base_sell_price = extract_gold(columns[3].text)

            # Iridium Sell Price (Base * 2)
            iridium_sell_price = "None"
            if base_sell_price != "None":
                iridium_price_value = int(base_sell_price.replace("g", "")) * 2
                iridium_sell_price = f"{iridium_price_value}g"

            # Extract Energy & Health directly from the 5th column
            energy, health = extract_energy_health(columns[4].text)

            # Extract season from the sources
            season = []
            for s in source:
                if any(word in s for word in ["Spring", "Summer", "Fall", "Winter"]):
                    season.append(s)
            if not season:
                season = ["Unknown"]

            # Fetch "Used In" from the item's page
            used_in = ["None"]
            if item_url:
                retry_attempts = 3
                while retry_attempts > 0:
                    try:
                        item_response = requests.get(BASE_URL + item_url, timeout=10)
                        if item_response.status_code == 200:
                            item_soup = BeautifulSoup(item_response.text, "html.parser")
                            used_in = extract_used_in(item_soup)
                        break  # If successful, break the retry loop
                    except requests.exceptions.RequestException as e:
                        print(f"⚠️ Request failed ({retry_attempts} retries left): {e}")
                        time.sleep(2)
                        retry_attempts -= 1

                time.sleep(1)  # Prevents hammering the server

            # Store extracted data
            item_data = {
                "Image URL": image_url,
                "Name": name,
                "Base Sell Price": base_sell_price,
                "Iridium Sell Price": iridium_sell_price,
                "Season": season,
                "Source": source,
                "Energy": energy,
                "Health": health,
                "Used In": used_in
            }

            foraging_data.append(item_data)
            print(f"✅ Extracted: {name}")

        except Exception as e:
            print(f"❌ Error processing row {row_index + 1} in Table {table_index + 1}: {e}")

# Save to JSON
output_file = "stardew_foraging.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(foraging_data, f, indent=4, ensure_ascii=False)

print(f"🎯 Scraped {len(foraging_data)} foraging items and saved to {output_file}")
