from backend.interaction_graph import analyze_interactions


ingredients = [
    "retinol",
    "vitamin c",
    "niacinamide",
    "salicylic acid"
]


result = analyze_interactions(
    ingredients
)


print("\n===== INTERACTION ANALYSIS =====")

print("\nIngredients:")
for ingredient in result["ingredients"]:
    print("-", ingredient)


print("\nConflicts:")
for item in result["conflicts"]:
    print(item)


print("\nCautions:")
for item in result["cautions"]:
    print(item)


print("\nBeneficial combinations:")
for item in result["beneficial_combinations"]:
    print(item)