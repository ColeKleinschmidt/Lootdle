import sys
import requests
from bs4 import BeautifulSoup
import json
import time
import re

sys.stdout.reconfigure(encoding='utf-8')

# Base URL for Stardew Valley Wiki
BASE_URL = "https://stardewvalleywiki.com"

# List of crop names (can be dynamically extracted from the main crop page)
crop_names = [
    "Garlic", "Cauliflower", "Wheat", "Pumpkin", "Strawberry", "Blueberry",
    "Tomato", "Corn", "Eggplant", "Yam", "Cranberries", "Beet", "Coffee_Bean",
    "Hops", "Ancient_Fruit", "Melon", "Potato", "Parsnip", "Radish", "Red_Cabbage"
    # Add more crops here or extract dynamically
]

# Function to fetch data from a crop's individual page
def fetch_crop_data(crop_name):
    crop_url = f"{BASE_URL}/{crop_name.replace(' ', '_')}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(crop_url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract Infobox Table
            infobox = soup.find("table", class_="infobox")

            # Extract Image URL
            image_tag = infobox.find("img") if infobox else None
            image_url = f"{BASE_URL}{image_tag['src']}" if image_tag else "None"

            # Extract Base Sell Price (Only the base price)
            sell_price_row = infobox.find("th", string="Sell Prices").find_next("td") if infobox else None
            base_sell_price = re.search(r"(\d+)g", sell_price_row.text).group(1) if sell_price_row else "None"

            # Extract Season(s)
            season = []
            season_row = infobox.find("th", string="Season") if infobox else None
            if season_row:
                season_icons = season_row.find_next("td").find_all("img")
                season = [icon["alt"] for icon in season_icons] if season_icons else ["Unknown"]

            # Extract Growth Time
            growth_time_row = infobox.find("th", string="Growth Time").find_next("td") if infobox else None
            growth_time = growth_time_row.text.strip().split()[0] if growth_time_row else "None"

            # Extract Regrowth Info (Yes/No)
            regrow_row = infobox.find("th", string="Regrowth").find_next("td") if infobox else None
            regrows = "Yes" if regrow_row else "No"

            # Extract Energy & Health (split into separate fields)
            energy_row = infobox.find("th", string="Energy").find_next("td") if infobox else None
            health_row = infobox.find("th", string="Health").find_next("td") if infobox else None
            energy = re.findall(r"\d+", energy_row.text.strip())[0] if energy_row else "N/A"
            health = re.findall(r"\d+", health_row.text.strip())[0] if health_row else "N/A"

            # Extract Used In (Recipes & Other Uses)
            used_in = []
            used_section = soup.find("span", id="Used_in")
            if used_section:
                used_table = used_section.find_next("table")
                if used_table:
                    used_links = used_table.find_all("a")
                    used_in = [link.text.strip() for link in used_links if link.text.strip()]

            return {
                "Image URL": image_url,
                "Name": crop_name,
                "Base Sell Price": f"{base_sell_price}g",
                "Season": season,
                "Growth Time": f"{growth_time} days",
                "Regrows": regrows,
                "Energy": energy,
                "Health": health,
                "Used In": used_in if used_in else ["None"]
            }

    except requests.exceptions.RequestException as e:
        print(f"⚠️ Failed to fetch data for {crop_name}: {e}")

    return None

# Scrape data for all crops
crop_data = []
for crop in crop_names:
    print(f"Fetching data for: {crop}...")
    data = fetch_crop_data(crop)
    if data:
        crop_data.append(data)

# Save to JSON file
output_file = "stardew_crops_final.json"
with open(output_file, "w", encoding="utf-8") as json_file:
    json.dump(crop_data, json_file, indent=4, ensure_ascii=False)

print(f"✅ Crop data saved to {output_file}")
