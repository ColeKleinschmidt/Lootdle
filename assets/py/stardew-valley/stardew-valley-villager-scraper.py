import requests
from bs4 import BeautifulSoup
import json
import sys

# Set UTF-8 encoding for Windows console
sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "https://stardewvalleywiki.com"

def get_hated_gifts(villager_name):
    url = f"{BASE_URL}/List_of_All_Gifts"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    gift_table = soup.find("table", {"class": "wikitable"})

    for row in gift_table.find_all("tr"):
        columns = row.find_all("td")
        if columns:
            name = columns[0].get_text(strip=True)
            if name.lower() == villager_name.lower():
                hated_gifts = [gift.text.strip() for gift in columns[-1].find_all("a")]
                return hated_gifts if hated_gifts else ["None"]
    
    return ["None"]

# Fetch the main Villagers page
villager_list_url = f"{BASE_URL}/Villagers"
response = requests.get(villager_list_url)
soup = BeautifulSoup(response.text, "html.parser")

# Find all villager links
villager_links = []
villager_galleries = soup.find_all("ul", class_="gallery mw-gallery-packed villagergallery")
for gallery in villager_galleries:
    for villager in gallery.find_all("a", title=True):
        villager_name = villager["title"]
        villager_links.append((villager_name, f"{BASE_URL}{villager['href']}"))

print(f"Found {len(villager_links)} villagers. Starting scraping...")

villager_data = []

# Scrape data for each villager
for name, url in villager_links:
    print(f"🔍 Scraping {name}... ({url})")
    
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    infobox = soup.find("table", id="infoboxtable")
    if not infobox:
        print(f"⚠️ No infobox found for {name}. Skipping...")
        continue

    data = {
        "Image URL": None,
        "Name": name,
        "Birthday": "None",
        "Lives In": "None",
        "Address": "None",
        "Marriage": "No",
        "Family": ["None"],
        "Loved Gifts": ["None"],
        "Hated Gifts": get_hated_gifts(name)
    }

    # Extract image
    img_tag = infobox.find("img")
    if img_tag:
        data["Image URL"] = f"{BASE_URL}{img_tag['src']}"

    # Extracting fields from the infobox
    rows = infobox.find_all("tr")
    for row in rows:
        header = row.find("td", id="infoboxsection")
        value = row.find("td", id="infoboxdetail")

        if header and value:
            field = header.text.strip()
            value_text = value.get_text(separator=" ", strip=True)

            if field == "Birthday":
                season_tag = value.find("a", title=True)
                season = season_tag.text.strip() if season_tag else "Unknown"
                day = value_text.replace(season, "").strip()
                data["Birthday"] = f"{season} {day}"

            elif field == "Lives In":
                data["Lives In"] = value_text

            elif field == "Address":
                data["Address"] = value_text

            elif field == "Marriage":
                data["Marriage"] = "Yes" if "Yes" in value_text else "No"

            elif field == "Family":
                family_members = [a.text.strip() for a in value.find_all("a")]
                data["Family"] = family_members if family_members else ["None"]

            elif field == "Loved Gifts":
                loved_gifts = [a.text.strip() for a in value.find_all("a")]
                data["Loved Gifts"] = loved_gifts if loved_gifts else ["None"]

    villager_data.append(data)

# Save the scraped data to a JSON file
output_file = "stardew_villagers.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(villager_data, f, indent=4, ensure_ascii=False)

print(f"\n✅ Scraped {len(villager_data)} villagers and saved to {output_file}")
