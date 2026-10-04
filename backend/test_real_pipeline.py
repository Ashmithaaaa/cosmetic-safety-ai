from backend.full_analysis import analyze_image


IMAGE_PATH = "test_ingredients.jpg"


print("\n=========================================")
print("       COSMETIC SAFETY AI PIPELINE")
print("=========================================\n")


# =========================================
# RUN FULL ANALYSIS
# =========================================

result = analyze_image(
    IMAGE_PATH
)


# =========================================
# OCR
# =========================================

print("===== OCR TEXT =====")
print(result["ocr_text"])


# =========================================
# INGREDIENT RESULTS
# =========================================

print("\n===== INGREDIENT ANALYSIS =====")

for item in result["ingredients"]:

    print("\nOCR:")
    print(item["ocr_name"])

    print("Canonical:")
    print(item["canonical_name"])

    print("Method:")
    print(item["matching_method"])

    print("Confidence:")
    print(item["confidence"])

    print("Status:")
    print(item["status"])

    if item["analysis"]:

        print("Functions:")
        print(
            item["analysis"].get("functions")
        )

        print("Allergen:")
        print(
            item["analysis"].get("common_allergen")
        )

        print("Comedogenicity:")
        print(
            item["analysis"].get(
                "comedogenic_rating"
            )
        )


# =========================================
# COUNTS
# =========================================

print("\n===== SUMMARY =====")

print(
    "Total ingredients:",
    result["ingredient_count"]
)

print(
    "Recognized:",
    result["recognized_count"]
)

print(
    "Uncertain:",
    result["uncertain_count"]
)


# =========================================
# INTERACTION ANALYSIS
# =========================================

interaction = result["interactions"]

print("\n===== INTERACTION ANALYSIS =====")

print("\nIngredients:")

for ingredient in interaction["ingredients"]:
    print("-", ingredient)


print("\nConflicts:")

if interaction["conflicts"]:

    for item in interaction["conflicts"]:

        print(
            f"- {item['ingredient_a']} + "
            f"{item['ingredient_b']}"
        )

        print(
            "  Reason:",
            item["reason"]
        )

        print(
            "  Recommendation:",
            item["recommendation"]
        )

else:

    print("None")


print("\nCautions:")

if interaction["cautions"]:

    for item in interaction["cautions"]:

        print(
            f"- {item['ingredient_a']} + "
            f"{item['ingredient_b']}"
        )

        print(
            "  Reason:",
            item["reason"]
        )

        print(
            "  Recommendation:",
            item["recommendation"]
        )

else:

    print("None")


print("\nBeneficial combinations:")

if interaction["beneficial_combinations"]:

    for item in interaction[
        "beneficial_combinations"
    ]:

        print(
            f"- {item['ingredient_a']} + "
            f"{item['ingredient_b']}"
        )

        print(
            "  Reason:",
            item["reason"]
        )

else:

    print("None")


print("\n=========================================")
print("             ANALYSIS COMPLETE")
print("=========================================")