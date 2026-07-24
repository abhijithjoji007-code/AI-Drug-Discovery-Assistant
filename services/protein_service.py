import pickle

import torch
from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoModel, AutoTokenizer


VALID_AMINO_ACIDS = set("ACDEFGHIKLMNPQRSTVWY")
MODEL_NAME = "facebook/esm2_t6_8M_UR50D"


tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME)
model.eval()


def clean_sequence(sequence: str) -> str:
    lines = sequence.strip().splitlines()

    sequence_lines = [
        line.strip()
        for line in lines
        if line.strip() and not line.startswith(">")
    ]

    cleaned = "".join(sequence_lines).upper()
    cleaned = "".join(
        character for character in cleaned if character.isalpha()
    )

    return cleaned


def validate_sequence(sequence: str) -> tuple[bool, str]:
    if not sequence:
        return False, "The protein sequence is empty."

    invalid_characters = set(sequence) - VALID_AMINO_ACIDS

    if invalid_characters:
        invalid = ", ".join(sorted(invalid_characters))
        return False, f"Invalid amino-acid characters: {invalid}"

    if len(sequence) < 20:
        return False, "The sequence is too short for meaningful analysis."

    if len(sequence) > 1022:
        return False, (
            "The sequence is longer than 1022 amino acids. "
            "Use a shorter sequence for this first version."
        )

    return True, ""


def generate_protein_embedding(sequence: str):
    inputs = tokenizer(
        sequence,
        return_tensors="pt",
        truncation=True,
        max_length=1024
    )

    with torch.no_grad():
        outputs = model(**inputs)

    residue_embeddings = outputs.last_hidden_state
    attention_mask = inputs["attention_mask"].unsqueeze(-1)
    masked_embeddings = residue_embeddings * attention_mask

    summed = masked_embeddings.sum(dim=1)
    counts = attention_mask.sum(dim=1).clamp(min=1)
    protein_embedding = summed / counts

    return protein_embedding.squeeze().cpu().numpy()


def find_similar_targets(query_embedding, top_n=5):
    with open("data/reference_embeddings.pkl", "rb") as file:
        reference_targets = pickle.load(file)

    results = []

    for target in reference_targets:
        reference_embedding = target["embedding"]

        similarity = cosine_similarity(
            query_embedding.reshape(1, -1),
            reference_embedding.reshape(1, -1)
        )[0][0]

        result = {
            "name": target["name"],
            "gene": target["gene"],
            "uniprot_id": target["uniprot_id"],
            "chembl_target_id": target["chembl_target_id"],
            "target_type": target["target_type"],
            "similarity": float(similarity)
        }

        results.append(result)

    results.sort(
        key=lambda item: item["similarity"],
        reverse=True
    )

    return results[:top_n]