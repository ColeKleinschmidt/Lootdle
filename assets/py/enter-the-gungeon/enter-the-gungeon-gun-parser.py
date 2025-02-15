import requests
from bs4 import BeautifulSoup
import json
import re

BASE_URL = "https://enterthegungeon.fandom.com"
GUNS_URL = "https://enterthegungeon.fandom.com/wiki/Guns"
OUTPUT_FILE = "gungeon_guns.json"

def clean_value(value):
    """Removes text inside parentheses and extra numbers."""
    cleaned = re.sub(r"\(.*?\)", "", value).strip()  # Remove anything in parentheses
    cleaned = re.findall(r"[\d.]+", cleaned)  # Extract only numbers
    return cleaned[0] if cleaned else "N/A"  # Keep only the first valid number

def get_gun_links():
    response = requests.get(GUNS_URL)
    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table", class_="sortable mw-collapsible wikitable")

    if not table:
        print("Error: Could not find the correct table.")
        return {}

    gun_links = {}

    for row in table.select("tr")[1:]:  # **Removes the 10-gun limit**
        cols = row.select("td")
        if cols:
            link_tag = cols[1].select_one("a")  # Name column (2nd column)
            if link_tag and 'href' in link_tag.attrs:
                gun_name = link_tag.text.strip()
                gun_url = BASE_URL + link_tag['href']
                gun_links[gun_name] = gun_url

    print(f"Found {len(gun_links)} guns.")
    return gun_links

def scrape_gun_page(gun_name, gun_url):
    response = requests.get(gun_url)
    soup = BeautifulSoup(response.text, "html.parser")

    infobox = soup.find("table", class_="infoboxtable")

    if not infobox:
        print(f"Error: No infobox found for {gun_name}")
        return None

    data = {"Name": gun_name, "URL": gun_url}

    img_tag = infobox.select_one("img")
    if img_tag and 'data-src' in img_tag.attrs:
        img_url = img_tag['data-src']
        data["Image URL"] = "https:" + img_url if not img_url.startswith("https:") else img_url

    quote_tag = infobox.select_one(".ammonomicon-quote")
    data["Quote"] = quote_tag.text.strip() if quote_tag else "N/A"

    rows = infobox.select("tr")
    for row in rows:
        bold_tag = row.find("b")  # Find <b> tags that contain the stat name
        if not bold_tag:
            continue

        key = bold_tag.text.strip().replace(":", "")  # Clean stat name
        value_tag = row.find_all("td")[-1]  # The last <td> is the value
        val = value_tag.text.strip() if value_tag else "N/A"

        # Extract Quality from Image ALT Attribute
        if key == "Quality":
            img_tag = value_tag.find("img")  # Locate the quality image
            if img_tag and "alt" in img_tag.attrs:
                alt_text = img_tag["alt"]
                if "N Quality Item" in alt_text:
                    val = "None"
                else:
                    val = alt_text[0]  # Extract first letter (e.g., "B" from "B Quality Item")
            else:
                val = "None"

            data["Quality"] = val  # Ensure value is assigned to data

        # Extract Type correctly
        if key == "Type":
            data["Type"] = val  # Ensure it is correctly stored

        # Clean up values by removing parentheses and keeping only the first number
        val = clean_value(val)

        if key in ["Magazine Size", "Max Ammo", "Damage", "Fire Rate", "Reload Time", "DPS"]:
            if key == "Max Ammo":
                if "∞" in val or value_tag.find("img"):
                    val = "Infinite"  # Replace infinity symbol or image with "Infinite"
            data[key] = val

        if "Sell Creep Price" in key:  # Handle sell price separately
            if val:
                data["Sell Price"] = val.split()[0]  # Remove currency icon
            else:
                data["Sell Price"] = "N/A"

    fields = ["Quote", "Type", "Quality", "Magazine Size", "Max Ammo", "Damage", "Fire Rate", "Reload Time", "Sell Price", "DPS"]
    for field in fields:
        if field not in data:
            data[field] = "N/A"

    return data

def main():
    guns = []
    gun_links = get_gun_links()

    if not gun_links:
        print("No guns found. Exiting...")
        return

    for index, (gun_name, gun_url) in enumerate(gun_links.items()):
        print(f"Scraping {index + 1}/{len(gun_links)}: {gun_name}")
        gun_data = scrape_gun_page(gun_name, gun_url)
        if gun_data:
            guns.append(gun_data)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(guns, f, indent=4, ensure_ascii=False)

    print(f"Scraping complete! Data saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
