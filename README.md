# AI Drug Discovery Assistant

## Overview

An AI-assisted biomedical exploration platform that combines ESM-2
protein embeddings with PubChem and ChEMBL data to identify similar
drug targets, retrieve reported compound-target activities, rank
interaction evidence, and generate interpretable visual summaries.

## Live Demo

The deployed application is available here:

**Live website:** https://ai-drug-discovery-assistant-34ai.onrender.com

## Key features

- Protein-sequence and compound-name input modes
- ESM-2 protein embeddings
- Cosine-similarity target matching
- PubChem compound properties
- ChEMBL bioactivity evidence
- Explainable interaction-evidence scoring
- Plotly interaction charts
- RDKit molecular structure images
- Evidence provenance and research-use disclaimer

## Installation

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Add real UniProt sequences to `data/reference_targets.json`, then run:

```bash
python prepare_embeddings.py
python app.py
```

Open `http://127.0.0.1:5000` in a browser.

## Limitations

The similarity scores and interaction rankings are computational and
retrieval-based indicators. They are not validated predictions of
therapeutic effectiveness, toxicity, clinical safety, or medical
suitability. Results require expert interpretation and experimental
validation.
