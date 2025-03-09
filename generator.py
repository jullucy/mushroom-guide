import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS  # Using DuckDuckGo Search
import time
import os
import re

# Create directories
os.makedirs("_mushrooms", exist_ok=True)
os.makedirs("assets", exist_ok=True)
counter = 0
mushroom_links = []

# URL of the mushroom article
URL = "https://www.sidechef.com/de/articles/1605/popular-types-of-mushrooms/"
response = requests.get(URL)
soup = BeautifulSoup(response.text, 'html.parser')

mushrooms = []

# Finding all sections with mushroom data
sections = soup.find_all("div", class_="content-section content-container")
print(sections)

def search_duckduckgo(query):
    """Search DuckDuckGo for additional information and return a short summary."""
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=3))

    if results:
        return "\n".join([f"- [{r['title']}]({r['href']})" for r in results])
    return "No additional information found."

for section in sections:
    counter += 1
    name_tag = section.find("h2", class_="h3 section-title")
    if name_tag is None:
        continue

    name = name_tag.text.strip()
    filename = name.lower().replace(" ", "_") + ".md"

    mushroom_links.append(f"- [{name}](mushrooms/{filename})")
    if (counter != 17):
        continue

    image_tag = section.find("img")
    image_url = image_tag["src"] if image_tag else ""
    image_path = f"assets/{filename.replace('.md', '.jpg')}"

    # Download the image
    if image_url:
        img_data = requests.get(image_url).content
        with open(image_path, "wb") as img_file:
            img_file.write(img_data)

    description = " ".join(p.text.strip() for p in section.find_all("p") if not p.find("h3"))

    match = re.search(r"Also Known As: (.*?\.)", description)
    also_known_as = match.group(1) if match else ""
    description = re.sub(r"Also Known As: .*?\.", "", description).strip()

    recipes = []
    for li in section.find_all("li"):
        recipe_name = li.text.strip()
        recipe_link = li.find("a")["href"] if li.find("a") else ""
        recipes.append(f"- [{recipe_name}]({recipe_link})")

    # Scrape recipe links from paragraphs
    for p in section.find_all("p"):
        a_tag = p.find("a")
        if a_tag:
            recipe_name = a_tag.text.strip()
            recipe_link = a_tag["href"]
            recipes.append(f"- [{recipe_name}]({recipe_link})")

    # Remove recipe names from the description
    for recipe in recipes:
        recipe_name = re.search(r"\[(.*?)\]", recipe).group(1)
        description = re.sub(re.escape(recipe_name), "", description).strip()

    # Fetch additional information using DuckDuckGo
    print(f"Searching for additional data on: {name}")
    additional_info = search_duckduckgo(f"{name} mushroom benefits and uses")
    time.sleep(1)  # Prevent rate-limiting

    mushroom_data = f"""---
layout: mushroom
title: {name}
image: /{image_path}
---

### Scientific Name:
{also_known_as}

### Description:
{description}

## Recipes:
{("\n".join(recipes)) if recipes else "No recipes found."}

## Benefits and uses:
{additional_info}
"""

    with open(f"_mushrooms/{filename}", "w", encoding="utf-8") as f:
        f.write(mushroom_data)

# Create the mushrooms.md file
with open("mushrooms.md", "w", encoding="utf-8") as f:
    f.write("---\nlayout: default\ntitle: List of Mushrooms\n---\n\n")
    f.write("# List of Popular Mushrooms\n\n")
    f.write("\n".join(mushroom_links) + "\n")

print("Markdown files for Jekyll generated successfully!")

# Generate index.md
index_content = f"""---
layout: default
title: Welcome to Mushroom Guide
---

# 🍄 Welcome to the Mushroom Guide

Welcome to my comprehensive guide on mushrooms! Here, you'll find information about different types of mushrooms, their characteristics, and how to use them in recipes.

➡️ **[View the List of Mushrooms](mushrooms.md)**

---
"""

with open("index.md", "w", encoding="utf-8") as f:
    f.write(index_content)

print("Markdown files generated successfully!")
