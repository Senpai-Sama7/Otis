"""RAG (Retrieval-Augmented Generation) module."""

from src.rag.index import build_index, query

__all__ = ["query", "build_index"]
