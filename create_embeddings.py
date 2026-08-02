import json
import os
import numpy as np
from sentence_transformers import SentenceTransformer

# -------------------------------------------------
# Paths
# -------------------------------------------------

BASE_DIR = os.path.dirname(__file__)

KB_PATH = os.path.join(
    BASE_DIR,
    "knowledge",
    "knowledge_final.json"
)

EMBEDDINGS_PATH = os.path.join(
    BASE_DIR,
    "knowledge",
    "embeddings.npy"
)

# -------------------------------------------------
# Load Knowledge Base
# -------------------------------------------------

print("Loading knowledge base...")

with open(KB_PATH, "r", encoding="utf-8") as f:
    knowledge = json.load(f)

# -------------------------------------------------
# Prepare Documents
# -------------------------------------------------

documents = []

for item in knowledge:

    title = item.get("title", "").strip()
    url = item.get("url", "").strip()
    content = item.get("content", "").strip()

    text = f"""
PRODUCT NAME:
{title}

PRODUCT URL:
{url}

PRODUCT DETAILS:
{content}
"""

    documents.append(text.strip())

print(f"Loaded {len(documents)} documents.")

# -------------------------------------------------
# Load Embedding Model
# -------------------------------------------------

print("Loading embedding model...")

model = SentenceTransformer("all-MiniLM-L6-v2")

# -------------------------------------------------
# Generate Embeddings
# -------------------------------------------------

print("Generating embeddings...")

embeddings = model.encode(
    documents,
    convert_to_numpy=True,
    show_progress_bar=True
)

# -------------------------------------------------
# Save Embeddings
# -------------------------------------------------

np.save(EMBEDDINGS_PATH, embeddings)

print("\nEmbeddings saved successfully!")

print(f"\nSaved to:\n{EMBEDDINGS_PATH}")

print(f"\nEmbedding Shape: {embeddings.shape}")