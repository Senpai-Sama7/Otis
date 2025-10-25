"""Chroma vector store service for RAG."""

import chromadb
from chromadb.config import Settings as ChromaSettings

from src.core.config import get_settings
from src.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class ChromaService:
    """Service for managing Chroma vector store."""

    def __init__(self):
        self.persist_directory = settings.chroma_persist_directory
        self.collection_name = settings.chroma_collection_name
        self.client = chromadb.Client(
            ChromaSettings(
                persist_directory=self.persist_directory,
                anonymized_telemetry=False,
            )
        )
        self._collection = None

    def get_collection(self):
        """Get or create the collection."""
        if self._collection is None:
            self._collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Cybersecurity threat intelligence and best practices"},
            )
        return self._collection

    def add_documents(
        self,
        documents: list[str],
        metadatas: list[dict],
        ids: list[str] | None = None,
    ) -> None:
        """Add documents to the vector store."""
        collection = self.get_collection()

        if ids is None:
            ids = [f"doc_{i}" for i in range(len(documents))]

        logger.info("Adding documents to Chroma", count=len(documents))
        collection.add(documents=documents, metadatas=metadatas, ids=ids)

    def query(
        self,
        query_text: str,
        n_results: int = 5,
        where: dict | None = None,
    ) -> dict:
        """Query the vector store."""
        collection = self.get_collection()

        logger.info("Querying Chroma", query=query_text, n_results=n_results)
        results = collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where=where,
        )

        return {
            "documents": results["documents"][0] if results["documents"] else [],
            "metadatas": results["metadatas"][0] if results["metadatas"] else [],
            "distances": results["distances"][0] if results["distances"] else [],
        }

    def delete_collection(self) -> None:
        """Delete the collection."""
        try:
            self.client.delete_collection(name=self.collection_name)
            self._collection = None
            logger.info("Collection deleted", collection=self.collection_name)
        except Exception as e:
            logger.error("Failed to delete collection", error=str(e))

    def get_collection_count(self) -> int:
        """Get the number of documents in the collection."""
        try:
            collection = self.get_collection()
            return collection.count()
        except Exception:
            return 0

    def check_health(self) -> bool:
        """Check if Chroma service is available."""
        try:
            self.client.heartbeat()
            return True
        except Exception as e:
            logger.error("Chroma health check failed", error=str(e))
            return False
