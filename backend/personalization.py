def personalize_ingredient(analysis, profile):
    """
    Analyze one ingredient against the user's profile.
    """

    if not analysis:
        return {
            "flags": [],
            "reasons": []
        }

    flags = []
    reasons = []

    # =========================================
    # USER PROFILE
    # =========================================

    skin_type = profile.skin_type.lower()

    sensitive_skin = profile.sensitive_skin

    allergies = [
        allergy.lower().strip()
        for allergy in profile.allergies
    ]

    # =========================================
    # INGREDIENT
    # =========================================

    ingredient = analysis.get(
        "ingredient",
        ""
    )

    ingredient_lower = ingredient.lower()

    # =========================================
    # ALLERGY CHECK
    # =========================================

    if ingredient_lower in allergies:

        flags.append(
            "allergy_match"
        )

        reasons.append(
            "This ingredient matches an allergy "
            "provided by the user."
        )

    # =========================================
    # COMMON ALLERGEN
    # =========================================

    common_allergen = analysis.get(
        "common_allergen"
    )

    if common_allergen in [1, True]:

        flags.append(
            "common_allergen"
        )

        reasons.append(
            "This ingredient is marked as a "
            "common allergen in the database."
        )

    # =========================================
    # OILY SKIN + COMEDOGENICITY
    # =========================================

    rating = analysis.get(
        "comedogenic_rating"
    )

    if (
        skin_type == "oily"
        and isinstance(rating, (int, float))
        and rating >= 3
    ):

        flags.append(
            "comedogenic_concern"
        )

        reasons.append(
            "The ingredient has a relatively "
            "high comedogenicity rating for "
            "an oily-skin profile."
        )

    # =========================================
    # SENSITIVE SKIN
    # =========================================

    if (
        sensitive_skin
        and common_allergen in [1, True]
    ):

        flags.append(
            "sensitive_skin_concern"
        )

        reasons.append(
            "The ingredient is flagged as a "
            "common allergen and the user has "
            "sensitive skin."
        )

    # =========================================
    # RESULT
    # =========================================

    return {
        "ingredient": ingredient,
        "flags": flags,
        "reasons": reasons
    }