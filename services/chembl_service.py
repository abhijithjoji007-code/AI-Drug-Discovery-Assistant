import requests


CHEMBL_BASE_URL = "https://www.ebi.ac.uk/chembl/api/data"
SUPPORTED_ACTIVITY_TYPES = {"IC50", "Ki", "Kd", "EC50"}


def search_chembl_molecule(compound_name: str):
    url = f"{CHEMBL_BASE_URL}/molecule/search.json"

    response = requests.get(
        url,
        params={"q": compound_name},
        timeout=20
    )
    response.raise_for_status()

    data = response.json()
    molecules = data.get("molecules", [])

    if not molecules:
        return None

    molecule = molecules[0]

    return {
        "chembl_id": molecule.get("molecule_chembl_id"),
        "preferred_name": molecule.get("pref_name"),
        "max_phase": molecule.get("max_phase"),
        "molecule_type": molecule.get("molecule_type")
    }


def get_molecule_activities(molecule_chembl_id: str, limit=100):
    url = f"{CHEMBL_BASE_URL}/activity.json"

    params = {
        "molecule_chembl_id": molecule_chembl_id,
        "limit": limit
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()
    return data.get("activities", [])


def get_target_activities(target_chembl_id: str, limit=100):
    url = f"{CHEMBL_BASE_URL}/activity.json"

    params = {
        "target_chembl_id": target_chembl_id,
        "limit": limit
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()
    return data.get("activities", [])


def filter_activities(activities):
    filtered = []

    for activity in activities:
        activity_type = activity.get("standard_type")
        value = activity.get("standard_value")
        units = activity.get("standard_units")

        if activity_type not in SUPPORTED_ACTIVITY_TYPES:
            continue

        try:
            numeric_value = float(value)
        except (TypeError, ValueError):
            continue

        if numeric_value <= 0:
            continue

        filtered.append({
            "molecule_chembl_id": activity.get(
                "molecule_chembl_id"
            ),
            "target_chembl_id": activity.get(
                "target_chembl_id"
            ),
            "target_name": activity.get("target_pref_name"),
            "activity_type": activity_type,
            "activity_value": numeric_value,
            "activity_units": units,
            "pchembl_value": activity.get("pchembl_value"),
            "assay_description": activity.get(
                "assay_description"
            ),
            "document_chembl_id": activity.get(
                "document_chembl_id"
            )
        })

    return filtered


def deduplicate_activities(activities):
    unique = {}

    for activity in activities:
        key = (
            activity.get("molecule_chembl_id"),
            activity.get("target_chembl_id"),
            activity.get("activity_type"),
            activity.get("activity_value"),
            activity.get("activity_units")
        )

        if key not in unique:
            unique[key] = activity

    return list(unique.values())