def normalize_pchembl(value):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return 0.3

    return min(max((value - 4.0) / 6.0, 0.0), 1.0)


def calculate_evidence_score(
    pchembl_value,
    protein_similarity=1.0,
    evidence_quality=0.7
):
    bioactivity_score = normalize_pchembl(pchembl_value)

    protein_similarity = min(
        max(protein_similarity, 0.0),
        1.0
    )
    evidence_quality = min(
        max(evidence_quality, 0.0),
        1.0
    )

    total = (
        bioactivity_score * 0.50
        + protein_similarity * 0.30
        + evidence_quality * 0.20
    )

    return round(total * 100, 2)


def classify_score(score):
    if score >= 75:
        return "Strong evidence"

    if score >= 50:
        return "Moderate evidence"

    if score >= 25:
        return "Limited evidence"

    return "Insufficient evidence"