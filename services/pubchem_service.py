import requests
from urllib.parse import quote


PUBCHEM_BASE_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"


def get_pubchem_cid(compound_name: str):
    encoded_name = quote(compound_name.strip())

    url = (
        f"{PUBCHEM_BASE_URL}/compound/name/"
        f"{encoded_name}/cids/JSON"
    )

    response = requests.get(url, timeout=20)
    response.raise_for_status()

    data = response.json()
    cids = data.get("IdentifierList", {}).get("CID", [])

    return cids[0] if cids else None


def get_compound_properties(cid: int):
    property_names = ",".join([
        "MolecularFormula",
        "MolecularWeight",
        "CanonicalSMILES",
        "IsomericSMILES",
        "XLogP",
        "TPSA",
        "HBondDonorCount",
        "HBondAcceptorCount"
    ])

    url = (
        f"{PUBCHEM_BASE_URL}/compound/cid/{cid}/"
        f"property/{property_names}/JSON"
    )

    response = requests.get(url, timeout=20)
    response.raise_for_status()

    data = response.json()
    properties = data.get(
        "PropertyTable", {}
    ).get("Properties", [])

    return properties[0] if properties else None


def search_compound(compound_name: str):
    cid = get_pubchem_cid(compound_name)

    if cid is None:
        return None

    properties = get_compound_properties(cid)

    return {
        "name": compound_name,
        "cid": cid,
        **(properties or {})
    }