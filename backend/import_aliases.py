import os
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)

db = client["cosmetic_safety"]
collection = db["ingredient_aliases"]

csv_path = "data/ingredient_name_map.csv"

print("Reading ingredient name map...")

df = pd.read_csv(
    csv_path,
    sep="|",
    dtype=str
)

print("CSV loaded successfully!")
print("Rows:", len(df))
print("Columns:", len(df.columns))

print("\nColumns:")
print(df.columns.tolist())

df = df.where(pd.notnull(df), None)

records = df.to_dict("records")

print("\nImporting into MongoDB...")

if records:
    result = collection.insert_many(records)
    print("Imported:", len(result.inserted_ids), "documents")

print(
    "Total alias documents:",
    collection.count_documents({})
)

client.close()

print("\nDone!")