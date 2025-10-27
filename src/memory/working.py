"""
Working Memory: Short-term active context management.
"""

from collections import OrderedDict
from typing import Any, Dict, Optional

import structlog

logger = structlog.get_logger(__name__)


class WorkingMemory:
    """
    Working memory stores short-term active context.

    This is used for:
    - Current reasoning context
    - Temporary variables and state
    - Active task information
    - Recent computations
    """

    def __init__(self, capacity: int = 10):
        """
        Initialize working memory.

        Args:
            capacity: Maximum number of items to store
        """
        self.capacity = capacity
        self.memory: OrderedDict[str, Any] = OrderedDict()
        logger.info("working_memory.initialized", capacity=capacity)

    def add(self, key: str, value: Any) -> None:
        """
        Add an item to working memory.

        If capacity is exceeded, oldest items are removed (LRU).

        Args:
            key: Item key
            value: Item value
        """
        # Remove oldest item if at capacity
        if len(self.memory) >= self.capacity and key not in self.memory:
            oldest_key = next(iter(self.memory))
            del self.memory[oldest_key]
            logger.debug("working_memory.evicted", key=oldest_key)

        # Add or update item
        self.memory[key] = value
        # Move to end (most recent)
        self.memory.move_to_end(key)

        logger.debug("working_memory.added", key=key)

    def get(self, key: str) -> Optional[Any]:
        """
        Get an item from working memory.

        Args:
            key: Item key

        Returns:
            Item value or None if not found
        """
        value = self.memory.get(key)
        if value is not None:
            # Move to end (mark as recently used)
            self.memory.move_to_end(key)
        return value

    def remove(self, key: str) -> bool:
        """
        Remove an item from working memory.

        Args:
            key: Item key

        Returns:
            True if removed, False if not found
        """
        if key in self.memory:
            del self.memory[key]
            logger.debug("working_memory.removed", key=key)
            return True
        return False

    def clear(self) -> None:
        """Clear all items from working memory."""
        self.memory.clear()
        logger.debug("working_memory.cleared")

    def get_all(self) -> Dict[str, Any]:
        """
        Get all items from working memory.

        Returns:
            Dictionary of all items
        """
        return dict(self.memory)

    def keys(self) -> list:
        """
        Get all keys in working memory.

        Returns:
            List of keys
        """
        return list(self.memory.keys())

    def __contains__(self, key: str) -> bool:
        """Check if key exists in working memory."""
        return key in self.memory

    def __len__(self) -> int:
        """Return number of items in working memory."""
        return len(self.memory)

    def __repr__(self) -> str:
        """String representation of working memory."""
        return f"WorkingMemory(capacity={self.capacity}, items={len(self.memory)})"
