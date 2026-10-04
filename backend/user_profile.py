def create_user_profile(
    skin_type,
    sensitive_skin,
    allergies,
    concerns
):
    return {
        "skin_type": skin_type.lower().strip(),
        "sensitive_skin": bool(sensitive_skin),
        "allergies": [
            allergy.lower().strip()
            for allergy in allergies
        ],
        "concerns": [
            concern.lower().strip()
            for concern in concerns
        ]
    }