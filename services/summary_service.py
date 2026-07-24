def generate_drug_summary(compound, interactions):
    name = compound.get("name", "The compound")
    formula = compound.get("MolecularFormula", "not available")
    weight = compound.get("MolecularWeight", "not available")

    if not interactions:
        return (
            f"{name} was found in PubChem with molecular formula "
            f"{formula} and molecular weight {weight}. "
            "No suitable target activity records were found in the "
            "retrieved ChEMBL results."
        )

    best = interactions[0]

    return (
        f"{name} was found in PubChem with molecular formula {formula} "
        f"and molecular weight {weight}. The strongest retrieved "
        f"interaction evidence was associated with "
        f"{best.get('target_name', 'an unspecified target')}. "
        f"The reported measurement type was "
        f"{best.get('activity_type', 'not available')}, with an "
        f"interaction evidence score of "
        f"{best.get('evidence_score', 0)} out of 100. "
        "This score is intended for research prioritization and does "
        "not establish clinical effectiveness or safety."
    )


def generate_protein_summary(sequence_length, similar_targets):
    if not similar_targets:
        return (
            f"The uploaded protein contains {sequence_length} amino acids. "
            "No sufficiently similar target was identified in the current "
            "reference database."
        )

    best = similar_targets[0]

    return (
        f"The uploaded protein contains {sequence_length} amino acids. "
        f"The closest reference target was {best['name']} "
        f"({best['gene']}), with an embedding similarity of "
        f"{best['similarity']:.3f}. This indicates similarity to the "
        "reference representation, but it does not confirm identical "
        "function or drug binding."
    )