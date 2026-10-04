import requests


PUBCHEM_URL = (
    "https://pubchem.ncbi.nlm.nih.gov/rest/pug/"
    "compound/name/{name}/property/CanonicalSMILES,IsomericSMILES/JSON"
)


def get_smiles_from_pubchem(ingredient_name):
    url = PUBCHEM_URL.format(
        name=requests.utils.quote(ingredient_name)
    )

    try:
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return None

        data = response.json()
        properties = data["PropertyTable"]["Properties"][0]

        return {
            "smiles": properties.get("ConnectivitySMILES")
            or properties.get("CanonicalSMILES"),
            "isomeric_smiles": properties.get("SMILES")
            or properties.get("IsomericSMILES")
        }

    except Exception:
        return None