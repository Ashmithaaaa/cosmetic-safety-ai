from backend.rag import (
    retrieve_ingredient_knowledge,
    build_rag_context
)


ingredients = [
    "Niacinamide",
    "Simethicone",
    "Water"
]


print("\n===== RAG RETRIEVAL TEST =====\n")

documents = retrieve_ingredient_knowledge(
    ingredients
)

print(
    f"Retrieved documents: {len(documents)}"
)

for document in documents:

    print(
        "\nIngredient:",
        document.get("ingredient")
    )

    print(
        "Functions:",
        document.get("functions")
    )

    print(
        "Common allergen:",
        document.get("common_allergen")
    )

    print(
        "Comedogenic rating:",
        document.get("comedogenic_rating")
    )


print("\n===== RAG CONTEXT =====\n")

context = build_rag_context(
    documents
)

print(context)