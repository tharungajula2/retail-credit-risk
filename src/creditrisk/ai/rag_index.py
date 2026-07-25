"""
RAG Indexer Module.

Parses regulatory PDFs, chunks content page-by-page, and embeds text chunks
locally using sentence-transformers (all-MiniLM-L6-v2) to build a vector search index.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

MODEL_NAME = "all-MiniLM-L6-v2"


def load_documents(kb_dir: Path) -> List[Dict[str, Any]]:
    """Loads PDF documents from kb_dir page by page.

    Skips pages with under 50 characters of text.
    """
    records = []
    pdf_files = sorted(list(kb_dir.glob("*.pdf")))
    logger.info(f"Found {len(pdf_files)} PDF documents in {kb_dir}")

    for pdf_path in pdf_files:
        try:
            reader = PdfReader(pdf_path)
            for page_idx, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                cleaned_text = text.strip()
                if len(cleaned_text) >= 50:
                    records.append({
                        "source": pdf_path.name,
                        "page": page_idx + 1,
                        "text": cleaned_text
                    })
        except Exception as exc:
            logger.error(f"Error reading PDF {pdf_path.name}: {exc}")

    logger.info(f"Loaded {len(records)} valid pages from {len(pdf_files)} PDFs.")
    return records


def chunk_documents(
    records: List[Dict[str, Any]],
    chunk_size: int = 800,
    overlap: int = 150
) -> List[Dict[str, Any]]:
    """Splits each page record into overlapping text chunks."""
    chunks = []
    chunk_counter = 0

    for rec in records:
        text = rec["text"]
        source = rec["source"]
        page = rec["page"]

        if len(text) <= chunk_size:
            chunk_counter += 1
            chunks.append({
                "chunk_id": f"chunk_{chunk_counter:05d}",
                "source": source,
                "page": page,
                "text": text
            })
        else:
            start = 0
            while start < len(text):
                end = min(start + chunk_size, len(text))
                chunk_text = text[start:end]

                chunk_counter += 1
                chunks.append({
                    "chunk_id": f"chunk_{chunk_counter:05d}",
                    "source": source,
                    "page": page,
                    "text": chunk_text
                })

                if end == len(text):
                    break
                start += (chunk_size - overlap)

    logger.info(f"Created {len(chunks)} chunks from {len(records)} page records.")
    return chunks


def build_embeddings(chunks: List[Dict[str, Any]]) -> np.ndarray:
    """Embeds all chunks using sentence-transformers model all-MiniLM-L6-v2."""
    texts = [c["text"] for c in chunks]
    logger.info(f"Loading embedding model '{MODEL_NAME}'...")
    model = SentenceTransformer(MODEL_NAME)
    logger.info(f"Embedding {len(texts)} text passages...")
    embeddings = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    return embeddings


def build_index(
    kb_dir: Path = Path("knowledge_base"),
    output_dir: Path = Path("outputs/models/rag_index")
) -> Dict[str, Any]:
    """Runs the full indexing pipeline and saves chunks and embedding matrix."""
    records = load_documents(kb_dir)
    chunks = chunk_documents(records, chunk_size=800, overlap=150)
    embeddings = build_embeddings(chunks)

    output_dir.mkdir(parents=True, exist_ok=True)

    chunks_path = output_dir / "chunks.json"
    embeddings_path = output_dir / "embeddings.npy"

    with open(chunks_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2)

    np.save(embeddings_path, embeddings)

    # Unique source documents count
    unique_docs = len(set(r["source"] for r in records))
    n_pages = len(records)
    n_chunks = len(chunks)
    emb_dim = embeddings.shape[1] if embeddings.ndim == 2 else 0

    stats = {
        "n_documents": unique_docs,
        "n_pages": n_pages,
        "n_chunks": n_chunks,
        "embedding_dimension": emb_dim
    }

    logger.info(
        f"RAG Index built successfully: {stats['n_documents']} docs, "
        f"{stats['n_pages']} pages, {stats['n_chunks']} chunks, dim={stats['embedding_dimension']}."
    )
    return stats


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    stats = build_index()
    print("Indexing Complete!")
    print(json.dumps(stats, indent=2))
