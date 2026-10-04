from backend.user_profile import create_user_profile


profile = create_user_profile(
    skin_type="Oily",
    sensitive_skin=True,
    allergies=["Simethicone"],
    concerns=["Acne", "Large pores"]
)


print("\n===== SKIN PROFILE =====")

print("Skin type:", profile["skin_type"])
print("Sensitive skin:", profile["sensitive_skin"])
print("Allergies:", profile["allergies"])
print("Concerns:", profile["concerns"])