import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

from backend.chemical_features import smiles_to_features


DATASET_PATH = "data/TDC_skin_reaction.csv"


# Load dataset
df = pd.read_csv(DATASET_PATH)

# Convert SMILES into chemical features
feature_rows = []

for smiles in df["SMILES"]:
    features = smiles_to_features(smiles)
    feature_rows.append(features)

features_df = pd.DataFrame(feature_rows)

# Target
y = df["Y"]

# Input features
X = features_df

print("Feature matrix shape:", X.shape)
print("Target shape:", y.shape)

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))

# Random Forest
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    class_weight="balanced"
)

# Train
model.fit(X_train, y_train)

# Predict
y_pred = model.predict(X_test)

# Evaluation
accuracy = accuracy_score(y_test, y_pred)

print("\nRandom Forest Results")
print("---------------------")
print("Accuracy:", accuracy)

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

print("\nFeature Importance:")
for name, importance in zip(X.columns, model.feature_importances_):
    print(f"{name}: {importance:.4f}")
    import joblib

joblib.dump(
    {
        "model": model,
        "features": X.columns.tolist()
    },
    "data/random_forest_model.pkl"
)

print("\nModel saved to: data/random_forest_model.pkl")