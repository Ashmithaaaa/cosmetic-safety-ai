from backend.llm import generate_explanation


rag_context = """
Ingredient: Niacinamide

Functions:
['skin conditioning', 'brightening']

Common allergen:
None

Comedogenic rating:
None
"""

analysis_results = """
Niacinamide was successfully identified.
Random Forest prediction is available, but its class should be treated
as a model prediction rather than a definitive safety conclusion.
"""

user_profile = {
    "skin_type": "oily",
    "sensitive_skin": True,
    "allergies": [],
    "concerns": ["acne"]
}


result = generate_explanation(
    rag_context,
    analysis_results,
    user_profile
)

print("\n===== GROQ LLM TEST =====\n")
print(result)