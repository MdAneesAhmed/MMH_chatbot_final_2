import json
from pathlib import Path
from difflib import SequenceMatcher

BASE_DIR = Path(__file__).resolve().parent.parent
KB_PATH = BASE_DIR / "knowledge" / "knowledge.json"

with open(KB_PATH, "r", encoding="utf-8") as f:
    KNOWLEDGE = json.load(f)


def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def search_knowledge(query, top_k=5):

    results = []

    for item in KNOWLEDGE:

        score = similarity(query, item["title"])

        if item.get("content"):
            score = max(
                score,
                similarity(query, item["content"][:1000])
            )

        results.append((score, item))

    results.sort(key=lambda x: x[0], reverse=True)

    return [x[1] for x in results[:top_k]]