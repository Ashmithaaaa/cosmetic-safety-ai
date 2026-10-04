import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

MODEL_NAME = "openai/gpt-oss-20b"


def generate_explanation(rag_context, analysis_results, user_profile=None):
    prompt = f"""
You are an explanation assistant for a cosmetic ingredient analysis system.

Your job is ONLY to explain the evidence provided by the application.

STRICT RULES:
1. Do not invent ingredient properties, benefits, risks, interactions,
   concentrations, medical advice, or scientific claims.
2. Do not add facts that are not present in the provided evidence.
3. Do not interpret Random Forest class numbers as "safe", "unsafe",
   "low risk", or "high risk" unless the provided analysis explicitly
   defines those classes.
4. If a Random Forest prediction is present, describe it only as a
   model prediction and report the provided probability values.
5. Do not make definitive safety claims.
6. If information is unavailable, say "Not available in the provided data."
7. Clearly distinguish database information, ML predictions, and
   interaction-graph results.
8. Use the user's profile only to identify matching flags or concerns
   explicitly supported by the structured analysis.
9. Never infer that missing information means the ingredient is safe,
   low-risk, non-irritating, or non-comedogenic.
10. Do not use phrases such as "suitable", "beneficial", "unlikely to
    cause", or "safe" unless those conclusions are explicitly present
    in the supplied evidence.

USER PROFILE:
{user_profile}

RETRIEVED KNOWLEDGE:
{rag_context}

STRUCTURED ANALYSIS:
{analysis_results}

Generate a concise explanation with these sections:

1. Overall Summary
2. Ingredient Information
3. Personalized Observations
4. Potential Conflicts or Beneficial Combinations
5. Practical Summary

Only use information explicitly supported by the provided data.
Missing data must be reported as unavailable rather than interpreted.
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a grounded explanation assistant. "
                    "Use only the evidence supplied by the application."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.1,
        max_tokens=1000
    )

    return response.choices[0].message.content