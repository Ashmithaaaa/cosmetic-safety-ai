from typing import List

from pydantic import BaseModel, Field

from backend.interaction_graph import analyze_interactions


# =========================================================
# Routine Product
# =========================================================

class RoutineProduct(BaseModel):

    product_name: str

    time_of_day: str = "any"

    order: int = 1

    ingredients: List[str] = Field(
        default_factory=list
    )


# =========================================================
# Routine
# =========================================================

class Routine(BaseModel):

    routine_name: str

    products: List[RoutineProduct] = Field(
        default_factory=list
    )


# =========================================================
# Analyze Routine
# =========================================================

def analyze_routine(routine: Routine):

    ingredient_products = {}

    # -----------------------------------------------------
    # Build ingredient -> product mapping
    # -----------------------------------------------------

    for product in routine.products:

        product_ingredients = set()

        for ingredient in product.ingredients:

            if not ingredient:
                continue

            ingredient_name = (
                ingredient.strip().upper()
            )

            if ingredient_name:

                product_ingredients.add(
                    ingredient_name
                )

        for ingredient_name in product_ingredients:

            if ingredient_name not in ingredient_products:

                ingredient_products[
                    ingredient_name
                ] = []

            ingredient_products[
                ingredient_name
            ].append(
                product.product_name
            )


    # -----------------------------------------------------
    # Combined ingredients
    # -----------------------------------------------------

    combined_ingredients = list(
        ingredient_products.keys()
    )


    # -----------------------------------------------------
    # Duplicate ingredients
    # -----------------------------------------------------

    duplicate_ingredients = []

    for ingredient_name, product_list in (
        ingredient_products.items()
    ):

        if len(product_list) > 1:

            duplicate_ingredients.append({

                "ingredient": ingredient_name,

                "product_count":
                    len(product_list),

                "products":
                    product_list,

                "message": (
                    f"{ingredient_name} appears in "
                    f"{len(product_list)} products."
                )
            })


    # -----------------------------------------------------
    # Interaction analysis
    # -----------------------------------------------------

    interaction_analysis = analyze_interactions(
        combined_ingredients
    )


    # -----------------------------------------------------
    # Group products by time of day
    # -----------------------------------------------------

    schedule = {}

    for product in routine.products:

        time_of_day = (
            product.time_of_day.lower().strip()
        )

        if time_of_day not in schedule:

            schedule[time_of_day] = []

        schedule[time_of_day].append({

            "product_name":
                product.product_name,

            "order":
                product.order,

            "ingredients":
                product.ingredients
        })


    # Sort products by order

    for time_of_day in schedule:

        schedule[time_of_day].sort(
            key=lambda item: item["order"]
        )


    # -----------------------------------------------------
    # Final result
    # -----------------------------------------------------

    return {

        "routine_name":
            routine.routine_name,

        "product_count":
            len(routine.products),

        "products":
            [
                product.model_dump()
                for product in routine.products
            ],

        "schedule":
            schedule,

        "combined_ingredients":
            combined_ingredients,

        "duplicate_ingredients":
            duplicate_ingredients,

        "duplicate_count":
            len(duplicate_ingredients),

        "interactions":
            interaction_analysis
    }