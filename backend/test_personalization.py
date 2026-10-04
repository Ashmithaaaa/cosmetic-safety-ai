from backend.analyzer import analyze_ingredients
from backend.personalization import analyze_personalization


normalized_ingredients = [
    {
        "ocr_text": "A a (Water)",
        "canonical_name": "WATER",
        "method": "ocr_word_recovery",
        "confidence": 100
    },
    {
        "ocr_text": "Hexyldecyl Lo urate",
        "canonical_name": "HEXYLDECYL LAURATE",
        "method": "ocr_split_word_recovery",
        "confidence": 94.44
    },
    {
        "ocr_text": "Etidronic Acid",
        "canonical_name": "ETIDRONIC ACID",
        "method": "exact_alias",
        "confidence": 100
    },
    {
        "ocr_text": "Simethicone",
        "canonical_name": "SIMETHICONE",
        "method": "exact_alias",
        "confidence": 100
    }
]


user_profile = {
    "skin_type": "oily",
    "sensitive_skin": True,
    "allergies": ["simethicone"],
    "concerns": ["acne"]
}


ingredient_results = analyze_ingredients(
    normalized_ingredients
)

personalized_results = analyze_personalization(
    ingredient_results,
    user_profile
)


print("\n===== PERSONALIZED ANALYSIS =====")

for result in personalized_results:

    print("\nIngredient:", result["ingredient"])

    print("Flags:", result["flags"])

    print("Reasons:", result["reasons"])