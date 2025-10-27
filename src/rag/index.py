"""Shared RAG interface for querying threat intelligence knowledge base."""

from typing import Any

from src.core.config import get_settings
from src.core.logging import get_logger
from src.services.chroma import ChromaService

logger = get_logger(__name__)
settings = get_settings()


def query(text: str, k: int = 3) -> list[dict[str, Any]]:
    """
    Query the RAG knowledge base.

    Args:
        text: Query text
        k: Number of results to return (default: 3)

    Returns:
        List of dictionaries with query results containing:
        - content: Document text
        - source: Source (MITRE, NIST, OWASP)
        - metadata: Additional metadata
        - relevance_score: Similarity score
    """
    logger.info("Querying RAG knowledge base", query=text, k=k)

    try:
        chroma_service = ChromaService()
        results = chroma_service.query(query_text=text, n_results=k)

        formatted_results = []
        if results and "documents" in results:
            documents = results.get("documents", [[]])[0] if results.get("documents") else []
            metadatas = results.get("metadatas", [[]])[0] if results.get("metadatas") else []
            distances = results.get("distances", [[]])[0] if results.get("distances") else []

            for i, doc in enumerate(documents):
                metadata = metadatas[i] if i < len(metadatas) else {}
                distance = distances[i] if i < len(distances) else 1.0

                formatted_results.append(
                    {
                        "content": doc,
                        "source": metadata.get("source", "Unknown"),
                        "metadata": metadata,
                        "relevance_score": 1.0 - distance,  # Convert distance to similarity
                    }
                )

        logger.info("RAG query completed", results_count=len(formatted_results))
        return formatted_results

    except Exception as e:
        logger.error("RAG query failed", error=str(e))
        return []


async def query_async(text: str, k: int = 3) -> list[dict[str, Any]]:
    """
    Async version of query.

    Args:
        text: Query text
        k: Number of results to return

    Returns:
        List of query results
    """
    import asyncio

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, query, text, k)


def build_index(
    sources: list[dict[str, Any]],
    collection_name: str | None = None,
) -> bool:
    """
    Build RAG index from sources.

    Args:
        sources: List of source documents with 'content', 'source', and 'metadata'
        collection_name: Optional collection name (uses default if not provided)

    Returns:
        True if successful, False otherwise
    """
    logger.info("Building RAG index", sources_count=len(sources))

    try:
        chroma_service = ChromaService(collection_name=collection_name)

        documents = []
        metadatas = []
        ids = []

        for i, source in enumerate(sources):
            documents.append(source.get("content", ""))
            metadatas.append(source.get("metadata", {}))
            ids.append(source.get("id", f"doc_{i}"))

        # Add documents to Chroma
        if documents:
            chroma_service.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids,
            )
            logger.info("RAG index built successfully", documents_count=len(documents))
            return True
        else:
            logger.warning("No documents to index")
            return False

    except Exception as e:
        logger.error("Failed to build RAG index", error=str(e))
        return False


class RAGIndex:
    """
    Class-based interface for RAG operations.
    """

    def __init__(self, collection_name: str | None = None):
        self.collection_name = collection_name
        self.chroma_service = ChromaService(collection_name=collection_name)

    def query(self, text: str, k: int = 3) -> list[dict[str, Any]]:
        """Query the index."""
        return query(text, k)

    async def query_async(self, text: str, k: int = 3) -> list[dict[str, Any]]:
        """Async query."""
        return await query_async(text, k)

    def build(self, sources: list[dict[str, Any]]) -> bool:
        """Build the index from sources."""
        return build_index(sources, self.collection_name)

    def add_document(
        self,
        content: str,
        metadata: dict[str, Any],
        doc_id: str | None = None,
    ) -> bool:
        """
        Add a single document to the index.

        Args:
            content: Document content
            metadata: Document metadata
            doc_id: Optional document ID

        Returns:
            True if successful
        """
        try:
            import uuid

            doc_id = doc_id or str(uuid.uuid4())

            self.chroma_service.collection.add(
                documents=[content],
                metadatas=[metadata],
                ids=[doc_id],
            )
            logger.info("Document added to RAG index", doc_id=doc_id)
            return True

        except Exception as e:
            logger.error("Failed to add document", error=str(e))
            return False
