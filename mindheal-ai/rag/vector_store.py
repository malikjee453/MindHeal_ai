import json
from typing import List, Dict, Tuple

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from core.config import EMBEDDING_MODEL, INDEX_DIR


INDEX_PATH = INDEX_DIR / "knowledge.faiss"
META_PATH = INDEX_DIR / "metadata.json"

_embedding_model = None


def get_embedding_model():
    """Load the embedding model once and reuse it."""
    global _embedding_model

    if _embedding_model is None:
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL)

    return _embedding_model


def load_index():
    """Load the FAISS index and metadata if they exist."""
    if not INDEX_PATH.exists() or not META_PATH.exists():
        return None, []

    index = faiss.read_index(str(INDEX_PATH))

    with open(META_PATH, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    return index, metadata


def add_documents(records: List[Dict]) -> int:
    """Embed and add document chunks to the FAISS index."""

    if not records:
        return 0

    model = get_embedding_model()

    texts = [record["text"] for record in records]

    vectors = model.encode(
        texts,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )

    vectors = np.asarray(vectors, dtype="float32")

    existing_index, metadata = load_index()

    if existing_index is None:
        index = faiss.IndexFlatIP(vectors.shape[1])
    else:
        index = existing_index

        # Protect against embedding-model dimension mismatches.
        if index.d != vectors.shape[1]:
            raise ValueError(
                f"Embedding dimension mismatch: "
                f"existing index={index.d}, new vectors={vectors.shape[1]}"
            )

    index.add(vectors)

    metadata.extend(records)

    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)

    faiss.write_index(index, str(INDEX_PATH))

    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(
            metadata,
            f,
            ensure_ascii=False,
            indent=2,
        )

    return len(records)


def search(query: str, top_k: int = 5) -> List[Tuple[Dict, float]]:
    """Search the knowledge base using semantic similarity."""

    index, metadata = load_index()

    if index is None or not metadata:
        return []

    model = get_embedding_model()

    vector = model.encode(
        [query],
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )

    vector = np.asarray(vector, dtype="float32")

    scores, ids = index.search(
        vector,
        min(top_k, len(metadata)),
    )

    results = []

    for score, idx in zip(scores[0], ids[0]):
        if idx >= 0 and idx < len(metadata):
            results.append(
                (
                    metadata[idx],
                    float(score),
                )
            )

    return results
