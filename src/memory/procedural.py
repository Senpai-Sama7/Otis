"""
Procedural Memory: Step-by-step procedures and methodologies.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

import structlog

logger = structlog.get_logger(__name__)


class ProceduralMemory:
    """
    Procedural memory stores step-by-step procedures and methodologies.

    Procedures include:
    - Attack methodologies (e.g., reconnaissance, exploitation)
    - Defense procedures (e.g., incident response, patching)
    - Tool usage workflows
    - Best practices
    """

    def __init__(self):
        """Initialize procedural memory."""
        self.procedures: Dict[str, Dict[str, Any]] = {}
        logger.info("procedural_memory.initialized")

    async def add_procedure(
        self,
        name: str,
        steps: List[str],
        category: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Add a procedure to memory.

        Args:
            name: Procedure name
            steps: List of procedure steps
            category: Optional category (e.g., 'red-team', 'blue-team')
            metadata: Optional metadata

        Returns:
            Procedure ID
        """
        procedure_id = str(uuid4())
        procedure = {
            "id": procedure_id,
            "name": name,
            "steps": steps,
            "category": category,
            "metadata": metadata or {},
        }

        self.procedures[name] = procedure
        logger.debug("procedural_memory.added", name=name, steps=len(steps))

        return procedure_id

    async def get_procedure(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a procedure by name.

        Args:
            name: Procedure name

        Returns:
            Procedure data or None if not found
        """
        return self.procedures.get(name)

    async def find_procedures(
        self, query: str, category: Optional[str] = None, k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find procedures matching query.

        Args:
            query: Search query
            category: Optional category filter
            k: Number of results to return

        Returns:
            List of matching procedures
        """
        query_lower = query.lower()
        query_words = set(query_lower.split())

        scored_procedures = []
        for procedure in self.procedures.values():
            # Category filter
            if category and procedure.get("category") != category:
                continue

            # Calculate similarity
            text = f"{procedure['name']} {' '.join(procedure['steps'])}".lower()
            text_words = set(text.split())

            intersection = len(query_words & text_words)
            union = len(query_words | text_words)
            similarity = intersection / union if union > 0 else 0.0

            if similarity > 0:
                scored_procedures.append((similarity, procedure))

        # Sort and return top k
        scored_procedures.sort(reverse=True, key=lambda x: x[0])
        return [proc for _, proc in scored_procedures[:k]]

    async def get_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get all procedures in a category.

        Args:
            category: Category name

        Returns:
            List of procedures in the category
        """
        return [
            proc
            for proc in self.procedures.values()
            if proc.get("category") == category
        ]

    async def list_all(self) -> List[Dict[str, Any]]:
        """
        List all procedures.

        Returns:
            List of all procedures
        """
        return list(self.procedures.values())

    async def delete_procedure(self, name: str) -> bool:
        """
        Delete a procedure by name.

        Args:
            name: Procedure name

        Returns:
            True if deleted, False if not found
        """
        if name in self.procedures:
            del self.procedures[name]
            logger.debug("procedural_memory.deleted", name=name)
            return True
        return False

    async def clear(self) -> None:
        """Clear all procedural memories."""
        self.procedures.clear()
        logger.info("procedural_memory.cleared")

    async def load(self, filepath: Path) -> None:
        """
        Load procedures from file.

        Args:
            filepath: Path to load from
        """
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
                self.procedures = data.get("procedures", {})
            logger.info("procedural_memory.loaded", count=len(self.procedures))
        except FileNotFoundError:
            logger.info("procedural_memory.no_file_found", filepath=str(filepath))
        except Exception as e:
            logger.error("procedural_memory.load_failed", error=str(e))

    async def save(self, filepath: Path) -> None:
        """
        Save procedures to file.

        Args:
            filepath: Path to save to
        """
        try:
            data = {"procedures": self.procedures, "count": len(self.procedures)}
            with open(filepath, "w") as f:
                json.dump(data, f, indent=2)
            logger.info("procedural_memory.saved", count=len(self.procedures))
        except Exception as e:
            logger.error("procedural_memory.save_failed", error=str(e))

    def __len__(self) -> int:
        """Return number of procedures."""
        return len(self.procedures)
