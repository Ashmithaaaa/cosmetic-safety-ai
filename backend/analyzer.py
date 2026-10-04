import os
import math

from pymongo import MongoClient
from dotenv import load_dotenv

from backend.rf_predictor import predict_skin_sensitization


load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)

db = client["cosmetic_safety"]
ingredients_collection = db["ingredients"]


def clean_value(value):
    if value is None:
        return None

    if isinstance(value, float) and math.isnan(value):
        return None

    return value


def analyze_ingredient(inci_name):
    ingredient = ingredients_collection.find_one(
        {
            "inci_name": {
                "$regex": f"^{inci_name}$",
                "$options": "i"
            }
        }
    )

    if not ingredient:
        return {
            "ingredient": inci_name,
            "found": False
        }

    smiles = clean_value(ingredient.get("smiles"))

    # Random Forest prediction
    rf_result = predict_skin_sensitization(smiles)

    return {
        "ingredient": ingredient.get("inci_name"),
        "found": True,

        "functions": clean_value(
            ingredient.get("functions")
        ),

        "chemical_description": clean_value(
            ingredient.get("chemical_description")
        ),

        "cosing_restriction": clean_value(
            ingredient.get("cosing_restriction")
        ),

        "common_allergen": clean_value(
            ingredient.get("is_common_allergen")
        ),

        "allergen_source": clean_value(
            ingredient.get("allergen_source")
        ),

        "comedogenic_rating": clean_value(
            ingredient.get("comedogenic_rating")
        ),

        "fungal_acne_trigger": clean_value(
            ingredient.get("is_fungal_acne_trigger")
        ),

        "smiles": smiles,

        "chemical_structure_source": clean_value(
            ingredient.get("chemical_structure_source")
        ),

        "random_forest": rf_result,

        "annex_ii": clean_value(
            ingredient.get("annex_ii")
        ),

        "annex_iii": clean_value(
            ingredient.get("annex_iii")
        ),

        "annex_iv": clean_value(
            ingredient.get("annex_iv")
        ),

        "annex_v": clean_value(
            ingredient.get("annex_v")
        ),

        "annex_vi": clean_value(
            ingredient.get("annex_vi")
        )
    }


def analyze_ingredients(normalized_ingredients):
    results = []

    for item in normalized_ingredients:

        canonical = item.get("canonical_name")

        if not canonical:
            results.append({
                "ocr_text": item.get("ocr_text"),
                "canonical_name": None,
                "found": False,
                "status": "uncertain"
            })

            continue

        analysis = analyze_ingredient(canonical)

        results.append({
            "ocr_text": item.get("ocr_text"),
            "canonical_name": canonical,

            "normalization_method": item.get(
                "method"
            ),

            "normalization_confidence": item.get(
                "confidence"
            ),

            **analysis
        })

    return results