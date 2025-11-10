"""
LLM-based query router for intelligent complexity classification.

Replaces heuristic-based complexity calculation with semantic understanding.
"""

import json
from typing import Any

import structlog

from src.models.schemas import QueryClassification
from src.reasoning.reasoning_engine import ReasoningStrategy

logger = structlog.get_logger(__name__)


class QueryRouter:
    """
    LLM-based router that classifies query complexity semantically.
    
    Uses a fast LLM call to determine the appropriate reasoning strategy.
    """

    ROUTER_PROMPT = """You are a query complexity classifier for a cybersecurity AI agent.

Classify the user's query into one of three categories:

1. SIMPLE: Direct questions with straightforward answers
   - Examples: "What is SQL injection?", "List OWASP Top 10"
   
2. MODERATE: Queries requiring a plan and 2-3 tool calls
   - Examples: "Scan localhost for vulnerabilities", "Find threat intel on ransomware"
   
3. COMPLEX: Queries requiring first-principles reasoning and multi-step plans
   - Examples: "Analyze and remediate advanced persistent threat", "Design defense strategy for zero-day exploit"

Query: {query}

Respond with a JSON object matching this schema:
{{
    "complexity": "SIMPLE" | "MODERATE" | "COMPLEX",
    "reasoning": "Brief explanation",
    "recommended_strategy": "direct" | "hypothesis_evolution" | "first_principles"
}}"""

    def __init__(self, ollama_client: Any):
        """
        Initialize query router.
        
        Args:
            ollama_client: Ollama client for LLM inference
        """
        self.ollama_client = ollama_client

    async def classify(self, query: str) -> QueryClassification:
        """
        Classify query complexity using LLM.
        
        Args:
            query: User query to classify
            
        Returns:
            QueryClassification with complexity and recommended strategy
        """
        logger.info("query_router.classifying", query_length=len(query))

        try:
            prompt = self.ROUTER_PROMPT.format(query=query)
            
            # Use low temperature for consistent classification
            response = await self.ollama_client.generate(
                prompt=prompt,
                temperature=0.1,
                max_tokens=200,
            )

            # Parse JSON response
            classification_data = self._parse_json_response(response)
            
            classification = QueryClassification(**classification_data)
            
            logger.info(
                "query_router.classified",
                complexity=classification.complexity,
                strategy=classification.recommended_strategy,
            )
            
            return classification

        except Exception as e:
            logger.error("query_router.classification_failed", error=str(e))
            # Fallback to moderate complexity
            return QueryClassification(
                complexity="MODERATE",
                reasoning="Classification failed, using default",
                recommended_strategy="darwin_godel",
            )

    def _parse_json_response(self, response: str) -> dict[str, Any]:
        """Parse JSON from LLM response."""
        # Try to extract JSON from response
        try:
            # Look for JSON object in response
            start = response.find("{")
            end = response.rfind("}") + 1
            if start != -1 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass

        # Fallback: try to parse entire response
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            logger.warning("query_router.json_parse_failed", response=response[:100])
            raise

    def get_strategy_from_classification(self, classification: QueryClassification) -> ReasoningStrategy:
        """
        Map classification to reasoning strategy.
        
        Args:
            classification: Query classification
            
        Returns:
            ReasoningStrategy enum value
        """
        strategy_map = {
            "SIMPLE": ReasoningStrategy.DIRECT,
            "MODERATE": ReasoningStrategy.HYPOTHESIS_EVOLUTION,
            "COMPLEX": ReasoningStrategy.FIRST_PRINCIPLES,
        }
        
        return strategy_map.get(classification.complexity, ReasoningStrategy.HYPOTHESIS_EVOLUTION)
