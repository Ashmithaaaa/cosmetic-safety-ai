import os
from pymongo import MongoClient
from dotenv import load_dotenv


# =========================================================
# MongoDB Connection
# =========================================================

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)

db = client["cosmetic_safety"]

ingredients_collection = db["ingredients"]


# =========================================================
# RAG Retrieval
# =========================================================

def retrieve_ingredient_knowledge(
    ingredient_names,
    top_k=5
):
    """
    Retrieve relevant ingredient knowledge from MongoDB.

    This is the retrieval stage of RAG.
    The retrieved information can later be passed
    to an LLM for explanation.
    """

    if not ingredient_names:
        return []

    retrieved_documents = []

    # Remove duplicates while preserving order
    ingredient_names = list(
        dict.fromkeys(ingredient_names)
    )

    for name in ingredient_names[:top_k]:

        document = ingredients_collection.find_one(
            {
                "inci_name": {
                    "$regex": f"^{name}$",
                    "$options": "i"
                }
            }
        )

        if not document:
            continue

        retrieved_documents.append(
            {
                "ingredient": document.get(
                    "inci_name"
                ),

                "functions": document.get(
                    "functions"
                ),

                "chemical_description":
                    document.get(
                        "chemical_description"
                    ),

                "common_allergen":
                    document.get(
                        "is_common_allergen"
                    ),

                "allergen_source":
                    document.get(
                        "allergen_source"
                    ),

                "comedogenic_rating":
                    document.get(
                        "comedogenic_rating"
                    ),

                "fungal_acne_trigger":
                    document.get(
                        "is_fungal_acne_trigger"
                    ),

                "cosing_restriction":
                    document.get(
                        "cosing_restriction"
                    ),

                "annex_ii":
                    document.get("annex_ii"),

                "annex_iii":
                    document.get("annex_iii"),

                "annex_iv":
                    document.get("annex_iv"),

                "annex_v":
                    document.get("annex_v"),

                "annex_vi":
                    document.get("annex_vi")
            }
        )

    return retrieved_documents


# =========================================================
# Create LLM Context
# =========================================================

def build_rag_context(
    retrieved_documents
):
    """
    Convert retrieved MongoDB knowledge into
    structured context for the future LLM.
    """

    if not retrieved_documents:
        return "No relevant ingredient knowledge was found."

    context_parts = []

    for document in retrieved_documents:

        ingredient = document.get(
            "ingredient"
        )

        context_parts.append(
            f"""
Ingredient: {ingredient}

Functions:
{document.get("functions")}

Chemical description:
{document.get("chemical_description")}

Common allergen:
{document.get("common_allergen")}

Allergen source:
{document.get("allergen_source")}

Comedogenic rating:
{document.get("comedogenic_rating")}

Fungal-acne trigger:
{document.get("fungal_acne_trigger")}

CosIng restriction:
{document.get("cosing_restriction")}

Annex II:
{document.get("annex_ii")}

Annex III:
{document.get("annex_iii")}

Annex IV:
{document.get("annex_iv")}

Annex V:
{document.get("annex_v")}

Annex VI:
{document.get("annex_vi")}
""".strip()
        )

    return "\n\n-------------------------\n\n".join(
        context_parts
    )