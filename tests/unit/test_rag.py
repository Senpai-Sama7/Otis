"""Tests for RAG index."""

from unittest.mock import MagicMock, patch

import pytest

from src.rag.index import RAGIndex, build_index, query


class TestRAGIndex:
    """Test RAG index functionality."""

    @patch("src.rag.index.ChromaService")
    def test_query_success(self, mock_chroma):
        """Test successful query."""
        mock_service = MagicMock()
        mock_chroma.return_value = mock_service
        mock_service.query.return_value = {
            "documents": [["Test document"]],
            "metadatas": [[{"source": "MITRE", "category": "test"}]],
            "distances": [[0.1]],
        }

        results = query("test query", k=1)

        assert len(results) == 1
        assert results[0]["content"] == "Test document"
        assert results[0]["source"] == "MITRE"
        assert results[0]["relevance_score"] == 0.9  # 1.0 - 0.1

    @patch("src.rag.index.ChromaService")
    def test_query_empty_results(self, mock_chroma):
        """Test query with empty results."""
        mock_service = MagicMock()
        mock_chroma.return_value = mock_service
        mock_service.query.return_value = {
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]],
        }

        results = query("test query", k=3)

        assert len(results) == 0

    @patch("src.rag.index.ChromaService")
    def test_query_handles_errors(self, mock_chroma):
        """Test query handles errors gracefully."""
        mock_service = MagicMock()
        mock_chroma.return_value = mock_service
        mock_service.query.side_effect = Exception("Test error")

        results = query("test query")

        assert results == []

    @patch("src.rag.index.ChromaService")
    def test_build_index_success(self, mock_chroma):
        """Test building index successfully."""
        mock_service = MagicMock()
        mock_collection = MagicMock()
        mock_service.collection = mock_collection
        mock_chroma.return_value = mock_service

        sources = [
            {
                "id": "test_1",
                "content": "Test content 1",
                "metadata": {"source": "MITRE"},
            },
            {
                "id": "test_2",
                "content": "Test content 2",
                "metadata": {"source": "NIST"},
            },
        ]

        success = build_index(sources)

        assert success is True
        mock_collection.add.assert_called_once()

    @patch("src.rag.index.ChromaService")
    def test_build_index_empty_sources(self, mock_chroma):
        """Test building index with empty sources."""
        mock_service = MagicMock()
        mock_chroma.return_value = mock_service

        success = build_index([])

        assert success is False

    @patch("src.rag.index.ChromaService")
    def test_rag_index_class_query(self, mock_chroma):
        """Test RAGIndex class query method."""
        mock_service = MagicMock()
        mock_chroma.return_value = mock_service
        mock_service.query.return_value = {
            "documents": [["Test"]],
            "metadatas": [[{"source": "OWASP"}]],
            "distances": [[0.2]],
        }

        rag_index = RAGIndex()
        results = rag_index.query("test", k=1)

        assert len(results) == 1

    @patch("src.rag.index.ChromaService")
    def test_rag_index_add_document(self, mock_chroma):
        """Test adding a document to index."""
        mock_service = MagicMock()
        mock_collection = MagicMock()
        mock_service.collection = mock_collection
        mock_chroma.return_value = mock_service

        rag_index = RAGIndex()
        success = rag_index.add_document(
            content="Test content",
            metadata={"source": "TEST"},
            doc_id="test_123",
        )

        assert success is True
        mock_collection.add.assert_called_once()

    @patch("src.rag.index.ChromaService")
    def test_rag_index_add_document_error(self, mock_chroma):
        """Test error handling when adding document."""
        mock_service = MagicMock()
        mock_collection = MagicMock()
        mock_collection.add.side_effect = Exception("Test error")
        mock_service.collection = mock_collection
        mock_chroma.return_value = mock_service

        rag_index = RAGIndex()
        success = rag_index.add_document(
            content="Test content",
            metadata={"source": "TEST"},
        )

        assert success is False

    @pytest.mark.asyncio
    @patch("src.rag.index.query")
    async def test_query_async(self, mock_query_sync):
        """Test async query wrapper."""
        from src.rag.index import query_async

        mock_query_sync.return_value = [{"content": "Test"}]

        results = await query_async("test query", k=1)

        assert len(results) == 1
        mock_query_sync.assert_called_once_with("test query", 1)
