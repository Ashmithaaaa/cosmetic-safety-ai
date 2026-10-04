import cv2
import pytesseract
import re


pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


# =========================================================
# PREPROCESSING VARIANTS
# =========================================================

def create_preprocessing_variants(image):

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    # -----------------------------------------------------
    # Variant 1: enlarged grayscale
    # -----------------------------------------------------

    enlarged = cv2.resize(
        gray,
        None,
        fx=4,
        fy=4,
        interpolation=cv2.INTER_CUBIC
    )

    # -----------------------------------------------------
    # Variant 2: CLAHE
    # -----------------------------------------------------

    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    enhanced = clahe.apply(
        enlarged
    )

    # -----------------------------------------------------
    # Variant 3: OTSU threshold
    # -----------------------------------------------------

    _, otsu = cv2.threshold(
        enhanced,
        0,
        255,
        cv2.THRESH_BINARY +
        cv2.THRESH_OTSU
    )

    # -----------------------------------------------------
    # Variant 4: Adaptive threshold
    # -----------------------------------------------------

    blurred = cv2.GaussianBlur(
        enhanced,
        (3, 3),
        0
    )

    adaptive = cv2.adaptiveThreshold(
        blurred,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11
    )

    return {
        "gray": enlarged,
        "clahe": enhanced,
        "otsu": otsu,
        "adaptive": adaptive
    }


# =========================================================
# FIND INGREDIENT REGION
# =========================================================

def find_ingredient_region(image):

    height, width = image.shape[:2]

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    data = pytesseract.image_to_data(
        gray,
        config="--psm 11",
        output_type=pytesseract.Output.DICT
    )

    heading_y = None

    for i, word in enumerate(
        data["text"]
    ):

        cleaned = re.sub(
            r"[^A-Za-z]",
            "",
            word
        ).upper()

        if cleaned in {
            "INGREDIENTS",
            "INGREDIENT",
            "INGREDENTS",
            "INGRED"
        }:

            heading_y = int(
                data["top"][i]
            )

            break

    if heading_y is not None:

        y_start = max(
            0,
            heading_y - int(
                height * 0.02
            )
        )

        return image[
            y_start:height,
            0:width
        ]

    # Fallback
    y_start = int(
        height * 0.40
    )

    return image[
        y_start:height,
        0:width
    ]


# =========================================================
# CLEAN OCR TEXT
# =========================================================

def clean_ocr_text(text):

    if not text:
        return ""

    replacements = {
        "—": "-",
        "–": "-",
        "−": "-",
        "¦": "|"
    }

    for old, new in replacements.items():

        text = text.replace(
            old,
            new
        )

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


# =========================================================
# SCORE OCR RESULT
# =========================================================

def score_ocr_text(text):

    if not text:
        return 0

    words = text.split()

    if not words:
        return 0

    alphabetic_words = 0

    for word in words:

        letters = len(
            re.findall(
                r"[A-Za-z]",
                word
            )
        )

        if letters >= 2:
            alphabetic_words += 1

    ratio = (
        alphabetic_words /
        len(words)
    )

    # Prefer OCR containing more readable words
    score = (
        len(text) * 0.2 +
        alphabetic_words * 5 +
        ratio * 20
    )

    return score


# =========================================================
# RUN MULTIPLE OCR PASSES
# =========================================================

def run_multiple_ocr(image):

    variants = create_preprocessing_variants(
        image
    )

    results = []

    for name, processed in variants.items():

        for psm in [6, 11]:

            text = pytesseract.image_to_string(
                processed,
                config=f"--psm {psm}"
            )

            text = clean_ocr_text(
                text
            )

            score = score_ocr_text(
                text
            )

            results.append(
                {
                    "variant": name,
                    "psm": psm,
                    "text": text,
                    "score": score
                }
            )

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return results


# =========================================================
# EXTRACT INGREDIENT TEXT
# =========================================================

def extract_text(image_path):

    image = cv2.imread(
        image_path
    )

    if image is None:

        raise ValueError(
            f"Could not read image: {image_path}"
        )

    height, width = image.shape[:2]

    print(
        f"Image size: {width} x {height}"
    )

    # -----------------------------------------------------
    # FULL IMAGE OCR
    # -----------------------------------------------------

    full_results = run_multiple_ocr(
        image
    )

    best_full = full_results[0]

    print(
        "\n===== FULL IMAGE OCR ====="
    )

    print(
        best_full["text"]
    )

    print(
        f"\nBest OCR variant: "
        f"{best_full['variant']} "
        f"| PSM: {best_full['psm']}"
    )

    # -----------------------------------------------------
    # INGREDIENT REGION
    # -----------------------------------------------------

    ingredient_region = (
        find_ingredient_region(
            image
        )
    )

    cv2.imwrite(
        "debug_ingredients_original.png",
        ingredient_region
    )

    # -----------------------------------------------------
    # OCR ON INGREDIENT REGION
    # -----------------------------------------------------

    ingredient_results = (
        run_multiple_ocr(
            ingredient_region
        )
    )

    print(
        "\n===== OCR VARIANT SCORES ====="
    )

    for result in ingredient_results:

        print(
            f"{result['variant']} "
            f"| PSM {result['psm']} "
            f"| Score {result['score']:.2f}"
        )

    best_ingredient = (
        ingredient_results[0]
    )

    print(
        "\n===== INGREDIENT REGION OCR ====="
    )

    print(
        best_ingredient["text"]
    )

    # -----------------------------------------------------
    # SAVE BEST DEBUG IMAGE
    # -----------------------------------------------------

    variants = create_preprocessing_variants(
        ingredient_region
    )

    best_variant = (
        best_ingredient["variant"]
    )

    cv2.imwrite(
        "debug_ingredients.png",
        variants[best_variant]
    )

    # -----------------------------------------------------
    # REMOVE INGREDIENTS HEADING
    # -----------------------------------------------------

    ingredient_text = (
        best_ingredient["text"]
    )

    match = re.search(
        r"INGRED(?:IENTS|ENTS)?\s*:?",
        ingredient_text,
        flags=re.IGNORECASE
    )

    if match:

        ingredient_section = (
            ingredient_text[
                match.end():
            ]
        )

    else:

        ingredient_section = (
            ingredient_text
        )

    # -----------------------------------------------------
    # REMOVE PROFESSIONAL USE TEXT
    # -----------------------------------------------------

    stop_patterns = [

        r"PROFESSIONAL\s+USE",

        r"USAGE\s+PROFESSIONNEL",

        r"USO\s+PROFESSIONALE",

        r"PROFESSIONAL.*USE",

        r"PROFESSIONALE.*USE"
    ]

    for pattern in stop_patterns:

        stop = re.search(
            pattern,
            ingredient_section,
            flags=re.IGNORECASE
        )

        if stop:

            ingredient_section = (
                ingredient_section[
                    :stop.start()
                ]
            )

            break

    ingredient_section = clean_ocr_text(
        ingredient_section
    )

    print(
        "\n===== CLEAN INGREDIENT OCR ====="
    )

    print(
        ingredient_section
    )

    return ingredient_section