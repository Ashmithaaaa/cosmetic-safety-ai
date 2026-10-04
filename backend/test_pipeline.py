from ingredient_parser import extract_ingredient_candidates
from normalizer import normalize_ingredient


ocr_text = """
Aqua, Glycerin, Niacinamde, Salicylic Acd,
Panthenol, Tocopherol
"""

ingredients = extract_ingredient_candidates(ocr_text)

print("===== NORMALIZED INGREDIENTS =====")

for ingredient in ingredients:
    result = normalize_ingredient(ingredient)
    print(result)