from typing import List

from pydantic import BaseModel, Field

from backend.analyzer import analyze_ingredient
from backend.personalization import personalize_ingredient
from backend.interaction_graph import analyze_interactions
from backend.profile import UserProfile


# =========================================================
# Compare Product Model
# =========================================================

class CompareProduct(BaseModel):

    product_name: str

    ingredients: List[str] = Field(
        default_factory=list
    )


# =========================================================
# Compare Request
# =========================================================

class CompareRequest(BaseModel):

    product1: CompareProduct

    product2: CompareProduct

    profile: UserProfile = Field(
        default_factory=UserProfile
    )


# =========================================================
# Clean Ingredient Names
# =========================================================

def clean_ingredients(ingredients):

    cleaned = []

    for ingredient in ingredients:

        if not ingredient:
            continue

        name = ingredient.strip().upper()

        if name:
            cleaned.append(name)

    return list(dict.fromkeys(cleaned))


# =========================================================
# Analyze Product Ingredients
# =========================================================

def analyze_product_ingredients(
    ingredients,
    profile
):

    results = []

    for ingredient_name in ingredients:

        analysis = analyze_ingredient(
            ingredient_name
        )

        personalization = personalize_ingredient(
            analysis,
            profile
        )

        results.append({

            "ingredient":
                ingredient_name,

            "analysis":
                analysis,

            "personalization":
                personalization
        })

    return results


# =========================================================
# Compare Products
# =========================================================

def compare_products(
    product1,
    product2,
    profile
):

    ingredients1 = clean_ingredients(
        product1.ingredients
    )

    ingredients2 = clean_ingredients(
        product2.ingredients
    )


    # -----------------------------------------------------
    # Ingredient comparison
    # -----------------------------------------------------

    set1 = set(ingredients1)

    set2 = set(ingredients2)

    common_ingredients = sorted(
        list(set1.intersection(set2))
    )

    product1_only = sorted(
        list(set1 - set2)
    )

    product2_only = sorted(
        list(set2 - set1)
    )


    # -----------------------------------------------------
    # Analyze ingredients
    # -----------------------------------------------------

    product1_analysis = analyze_product_ingredients(
        ingredients1,
        profile
    )

    product2_analysis = analyze_product_ingredients(
        ingredients2,
        profile
    )


    # -----------------------------------------------------
    # Interaction analysis
    # -----------------------------------------------------

    product1_interactions = analyze_interactions(
        ingredients1
    )

    product2_interactions = analyze_interactions(
        ingredients2
    )

    combined_interactions = analyze_interactions(
        sorted(list(set1.union(set2)))
    )


    # -----------------------------------------------------
    # Comparison summary
    # -----------------------------------------------------

    if len(ingredients1) > len(ingredients2):

        larger_product = product1.product_name

    elif len(ingredients2) > len(ingredients1):

        larger_product = product2.product_name

    else:

        larger_product = "equal"


    # -----------------------------------------------------
    # Final result
    # -----------------------------------------------------

    return {

        "product1": {

            "product_name":
                product1.product_name,

            "ingredient_count":
                len(ingredients1),

            "ingredients":
                ingredients1,

            "analysis":
                product1_analysis,

            "interactions":
                product1_interactions
        },


        "product2": {

            "product_name":
                product2.product_name,

            "ingredient_count":
                len(ingredients2),

            "ingredients":
                ingredients2,

            "analysis":
                product2_analysis,

            "interactions":
                product2_interactions
        },


        "comparison": {

            "common_ingredients":
                common_ingredients,

            "common_count":
                len(common_ingredients),

            "product1_only":
                product1_only,

            "product1_only_count":
                len(product1_only),

            "product2_only":
                product2_only,

            "product2_only_count":
                len(product2_only),

            "larger_ingredient_list":
                larger_product
        },


        "combined_interactions":
            combined_interactions,

        "profile":
            profile.model_dump()
    }