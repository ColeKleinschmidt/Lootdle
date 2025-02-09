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

def get_version_added(soup):
    version = None
    history_section = soup.find("h2", id="History")
    if history_section:
        # Locate the correct version tag
        history_div = history_section.find_next("div", class_="history-header", id="history_desktop")
        if history_div:
            version_tag = history_div.find_next("ul").find("li", id=re.compile(r"history_Desktop_\d"))
            if version_tag:
                version = version_tag["id"].replace("history_Desktop_", "")

    return version if version else "Unknown"

def get_method_of_obtainment(soup):
    obtain_methods = set()

    # Crafting detection
    crafting_section = soup.find("h3", id="Recipes")
    crafting_table = soup.find("table", class_="terraria cellborder recipes sortable jquery-tablesorter")
    if crafting_section and crafting_table:
        obtain_methods.add("Crafting")

    # Buy detection
    buy_section = soup.find("table", class_="stat")
    if buy_section and buy_section.find("th", string=lambda s: s and "Buy" in s):
        obtain_methods.add("Buy")

    # Loot detection (Check for % and 'chest' in paragraphs)
    parser_output = soup.find("div", class_="mw-parser-output")
    if parser_output:
        for p in parser_output.find_all("p"):
            if re.search(r"\d{1,2}\.\d{1,2}%", p.text) and "chest" in p.text.lower():
                obtain_methods.add("Loot")

    # Enemy Drop detection
    enemy_drop_section = soup.find("div", class_="drop infobox modesbox c-normal mw-collapsible mw-made-collapsible")
    if enemy_drop_section and enemy_drop_section.find("div", class_="title", string=lambda s: s and "Obtained From" in s):
        obtain_methods.add("Enemy Drop")

    return list(obtain_methods) if obtain_methods else ["Unknown"]

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

    # Extract Stats from <table class="stat">
    stats_table = soup.find("table", class_="stat")
    if stats_table:
        for row in stats_table.find_all("tr"):
            th = row.find("th")
            td = row.find("td")
            if th and td:
                key = th.text.strip()
                value = td.text.strip()
                weapon_data[key] = value  # Store all stats dynamically

    # Extract Version Added
    weapon_data["Version Added"] = get_version_added(soup)

    # Extract Method of Obtainment
    weapon_data["Method of Obtainment"] = get_method_of_obtainment(soup)

    return weapon_data

def main():
    weapons = []
    weapon_links = get_weapon_links()

    for index, link in enumerate(weapon_links[:20]):  # Scrapes all weapons
        print(f"Scraping {index+1}/{len(weapon_links)}: {link}")
        weapon_data = get_weapon_data(link)
        weapons.append(weapon_data)

    # Save data to JSON file
    with open("weapons.json", "w", encoding="utf-8") as f:
        json.dump(weapons, f, indent=4)

    print("Scraping completed! Data saved in weapons.json")

if __name__ == "__main__":
    main()
