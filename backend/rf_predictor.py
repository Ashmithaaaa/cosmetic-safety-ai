import joblib
import pandas as pd

from backend.chemical_features import smiles_to_features


MODEL_PATH = "data/random_forest_model.pkl"


model_data = joblib.load(MODEL_PATH)

model = model_data["model"]
feature_names = model_data["features"]


def predict_skin_sensitization(smiles):
    if not smiles:
        return {
            "available": False,
            "reason": "Chemical structure not available"
        }

    features = smiles_to_features(smiles)

    if features is None:
        return {
            "available": False,
            "reason": "Invalid SMILES"
        }

    X = pd.DataFrame([features])
    X = X[feature_names]

    prediction = int(model.predict(X)[0])
    probabilities = model.predict_proba(X)[0]

    return {
        "available": True,
        "prediction": prediction,
        "probability_class_0": float(probabilities[0]),
        "probability_class_1": float(probabilities[1])
    }