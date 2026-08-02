import json
import re
from pathlib import Path

# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = BASE_DIR / "knowledge" / "knowledge.json"
OUTPUT_FILE = BASE_DIR / "knowledge" / "cleaned_knowledge.json"

# ---------------------------------------------------------
# Lines containing these words will be removed
# ---------------------------------------------------------

REMOVE_PATTERNS = [

    # Navigation
    "Skip to content",
    "Shopping cart",
    "View Cart",
    "Check out",
    "Checkout",
    "Continue shopping",
    "Menu",
    "Home",
    "Catalog",
    "Collections",
    "Categories",
    "Search",
    "Track Order",
    "Track your order",

    # Account
    "Login",
    "Log in",
    "Register",
    "Sign In",
    "Sign Up",
    "Forgot your password",
    "Wishlist",

    # Policies
    "Privacy Policy",
    "Refund Policy",
    "Shipping Policy",
    "Terms of Service",

    # Store info
    "Newsletter",
    "Follow us",
    "Language",
    "English",
    "తెలుగు",

    # Shopping
    "Add to Cart",
    "Buy Now",
    "Regular price",
    "Sale price",
    "Unit price",
    "Sold Out",
    "reviews",
    "review",
    "off",

    # Generic marketing
    "Free Shipping",
    "Best Quality",
    "Verified & Certified",

]

# ---------------------------------------------------------
# Regex patterns
# ---------------------------------------------------------

IMAGE_PATTERN = re.compile(r'!\[.*?\]\(.*?\)')
LINK_PATTERN = re.compile(r'\[(.*?)\]\(.*?\)')
HTML_PATTERN = re.compile(r'<[^>]+>')
URL_PATTERN = re.compile(r'https?://\S+')

# ---------------------------------------------------------
# Cleaning function
# ---------------------------------------------------------

def clean_content(text):

    # Remove HTML
    text = HTML_PATTERN.sub("", text)

    # Remove markdown images
    text = IMAGE_PATTERN.sub("", text)

    # Keep markdown link text only
    text = LINK_PATTERN.sub(r"\1", text)

    # Remove raw URLs
    text = URL_PATTERN.sub("", text)

    # Split into lines
    lines = text.splitlines()

    cleaned = []
    seen = set()

    for line in lines:

        line = line.strip()

        if not line:
            continue

        # Remove unwanted lines
        if any(pattern.lower() in line.lower() for pattern in REMOVE_PATTERNS):
            continue

        # Remove duplicate consecutive lines
        if line in seen:
            continue

        seen.add(line)
        cleaned.append(line)

    text = "\n".join(cleaned)

    # Collapse excessive blank spaces
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' +', ' ', text)

    return text.strip()

# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    print("Loading knowledge base...")

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        knowledge = json.load(f)

    cleaned = []

    for item in knowledge:

        cleaned.append({

            "url": item["url"],

            "title": item["title"],

            "content": clean_content(item["content"])

        })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, indent=4, ensure_ascii=False)

    print("-------------------------------------")
    print(f"Original Entries : {len(knowledge)}")
    print(f"Cleaned Entries  : {len(cleaned)}")
    print(f"Saved to         : {OUTPUT_FILE}")
    print("-------------------------------------")

if __name__ == "__main__":
    main()