from backend.recommendation import recommend_alternatives
from backend.profile import UserProfile
import pprint


profile = UserProfile(
    skin_type="oily",
    sensitive_skin=True,
    allergies=["simethicone"],
    concerns=["acne"]
)


result = recommend_alternatives(
    "Simethicone",
    profile
)


print("\n===== ALTERNATIVE RECOMMENDATIONS =====\n")

pprint.pp(result)