"""
Comprehensive memory system integrating multiple memory types with persistent storage.
"""

from pathlib import Path
from typing import Any

import structlog

from src.memory.episodic import EpisodicMemory
from src.memory.procedural import ProceduralMemory
from src.memory.semantic import SemanticMemory
from src.memory.working import WorkingMemory

logger = structlog.get_logger(__name__)


class MemorySystem:
    """
    Comprehensive memory system with multiple memory types for cybersecurity operations.

    Memory Types:
    - Episodic: Interaction history and specific experiences
    - Semantic: Conceptual cybersecurity knowledge
    - Procedural: Step-by-step methodologies and procedures
    - Working: Short-term active context
    """

    def __init__(
        self,
        vector_store: Any | None = None,
        persistence_path: str = "./data/memory",
        working_memory_capacity: int = 10,
    ):
        """
        Initialize the memory system.

        Args:
            vector_store: Vector store for semantic memory (e.g., Chroma)
            persistence_path: Path for persistent storage
            working_memory_capacity: Maximum items in working memory
        """
        self.persistence_path = Path(persistence_path)
        self.persistence_path.mkdir(parents=True, exist_ok=True)

        self.vector_store = vector_store

        # Initialize memory subsystems
        self.episodic = EpisodicMemory()
        self.semantic = SemanticMemory(vector_store)
        self.procedural = ProceduralMemory()
        self.working = WorkingMemory(capacity=working_memory_capacity)

        self.initialized = False

        logger.info(
            "memory_system.created",
            persistence_path=str(self.persistence_path),
            working_capacity=working_memory_capacity,
        )

    async def initialize(self) -> None:
        """Initialize the memory system and load persistent data."""
        if self.initialized:
            logger.warn("memory_system.already_initialized")
            return

        logger.info("memory_system.initializing")

        # Load persistent memory components
        await self._load_persistent_memories()

        self.initialized = True
        logger.info("memory_system.initialized")

    async def _load_persistent_memories(self) -> None:
        """Load persistent memory data from disk."""
        try:
            # Load episodic memory
            episodic_path = self.persistence_path / "episodic.json"
            if episodic_path.exists():
                await self.episodic.load(episodic_path)
                logger.info("memory_system.episodic_loaded", count=len(self.episodic.memories))

            # Load procedural memory
            procedural_path = self.persistence_path / "procedural.json"
            if procedural_path.exists():
                await self.procedural.load(procedural_path)
                logger.info(
                    "memory_system.procedural_loaded", count=len(self.procedural.procedures)
                )

            # Semantic memory is handled by vector store

        except Exception as e:
            logger.error("memory_system.load_failed", error=str(e))

    async def save_persistent_memories(self) -> None:
        """Save persistent memory data to disk."""
        try:
            # Save episodic memory
            episodic_path = self.persistence_path / "episodic.json"
            await self.episodic.save(episodic_path)

            # Save procedural memory
            procedural_path = self.persistence_path / "procedural.json"
            await self.procedural.save(procedural_path)

            logger.info("memory_system.saved")

        except Exception as e:
            logger.error("memory_system.save_failed", error=str(e))

    async def add_interaction(
        self,
        query: str,
        response: str,
        context: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Add an interaction to episodic memory.

        Args:
            query: User query
            response: Agent response
            context: Optional context information
            metadata: Optional metadata
        """
        await self.episodic.add_memory(
            content={"query": query, "response": response, "context": context or {}},
            metadata=metadata,
        )

        logger.debug("memory_system.interaction_added", query_length=len(query))

    async def recall_similar_interactions(self, query: str, k: int = 5) -> list[dict[str, Any]]:
        """
        Recall similar past interactions from episodic memory.

        Args:
            query: Query to find similar interactions
            k: Number of similar interactions to return

        Returns:
            List of similar interactions
        """
        return await self.episodic.recall_similar(query, k=k)

    async def add_concept(
        self,
        concept: str,
        embedding: list[float] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Add a concept to semantic memory.

        Args:
            concept: Concept text
            embedding: Optional pre-computed embedding
            metadata: Optional metadata (category, source, etc.)
        """
        await self.semantic.add_concept(concept, embedding=embedding, metadata=metadata)

        logger.debug("memory_system.concept_added", concept_length=len(concept))

    async def query_knowledge(self, query: str, k: int = 5) -> list[dict[str, Any]]:
        """
        Query semantic knowledge base.

        Args:
            query: Knowledge query
            k: Number of results to return

        Returns:
            List of relevant knowledge items
        """
        return await self.semantic.query(query, k=k)

    async def add_procedure(
        self,
        name: str,
        steps: list[str],
        category: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Add a procedure to procedural memory.

        Args:
            name: Procedure name
            steps: List of procedure steps
            category: Optional category (e.g., 'red-team', 'blue-team')
            metadata: Optional metadata
        """
        await self.procedural.add_procedure(
            name=name, steps=steps, category=category, metadata=metadata
        )

        logger.debug("memory_system.procedure_added", name=name, steps=len(steps))

    async def get_procedure(self, name: str) -> dict[str, Any] | None:
        """
        Get a procedure by name.

        Args:
            name: Procedure name

        Returns:
            Procedure data or None if not found
        """
        return await self.procedural.get_procedure(name)

    async def find_procedures(
        self, query: str, category: str | None = None, k: int = 5
    ) -> list[dict[str, Any]]:
        """
        Find procedures matching query.

        Args:
            query: Search query
            category: Optional category filter
            k: Number of results to return

        Returns:
            List of matching procedures
        """
        return await self.procedural.find_procedures(query, category=category, k=k)

    def add_to_working_memory(self, key: str, value: Any) -> None:
        """
        Add item to working memory.

        Args:
            key: Item key
            value: Item value
        """
        self.working.add(key, value)
        logger.debug("memory_system.working_memory_updated", key=key)

    def get_from_working_memory(self, key: str) -> Any | None:
        """
        Get item from working memory.

        Args:
            key: Item key

        Returns:
            Item value or None if not found
        """
        return self.working.get(key)

    def clear_working_memory(self) -> None:
        """Clear working memory."""
        self.working.clear()
        logger.debug("memory_system.working_memory_cleared")

    async def get_context_for_reasoning(self, query: str, max_items: int = 10) -> dict[str, Any]:
        """
        Get comprehensive context for reasoning from all memory types.

        Args:
            query: Current query
            max_items: Maximum items to retrieve per memory type

        Returns:
            Dictionary with context from all memory types
        """
        context = {
            "similar_interactions": await self.recall_similar_interactions(query, k=max_items // 2),
            "relevant_knowledge": await self.query_knowledge(query, k=max_items // 2),
            "relevant_procedures": await self.find_procedures(query, k=3),
            "working_memory": self.working.get_all(),
        }

        logger.debug(
            "memory_system.context_retrieved",
            interactions=len(context["similar_interactions"]),
            knowledge=len(context["relevant_knowledge"]),
            procedures=len(context["relevant_procedures"]),
        )

        return context

    async def shutdown(self) -> None:
        """Shutdown the memory system and save all data."""
        logger.info("memory_system.shutting_down")
        await self.save_persistent_memories()
        logger.info("memory_system.shutdown_complete")
