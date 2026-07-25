from flask import Flask, render_template, request
import requests

from services.protein_service import (
    clean_sequence,
    validate_sequence,
    generate_protein_embedding,
    find_similar_targets
)
from services.pubchem_service import search_compound
from services.chembl_service import (
    search_chembl_molecule,
    get_molecule_activities,
    get_target_activities,
    filter_activities,
    deduplicate_activities
)
from services.scoring_service import (
    calculate_evidence_score,
    classify_score
)
from services.summary_service import (
    generate_drug_summary,
    generate_protein_summary
)
from services.visualization_service import (
    create_interaction_chart,
    create_structure_image,
    calculate_lipinski_summary
)


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/health")
def health():
    return {"status": "healthy"}, 200

@app.route("/analyze", methods=["POST"])
def analyze():
    analysis_type = request.form.get("analysis_type")

    try:
        if analysis_type == "protein":
            return analyze_protein()

        if analysis_type == "drug":
            return analyze_drug()

        return render_template(
            "results.html",
            error="Please select a valid analysis type."
        )

    except requests.Timeout:
        return render_template(
            "results.html",
            error="The biomedical database request timed out."
        )

    except requests.RequestException:
        return render_template(
            "results.html",
            error="A biomedical database could not be reached."
        )

    except FileNotFoundError:
        return render_template(
            "results.html",
            error=(
                "Reference embeddings were not found. Run "
                "python prepare_embeddings.py first."
            )
        )

    except Exception as error:
        app.logger.exception("Analysis failed")

        return render_template(
            "results.html",
            error=(
                "The analysis could not be completed. "
                "Please try again after a few moments."
        )
    ), 500



def analyze_protein():
    raw_sequence = request.form.get("protein_sequence", "")
    sequence = clean_sequence(raw_sequence)

    is_valid, validation_message = validate_sequence(sequence)

    if not is_valid:
        return render_template(
            "results.html",
            error=validation_message
        )

    embedding = generate_protein_embedding(sequence)
    similar_targets = find_similar_targets(embedding, top_n=5)

    candidate_interactions = []

    if similar_targets:
        best_target = similar_targets[0]

        activities = get_target_activities(
            best_target["chembl_target_id"],
            limit=100
        )

        filtered = filter_activities(activities)
        filtered = deduplicate_activities(filtered)

        for interaction in filtered:
            score = calculate_evidence_score(
                interaction.get("pchembl_value"),
                protein_similarity=best_target["similarity"],
                evidence_quality=0.8
            )

            interaction["evidence_score"] = score
            interaction["evidence_label"] = classify_score(score)
            candidate_interactions.append(interaction)

        candidate_interactions.sort(
            key=lambda item: item["evidence_score"],
            reverse=True
        )

    summary = generate_protein_summary(
        len(sequence),
        similar_targets
    )

    chart_html = create_interaction_chart(
        candidate_interactions[:10]
    )

    return render_template(
        "results.html",
        mode="protein",
        sequence_length=len(sequence),
        similar_targets=similar_targets,
        interactions=candidate_interactions[:10],
        summary=summary,
        chart_html=chart_html
    )


def analyze_drug():
    compound_name = request.form.get("drug_name", "").strip()

    if not compound_name:
        return render_template(
            "results.html",
            error="Please enter a compound name."
        )

    pubchem_data = search_compound(compound_name)

    if not pubchem_data:
        return render_template(
            "results.html",
            error="The compound was not found in PubChem."
        )

    chembl_molecule = search_chembl_molecule(compound_name)
    interactions = []

    if chembl_molecule:
        activities = get_molecule_activities(
            chembl_molecule["chembl_id"],
            limit=100
        )

        interactions = filter_activities(activities)
        interactions = deduplicate_activities(interactions)

        for interaction in interactions:
            score = calculate_evidence_score(
                interaction.get("pchembl_value"),
                protein_similarity=1.0,
                evidence_quality=0.9
            )

            interaction["evidence_score"] = score
            interaction["evidence_label"] = classify_score(score)

        interactions.sort(
            key=lambda item: item["evidence_score"],
            reverse=True
        )

    summary = generate_drug_summary(
        pubchem_data,
        interactions
    )

    chart_html = create_interaction_chart(interactions[:10])

    smiles = (
        pubchem_data.get("CanonicalSMILES")
        or pubchem_data.get("IsomericSMILES")
    )

    structure_image = create_structure_image(
        smiles,
        pubchem_data["cid"]
    )

    lipinski = calculate_lipinski_summary(pubchem_data)

    return render_template(
        "results.html",
        mode="drug",
        compound=pubchem_data,
        chembl_molecule=chembl_molecule,
        interactions=interactions[:10],
        summary=summary,
        chart_html=chart_html,
        structure_image=structure_image,
        lipinski=lipinski
    )

@app.errorhandler(404)
def page_not_found(error):
    return render_template(
        "results.html",
        error="The requested page could not be found."
    ), 404


@app.errorhandler(413)
def request_too_large(error):
    return render_template(
        "results.html",
        error="The submitted input is too large."
    ), 413


@app.errorhandler(500)
def internal_server_error(error):
    return render_template(
        "results.html",
        error="The server encountered an unexpected error."
    ), 500

if __name__ == "__main__":
    app.run(debug=False)