"""
RAG Retriever Module.

Loads pre-built vector index and metadata to perform cosine-similarity search.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

MODEL_NAME = "all-MiniLM-L6-v2"


class Retriever:
    """Vector index search retriever based on cosine similarity."""

    def __init__(self, index_dir: Path = Path("outputs/models/rag_index")):
        self.index_dir = Path(index_dir)
        self.chunks_path = self.index_dir / "chunks.json"
        self.embeddings_path = self.index_dir / "embeddings.npy"

        if not self.chunks_path.exists() or not self.embeddings_path.exists():
            raise FileNotFoundError(f"Index files missing in {self.index_dir}. Run build_index first.")

        with open(self.chunks_path, "r", encoding="utf-8") as f:
            self.chunks: List[Dict[str, Any]] = json.load(f)

        self.embeddings: np.ndarray = np.load(self.embeddings_path)

        # Normalize embedding matrix for cosine similarity via dot product
        norms = np.linalg.norm(self.embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1e-10
        self.normalized_embeddings = self.embeddings / norms

        self.model = SentenceTransformer(MODEL_NAME)

    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Performs cosine-similarity search for query across indexed chunks."""
        query_emb = self.model.encode([query], show_progress_bar=False, convert_to_numpy=True)[0]
        q_norm = np.linalg.norm(query_emb)
        if q_norm > 0:
            query_emb = query_emb / q_norm

        scores = np.dot(self.normalized_embeddings, query_emb)
        top_k_indices = np.argsort(scores)[::-1][:k]

        results = []
        for idx in top_k_indices:
            chunk = self.chunks[idx].copy()
            chunk["score"] = float(scores[idx])
            results.append(chunk)

        return results
