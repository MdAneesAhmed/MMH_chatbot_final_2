import os
from openai import OpenAI
from dotenv import load_dotenv
import json

from services.knowledge_loader import get_context
from services.intent_analyzer import analyze_intent

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

MODEL = os.getenv("GROQ_MODEL")
print("MODEL:", MODEL)
print("API KEY FOUND:", bool(os.getenv("GROQ_API_KEY")))

# Minimum similarity score
SIMILARITY_THRESHOLD = 0.15
import re

def clean_product_title(title):
    if not title:
        return ""

    title = re.sub(r"\s*[-–|]\s*Magic Money Box.*$", "", title)

    title = re.sub(
        r"\s*[-–|]\s*(Confidence|Action|Abundance|Prosperity|Healing|Protection|Positive Energy|Emotional Balance).*",
        "",
        title,
        flags=re.IGNORECASE,
    )

    title = re.sub(r"\s+", " ", title)

    return title.strip()


def generate_response(user_message):

    # ----------------------------
    # Analyze User Intent
    # ----------------------------
    try:
        intent_data = analyze_intent(user_message)
        print("\n")
        print("=" * 60)
        print("INTENT ANALYZER OUTPUT")
        print("=" * 60)
        
        print(json.dumps(intent_data, indent=4))
        
        print("=" * 60)
        print("\n")
    except Exception as e:
        print("Intent Analyzer Error:", e)
        intent_data = {
            "intent": "Support",
            "emotion": "neutral",
            "needs": [],
            "search_query": user_message,
            "domain_related": True
        }
    # if intent_data["intent"] == "OutOfScope":
    #     return {
    #         "reply": (
    #             "I'm the Magic Money Box AI Assistant. "
    #             "I can help you with our crystal products, recommendations, "
    #             "orders, and related services. "
    #             "Please ask me something related to Magic Money Box."
    #         ),
    #         "products": []
    #     }

    # ----------------------------
    # Reject unrelated questions
    # ----------------------------
    # ----------------------------
# Redirectable Out-of-Domain Queries
# ----------------------------

    REDIRECTABLE_KEYWORDS = {
        "love",
        "relationship",
        "girlfriend",
        "boyfriend",
        "marriage",
        "stress",
        "anxiety",
        "confidence",
        "focus",
        "career",
        "success",
        "money",
        "wealth",
        "prosperity",
        "motivation",
        "peace",
        "calm",
        "fear",
        "negative energy",
        "positivity",
        "self love",
        "emotional balance"
    }
    
    message_lower = user_message.lower()
    
    redirectable = any(
        keyword in message_lower
        for keyword in REDIRECTABLE_KEYWORDS
    )

    if intent_data["intent"] == "OutOfScope":

        if not redirectable:

            return {
                "reply": (
                    "I'm the Magic Money Box AI Assistant. "
                    "I can help you with our crystal products, "
                    "recommendations, orders, and related services. "
                    "Please ask me something related to Magic Money Box."
                ),
                "products": []
            }

        # Continue to semantic search
        intent_data = {
            "intent": "Advice",
            "emotion": "neutral",
            "needs": [],
            "search_query": user_message,
            "domain_related": True
        }


    # ----------------------------
    # Retrieve Knowledge
    # ----------------------------
    search_query = intent_data.get("search_query", user_message)

    result = get_context(search_query)

    print("===== RESULT =====")

    print(type(result))
    print(result.keys())
    print("Context length:", len(result["context"]))
    print("Documents:", len(result["documents"]))
    print("Max Score:", result["max_score"])
    print("Average Score:", result["average_score"])
    print("Reached here successfully")

    knowledge = result["context"]
    max_score = result["max_score"]
    average_score = result["average_score"]
    documents = result.get("documents", [])

    print(f"Intent : {intent_data.get('intent')}")
    print(f"Emotion: {intent_data.get('emotion')}")
    print(f"Needs  : {intent_data.get('needs')}")
    print(f"Max Similarity Score     : {max_score:.3f}")
    print(f"Average Similarity Score : {average_score:.3f}")
    # ----------------------------
    # Handle Low Similarity
    # ----------------------------
    if max_score < SIMILARITY_THRESHOLD:
        knowledge = (
            "No highly relevant product information was found. "
            "If the user's question is about Magic Money Box, politely explain "
            "that the exact information is unavailable. "
            "Do not invent facts."
        )

    # ----------------------------
    # Build Prompt
    # ----------------------------
    system_prompt = f"""
You are Maya, the official AI assistant for Magic Money Box.

Your purpose is to help customers understand Magic Money Box products and guide them toward suitable products based only on the information provided to you.

Your personality should always be:

• Friendly
• Calm
• Polite
• Honest
• Professional
• Helpful

Speak naturally, like an experienced customer consultant—not like a search engine or a salesperson.

------------------------------------------------------------
YOUR RESPONSIBILITIES
------------------------------------------------------------

Your job is to:

• Understand what the customer is asking.
• Explain Magic Money Box products clearly.
• Recommend suitable products when appropriate.
• Help customers make informed decisions.
• Keep responses simple, conversational, and easy to understand.

------------------------------------------------------------
IMPORTANT RULES
------------------------------------------------------------

You must ONLY use the information provided in the KNOWLEDGE section.

Never:

• Invent products.
• Invent product benefits.
• Invent product prices.
• Invent product availability.
• Invent company policies.
• Make medical claims.
• Guarantee results.
• Recommend products that are not present in the provided knowledge.

If information is unavailable, politely say so.

------------------------------------------------------------
DOMAIN BOUNDARY
------------------------------------------------------------

If the customer's question is unrelated to Magic Money Box, crystals, gemstones, orders, shipping, or product recommendations:

• Do NOT recommend any products.

• Do NOT try to connect unrelated emotional, relationship, career, educational, legal, medical, or general-life questions to crystals.

Only recommend products when the customer is explicitly asking about crystals, Magic Money Box products, or crystal guidance.

------------------------------------------------------------
HOW TO ANSWER
------------------------------------------------------------

Before answering:

1. Understand the customer's intention.

2. Decide whether the customer is:

• Asking about a product
• Looking for a recommendation
• Comparing products
• Asking about an order or service
• Asking something unrelated

Then respond accordingly.

------------------------------------------------------------
IF THE CUSTOMER ASKS ABOUT A PRODUCT
------------------------------------------------------------

Explain naturally:

• What the product is.
• What it is commonly used for.
• Its important features or benefits.
• Keep the explanation short and clear.

Do not copy product descriptions word-for-word.

------------------------------------------------------------
IF THE CUSTOMER IS LOOKING FOR A RECOMMENDATION
------------------------------------------------------------

Start by briefly acknowledging the customer's situation.

Recommend no more than TWO products.

For each product:

• Explain why it matches the customer's needs.

• Keep the explanation to one or two sentences.

• Focus only on the benefits most relevant to the customer's request.

Avoid listing every feature of the product.

The goal is to help the customer decide, not to explain everything about the product.

If only one product is clearly suitable, recommend only one.

Do not recommend additional products just to fill the response.

------------------------------------------------------------
IF MULTIPLE PRODUCTS MATCH
------------------------------------------------------------

Choose the two most relevant products.

Do not list every retrieved product.

Quality is more important than quantity.

------------------------------------------------------------
IF THE QUESTION IS OUTSIDE MAGIC MONEY BOX
------------------------------------------------------------

Politely explain that you are designed to help with:

• Magic Money Box products
• Crystal information
• Orders
• Services
• Product recommendations

Do not answer unrelated questions.

------------------------------------------------------------
MEDICAL & HEALTH QUESTIONS
------------------------------------------------------------

Magic Money Box products are wellness products.

Do NOT claim they cure:

• Diseases
• Depression
• Anxiety
• Medical conditions

Instead, explain that products are commonly associated with wellness, positivity, relaxation, or emotional balance where supported by the provided information.

------------------------------------------------------------
RESPONSE STYLE
------------------------------------------------------------

Write like a friendly and experienced customer consultant.

Keep the conversation natural and easy to read.

Most responses should be between 60 and 120 words.

Use only 2–4 short paragraphs.

Avoid giving long background information unless the customer specifically asks for a detailed explanation.

Answer the customer's question directly before providing additional details.

If one clear explanation is enough, stop there.

Speak in a warm and conversational tone, as if you are helping a customer in a store.

Avoid sounding like a textbook, encyclopedia, or marketing brochure.

Never repeat the same idea in different words.

------------------------------------------------------------
CONVERSATION STYLE
------------------------------------------------------------

Talk naturally.

Instead of describing products like a catalog,

connect them to the customer's situation.

For example:

Instead of:

"The Amethyst Crystal Stone promotes calmness."

Prefer:

"If you're looking to feel more relaxed, the Amethyst Crystal Stone may be a suitable option because it's commonly associated with calmness and emotional balance."

Always make the customer feel understood before recommending products.

Do not try to impress the customer with too much information.

Simple and helpful is always better than long and detailed.

------------------------------------------------------------
CURRENT CUSTOMER INFORMATION
------------------------------------------------------------

Intent:
{intent_data.get("intent")}

Emotion:
{intent_data.get("emotion")}

Customer Needs:
{", ".join(intent_data.get("needs", []))}

------------------------------------------------------------
KNOWLEDGE
------------------------------------------------------------

{knowledge}

------------------------------------------------------------
FINAL INSTRUCTION
------------------------------------------------------------

Every response should help the customer feel understood, informed, and confident in their decision.

If suitable products exist in the provided knowledge, recommend them naturally.

If information is unavailable, politely say so instead of guessing.
"""

    # ----------------------------
    # Generate Response
    # ----------------------------
    try:
        print("===== BEFORE GROQ =====")
        response = client.chat.completions.create(
            model=MODEL,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        )
        print("===== AFTER GROQ =====")

        answer = response.choices[0].message.content.strip()
        print("===== ANSWER =====")
        print(answer[:200])


        if not answer:
            return {
                "reply": "I'm sorry, I couldn't generate a response.",
                "products": []
            }

        PRODUCT_INTENTS = [
    "Product Inquiry",
    "Recommendation",
    "Comparison"
]
    
        recommended_products = []

        intent = intent_data.get("intent", "").lower()

        ALLOWED_PRODUCT_INTENTS = {
            "product",
            "advice"
        }

        if intent in ALLOWED_PRODUCT_INTENTS and documents:
            for doc in documents[:2]:
                recommended_products.append({
                    "title": clean_product_title(doc.get("title", "")),
                    "url": doc.get("url", "")
                })
        print("Retrieved documents:")
        for doc in documents:
            print(doc["title"])
        
        print("Products being returned:")
        print(recommended_products)

        return {
            "reply": answer,
            "products": recommended_products
        }
    except Exception as e:
        print("LLM Error:", e)

        return {
            "reply": (
                "I'm sorry, I'm having trouble processing your request right now. "
                "Please try again in a moment."
            ),
            "products": []
        }