import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)

db = client["cosmetic_safety"]
ingredients_collection = db["ingredients"]


def normalize_functions(functions):
    """
    Convert ingredient functions into a clean list.

    The database may store multiple functions as:
    ['FUNCTION A;FUNCTION B;FUNCTION C']
    """

    if not functions:
        return []

    if isinstance(functions, str):
        functions = [functions]

    normalized = []

    for function in functions:

        if not function:
            continue

        parts = str(function).split(";")

        for part in parts:

            part = part.strip()

            if part:
                normalized.append(
                    part.upper()
                )

    return list(dict.fromkeys(normalized))


def recommend_alternatives(
    ingredient_name,
    profile,
    limit=5
):
    """
    Recommend alternative ingredients based on
    shared functions while excluding ingredients
    that conflict with the user's profile.
    """

    ingredient = ingredients_collection.find_one(
        {
            "inci_name": {
                "$regex": f"^{ingredient_name}$",
                "$options": "i"
            }
        }
    )

    if not ingredient:
        return {
            "ingredient": ingredient_name,
            "available": False,
            "alternatives": []
        }

    original_functions = normalize_functions(
        ingredient.get("functions", [])
    )

    if not original_functions:
        return {
            "ingredient": ingredient.get(
                "inci_name",
                ingredient_name
            ),
            "available": False,
            "reason": "No ingredient functions available.",
            "alternatives": []
        }

    allergies = [
        str(item).lower().strip()
        for item in getattr(
            profile,
            "allergies",
            []
        )
    ]

    sensitivities = [
        str(item).lower().strip()
        for item in getattr(
            profile,
            "sensitivities",
            []
        )
    ]

    excluded_names = set(
        allergies + sensitivities
    )

    original_name = ingredient.get(
        "inci_name",
        ingredient_name
    )

    alternatives = []

    candidates = ingredients_collection.find(
        {
            "functions": {
                "$regex": "|".join(
                    [
                        function.replace(
                            " ",
                            r"\s*"
                        )
                        for function in original_functions
                    ]
                ),
                "$options": "i"
            }
        }
    ).limit(100)

    for candidate in candidates:

        candidate_name = candidate.get(
            "inci_name"
        )

        if not candidate_name:
            continue

        # Do not recommend the same ingredient
        if candidate_name.lower() == original_name.lower():
            continue

        # Exclude explicit allergy/sensitivity matches
        if candidate_name.lower() in excluded_names:
            continue

        candidate_functions = normalize_functions(
            candidate.get("functions", [])
        )

        shared_functions = [
            function
            for function in candidate_functions
            if function in original_functions
        ]

        if not shared_functions:
            continue

        # Avoid ingredients explicitly marked
        # as common allergens
        common_allergen = candidate.get(
            "is_common_allergen"
        )

        if common_allergen in [True, 1]:
            continue

        alternatives.append(
            {
                "ingredient": candidate_name,
                "shared_functions": shared_functions,
                "reason": (
                    "This ingredient shares one or more "
                    "functions with the flagged ingredient."
                )
            }
        )

        if len(alternatives) >= limit:
            break

    return {
        "ingredient": original_name,
        "available": True,
        "original_functions": original_functions,
        "alternatives": alternatives
    }