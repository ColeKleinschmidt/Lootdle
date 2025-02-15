import requests
from bs4 import BeautifulSoup
import json
import time
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Base URL for Stardew Valley Wiki
BASE_URL = "https://stardewvalleywiki.com"

# Load JSON data with cooking items
with open("cooking_items.json", "r", encoding="utf-8") as file:
    cooking_data = json.load(file)

# Function to fetch the correct image URL from the File Page
def fetch_image_url(item_name):
    # Correct format: File:Item_Name.png
    file_page_url = f"{BASE_URL}/File:{item_name.replace(' ', '_')}.png"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(file_page_url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            # Locate the image inside <div id="file">
            file_div = soup.find("div", id="file")
            if file_div:
                image_tag = file_div.find("a")
                if image_tag and "href" in image_tag.attrs:
                    return f"{BASE_URL}{image_tag['href']}"  # Correct full image URL

        print(f"⚠️ No valid image found for {item_name}.")
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Failed to fetch image for {item_name}: {e}")

    return "None"


# Fetch correct image URLs for all items
for item in cooking_data:
    print(f"Fetching image for: {item['Name']}...")
    item["Image URL"] = fetch_image_url(item["Name"])

# Save the updated JSON file
output_file = "cooking_items_with_images.json"
with open(output_file, "w", encoding="utf-8") as json_file:
    json.dump(cooking_data, json_file, indent=4, ensure_ascii=False)

print(f"✅ Updated JSON saved as {output_file}")
