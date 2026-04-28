# ai/context7/chroma_pipeline.py
"""
Chroma-based vector RAG pipeline.
Replaces naive keyword search in rag_pipeline.py with semantic similarity.

Falls back to rag_pipeline.fetch_top_k when chromadb is not installed
or the collection is empty, ensuring zero-downtime migration.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import List, Dict, Any, Optional

_CHROMA_AVAILABLE = False
try:
    import chromadb
    from chromadb.config import Settings
    _CHROMA_AVAILABLE = True
except ImportError:
    pass

CHROMA_DIR = Path("ai/context7/.chroma_db")
COLLECTION_NAME = "repo_docs"

# Chunk size for splitting large documents
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100


def _get_or_create_collection(persist_dir: Path = CHROMA_DIR):
    """Return Chroma collection, creating it if it does not exist."""
    client = chromadb.PersistentClient(
        path=str(persist_dir),
        settings=Settings(anonymized_telemetry=False),
    )
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def _chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """Split text into overlapping chunks."""
    if len(text) <= chunk_size:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


def build_chroma_index(
    docs: List[Dict[str, Any]],
    persist_dir: Path = CHROMA_DIR,
) -> int:
    """
    Build or refresh the Chroma collection from a list of documents.

    Args:
        docs: List of dicts with 'path' and 'content' keys
        persist_dir: Directory for Chroma persistence

    Returns:
        Number of chunks indexed
    """
    if not _CHROMA_AVAILABLE:
        print("⚠️ chromadb not installed — skipping vector index build")
        return 0

    collection = _get_or_create_collection(persist_dir)

    # Clear existing entries for a clean rebuild
    try:
        existing = collection.get()
        if existing["ids"]:
            collection.delete(ids=existing["ids"])
    except Exception:
        pass

    ids: List[str] = []
    documents: List[str] = []
    metadatas: List[Dict[str, str]] = []

    for doc in docs:
        path = doc.get("path", "")
        content = doc.get("content", "")
        if not content:
            continue

        chunks = _chunk_text(content)
        for i, chunk in enumerate(chunks):
            chunk_id = f"{path}::chunk_{i}"
            ids.append(chunk_id)
            documents.append(chunk)
            metadatas.append({"path": path, "chunk_index": str(i)})

    if not ids:
        return 0

    # Chroma has a batch limit — insert in batches of 500
    batch_size = 500
    for start in range(0, len(ids), batch_size):
        end = start + batch_size
        collection.add(
            ids=ids[start:end],
            documents=documents[start:end],
            metadatas=metadatas[start:end],
        )

    print(f"✅ Chroma index built: {len(ids)} chunks from {len(docs)} docs")
    return len(ids)


def fetch_top_k_chroma(
    query: str,
    k: int = 5,
    persist_dir: Path = CHROMA_DIR,
) -> List[Dict[str, Any]]:
    """
    Retrieve top-k documents from Chroma using semantic similarity.

    Returns dicts with 'path' and 'content' keys, same shape as
    rag_pipeline.fetch_top_k for drop-in compatibility.

    Falls back to [] if Chroma is unavailable or collection is empty.
    """
    if not _CHROMA_AVAILABLE:
        return []

    if not persist_dir.exists():
        return []

    try:
        collection = _get_or_create_collection(persist_dir)
        count = collection.count()
        if count == 0:
            return []

        results = collection.query(
            query_texts=[query],
            n_results=min(k, count),
            include=["documents", "metadatas", "distances"],
        )

        docs: List[Dict[str, Any]] = []
        seen_paths: set = set()

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for doc_text, meta, dist in zip(documents, metadatas, distances):
            path = meta.get("path", "")
            # De-duplicate: return one result per file
            if path in seen_paths:
                continue
            seen_paths.add(path)
            docs.append({
                "path": path,
                "content": doc_text,
                "score": round(1.0 - float(dist), 4),
            })

        return docs

    except Exception as e:
        print(f"⚠️ Chroma query failed, returning empty: {e}")
        return []


def fetch_top_k(
    query: str,
    k: int = 5,
    persist_dir: Optional[Path] = None,
    index_path: str = "ai/context7/index.json",
) -> List[Dict[str, Any]]:
    """
    Unified fetch_top_k: uses Chroma if available, falls back to keyword search.

    This is the primary entrypoint for all runners. It maintains
    backward compatibility with rag_pipeline.fetch_top_k.
    """
    chroma_dir = persist_dir or CHROMA_DIR

    # Try Chroma first
    if _CHROMA_AVAILABLE and chroma_dir.exists():
        results = fetch_top_k_chroma(query, k=k, persist_dir=chroma_dir)
        if results:
            return results

    # Fallback: keyword-based search
    from ai.context7.rag_pipeline import fetch_top_k as keyword_fetch
    return keyword_fetch(query, k=k, index_path=index_path)
