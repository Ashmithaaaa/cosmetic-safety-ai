import re


def clean_text(text):

    if not text:
        return ""

    replacements = {
        "—": "-",
        "–": "-",
        "−": "-",
        "|": " ",
        "!": "l",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(
        r"[\x00-\x1F\x7F]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def remove_ocr_noise(text):

    if not text:
        return ""

    # Remove INGREDIENTS heading
    text = re.sub(
        r"\b(?:INGREDIENTS?|INGREDENTS?)\s*:?",
        " ",
        text,
        flags=re.IGNORECASE
    )

    # Remove text after professional-use warning
    text = re.sub(
        r"\b(?:PROFESSIONAL\s+USE|"
        r"USAGE\s+PROFESSIONNEL|"
        r"USO\s+PROFESSIONALE)\b.*",
        " ",
        text,
        flags=re.IGNORECASE
    )

    # Remove repeated whitespace
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def is_valid_candidate(text):

    text = text.strip()

    if len(text) < 3:
        return False

    letters = len(
        re.findall(
            r"[A-Za-z]",
            text
        )
    )

    if letters < 3:
        return False

    # Reject mostly OCR symbols
    if letters / max(len(text), 1) < 0.45:
        return False

    if text.lower() in {
        "ingredient",
        "ingredients",
        "professional use",
        "usage professionnel",
        "uso professionale",
    }:
        return False

    return True


def extract_ingredient_candidates(ocr_text):

    if not ocr_text:
        return []

    text = clean_text(
        ocr_text
    )

    text = remove_ocr_noise(
        text
    )

    # Ingredients are normally comma-separated.
    # Semicolon is also common in some labels.
    parts = re.split(
        r"[,;]",
        text
    )

    candidates = []

    for part in parts:

        part = part.strip()

        if not part:
            continue

        # Remove OCR punctuation around candidate
        part = re.sub(
            r"^[\s\.\:\-\|]+",
            "",
            part
        )

        part = re.sub(
            r"[\s\.\:\-\|]+$",
            "",
            part
        )

        part = re.sub(
            r"\s+",
            " ",
            part
        ).strip()

        if not is_valid_candidate(
            part
        ):
            continue

        candidates.append(
            part
        )

    # Remove duplicates
    final = []

    seen = set()

    for candidate in candidates:

        key = candidate.lower()

        if key in seen:
            continue

        seen.add(key)

        final.append(
            candidate
        )

    print(
        "\n===== INGREDIENT CANDIDATES ====="
    )

    for i, ingredient in enumerate(
        final,
        start=1
    ):
        print(
            f"{i}. {ingredient}"
        )

    return final