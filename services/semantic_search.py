import json
import os
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# -------------------------------------------------
# Load Knowledge Base
# -------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
KB_PATH = os.path.join(BASE_DIR, "knowledge", "knowledge_final.json")
EMBEDDINGS_PATH = os.path.join(BASE_DIR, "knowledge", "embeddings.npy")

with open(KB_PATH, "r", encoding="utf-8") as f:
    knowledge = json.load(f)

# -------------------------------------------------
# Load Embedding Model
# -------------------------------------------------

model = SentenceTransformer("all-MiniLM-L6-v2")

# -------------------------------------------------
# Create Documents
# -------------------------------------------------

documents = []

for item in knowledge:

    title = item.get("title", "").strip()
    url = item.get("url", "").strip()
    content = item.get("content", "").strip()

    text = f"""
Product Name:
{title}

Product URL:
{url}

Product Information:
{content}
"""

    documents.append(text.strip())

# Create embeddings once during startup
embeddings = np.load(EMBEDDINGS_PATH)

# -------------------------------------------------
# Semantic Search
# -------------------------------------------------

def semantic_search(query, top_k=5):

    # Embed user query
    query_embedding = model.encode([query], convert_to_numpy=True)

    # Compute similarity
    scores = cosine_similarity(query_embedding, embeddings)[0]
    SIMILARITY_THRESHOLD = 0.15

    # Highest similarity score
    max_score = float(np.max(scores))

    # Best matching documents
    top_indices = np.argsort(scores)[::-1][:top_k]

    context = ""
    retrieved_documents = []
    retrieved_scores = []

    for idx in top_indices:

        if scores[idx] < SIMILARITY_THRESHOLD:
            continue
        retrieved_scores.append(float(scores[idx]))

        item = knowledge[idx]
        print("\n" + "=" * 60)
        print(f"Rank: {len(retrieved_documents)+1}")
        print(f"Title : {item.get('title', '')}")
        print(f"Score : {round(float(scores[idx]),4)}")
        print("=" * 60)

        context += f"""
    ----------------------------------------

    PRODUCT NAME:
    {item.get("title", "")}

    PRODUCT URL:
    {item.get("url", "")}

    PRODUCT DETAILS:
    {item.get("content", "")}

    ----------------------------------------
    """

        retrieved_documents.append(
            {
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "type": item.get("type", ""),
                "content": item.get("content", ""),
                "score": round(float(scores[idx]), 4)
            }
        )
    average_score = (
    sum(retrieved_scores) / len(retrieved_scores)
    if retrieved_scores else 0.0
    )

    return {
    "context": context.strip(),
    "max_score": round(max_score, 4),
    "average_score": round(average_score, 4),
    "documents": retrieved_documents
    }