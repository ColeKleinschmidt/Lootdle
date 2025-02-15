import requests
from bs4 import BeautifulSoup
import json

# URL of the Stardew Valley Wiki Fish page
url = "https://stardewvalleywiki.com/Fish"

# Fetch the page content
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# Locate all fish tables
tables = soup.find_all("table", class_="wikitable sortable roundedborder")

if not tables:
    print("No fish tables found.")
    exit()

fish_data = []

# Function to clean and properly split text
def clean_list(text):
    return [item.strip() for item in text.replace("\n", "|").replace("+", "|").split("|") if item.strip()]

# Process each table
for table in tables:
    tbody = table.find("tbody")
    rows = tbody.find_all("tr")[1:]  # Skip header row

    # Process rows
    for row in rows:
        columns = row.find_all("td")

        # Skip rows with unexpected column counts
        if len(columns) < 38:
            continue

        # Extract Image URL
        image_tag = columns[0].find("img")
        image_url = f"https://stardewvalleywiki.com{image_tag['src']}" if image_tag else None

        # Extract Name
        name_tag = columns[1].find("a")
        name = name_tag.text.strip() if name_tag else None

        # Extract Description
        description = columns[2].text.strip()

        # Extract Base Sell Price (Inside <table class="no-wrap">)
        base_sell_price = ""
        price_column = columns[3]

        price_table = price_column.find("table", class_="no-wrap")
        if price_table:
            rows_in_price_table = price_table.find_all("tr")
            if rows_in_price_table:
                first_price_td = rows_in_price_table[0].find_all("td")
                if len(first_price_td) > 1:  # The price is in the second <td>
                    base_sell_price = first_price_td[1].get_text(strip=True).replace("g", "")

        # Extracting Correct Fields
        location = clean_list(columns[30].text.replace("(", "").replace(")", "")) if len(columns) > 30 else []
        time = clean_list(columns[31].text) if len(columns) > 31 else []
        season = clean_list(columns[32].text.replace("(", "").replace(")", "")) if len(columns) > 32 else []
        weather = clean_list(columns[33].text) if len(columns) > 33 else []
        size = f"{columns[34].text.strip()} in" if len(columns) > 34 and columns[34].text.strip() else ""

        # Ensuring correct spacing for size
        size = size.replace("in", " in")

        # Extract Used In (Splitting into multiple values)
        used_in_raw = columns[37].text.strip() if len(columns) > 37 else ""
        used_in = clean_list(used_in_raw.replace(" ", " "))  # Fixes spacing issues

        # Ensuring proper time formatting
        if len(time) > 1:
            time = [" | ".join(time)]  # Formats time as "X | Y"

        # Save fish data
        fish = {
            "Image URL": image_url,
            "Name": name,
            "Description": description,
            "Base Sell Price": base_sell_price,
            "Location": location,
            "Time": time,
            "Season": season,
            "Weather": weather,
            "Size": size,
            "Used In": used_in
        }

        fish_data.append(fish)

# Save to JSON
output_file = "stardew_fish.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(fish_data, f, indent=4, ensure_ascii=False)

print(f"\nScraped {len(fish_data)} fish and saved to {output_file}")
