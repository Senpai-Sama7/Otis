"""Threat intelligence query tool for ReAct agent."""

from typing import Any

from src.core.logging import get_logger
from src.services.chroma import ChromaService
from src.tools.base import BaseTool

logger = get_logger(__name__)


class QueryThreatIntelTool(BaseTool):
    """Tool for querying threat intelligence database."""

    def __init__(self, chroma_service: ChromaService):
        super().__init__(
            name="query_threat_intel",
            description="Query the threat intelligence database for information about threats, vulnerabilities, and mitigations",
        )
        self.chroma_service = chroma_service

    def get_parameters(self) -> dict[str, Any]:
        """Get parameter schema."""
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Natural language query about threats or vulnerabilities",
                },
                "sources": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["MITRE", "NIST", "OWASP"]},
                    "description": "Filter results by specific sources",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results to return",
                    "default": 5,
                    "minimum": 1,
                    "maximum": 20,
                },
            },
            "required": ["query"],
        }

    async def execute(self, **kwargs) -> dict[str, Any]:
        """Execute threat intelligence query."""
        query = kwargs.get("query", "")
        sources = kwargs.get("sources", [])
        limit = kwargs.get("limit", 5)

        logger.info("Querying threat intelligence", query=query, sources=sources, limit=limit)

        try:
            # Build where clause for filtering by source
            where = None
            if sources:
                where = {"source": {"$in": sources}}

            # Query Chroma vector store
            results = self.chroma_service.query(
                query_text=query,
                n_results=limit,
                where=where,
            )

            # Format results
            formatted_results = []
            for doc, metadata, distance in zip(
                results["documents"],
                results["metadatas"],
                results["distances"],
                strict=True,
            ):
                formatted_results.append(
                    {
                        "content": doc,
                        "source": metadata.get("source", "Unknown"),
                        "category": metadata.get("category", "Unknown"),
                        "relevance_score": 1.0 - distance,  # Convert distance to similarity
                        **metadata,
                    }
                )

            logger.info("Threat intel query completed", results_count=len(formatted_results))

            return {
                "success": True,
                "query": query,
                "results": formatted_results,
                "sources_searched": sources if sources else ["MITRE", "NIST", "OWASP"],
            }

        except Exception as e:
            logger.error("Threat intel query failed", error=str(e))
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "results": [],
            }
