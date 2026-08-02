import json
import re

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
KNOWLEDGE_DIR = BASE_DIR / "knowledge"

INPUT_FILE = KNOWLEDGE_DIR / "knowledge.json"
OUTPUT_FILE = KNOWLEDGE_DIR / "knowledge_refined.json"

# Sections that usually indicate the start of footer/UI content
STOP_SECTIONS = [
    "Customer Reviews",
    "Related Products",
    "Recently Viewed",
    "You may also like",
    "Share",
    "Sign In",
    "Login",
    "Register",
    "Wishlist",
    "Shopping Cart",
    "Your cart",
    "Categories",
    "Language",
    "Search",
    "Footer",
    "Quick Links",
    "Policies",
    "Follow us",
    "Powered by Shopify",
    "Contact Us",
]

# Lines that are just UI noise
REMOVE_LINES = {
    "",
    "Menu",
    "Home",
    "Cart",
    "Wishlist",
    "Search",
    "Login",
    "Register",
    "Sign In",
    "Buy Now",
    "Add to cart",
    "Continue Shopping",
    "Skip to content",
}


def clean_content(text: str) -> str:
    if not text:
        return ""

    # Remove markdown images
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)

    # Remove markdown links but keep visible text
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)

    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    lines = text.splitlines()

    cleaned = []

    for line in lines:

        line = line.strip()

        if not line:
            continue

        # Remove obvious UI lines
        if line in REMOVE_LINES:
            continue

        # Stop once footer/reviews/navigation starts
        stop = False
        for keyword in STOP_SECTIONS:
            if keyword.lower() in line.lower():
                stop = True
                break

        if stop:
            break

        # Remove URLs
        if line.startswith("http"):
            continue

        # Remove markdown separators
        if line.startswith("---"):
            continue

        cleaned.append(line)

    text = "\n".join(cleaned)

    # Collapse multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Remove repeated spaces
    text = re.sub(r"[ \t]+", " ", text)

    return text.strip()


def detect_type(url):
    if "/products/" in url:
        return "product"
    if "/pages/" in url:
        return "page"
    if "/collections/" in url:
        return "collection"
    if "/blogs/" in url:
        return "blog"
    return "other"


with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

refined = []

for item in data:

    title = item.get("title", "").replace("– Magic Money Box", "").strip()

    refined.append({
        "title": title,
        "type": detect_type(item.get("url", "")),
        "url": item.get("url", ""),
        "content": clean_content(item.get("content", ""))
    })

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(refined, f, indent=2, ensure_ascii=False)

print("=" * 50)
print("Knowledge Base Refined Successfully")
print(f"Saved to: {OUTPUT_FILE}")
print(f"Processed: {len(refined)} pages")
print("=" * 50)
