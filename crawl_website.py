import asyncio
import json
import os
import xml.etree.ElementTree as ET
import requests

from crawl4ai import AsyncWebCrawler

# -------------------------------
# CONFIG
# -------------------------------

SITEMAP_URL = "https://magicmoneybox.in/sitemap_products_1.xml?from=8445965861001&to=8719706849417"

OUTPUT_FOLDER = "knowledge"
OUTPUT_FILE = os.path.join(OUTPUT_FOLDER, "knowledge.json")


# -------------------------------
# Read Product URLs from Sitemap
# -------------------------------

def get_product_urls():

    print("Downloading sitemap...")

    response = requests.get(SITEMAP_URL)
    response.raise_for_status()

    root = ET.fromstring(response.text)

    namespace = {
        "ns": "http://www.sitemaps.org/schemas/sitemap/0.9"
    }

    urls = []

    for url in root.findall("ns:url", namespace):

        loc = url.find("ns:loc", namespace)

        if loc is not None:
            urls.append(loc.text)

    print(f"Found {len(urls)} product pages.")

    return urls


# -------------------------------
# Crawl Website
# -------------------------------

async def crawl():

    urls = get_product_urls()

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    knowledge = []

    async with AsyncWebCrawler(verbose=True) as crawler:

        for i, url in enumerate(urls, start=1):

            print(f"[{i}/{len(urls)}] Crawling {url}")

            try:

                result = await crawler.arun(url=url)

                page = {
                    "url": url,
                    "title": result.metadata.get("title", ""),
                    "content": result.markdown
                }

                knowledge.append(page)

            except Exception as e:

                print(f"Failed: {url}")
                print(e)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:

        json.dump(
            knowledge,
            f,
            indent=4,
            ensure_ascii=False
        )

    print()
    print("=" * 50)
    print("Knowledge Base Generated Successfully!")
    print(f"Saved to: {OUTPUT_FILE}")
    print(f"Total Pages: {len(knowledge)}")
    print("=" * 50)


# -------------------------------
# Run
# -------------------------------

if __name__ == "__main__":
    asyncio.run(crawl())