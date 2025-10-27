"""
Semantic Memory: Conceptual knowledge with vector-based retrieval.
"""

from typing import Any, Dict, List, Optional

import structlog

logger = structlog.get_logger(__name__)


class SemanticMemory:
    """
    Semantic memory stores conceptual cybersecurity knowledge with vector-based retrieval.

    Concepts include:
    - Security principles and techniques
    - Attack patterns and defense strategies
    - Tool usage and best practices
    - Threat intelligence
    """

    def __init__(self, vector_store: Optional[Any] = None):
        """
        Initialize semantic memory.

        Args:
            vector_store: Vector store for embeddings (e.g., Chroma)
        """
        self.vector_store = vector_store
        self.concepts: List[Dict[str, Any]] = []  # Fallback in-memory storage

        logger.info(
            "semantic_memory.initialized",
            has_vector_store=vector_store is not None,
        )

    async def add_concept(
        self,
        concept: str,
        embedding: Optional[List[float]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Add a concept to semantic memory.

        Args:
            concept: Concept text
            embedding: Optional pre-computed embedding
            metadata: Optional metadata (category, source, etc.)
        """
        concept_data = {
            "text": concept,
            "embedding": embedding,
            "metadata": metadata or {},
        }

        if self.vector_store:
            # Store in vector database
            try:
                # Assuming vector store has an add method
                # This would need to be adapted based on actual vector store implementation
                await self._add_to_vector_store(concept, embedding, metadata)
            except Exception as e:
                logger.error("semantic_memory.vector_store_add_failed", error=str(e))
                self.concepts.append(concept_data)
        else:
            # Fallback to in-memory storage
            self.concepts.append(concept_data)

        logger.debug("semantic_memory.concept_added", concept_length=len(concept))

    async def query(
        self, query: str, k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Query semantic memory for relevant concepts.

        Args:
            query: Query text
            k: Number of results to return

        Returns:
            List of relevant concepts
        """
        if self.vector_store:
            # Use vector store for similarity search
            try:
                results = await self._query_vector_store(query, k)
                return results
            except Exception as e:
                logger.error("semantic_memory.vector_store_query_failed", error=str(e))

        # Fallback to simple keyword matching
        return self._keyword_search(query, k)

    def _keyword_search(self, query: str, k: int) -> List[Dict[str, Any]]:
        """Simple keyword-based search fallback."""
        query_lower = query.lower()
        query_words = set(query_lower.split())

        scored_concepts = []
        for concept in self.concepts:
            text_lower = concept["text"].lower()
            text_words = set(text_lower.split())

            # Calculate similarity
            intersection = len(query_words & text_words)
            union = len(query_words | text_words)
            similarity = intersection / union if union > 0 else 0.0

            if similarity > 0:
                scored_concepts.append((similarity, concept))

        # Sort and return top k
        scored_concepts.sort(reverse=True, key=lambda x: x[0])
        return [concept for _, concept in scored_concepts[:k]]

    async def _add_to_vector_store(
        self, concept: str, embedding: Optional[List[float]], metadata: Optional[Dict[str, Any]]
    ) -> None:
        """Add concept to vector store (implementation depends on store type)."""
        # This would be implemented based on the actual vector store being used
        # For Chroma, it might look like:
        # await self.vector_store.add(texts=[concept], metadatas=[metadata])
        pass

    async def _query_vector_store(self, query: str, k: int) -> List[Dict[str, Any]]:
        """Query vector store (implementation depends on store type)."""
        # This would be implemented based on the actual vector store being used
        # For Chroma, it might look like:
        # results = await self.vector_store.similarity_search(query, k=k)
        # return [{"text": r.page_content, "metadata": r.metadata} for r in results]
        return []

    async def get_by_category(
        self, category: str, k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get concepts by category.

        Args:
            category: Category name (e.g., 'red-team', 'blue-team')
            k: Number of results to return

        Returns:
            List of concepts in the category
        """
        filtered = [
            concept
            for concept in self.concepts
            if concept.get("metadata", {}).get("category") == category
        ]
        return filtered[:k]

    async def clear(self) -> None:
        """Clear all semantic memories."""
        self.concepts.clear()
        logger.info("semantic_memory.cleared")

    def __len__(self) -> int:
        """Return number of concepts."""
        return len(self.concepts)
