import requests
from bs4 import BeautifulSoup
import json
import time
import sys
import re
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "https://leagueoflegends.fandom.com"
CATEGORIES = [
    ("Starter", "https://leagueoflegends.fandom.com/wiki/Category:Starter_items"),
    ("Boots", "https://leagueoflegends.fandom.com/wiki/Category:Boots_items"),
    ("Basic", "https://leagueoflegends.fandom.com/wiki/Category:Basic_items"),
    ("Epic", "https://leagueoflegends.fandom.com/wiki/Category:Epic_items"),
    ("Legendary", "https://leagueoflegends.fandom.com/wiki/Category:Legendary_items")
]
HEADERS = {"User-Agent": "Mozilla/5.0"}

CORE_STATS = {
    "Ability Power", "Attack Speed", "Armor", "Magic Resistance", "Health",
    "Movement Speed", "Ability Haste", "Lifesteal", "Omnivamp", "Tenacity",
    "Critical Strike Chance", "Spell Vamp", "Attack Damage", "Mana", "Mana Regeneration",
    "Heal and Shield Power", "Health Regeneration", "Gold Per Second", "Lethality"
}

def get_item_links(category_url):
    response = requests.get(category_url, headers=HEADERS)
    if response.status_code != 200:
        print(f"⚠️ Failed to fetch category: {category_url}")
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    item_links = []
    for a_tag in soup.select(".category-page__member-link"):  # Get ALL items
        href = a_tag.get("href")
        if href:
            item_links.append(BASE_URL + href)
    
    return item_links

def extract_gold_efficiency(name, text):
    if "Cull" in name:
        return "154%"  # Manually override Cull's efficiency
    if "Black Spear" in name:
        return "0%"  # Kalista's Black Spear is the only 0% gold efficient item
    match = re.search(r"(\d+(?:\.\d+)?)%", text)
    if match:
        return str(int(round(float(match.group(1))))) + "%"
    return "100%"  # Default to 100% if no efficiency found

def extract_stats(soup, name):
    """ Extracts only correct stats from the infobox, ensuring full accuracy. """
    if "Black Spear" in name:
        return "None"  # Special case for Black Spear
    
    stats = []
    
    # Extract stats from both <a> tags and plain text inside <div class="pi-data-value">
    stat_elements = soup.select("aside.pi-theme-wikia .pi-item.pi-data .pi-data-value a, aside.pi-theme-wikia .pi-item.pi-data .pi-data-value")

    for stat in stat_elements:
        stat_text = stat.text.strip()
        clean_stat = re.sub(r"[0-9+%]", "", stat_text).strip()  # Remove numbers and symbols
        clean_stat = clean_stat.replace("\n", " ").replace("  ", " ").title()

        # Ensure stats like "Lethality" & "Gold Per Second" are correctly included
        for core_stat in CORE_STATS:
            if core_stat.lower() in clean_stat.lower() and core_stat not in stats:
                stats.append(core_stat)

    if not stats:  # If no stats were found, store "None"
        return "None"

    print(f"✅ Verified Stats for {name}: {stats}")  # Debugging output
    return stats

def extract_item_data(item_url, category):
    response = requests.get(item_url, headers=HEADERS)
    if response.status_code != 200:
        print(f"⚠️ Failed to fetch item: {item_url}")
        return None
    
    soup = BeautifulSoup(response.text, "html.parser")
    item_data = {}
    
    item_data["Name"] = soup.find("h1", class_="page-header__title").text.strip()
    
    # Extract image URL and clean it
    img_tag = soup.select_one("aside.pi-theme-wikia img")
    if img_tag and "src" in img_tag.attrs:
        image_url = img_tag["src"]
        image_url = re.sub(r"^https://leagueoflegends.fandom.com", "", image_url)  # Remove extra prefix
        item_data["Image URL"] = image_url
    else:
        item_data["Image URL"] = "None"
    
    # Add category (removing 'Item' from the category name)
    item_data["Category"] = category
    
    # Extract cost and add "g" to gold values
    cost_tag = soup.select_one("aside.pi-theme-wikia .pi-data-value[data-source='buy']")
    cost_value = "0g" if "Black Spear" in item_data["Name"] else (cost_tag.text.strip() if cost_tag else "Unknown")
    if cost_value.isdigit():
        cost_value += "g"  # Append "g" if it's just a number
    item_data["Cost"] = cost_value
    
    # Extract stats and ensure full accuracy
    item_data["Stats"] = extract_stats(soup, item_data["Name"])
    
    # Extract gold efficiency
    efficiency_tag = soup.select_one(".mw-collapsible-content ul:nth-child(4)")
    item_data["Gold Efficiency"] = extract_gold_efficiency(item_data["Name"], efficiency_tag.text if efficiency_tag else "")
    
    # Determine if the item is unique
    if category in ["Boots", "Legendary"]:
        item_data["Unique"] = "Yes"  # All Boots and Legendary items are Unique by default
    else:
        unique_tag = soup.select_one("aside.pi-theme-wikia .pi-data-value b")
        limitations_tag = soup.select_one("aside.pi-theme-wikia .pi-group[data-source='limitations']")
        item_data["Unique"] = "Yes" if (unique_tag and "Unique" in unique_tag.text) or limitations_tag else "No"
    
    # Determine if the item is a component
    builds_into_section = soup.select_one("aside.pi-theme-wikia .pi-group[data-source='recipe']")
    item_data["Component"] = "No" if not builds_into_section else "Yes"
    
    # Extract maps with manual renaming
    maps_section = soup.select("aside.pi-theme-wikia .pi-smart-data-value")
    maps = []
    for map_tag in maps_section:
        map_text = map_tag.text.strip()
        if map_text == "SR 5v5":
            maps.append("Summoner's Rift")
        elif map_text == "HA ARAM":
            maps.append("ARAM")
        else:
            maps.append(map_text)
    item_data["Maps"] = maps if maps else ["Unknown"]
    
    # Remove items that have "Arena" as their only map
    if len(item_data["Maps"]) == 1 and item_data["Maps"][0] == "Arena":
        print(f"🗑️ Skipping {item_data['Name']} (Only in Arena)")
        return None
    
    return item_data

def main():
    all_items = []
    for category_name, category_url in CATEGORIES:
        print(f"Scraping category: {category_url}")
        item_links = get_item_links(category_url)
        
        for item_url in item_links:
            print(f"Fetching item: {item_url}")
            item_data = extract_item_data(item_url, category_name)
            if item_data:
                all_items.append(item_data)
    
    output_file = "lol_items.json"
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(all_items, file, indent=4, ensure_ascii=False)
    
    print(f"✅ Scraping complete! Data saved to {output_file}")

if __name__ == "__main__":
    main()
