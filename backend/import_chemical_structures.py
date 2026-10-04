import time

from backend.database import ingredients_collection
from backend.chemical_lookup import get_smiles_from_pubchem


def import_chemical_structures():
    processed = 0
    matched = 0
    failed = 0

    for ingredient in ingredients_collection.find(
        {},
        {"_id": 0, "inci_name": 1}
    ):
        inci_name = ingredient.get("inci_name")

        if not inci_name:
            continue

        processed += 1

        result = get_smiles_from_pubchem(inci_name)

        if result and result.get("smiles"):
            ingredients_collection.update_one(
                {"inci_name": inci_name},
                {
                    "$set": {
                        "smiles": result["smiles"],
                        "isomeric_smiles": result.get("isomeric_smiles"),
                        "chemical_structure_source": "PubChem"
                    }
                }
            )

            matched += 1
            print(f"[MATCHED] {inci_name}")

        else:
            failed += 1
            print(f"[NOT FOUND] {inci_name}")

        time.sleep(0.1)

    print("\nImport complete")
    print("Processed:", processed)
    print("Matched:", matched)
    print("Not found:", failed)


if __name__ == "__main__":
    import_chemical_structures()