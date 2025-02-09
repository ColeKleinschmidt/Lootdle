import requests
from bs4 import BeautifulSoup
import json
import re

BASE_URL = "https://terraria.wiki.gg"

def get_weapon_links():
    url = f"{BASE_URL}/wiki/List_of_weapons"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to fetch page, status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    weapon_links = []
    
    # Find all links inside the weapons list
    for a_tag in soup.select("td a[href^='/wiki/']"):
        link = a_tag["href"]
        if "List_of_weapons" not in link:  # Exclude self-referencing link
            weapon_links.append(BASE_URL + link)

    print(f"Found {len(weapon_links)} weapon links")
    return list(set(weapon_links))  # Remove duplicates

def detect_crafting(soup):
    crafting_header = soup.find("span", class_="mw-headline", id="Recipes")
    if crafting_header:
        crafting_table = crafting_header.find_next("table", class_=re.compile(r"cellborder|craftingtable"))
        if crafting_table:
            return "Crafting"
    return None

def detect_drop(soup):
    keywords = ["drop", "chance", "%"]
    paragraphs = soup.find_all("p")
    for paragraph in paragraphs:
        text = paragraph.get_text().lower()
        if all(keyword in text for keyword in keywords):
            return "Drop"
    return None

def detect_loot(soup):
    loot_phrases = ["found in chests", "found in crates", "can be found in", "chest", "crate"]
    paragraphs = soup.find_all("p")
    for paragraph in paragraphs:
        text = paragraph.get_text().lower()
        if any(phrase in text for phrase in loot_phrases):
            return "Loot"
    return None

def detect_buy(soup):
    buy_row = soup.select_one("#mw-content-text > div.mw-parser-output > div.infobox.item > div:nth-child(3) > table > tbody > tr:nth-child(9)")
    if buy_row and "Buy" in buy_row.get_text():
        return "Buy"
    return None

def detect_game_stage(soup):
    paragraphs = soup.find_all("p")
    for paragraph in paragraphs:
        text = paragraph.get_text().lower()
        if "pre-hardmode" in text:
            return "Pre-Hardmode"
        if "hardmode" in text:
            return "Hardmode"
    return None

def extract_number(value):
    match = re.search(r"\d+", value)
    return match.group(0) if match else value

def extract_text_after_number(value):
    match = re.search(r"\((.*?)\)", value)  # Extract text inside parentheses
    return match.group(1) if match else value

def get_weapon_data(weapon_url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(weapon_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    weapon_data = {"URL": weapon_url}

    # Extract Weapon Name
    title = soup.find("h1", class_="page-header")
    if title:
        weapon_data["Name"] = title.text.strip()

    # Extract Image (Thumbnail)
    image_tag = soup.select_one(".section.images .infobox-inline li img")
    if image_tag:
        img_src = image_tag["src"]
        weapon_data["Image"] = BASE_URL + img_src if img_src.startswith("/") else img_src

    # Extract All Stats from <table class="stat">
    stats_table = soup.find("table", class_="stat")

    if stats_table:
        for row in stats_table.find_all("tr"):
            th = row.find("th")
            td = row.find("td")
            if th and td:
                key = th.text.strip()
                value = td.text.strip()

                if "Damage" in key and "Critical" not in key:
                    damage_number = extract_number(value)
                    weapon_data["Damage"] = damage_number if damage_number else "Unknown"
                    damage_type = td.find("span", class_="small-bold")
                    weapon_data["Damage Type"] = damage_type.text.strip().strip("()") if damage_type else "Unknown"

                elif "Knockback" in key:
                    knockback = td.find("span", class_="knockback")
                    weapon_data["Knockback"] = knockback.text.strip().strip("()") if knockback else "Unknown"

                elif "Use time" in key:
                    usetime = td.find("span", class_="usetime")
                    weapon_data["Use Time"] = usetime.text.strip().strip("()") if usetime else "Unknown"

                elif "Critical chance" in key:
                    critical_match = re.search(r"\d+%", value)
                    weapon_data["Critical chance"] = critical_match.group(0) if critical_match else "Unknown"

                elif "Consumable" in key:
                    weapon_data["Consumable"] = "Yes" if "\u2714\ufe0f" in value else "No"

                else:
                    weapon_data[key] = value

    # Detect methods of obtainment
    methods = []
    crafting = detect_crafting(soup)
    if crafting:
        methods.append(crafting)

    drop = detect_drop(soup)
    if drop:
        methods.append(drop)

    loot = detect_loot(soup)
    if loot:
        methods.append(loot)

    buy = detect_buy(soup)
    if buy:
        methods.append(buy)

    weapon_data["Method of Obtainment"] = methods if methods else None

    # Detect game stage
    weapon_data["Game Stage"] = detect_game_stage(soup)

    return weapon_data

def main():
    weapons = []
    weapon_links = get_weapon_links()  # Get all weapon links dynamically

    for index, link in enumerate(weapon_links):  # Scrape all weapons
        print(f"Scraping {index+1}/{len(weapon_links)}: {link}")
        weapon_data = get_weapon_data(link)
        weapons.append(weapon_data)

    # Save data to JSON file
    with open("weapons.json", "w", encoding="utf-8") as f:
        json.dump(weapons, f, indent=4)

    print("Scraping completed! Data saved in weapons.json")

if __name__ == "__main__":
    main()
