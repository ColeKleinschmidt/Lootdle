import requests
from bs4 import BeautifulSoup
import json
import re

BASE_URL = "https://bindingofisaacrebirth.wiki.gg"
CHEAT_SHEET_URL = "https://tboi.com/repentance"

# Keywords for detecting effects
DESCRIPTION_KEYWORDS = {
    "Flight": ["flight"],
    "Dash": ["dash", "charge"],
    "Invincibility": ["invincibility", "immune"],
    "Speed": ["speed", "faster"],
    "Contact Damage": ["contact damage", "touch damage"],
    "Tears": ["tears", "shoot", "fire rate", "projectile"],
    "Health": ["health", "hearts", "hp"],
    "Shield": ["shield", "holy mantle"],
    "Bombs": ["explosion", "bomb", "detonation", "blast", "explodes", "bombs", "explodes"],
    "Familiar": ["familiar", "summon", "spawns", "dummy", "decoy", "companion"],
    "Lives": ["extra life", "respawn"],
    "Cards": ["tarot", "card", "deck", "mimic"],
    "Items": ["store", "shop", "inventory", "active item", "purchase"],
    "Size": ["size", "growth", "big"],
    "Poison": ["poison", "toxic", "venom"],
    "Throwable": ["throw", "lob", "toss"],
    "Range": ["range", "distance", "longer"],
    "Damage": ["damage", "attack boost", "increased attack"]
}

# Mapping release containers
RELEASE_MAP = {
    "repentanceitems-container": "Repentance",
    "afterbirthplusitems-container": "Afterbirth+",
    "afterbirthitems-container": "Afterbirth",
    "items-container rebirth": "Rebirth"
}

# The 9 test items
TEST_ITEMS = [
    "A Pony", "Anarchist Cookbook", "Best Friend",
    "Blank Card", "Blood Rights", "Bob's Rotten Head",
    "Schoolbag", "Restock", "Mega Mush"
]

def fetch_release_versions():
    """ Scrapes the official TBOI cheat sheet for release versions. """
    response = requests.get(CHEAT_SHEET_URL)
    soup = BeautifulSoup(response.text, "html.parser")

    release_versions = {}

    for div_class, release_name in RELEASE_MAP.items():
        container = soup.find("div", class_=div_class)
        if container:
            items = container.find_all("p", class_="item-title")
            for item in items:
                item_name = item.text.strip()
                release_versions[item_name.lower()] = release_name

    return release_versions

def get_test_item_links():
    """Fetches direct links for the 9 test items."""
    return [f"{BASE_URL}/wiki/{item.replace(' ', '_')}" for item in TEST_ITEMS]

def extract_effects_description(soup):
    """ Extracts the Effects section and generates a meaningful description using keywords. """
    effects_section = soup.find("h2", string="Effects")
    effects_text = ""

    if effects_section:
        effects_parts = []
        for sibling in effects_section.find_next_siblings():
            if sibling.name == "h2":
                break
            if sibling.name in ["p", "ul"]:
                effects_parts.append(sibling.text.strip())

        effects_text = " ".join(effects_parts) if effects_parts else ""

    if not effects_text:
        first_paragraph = soup.select_one("#mw-content-text p")
        effects_text = first_paragraph.text.strip() if first_paragraph else ""

    # Parse keywords into a description
    description = set()
    lower_text = effects_text.lower()

    for keyword, variations in DESCRIPTION_KEYWORDS.items():
        if any(re.search(rf"\b{variation}\b", lower_text) for variation in variations):
            description.add(keyword)

    return sorted(description) if description else ["No effects listed"]

def scrape_item(url, release_versions):
    """Scrapes individual item pages and extracts details."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        item_data = {}

        # Extract Name
        item_name = soup.find("h1").text.strip()
        normalized_name = item_name.lower()
        item_data["Name"] = item_name

        # Extract Image URL
        image_tag = soup.select_one("aside div:nth-child(2) img")
        if image_tag and "src" in image_tag.attrs and "Collectible_" in image_tag["src"]:
            image_url = image_tag["src"]
        else:
            image_tag = soup.select_one("aside img")
            image_url = image_tag["src"] if image_tag and "Collectible_" in image_tag["src"] else "N/A"

        if image_url != "N/A" and not image_url.startswith("http"):
            image_url = BASE_URL + image_url

        item_data["Image URL"] = image_url

        # Determine if Active
        charge_section = soup.find("h3", string="Recharge Time")
        item_data["Active"] = "Yes" if charge_section else "No"

        # Extract Pickup Quote
        quote_tag = soup.find("h3", string="Pickup Quote")
        item_data["Quote"] = quote_tag.find_next("div").text.strip().strip('"') if quote_tag else "N/A"

        # Extract Charge Time
        if charge_section:
            charge_text = charge_section.find_next("div").text.strip()
            charge_times = re.findall(r"\d+\s*rooms?", charge_text)
            item_data["Charge"] = charge_times[-1].replace("  ", " ") if charge_times else "N/A"
        else:
            item_data["Charge"] = "N/A"

        # Extract Quality (clean up any extra text)
        quality_tag = soup.find("h3", string="Quality")
        if quality_tag:
            raw_quality = quality_tag.find_next("div").text.strip()
            quality_number = re.search(r"\d+", raw_quality)
            item_data["Quality"] = quality_number.group(0) if quality_number else "N/A"
        else:
            item_data["Quality"] = "N/A"

        # Extract Item Pool (fix "None" detection)
        pool_tag = soup.find("h3", string="Item Pool")
        if pool_tag:
            pool_list = pool_tag.find_next("ul")
            pool_values = [li.text.strip() for li in pool_list.find_all("li")] if pool_list else []
            pool_text = pool_tag.find_next("div").text.strip() if not pool_list else ""
            pool_values.extend(re.split(r",|\n|\s{2,}", pool_text))
            pool_values = [p.strip() for p in pool_values if p.strip() and "DLC" not in p]

            if not pool_values or any(x.isdigit() for x in pool_values[0]) or len(pool_values[0]) < 3:
                item_data["Item Pool"] = ["None"]
            else:
                item_data["Item Pool"] = list(dict.fromkeys(pool_values))
        else:
            item_data["Item Pool"] = ["None"]

        # Extract Unlock Condition
        unlock_tag = soup.find("h3", string="Unlock Method")
        item_data["Unlock"] = "Default" if not unlock_tag else unlock_tag.find_next("div").text.strip()

        # Extract Effects-based description (fixed!)
        item_data["Description"] = extract_effects_description(soup)

        # Assign Release Version
        assigned_release = release_versions.get(normalized_name, "Original")
        item_data["Released"] = assigned_release

        # Print debug info only for test items
        if item_name in TEST_ITEMS:
            print(f"\nScraping: {url}")
            print(f"Item: {item_name} -> Normalized: {normalized_name}")
            print(f"Assigned Release: {assigned_release}")
            print(f"Detected Description: {item_data['Description']}")

        return item_data

    except Exception as e:
        print(f"Error scraping {url}: {e}")

    return None

if __name__ == "__main__":
    release_versions = fetch_release_versions()
    print(f"Loaded {len(release_versions)} items with release versions.")

    item_links = get_test_item_links()
    all_items = []

    for link in item_links:
        item_data = scrape_item(link, release_versions)
        if item_data:
            all_items.append(item_data)

    with open("binding_of_isaac_items.json", "w", encoding="utf-8") as f:
        json.dump(all_items, f, indent=4)

    print("\nScraping complete. Data saved to binding_of_isaac_items.json")
