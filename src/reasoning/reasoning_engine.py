"""
Multi-layered reasoning engine that automatically selects the optimal reasoning
strategy based on query complexity and context.
"""

import asyncio
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

import structlog

logger = structlog.get_logger(__name__)


class ReasoningStrategy(str, Enum):
    """Available reasoning strategies."""

    ZERO_SHOT = "zero_shot"
    DARWIN_GODEL = "darwin_godel"
    ABSOLUTE_ZERO = "absolute_zero"


@dataclass
class ReasoningContext:
    """Context for reasoning operations."""

    query: str
    user_context: Optional[Dict[str, Any]] = None
    relevant_memories: Optional[List[Dict[str, Any]]] = None
    complexity_score: float = 0.0


@dataclass
class ReasoningResult:
    """Result of a reasoning operation."""

    strategy_used: ReasoningStrategy
    response: str
    steps: List[Dict[str, Any]]
    confidence: float
    reasoning_trace: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class ReasoningEngine:
    """
    Multi-layered reasoning engine that intelligently selects and applies
    the appropriate reasoning strategy based on query complexity.

    Complexity Ranges:
    - < 0.3: Zero-shot reasoning (simple, direct responses)
    - 0.3 - 0.7: Darwin-Gödel engine (evolutionary optimization)
    - ≥ 0.7: Absolute Zero reasoner (first-principles reasoning)
    """

    def __init__(
        self,
        ollama_client: Any,
        memory_system: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the reasoning engine.

        Args:
            ollama_client: Client for LLM inference
            memory_system: Memory system for context and history
            config: Configuration options for reasoning strategies
        """
        self.ollama_client = ollama_client
        self.memory_system = memory_system
        self.config = config or {}

        # Initialize reasoning strategies (lazy import to avoid circular dependencies)
        self.darwin_godel = None
        self.absolute_zero = None

        logger.info("reasoning_engine.initialized", strategies=["zero_shot", "darwin_godel", "absolute_zero"])

    async def reason(self, context: ReasoningContext) -> ReasoningResult:
        """
        Execute reasoning with automatic strategy selection.

        Args:
            context: Reasoning context with query and metadata

        Returns:
            ReasoningResult with response and reasoning trace
        """
        # Calculate complexity if not provided
        if context.complexity_score == 0.0:
            context.complexity_score = await self._calculate_complexity(context.query)

        # Select reasoning strategy based on complexity
        strategy = self._select_strategy(context.complexity_score)

        logger.info(
            "reasoning_engine.executing",
            strategy=strategy.value,
            complexity=context.complexity_score,
            query_length=len(context.query),
        )

        # Execute appropriate reasoning strategy
        if strategy == ReasoningStrategy.ZERO_SHOT:
            result = await self._zero_shot_reasoning(context)
        elif strategy == ReasoningStrategy.DARWIN_GODEL:
            result = await self._darwin_godel_reasoning(context)
        else:  # ABSOLUTE_ZERO
            result = await self._absolute_zero_reasoning(context)

        logger.info(
            "reasoning_engine.completed",
            strategy=strategy.value,
            confidence=result.confidence,
            steps=len(result.steps),
        )

        return result

    def _select_strategy(self, complexity: float) -> ReasoningStrategy:
        """Select reasoning strategy based on complexity score."""
        if complexity < 0.3:
            return ReasoningStrategy.ZERO_SHOT
        elif complexity < 0.7:
            return ReasoningStrategy.DARWIN_GODEL
        else:
            return ReasoningStrategy.ABSOLUTE_ZERO

    async def _calculate_complexity(self, query: str) -> float:
        """
        Calculate query complexity based on multiple factors.

        Factors considered:
        - Length and structure of query
        - Number of cybersecurity concepts involved
        - Presence of technical terms
        - Question complexity (simple vs. multi-part)

        Returns:
            Complexity score between 0.0 and 1.0
        """
        # Basic complexity factors
        length_factor = min(len(query) / 200, 1.0)  # Adjusted from 500 to 200

        # Technical term density (expanded list)
        technical_terms = [
            "exploit", "vulnerability", "CVE", "attack vector", "zero-day",
            "lateral movement", "privilege escalation", "persistence mechanism",
            "advanced persistent threat", "supply chain", "SQL injection", "XSS",
            "WAF", "firewall", "malware", "ransomware", "phishing", "DDoS",
            "intrusion", "breach", "compromise", "mitigation", "detection",
            "prevention", "encryption", "authentication", "authorization"
        ]
        term_count = sum(1 for term in technical_terms if term.lower() in query.lower())
        term_density = min(term_count / 2, 1.0)  # Adjusted threshold

        # Question complexity
        question_words = ["why", "how", "explain", "analyze", "compare", "contrast", "detect", "prevent"]
        question_complexity = min(sum(1 for word in question_words if word in query.lower()) / 2, 1.0)

        # Multi-part query detection (multiple questions or "and" clauses)
        multi_part_factor = min(query.count("?") + query.count(" and ") / 2, 1.0)

        # Combine factors
        complexity = (
            (length_factor * 0.2) + 
            (term_density * 0.4) + 
            (question_complexity * 0.2) +
            (multi_part_factor * 0.2)
        )

        return min(complexity, 1.0)

    async def _zero_shot_reasoning(self, context: ReasoningContext) -> ReasoningResult:
        """
        Execute simple zero-shot reasoning for straightforward queries.

        Args:
            context: Reasoning context

        Returns:
            ReasoningResult with direct response
        """
        # Add context from memory if available
        memory_context = ""
        if self.memory_system and context.relevant_memories:
            memory_context = "\n".join(
                [f"- {mem.get('content', '')}" for mem in context.relevant_memories[:3]]
            )

        prompt = f"""Query: {context.query}

{f"Relevant Context:\n{memory_context}\n" if memory_context else ""}
Provide a clear, concise answer to the query above."""

        try:
            response = await self.ollama_client.generate(prompt, temperature=0.1, max_tokens=500)

            return ReasoningResult(
                strategy_used=ReasoningStrategy.ZERO_SHOT,
                response=response,
                steps=[{"type": "zero_shot", "description": "Direct generation", "output": response}],
                confidence=0.8,
                reasoning_trace=["Applied zero-shot reasoning for simple query"],
            )
        except Exception as e:
            logger.error("zero_shot_reasoning.failed", error=str(e))
            raise

    async def _darwin_godel_reasoning(self, context: ReasoningContext) -> ReasoningResult:
        """
        Execute Darwin-Gödel reasoning with evolutionary optimization.

        Args:
            context: Reasoning context

        Returns:
            ReasoningResult with optimized response
        """
        # Lazy import
        if self.darwin_godel is None:
            from src.reasoning.darwin_godel import DarwinGodelEngine

            self.darwin_godel = DarwinGodelEngine(
                client=self.ollama_client,
                memory=self.memory_system,
                config=self.config.get("darwin_godel", {}),
            )

        return await self.darwin_godel.reason(context)

    async def _absolute_zero_reasoning(self, context: ReasoningContext) -> ReasoningResult:
        """
        Execute Absolute Zero reasoning from first principles.

        Args:
            context: Reasoning context

        Returns:
            ReasoningResult with first-principles analysis
        """
        # Lazy import
        if self.absolute_zero is None:
            from src.reasoning.absolute_zero import AbsoluteZeroReasoner

            self.absolute_zero = AbsoluteZeroReasoner(
                client=self.ollama_client,
                memory=self.memory_system,
                config=self.config.get("absolute_zero", {}),
            )

        return await self.absolute_zero.reason(context)
