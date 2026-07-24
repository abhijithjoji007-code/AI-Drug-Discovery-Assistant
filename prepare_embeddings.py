import json
import pickle

from services.protein_service import generate_protein_embedding


with open(
    "data/reference_targets.json",
    encoding="utf-8"
) as file:
    targets = json.load(file)

reference_data = []

for target in targets:
    sequence = target["sequence"]
    embedding = generate_protein_embedding(sequence)

    reference_data.append({
        **target,
        "embedding": embedding
    })

with open("data/reference_embeddings.pkl", "wb") as file:
    pickle.dump(reference_data, file)

print("Reference embeddings created successfully.")