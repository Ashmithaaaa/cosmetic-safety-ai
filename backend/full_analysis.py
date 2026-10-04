from backend.ocr import extract_text
from backend.ingredient_parser import extract_ingredient_candidates
from backend.normalizer import normalize_ingredient
from backend.analyzer import analyze_ingredient
from backend.personalization import personalize_ingredient
from backend.recommendation import recommend_alternatives
from backend.interaction_graph import analyze_interactions
from backend.rag import retrieve_ingredient_knowledge, build_rag_context
from backend.llm import generate_explanation


def analyze_image(image_path, profile=None):
    # -------------------------
    # 1. OCR
    # -------------------------
    ocr_text = extract_text(image_path)

    # -------------------------
    # 2. Extract ingredient candidates
    # -------------------------
    candidates = extract_ingredient_candidates(ocr_text)

    results = []
    recognized_count = 0
    uncertain_count = 0

    # -------------------------
    # 3. Normalize + analyze
    # -------------------------
    for ingredient in candidates:

        normalized = normalize_ingredient(ingredient)

        canonical_name = normalized.get("canonical_name")
        matching_method = normalized.get("method")
        confidence = normalized.get("confidence")

        if canonical_name:
            status = "recognized"
            recognized_count += 1
        else:
            status = "uncertain"
            uncertain_count += 1

        ingredient_result = {
            "ocr_name": ingredient,
            "matched_name": normalized.get("matched_name"),
            "canonical_name": canonical_name,
            "matching_method": matching_method,
            "confidence": confidence,
            "status": status,
            "analysis": None,
            "personalization": None,
            "recommendations": None
        }

        if canonical_name:

            # -------------------------
            # Ingredient analysis
            # -------------------------
            analysis = analyze_ingredient(canonical_name)

            ingredient_result["analysis"] = analysis

            # -------------------------
            # Personalization
            # -------------------------
            if profile is not None:

                personalization = personalize_ingredient(
                    analysis,
                    profile
                )

                ingredient_result["personalization"] = personalization

                # -------------------------
                # Alternative recommendations
                # -------------------------
                flags = personalization.get("flags", [])

                if flags:

                    recommendations = recommend_alternatives(
                        canonical_name,
                        profile
                    )

                    ingredient_result["recommendations"] = recommendations

        results.append(ingredient_result)

    # -------------------------
    # 4. Get recognized ingredients
    # -------------------------
    normalized_ingredients = [
        item["canonical_name"]
        for item in results
        if item["canonical_name"]
    ]

    # -------------------------
    # 5. Interaction analysis
    # -------------------------
    interaction_analysis = analyze_interactions(
        normalized_ingredients
    )

    # -------------------------
    # 6. RAG retrieval
    # -------------------------
    rag_documents = retrieve_ingredient_knowledge(
        normalized_ingredients
    )

    rag_context = build_rag_context(
        rag_documents
    )

    # -------------------------
    # 7. Prepare structured analysis
    # -------------------------
    structured_analysis = {
        "ingredients": results,
        "interactions": interaction_analysis,
        "recognized_count": recognized_count,
        "uncertain_count": uncertain_count
    }

    # -------------------------
    # 8. User profile
    # -------------------------
    profile_data = None

    if profile is not None:
        profile_data = profile.model_dump()

    # -------------------------
    # 9. Groq explanation
    # -------------------------
    explanation = generate_explanation(
        rag_context=rag_context,
        analysis_results=structured_analysis,
        user_profile=profile_data
    )

    # -------------------------
    # 10. Final response
    # -------------------------
    response = {
        "ocr_text": ocr_text,
        "ingredients": results,
        "ingredient_count": len(results),
        "recognized_count": recognized_count,
        "uncertain_count": uncertain_count,
        "interactions": interaction_analysis,
        "rag": {
            "retrieved_count": len(rag_documents)
        },
        "llm_explanation": explanation
    }

    if profile is not None:
        response["profile"] = profile_data

    return response