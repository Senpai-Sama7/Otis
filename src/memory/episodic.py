"""
Episodic Memory: Stores specific interaction history and experiences.
"""

import json
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Any, Deque, Dict, List, Optional
from uuid import uuid4

import structlog

logger = structlog.get_logger(__name__)


class EpisodicMemory:
    """
    Episodic memory stores specific interactions and experiences with temporal context.

    Each memory includes:
    - Content (query, response, context)
    - Timestamp
    - Metadata (user, session, tags)
    """

    def __init__(self, max_memories: int = 1000):
        """
        Initialize episodic memory.

        Args:
            max_memories: Maximum number of memories to retain
        """
        self.max_memories = max_memories
        self.memories: Deque[Dict[str, Any]] = deque(maxlen=max_memories)
        logger.info("episodic_memory.initialized", max_memories=max_memories)

    async def add_memory(
        self,
        content: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Add a new memory to episodic storage.

        Args:
            content: Memory content (query, response, context)
            metadata: Optional metadata

        Returns:
            Memory ID
        """
        memory_id = str(uuid4())
        memory = {
            "id": memory_id,
            "content": content,
            "timestamp": datetime.now(datetime.UTC).isoformat() if hasattr(datetime, 'UTC') else datetime.utcnow().isoformat(),
            "metadata": metadata or {},
        }

        self.memories.append(memory)
        logger.debug("episodic_memory.added", memory_id=memory_id)

        return memory_id

    async def recall_similar(
        self, query: str, k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Recall memories similar to the query.

        Args:
            query: Query text
            k: Number of memories to return

        Returns:
            List of similar memories
        """
        # Simple keyword-based similarity for now
        # In production, would use embeddings and vector similarity
        query_lower = query.lower()
        query_words = set(query_lower.split())

        scored_memories = []
        for memory in self.memories:
            # Calculate similarity score based on keyword overlap
            content_text = json.dumps(memory["content"]).lower()
            content_words = set(content_text.split())

            # Calculate Jaccard similarity
            intersection = len(query_words & content_words)
            union = len(query_words | content_words)
            similarity = intersection / union if union > 0 else 0.0

            if similarity > 0:
                scored_memories.append((similarity, memory))

        # Sort by similarity and return top k
        scored_memories.sort(reverse=True, key=lambda x: x[0])
        similar_memories = [mem for _, mem in scored_memories[:k]]

        logger.debug("episodic_memory.recalled", query_length=len(query), found=len(similar_memories))

        return similar_memories

    async def get_recent(self, n: int = 10) -> List[Dict[str, Any]]:
        """
        Get the n most recent memories.

        Args:
            n: Number of recent memories to return

        Returns:
            List of recent memories
        """
        return list(self.memories)[-n:]

    async def get_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific memory by ID.

        Args:
            memory_id: Memory ID

        Returns:
            Memory data or None if not found
        """
        for memory in self.memories:
            if memory["id"] == memory_id:
                return memory
        return None

    async def clear(self) -> None:
        """Clear all episodic memories."""
        self.memories.clear()
        logger.info("episodic_memory.cleared")

    async def load(self, filepath: Path) -> None:
        """
        Load memories from file.

        Args:
            filepath: Path to load from
        """
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
                self.memories = deque(data["memories"], maxlen=self.max_memories)
            logger.info("episodic_memory.loaded", count=len(self.memories))
        except FileNotFoundError:
            logger.info("episodic_memory.no_file_found", filepath=str(filepath))
        except Exception as e:
            logger.error("episodic_memory.load_failed", error=str(e))

    async def save(self, filepath: Path) -> None:
        """
        Save memories to file.

        Args:
            filepath: Path to save to
        """
        try:
            data = {"memories": list(self.memories), "count": len(self.memories)}
            with open(filepath, "w") as f:
                json.dump(data, f, indent=2)
            logger.info("episodic_memory.saved", count=len(self.memories))
        except Exception as e:
            logger.error("episodic_memory.save_failed", error=str(e))

    def __len__(self) -> int:
        """Return number of memories."""
        return len(self.memories)
