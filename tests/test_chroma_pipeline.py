# tests/test_chroma_pipeline.py
"""
Unit tests for Chroma RAG pipeline.
Tests both Chroma path and keyword fallback.
"""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestFetchTopKFallback:
    """Tests for keyword fallback when Chroma is unavailable."""

    def test_fallback_when_chroma_unavailable(self, tmp_path):
        """When Chroma dir does not exist, falls back to keyword search."""
        from ai.context7.chroma_pipeline import fetch_top_k
        import ai.context7.chroma_pipeline as cp

        with patch.object(cp, '_CHROMA_AVAILABLE', False):
            with patch('ai.context7.rag_pipeline.fetch_top_k') as mock_kw:
                mock_kw.return_value = [{"path": "foo.py", "content": "hello"}]
                results = fetch_top_k("hello", k=3, persist_dir=tmp_path / "nonexistent")
                mock_kw.assert_called_once()
                assert results == [{"path": "foo.py", "content": "hello"}]

    def test_fallback_when_no_chroma_dir(self, tmp_path):
        """When Chroma dir does not exist, fallback is used."""
        from ai.context7.chroma_pipeline import fetch_top_k

        with patch('ai.context7.rag_pipeline.fetch_top_k') as mock_kw:
            mock_kw.return_value = []
            results = fetch_top_k("test", persist_dir=tmp_path / "no_db")
            mock_kw.assert_called_once()

    def test_empty_chroma_falls_back(self, tmp_path):
        """Empty Chroma collection triggers keyword fallback."""
        import ai.context7.chroma_pipeline as cp
        if not cp._CHROMA_AVAILABLE:
            pytest.skip("chromadb not installed")

        from ai.context7.chroma_pipeline import fetch_top_k
        # Use fresh tmp_path (no collection built) — count will be 0
        with patch('ai.context7.rag_pipeline.fetch_top_k') as mock_kw:
            mock_kw.return_value = []
            fetch_top_k("query", persist_dir=tmp_path)
            mock_kw.assert_called_once()


class TestChunkText:

    def test_short_text_no_split(self):
        from ai.context7.chroma_pipeline import _chunk_text
        result = _chunk_text("hello world", chunk_size=100)
        assert result == ["hello world"]

    def test_long_text_splits(self):
        from ai.context7.chroma_pipeline import _chunk_text
        text = "a" * 2500
        chunks = _chunk_text(text, chunk_size=1000, overlap=100)
        assert len(chunks) > 1
        # Each chunk must be <= chunk_size
        for chunk in chunks:
            assert len(chunk) <= 1000

    def test_overlap(self):
        from ai.context7.chroma_pipeline import _chunk_text
        text = "x" * 1100
        chunks = _chunk_text(text, chunk_size=1000, overlap=100)
        assert len(chunks) == 2
        # Second chunk starts at position 900 (1000 - 100 overlap)
        assert len(chunks[1]) == 200


class TestBuildChromaIndex:

    def test_no_op_when_chroma_unavailable(self, tmp_path):
        import ai.context7.chroma_pipeline as cp
        with patch.object(cp, '_CHROMA_AVAILABLE', False):
            from ai.context7.chroma_pipeline import build_chroma_index
            count = build_chroma_index([], persist_dir=tmp_path)
            assert count == 0

    def test_empty_docs(self, tmp_path):
        import ai.context7.chroma_pipeline as cp
        if not cp._CHROMA_AVAILABLE:
            pytest.skip("chromadb not installed")

        from ai.context7.chroma_pipeline import build_chroma_index
        count = build_chroma_index([], persist_dir=tmp_path)
        assert count == 0

    def test_build_and_query(self, tmp_path):
        import ai.context7.chroma_pipeline as cp
        if not cp._CHROMA_AVAILABLE:
            pytest.skip("chromadb not installed")

        from ai.context7.chroma_pipeline import build_chroma_index, fetch_top_k_chroma
        docs = [
            {"path": "router.py", "content": "router decides mode and enabled agents"},
            {"path": "readme.md", "content": "this is the readme for ai-collab-starter"},
            {"path": "budget.py", "content": "monthly budget tracking and cost limits"},
        ]
        count = build_chroma_index(docs, persist_dir=tmp_path)
        assert count >= len(docs)

        results = fetch_top_k_chroma("budget cost", k=2, persist_dir=tmp_path)
        assert len(results) >= 1
        paths = [r["path"] for r in results]
        assert "budget.py" in paths
