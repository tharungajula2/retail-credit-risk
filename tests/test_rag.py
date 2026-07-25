"""
Unit tests for local RAG indexer and retriever modules.
"""

from pathlib import Path
import pytest
from creditrisk.ai.rag_index import build_index, chunk_documents
from creditrisk.ai.retriever import Retriever


def test_chunk_documents_preserves_metadata_and_overlap():
    records = [{
        "source": "bcbs128.pdf",
        "page": 12,
        "text": "A" * 1200
    }]

    chunks = chunk_documents(records, chunk_size=800, overlap=150)
    assert len(chunks) == 2
    assert chunks[0]["source"] == "bcbs128.pdf"
    assert chunks[0]["page"] == 12
    assert chunks[1]["source"] == "bcbs128.pdf"
    assert chunks[1]["page"] == 12
    assert "chunk_id" in chunks[0]


def test_retriever_search():
    kb_dir = Path("knowledge_base")
    if not kb_dir.exists():
        pytest.skip("knowledge_base directory missing")

    # Build index
    build_index(kb_dir=kb_dir)

    retriever = Retriever()
    results = retriever.search("risk weight", k=5)

    assert len(results) == 5
    # Check sorted by score descending
    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True)

    # Check top result for risk weight query comes from Basel regulatory docs (e.g., d350 or bcbs128)
    top_source = results[0]["source"].lower()
    assert ("bcbs" in top_source or "d350" in top_source or "d424" in top_source)
