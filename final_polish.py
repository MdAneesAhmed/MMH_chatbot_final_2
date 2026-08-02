
import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = BASE_DIR / "knowledge" / "cleaned_knowledge_v2.json"
OUTPUT_FILE = BASE_DIR / "knowledge" / "knowledge_final.json"

REMOVE_EXACT = {
    "Description",
    "Shipping Information",
    "Back",
    "Next",
    "Rating",
    "Picture/Video (optional)",
    "Display name",
    "Email address",
    "Anonymous",
}

REVIEW_START = [
    "100%",
    "5.00 out of 5",
    "Sort by",
    "Most Recent",
    "Highest Rating",
    "Lowest Rating",
]

BAD_HEADER = [
    "Your cart is empty",
    "Have an account?",
    "Loading...",
    "Country India",
    "Welcome To Millionaire Mindhub",
    "Skip to product information",
]

DATE = re.compile(r"\d{2}/\d{2}/\d{4}")

def normalize(text):
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def clean_content(text):
    lines = text.splitlines()
    cleaned = []
    stop_reviews = False

    for line in lines:
        s = line.strip()
        if not s:
            if cleaned and cleaned[-1] != "":
                cleaned.append("")
            continue

        if any(x in s for x in BAD_HEADER):
            continue

        if s in REMOVE_EXACT:
            continue

        if any(s.startswith(x) for x in REVIEW_START):
            stop_reviews = True

        if DATE.fullmatch(s):
            stop_reviews = True

        if stop_reviews:
            continue

        if re.fullmatch(r"\(\d+\)", s):
            continue

        if re.fullmatch(r"\d+%", s):
            continue

        if re.fullmatch(r"[A-Z]", s):
            continue

        if "received exactly what i ordered" in s.lower():
            continue

        if "good things started" in s.lower():
            continue

        cleaned.append(s)

    result = normalize("\n".join(cleaned))

    # If extraction failed and Shopify header leaked through,
    # return empty content instead of noisy page.
    if ("Your cart is empty" in result or
        "Welcome To Millionaire Mindhub" in result):
        return ""

    return result

def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    for item in data:
        item["content"] = clean_content(item.get("content", ""))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(data)} records to:")
    print(OUTPUT_FILE)

if __name__ == "__main__":
    main()
