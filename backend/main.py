import os
import json
import uuid
import shutil

from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

from backend.ocr import extract_text
from backend.ingredient_parser import extract_ingredient_candidates
from backend.normalizer import normalize_ingredient
from backend.analyzer import analyze_ingredient
from backend.full_analysis import analyze_image
from backend.profile import UserProfile
from backend.routine import Routine, analyze_routine
from backend.interaction_graph import analyze_interactions
from backend.compare import CompareRequest, compare_products

# =========================================================
# FastAPI Application
# =========================================================

app = FastAPI(
    title="Cosmetic Safety AI",
    description="AI-powered cosmetic ingredient safety analysis API",
    version="1.0.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# Root
# =========================================================

@app.get("/")
def root():

    return {
        "message": "Cosmetic Safety AI API is running"
    }


# =========================================================
# Profile
# =========================================================

@app.post("/api/profile")
async def create_profile(profile: UserProfile):

    return {
        "success": True,
        "profile": profile.model_dump()
    }


# =========================================================
# Routine
# =========================================================

@app.post("/api/routine/analyze")
async def analyze_routine_api(
    routine: Routine
):

    try:

        result = analyze_routine(
            routine
        )

        return {
            "success": True,
            "routine": result
        }

    except Exception as error:

        return {
            "success": False,
            "error": "Routine analysis failed",
            "details": str(error)
        }
    # =========================================================
# Compare Products
# =========================================================

@app.post("/api/compare")
async def compare_products_api(
    request: CompareRequest
):

    try:

        result = compare_products(
            request.product1,
            request.product2,
            request.profile
        )

        return {
            "success": True,
            "comparison": result
        }

    except Exception as error:

        return {
            "success": False,
            "error": "Product comparison failed",
            "details": str(error)
        }


# =========================================================
# OCR
# =========================================================

@app.post("/api/ocr")
async def process_ocr(
    file: UploadFile = File(...)
):

    extension = (
        os.path.splitext(file.filename or "")[1]
        or ".jpg"
    )

    temp_path = f"temp_{uuid.uuid4().hex}{extension}"

    try:

        with open(temp_path, "wb") as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

        text = extract_text(temp_path)

        return {
            "filename": file.filename,
            "ocr_text": text
        }

    finally:

        if os.path.exists(temp_path):
            os.remove(temp_path)


# =========================================================
# Extract Ingredients
# =========================================================

@app.post("/api/ingredients/extract")
async def extract_ingredients_api(
    file: UploadFile = File(...)
):

    extension = (
        os.path.splitext(file.filename or "")[1]
        or ".jpg"
    )

    temp_path = f"temp_{uuid.uuid4().hex}{extension}"

    try:

        with open(temp_path, "wb") as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

        ocr_text = extract_text(temp_path)

        ingredients = extract_ingredient_candidates(
            ocr_text
        )

        return {
            "filename": file.filename,
            "ocr_text": ocr_text,
            "ingredients": ingredients
        }

    finally:

        if os.path.exists(temp_path):
            os.remove(temp_path)


# =========================================================
# Normalize Ingredient
# =========================================================

@app.post("/api/ingredients/normalize")
async def normalize_ingredient_api(
    ingredient: str
):

    result = normalize_ingredient(
        ingredient
    )

    return result


# =========================================================
# Get Ingredient Details
# =========================================================

@app.get("/api/ingredients/{name}")
async def get_ingredient_details(
    name: str
):

    return analyze_ingredient(name)


# =========================================================
# Analyze Single Product
# =========================================================

@app.post("/api/analyze")
async def analyze_product(
    file: UploadFile = File(...),
    profile: str = Form("{}")
):

    extension = (
        os.path.splitext(file.filename or "")[1]
        or ".jpg"
    )

    temp_path = f"temp_{uuid.uuid4().hex}{extension}"

    try:

        # ---------------------------------------------
        # Parse user profile
        # ---------------------------------------------

        try:

            profile_data = json.loads(
                profile
            )

            user_profile = UserProfile(
                **profile_data
            )

        except Exception as error:

            return {
                "error": "Invalid user profile",
                "details": str(error)
            }


        # ---------------------------------------------
        # Save uploaded image
        # ---------------------------------------------

        with open(
            temp_path,
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )


        # ---------------------------------------------
        # Run complete analysis
        # ---------------------------------------------

        result = analyze_image(
            temp_path,
            user_profile
        )

        result["filename"] = file.filename

        return result

    finally:

        if os.path.exists(temp_path):
            os.remove(temp_path)


# =========================================================
# Analyze Multiple Products
# =========================================================

#
# We use separate UploadFile fields instead of
# List[UploadFile] so Swagger displays proper
# file-upload controls.
#
# Product 1 = required
# Product 2 = required
# Product 3 = optional
#
# Also detects ingredients that appear in
# more than one product.
#
# =========================================================

@app.post("/api/analyze/multiple")
async def analyze_multiple_products(
    file1: UploadFile = File(...),
    file2: UploadFile = File(...),
    file3: Optional[UploadFile] = File(None),
    profile: str = Form("{}")
):

    temp_paths = []

    try:

        # ---------------------------------------------
        # Parse user profile
        # ---------------------------------------------

        try:

            profile_data = json.loads(
                profile
            )

            user_profile = UserProfile(
                **profile_data
            )

        except Exception as error:

            return {
                "error": "Invalid user profile",
                "details": str(error)
            }


        # ---------------------------------------------
        # Collect uploaded products
        # ---------------------------------------------

        uploaded_files = [
            file1,
            file2
        ]

        if file3 is not None:

            uploaded_files.append(
                file3
            )


        # ---------------------------------------------
        # Analyze each product separately
        # ---------------------------------------------

        products = []

        for file in uploaded_files:

            extension = (
                os.path.splitext(
                    file.filename or ""
                )[1]
                or ".jpg"
            )

            temp_path = (
                f"temp_{uuid.uuid4().hex}{extension}"
            )

            temp_paths.append(
                temp_path
            )


            # -----------------------------------------
            # Save uploaded image
            # -----------------------------------------

            with open(
                temp_path,
                "wb"
            ) as buffer:

                shutil.copyfileobj(
                    file.file,
                    buffer
                )


            # -----------------------------------------
            # Run existing complete pipeline
            # -----------------------------------------

            result = analyze_image(
                temp_path,
                user_profile
            )

            products.append({
                "filename": file.filename,
                "analysis": result
            })


        # ---------------------------------------------
        # Build ingredient -> product mapping
        # ---------------------------------------------

        ingredient_products = {}

        for product in products:

            filename = product["filename"]

            ingredients = (
                product["analysis"]
                .get("ingredients", [])
            )


            # Prevent the same ingredient from being
            # counted twice inside one product

            product_ingredients = set()

            for ingredient in ingredients:

                canonical_name = (
                    ingredient.get(
                        "canonical_name"
                    )
                )

                if canonical_name:

                    canonical_name = (
                        canonical_name.strip().upper()
                    )

                    product_ingredients.add(
                        canonical_name
                    )


            # Store which product contains each ingredient

            for ingredient_name in product_ingredients:

                if (
                    ingredient_name
                    not in ingredient_products
                ):

                    ingredient_products[
                        ingredient_name
                    ] = []


                ingredient_products[
                    ingredient_name
                ].append(
                    filename
                )


        # ---------------------------------------------
        # Detect duplicate ingredients
        # ---------------------------------------------

        duplicate_ingredients = []

        for (
            ingredient_name,
            product_list
        ) in ingredient_products.items():

            # Duplicate means the ingredient occurs
            # in at least two different products.

            if len(product_list) > 1:

                duplicate_ingredients.append({

                    "ingredient":
                        ingredient_name,

                    "product_count":
                        len(product_list),

                    "products":
                        product_list,

                    "message": (
                        f"{ingredient_name} appears in "
                        f"{len(product_list)} products."
                    )
                })


        # ---------------------------------------------
        # Combine recognized ingredients
        # ---------------------------------------------

        combined_ingredients = list(
            ingredient_products.keys()
        )


        # ---------------------------------------------
        # Analyze interactions between products
        # ---------------------------------------------

        interaction_analysis = (
            analyze_interactions(
                combined_ingredients
            )
        )


        # ---------------------------------------------
        # Return final multi-product result
        # ---------------------------------------------

        return {

            "product_count":
                len(products),

            "products":
                products,

            "combined_ingredients":
                combined_ingredients,

            "duplicate_ingredients":
                duplicate_ingredients,

            "duplicate_count":
                len(duplicate_ingredients),

            "combined_interactions":
                interaction_analysis,

            "profile":
                user_profile.model_dump()
        }


    except Exception as error:

        return {

            "error":
                "Multi-product analysis failed",

            "details":
                str(error)
        }


    finally:

        # ---------------------------------------------
        # Delete temporary image files
        # ---------------------------------------------

        for path in temp_paths:

            if os.path.exists(path):

                os.remove(path)