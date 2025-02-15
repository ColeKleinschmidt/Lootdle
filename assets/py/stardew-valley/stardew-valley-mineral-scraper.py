import requests
from bs4 import BeautifulSoup
import json
import math

# URL of the Stardew Valley Wiki Minerals page
url = "https://stardewvalleywiki.com/Minerals"

# Fetch the page content
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# Locate all mineral tables
tables = soup.find_all("table", class_="wikitable sortable roundedborder")

if not tables:
    print("No mineral tables found.")
    exit()

minerals_data = []

# Process each table
for table in tables:
    tbody = table.find("tbody")
    rows = tbody.find_all("tr")[1:]  # Skip header row

    for row in rows:
        columns = row.find_all("td")
        if len(columns) < 7:  # Ensure there are enough columns
            continue

        # Extract Image URL
        image_tag = columns[0].find("img")
        image_url = f"https://stardewvalleywiki.com{image_tag['src']}" if image_tag else None

        # Extract Name
        name_tag = columns[1].find("a")
        name = name_tag.text.strip() if name_tag else None

        # Extract Description
        description = columns[2].text.strip()

        # Extract Base Sell Price
        base_sell_price = columns[3].get("data-sort-value", "").strip()
        if not base_sell_price.isdigit():
            base_sell_price = columns[3].text.strip()

        # Convert Base Sell Price to integer (if valid), else set to None
        base_sell_price = int(base_sell_price) if base_sell_price.isdigit() else None

        # Calculate Gemologist Sell Price (Base * 1.3, rounded)
        gemologist_sell_price = math.ceil(base_sell_price * 1.3) if base_sell_price else None

        # Extract Loved By
        loved_by = []

        # Extract Hated By
        hated_by = []

        # Extract Sources
        sources = [a.text.strip() for a in columns[5].find_all("a")] if columns[5].find("a") else []

        # Extract Used In
        used_in = [a.text.strip() for a in columns[6].find_all("a")] if columns[6].find("a") else []

        # Museum Donation (defaulting to "No" for now)
        museum_donation = "No"

        mineral = {
            "Image URL": image_url,
            "Name": name,
            "Description": description,
            "Base Sell Price": base_sell_price,
            "Gemologist Sell Price": gemologist_sell_price,
            "Sources": sources,
            "Used In": used_in,
            "Loved By": loved_by,
            "Hated By": hated_by,
            "Museum Donation": museum_donation
        }

        minerals_data.append(mineral)

# Save to JSON
output_file = "stardew_minerals.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(minerals_data, f, indent=4, ensure_ascii=False)

print(f"Scraped {len(minerals_data)} minerals and saved to {output_file}")
