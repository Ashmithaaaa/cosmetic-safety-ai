import os
import re

from pymongo import MongoClient
from dotenv import load_dotenv
from rapidfuzz import process, fuzz


# =========================================================
# DATABASE
# =========================================================

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)

db = client["cosmetic_safety"]

ingredients_collection = db["ingredients"]
aliases_collection = db["ingredient_aliases"]


# =========================================================
# TEXT NORMALIZATION
# =========================================================

def clean_text(text):
    if not text:
        return ""

    text = str(text).lower()

    replacements = {
        "!": "l",
        "|": "i",
        "–": "-",
        "—": "-",
        "−": "-"
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Remove brackets
    text = re.sub(r"[\(\)\[\]\{\}]", " ", text)

    # Keep letters, numbers, spaces and hyphens
    text = re.sub(r"[^a-z0-9\-\s]", " ", text)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def valid_text(text):
    cleaned = clean_text(text)

    if len(cleaned) < 3:
        return False

    if not re.search(r"[a-z]", cleaned):
        return False

    return True


# =========================================================
# LOAD CANONICAL INGREDIENTS
# =========================================================

def get_canonical_map():

    canonical_map = {}

    for doc in ingredients_collection.find(
        {},
        {"_id": 0, "inci_name": 1}
    ):

        name = doc.get("inci_name")

        if not name:
            continue

        cleaned = clean_text(name)

        if len(cleaned) >= 3:
            canonical_map[cleaned] = name

    return canonical_map


# =========================================================
# LOAD ALIASES
# =========================================================

def get_alias_map(canonical_map):

    alias_map = {}

    for doc in aliases_collection.find(
        {},
        {
            "_id": 0,
            "raw_name": 1,
            "canonical_name": 1
        }
    ):

        raw = doc.get("raw_name")
        canonical = doc.get("canonical_name")

        if not raw or not canonical:
            continue

        raw_clean = clean_text(raw)
        canonical_clean = clean_text(canonical)

        if len(raw_clean) < 3:
            continue

        if canonical_clean not in canonical_map:
            continue

        if raw_clean in {
            "-",
            "_",
            ".",
            "l",
            "i"
        }:
            continue

        alias_map[raw_clean] = canonical_map[
            canonical_clean
        ]

    return alias_map


# =========================================================
# EXACT MATCH
# =========================================================

def exact_match(
    text,
    canonical_map,
    alias_map
):

    cleaned = clean_text(text)

    # Exact alias
    if cleaned in alias_map:

        return {
            "canonical_name": alias_map[cleaned],
            "method": "exact_alias",
            "confidence": 100,
            "source_text": text
        }

    # Exact INCI
    if cleaned in canonical_map:

        return {
            "canonical_name": canonical_map[cleaned],
            "method": "exact_inci",
            "confidence": 100,
            "source_text": text
        }

    return None


# =========================================================
# OCR SPLIT-WORD RECOVERY
# =========================================================

def join_split_words(
    text,
    canonical_map
):

    cleaned = clean_text(text)

    if not valid_text(cleaned):
        return None

    words = cleaned.split()

    if len(words) < 2:
        return None

    names = list(canonical_map.keys())

    if not names:
        return None

    best = None

    # Try joining adjacent OCR words.
    #
    # Examples:
    #   "hydr en peroxide"
    #       -> "hydren peroxide"
    #
    #   "hexyldecyl lo urate"
    #       -> "hexyldecyl lourate"
    #
    #   "cel eareth 20"
    #       -> "celeareth 20"

    for i in range(len(words) - 1):

        joined = words[i] + words[i + 1]

        new_words = (
            words[:i]
            + [joined]
            + words[i + 2:]
        )

        candidate = " ".join(new_words)

        result = process.extractOne(
            candidate,
            names,
            scorer=fuzz.ratio
        )

        if not result:
            continue

        matched_name = result[0]
        score = result[1]

        if score >= 94:

            if best is None or score > best[0]:
                best = (
                    score,
                    matched_name
                )

    if best is None:
        return None

    score, matched_name = best

    canonical = canonical_map[
        matched_name
    ]

    return {
        "canonical_name": canonical,
        "method": "ocr_split_word_recovery",
        "confidence": round(score, 2),
        "source_text": text
    }


# =========================================================
# SAFE FUZZY MATCH
# =========================================================

def safe_fuzzy_match(
    text,
    canonical_map,
    alias_map
):

    cleaned = clean_text(text)

    if not valid_text(cleaned):
        return None

    source_words = cleaned.split()

    # -----------------------------------------------------
    # Fuzzy alias
    # -----------------------------------------------------

    if alias_map:

        result = process.extractOne(
            cleaned,
            list(alias_map.keys()),
            scorer=fuzz.ratio
        )

        if result:

            matched_alias = result[0]
            score = result[1]

            if score >= 94:

                canonical = alias_map[
                    matched_alias
                ]

                candidate_words = clean_text(
                    canonical
                ).split()

                # Don't map a long noisy phrase
                # to a generic one-word ingredient.
                if (
                    len(source_words) > 1
                    and len(candidate_words) == 1
                ):
                    return None

                return {
                    "canonical_name": canonical,
                    "method": "fuzzy_alias",
                    "confidence": round(score, 2),
                    "source_text": text
                }

    # -----------------------------------------------------
    # Fuzzy canonical INCI
    # -----------------------------------------------------

    names = list(canonical_map.keys())

    if not names:
        return None

    result = process.extractOne(
        cleaned,
        names,
        scorer=fuzz.ratio
    )

    if not result:
        return None

    matched_name = result[0]
    score = result[1]

    if score < 94:
        return None

    canonical = canonical_map[
        matched_name
    ]

    candidate_words = clean_text(
        canonical
    ).split()

    # Prevent generic matches
    if (
        len(source_words) > 1
        and len(candidate_words) == 1
    ):
        return None

    return {
        "canonical_name": canonical,
        "method": "fuzzy_inci",
        "confidence": round(score, 2),
        "source_text": text
    }


# =========================================================
# SAFE WATER RECOVERY
# =========================================================

def recover_water(
    text,
    canonical_map
):

    cleaned = clean_text(text)

    if "water" not in cleaned.split():
        return None

    if "water" not in canonical_map:
        return None

    return {
        "canonical_name": canonical_map["water"],
        "method": "ocr_word_recovery",
        "confidence": 100,
        "source_text": "water"
    }


# =========================================================
# MAIN NORMALIZER
# =========================================================

def normalize_ingredient(ocr_text):

    canonical_map = get_canonical_map()

    alias_map = get_alias_map(
        canonical_map
    )

    # -----------------------------------------------------
    # 1. Known simple OCR recovery
    # -----------------------------------------------------

    result = recover_water(
        ocr_text,
        canonical_map
    )

    if result:
        return result

    # -----------------------------------------------------
    # 2. Exact match
    # -----------------------------------------------------

    result = exact_match(
        ocr_text,
        canonical_map,
        alias_map
    )

    if result:
        return result

    # -----------------------------------------------------
    # 3. OCR split-word recovery
    # -----------------------------------------------------

    result = join_split_words(
        ocr_text,
        canonical_map
    )

    if result:
        return result

    # -----------------------------------------------------
    # 4. High-confidence fuzzy match
    # -----------------------------------------------------

    result = safe_fuzzy_match(
        ocr_text,
        canonical_map,
        alias_map
    )

    if result:
        return result

    # -----------------------------------------------------
    # 5. Do NOT guess
    # -----------------------------------------------------

    return {
        "canonical_name": None,
        "method": "not_found",
        "confidence": 0,
        "source_text": ocr_text
    }


# =========================================================
# MULTIPLE INGREDIENTS
# =========================================================

def normalize_ingredients(
    ingredient_list
):

    results = []

    for ingredient in ingredient_list:

        result = normalize_ingredient(
            ingredient
        )

        results.append({
            "ocr_text": ingredient,
            **result
        })

    return results