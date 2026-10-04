import pandas as pd
from backend.chemical_features import smiles_to_features


DATASET_PATH = "data/TDC_skin_reaction.csv"


df = pd.read_csv(DATASET_PATH)

successful = 0
failed = 0

print("Testing chemical feature extraction...\n")

for smiles in df["SMILES"]:
    features = smiles_to_features(smiles)

    if features is not None:
        successful += 1
    else:
        failed += 1

print("Total molecules:", len(df))
print("Successfully converted:", successful)
print("Failed:", failed)

print("\nExample:")
example = smiles_to_features(df["SMILES"].iloc[0])
print(example)