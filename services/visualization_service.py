from pathlib import Path

import plotly.express as px
try:
    from rdkit import Chem
    from rdkit.Chem import Draw

    RDKIT_AVAILABLE = True
except ImportError:
    Chem = None
    Draw = None
    RDKIT_AVAILABLE = False


def create_interaction_chart(interactions):
    if not interactions:
        return None

    target_names = [
        item.get("target_name")
        or item.get("molecule_chembl_id")
        or "Unknown"
        for item in interactions
    ]

    scores = [
        item.get("evidence_score", 0)
        for item in interactions
    ]

    figure = px.bar(
        x=scores,
        y=target_names,
        orientation="h",
        labels={
            "x": "Interaction evidence score",
            "y": "Target or compound"
        },
        title="Top interaction evidence"
    )

    figure.update_layout(
        yaxis={"categoryorder": "total ascending"},
        xaxis={"range": [0, 100]}
    )

    return figure.to_html(
        full_html=False,
        include_plotlyjs="cdn"
    )


def create_structure_image(smiles: str, cid: int):
    if not RDKIT_AVAILABLE:
        return None

    if not smiles:
        return None

    molecule = Chem.MolFromSmiles(smiles)

    if molecule is None:
        return None

    output_directory = Path("static/generated")
    output_directory.mkdir(parents=True, exist_ok=True)

    filename = f"compound_{cid}.png"
    output_path = output_directory / filename

    Draw.MolToFile(
        molecule,
        str(output_path),
        size=(500, 350)
    )

    return f"generated/{filename}"


def calculate_lipinski_summary(properties):
    def safe_float(value, default=9999):
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    def safe_int(value, default=9999):
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    checks = {
        "Molecular weight ≤ 500":
            safe_float(properties.get("MolecularWeight")) <= 500,
        "XLogP ≤ 5":
            safe_float(properties.get("XLogP")) <= 5,
        "Hydrogen-bond donors ≤ 5":
            safe_int(properties.get("HBondDonorCount")) <= 5,
        "Hydrogen-bond acceptors ≤ 10":
            safe_int(properties.get("HBondAcceptorCount")) <= 10
    }

    passed = sum(checks.values())

    return {
        "checks": checks,
        "passed": passed,
        "total": len(checks)
    }