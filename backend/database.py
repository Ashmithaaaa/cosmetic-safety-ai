import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)

db = client["cosmetic_safety"]

ingredients_collection = db["ingredients"]

print("Connected to MongoDB!")
print("Database:", db.name)
print("Ingredient documents:", ingredients_collection.count_documents({}))