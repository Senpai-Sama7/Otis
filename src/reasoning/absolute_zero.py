"""
Absolute Zero Reasoner: First-principles reasoning system.

This reasoner builds solutions from fundamental axioms without assumptions,
using a ground-up approach to cybersecurity analysis.
"""

from typing import Any

import structlog

from src.reasoning.reasoning_engine import ReasoningContext, ReasoningResult, ReasoningStrategy

logger = structlog.get_logger(__name__)


class AbsoluteZeroReasoner:
    """
    Absolute Zero reasoning system that grounds all reasoning in fundamental
    axioms and builds up from first principles with zero assumptions.

    Process:
    1. Extract fundamental principles
    2. Decompose complex concepts into simpler elements
    3. Establish ground truth statements
    4. Build logical inferences from ground truth
    5. Validate reasoning through verification
    6. Synthesize verified inferences into solution
    """

    def __init__(
        self,
        client: Any,
        memory: Any | None = None,
        config: dict[str, Any] | None = None,
    ):
        """
        Initialize the Absolute Zero reasoner.

        Args:
            client: LLM client for generation
            memory: Memory system for context
            config: Configuration options
        """
        self.client = client
        self.memory = memory
        self.config = config or {}

        # Reasoning parameters
        self.axiom_depth = self.config.get("axiom_depth", 3)
        self.inference_levels = self.config.get("inference_levels", 4)
        self.validation_enabled = self.config.get("validation_steps", True)

        logger.info(
            "absolute_zero.initialized",
            axiom_depth=self.axiom_depth,
            inference_levels=self.inference_levels,
        )

    async def reason(self, context: ReasoningContext) -> ReasoningResult:
        """
        Execute Absolute Zero reasoning from first principles.

        Args:
            context: Reasoning context

        Returns:
            ReasoningResult with first-principles analysis
        """
        steps = []
        reasoning_trace = []

        # Step 1: Extract fundamental principles
        logger.debug("absolute_zero.extracting_principles", query=context.query[:100])
        principles = await self._extract_fundamental_principles(context)
        steps.append(
            {
                "type": "principle_extraction",
                "description": "Extract fundamental principles and axioms",
                "principles": principles,
            }
        )
        reasoning_trace.append(f"Extracted {len(principles)} fundamental principles")

        # Step 2: Decompose concepts
        logger.debug("absolute_zero.decomposing_concepts")
        decomposition = await self._decompose_concepts(context, principles)
        steps.append(
            {
                "type": "concept_decomposition",
                "description": "Decompose complex concepts into simpler elements",
                "components": str(len(decomposition)),
            }
        )
        reasoning_trace.append(f"Decomposed into {len(decomposition)} base concepts")

        # Step 3: Establish ground truth
        logger.debug("absolute_zero.establishing_ground_truth")
        ground_truths = await self._establish_ground_truth(context, principles, decomposition)
        steps.append(
            {
                "type": "ground_truth_establishment",
                "description": "Establish ground truth statements",
                "truths": str(ground_truths),
            }
        )
        reasoning_trace.append(f"Established {len(ground_truths)} ground truth statements")

        # Step 4: Build logical inferences
        logger.debug("absolute_zero.building_inferences", levels=self.inference_levels)
        inferences = await self._build_logical_inferences(context, ground_truths, principles)
        steps.append(
            {
                "type": "logical_inference",
                "description": "Build logical inferences from ground truth",
                "inference_count": str(len(inferences)),
            }
        )
        reasoning_trace.append(f"Built {len(inferences)} logical inferences")

        # Step 5: Validate reasoning
        if self.validation_enabled:
            logger.debug("absolute_zero.validating")
            validation_result = await self._validate_reasoning(inferences, principles)
            steps.append(
                {
                    "type": "validation_verification",
                    "description": "Validate reasoning through verification",
                    "validated": str(validation_result),
                }
            )
            reasoning_trace.append(f"Validation: {'PASSED' if validation_result else 'PARTIAL'}")
        else:
            validation_result = True

        # Step 6: Synthesize solution
        logger.debug("absolute_zero.synthesizing")
        solution = await self._synthesize_solution(context, inferences, principles)
        steps.append(
            {
                "type": "solution_synthesis",
                "description": "Synthesize verified inferences into solution",
            }
        )
        reasoning_trace.append("Synthesized final solution from verified inferences")

        # Calculate confidence
        confidence = 0.95 if validation_result else 0.85

        return ReasoningResult(
            strategy_used=ReasoningStrategy.ABSOLUTE_ZERO,
            response=solution,
            steps=steps,
            confidence=confidence,
            reasoning_trace=reasoning_trace,
            metadata={
                "principle_count": len(principles),
                "inference_count": len(inferences),
                "validated": validation_result,
            },
        )

    async def _extract_fundamental_principles(self, context: ReasoningContext) -> list[str]:
        """Extract fundamental cybersecurity principles relevant to the query."""
        prompt = f"""Identify the fundamental cybersecurity principles that apply to this query.
Focus on first-principles thinking - what are the most basic, foundational concepts?

Query: {context.query}

List 3-5 fundamental principles as a numbered list."""

        try:
            response = await self.client.generate(prompt, temperature=0.15, max_tokens=300)
            principles = [
                line.strip().split(". ", 1)[1] if ". " in line else line.strip()
                for line in response.split("\n")
                if line.strip() and any(c.isdigit() for c in line[:3])
            ]
            return (
                principles[: self.axiom_depth]
                if principles
                else [
                    "Confidentiality, Integrity, and Availability (CIA triad)",
                    "Defense in depth",
                    "Least privilege principle",
                ]
            )
        except Exception as e:
            logger.error("absolute_zero.principle_extraction_failed", error=str(e))
            return [
                "Confidentiality, Integrity, and Availability (CIA triad)",
                "Defense in depth",
                "Least privilege principle",
            ]

    async def _decompose_concepts(
        self, context: ReasoningContext, principles: list[str]
    ) -> list[str]:
        """Decompose complex concepts into simpler base elements."""
        principles_text = "\n".join([f"- {p}" for p in principles])

        prompt = f"""Break down this cybersecurity query into its most basic components.
Decompose complex concepts into simpler, fundamental elements.

Query: {context.query}

Principles to consider:
{principles_text}

List 4-6 base components as a numbered list."""

        try:
            response = await self.client.generate(prompt, temperature=0.2, max_tokens=300)
            components = [
                line.strip().split(". ", 1)[1] if ". " in line else line.strip()
                for line in response.split("\n")
                if line.strip() and any(c.isdigit() for c in line[:3])
            ]
            return (
                components[:6]
                if components
                else ["Threat actors", "Attack vectors", "Assets", "Vulnerabilities"]
            )
        except Exception as e:
            logger.error("absolute_zero.decomposition_failed", error=str(e))
            return ["Threat actors", "Attack vectors", "Assets", "Vulnerabilities"]

    async def _establish_ground_truth(
        self, context: ReasoningContext, principles: list[str], decomposition: list[str]
    ) -> list[str]:
        """Establish ground truth statements based on principles and decomposition."""
        principles_text = "\n".join([f"- {p}" for p in principles])
        decomposition_text = "\n".join([f"- {d}" for d in decomposition])

        prompt = f"""Based on these fundamental principles and components, establish ground truth statements.
These should be indisputable facts that we can build upon.

Query: {context.query}

Principles:
{principles_text}

Components:
{decomposition_text}

List 3-5 ground truth statements as a numbered list."""

        try:
            response = await self.client.generate(prompt, temperature=0.15, max_tokens=300)
            truths = [
                line.strip().split(". ", 1)[1] if ". " in line else line.strip()
                for line in response.split("\n")
                if line.strip() and any(c.isdigit() for c in line[:3])
            ]
            return (
                truths[:5]
                if truths
                else ["Systems have vulnerabilities", "Attackers seek to exploit weaknesses"]
            )
        except Exception as e:
            logger.error("absolute_zero.ground_truth_failed", error=str(e))
            return ["Systems have vulnerabilities", "Attackers seek to exploit weaknesses"]

    async def _build_logical_inferences(
        self, context: ReasoningContext, ground_truths: list[str], principles: list[str]
    ) -> list[str]:
        """Build logical inferences from ground truth statements."""
        truths_text = "\n".join([f"- {t}" for t in ground_truths])
        principles_text = "\n".join([f"- {p}" for p in principles])

        prompt = f"""From these ground truth statements, build logical inferences that help answer the query.
Each inference should follow logically from the ground truths.

Query: {context.query}

Ground Truths:
{truths_text}

Principles:
{principles_text}

List {self.inference_levels} logical inferences as a numbered list."""

        try:
            response = await self.client.generate(prompt, temperature=0.2, max_tokens=400)
            inferences = [
                line.strip().split(". ", 1)[1] if ". " in line else line.strip()
                for line in response.split("\n")
                if line.strip() and any(c.isdigit() for c in line[:3])
            ]
            return (
                inferences[: self.inference_levels]
                if inferences
                else [
                    "Security requires multiple layers of defense",
                    "Prevention is more efficient than detection",
                ]
            )
        except Exception as e:
            logger.error("absolute_zero.inference_failed", error=str(e))
            return [
                "Security requires multiple layers of defense",
                "Prevention is more efficient than detection",
            ]

    async def _validate_reasoning(self, inferences: list[str], principles: list[str]) -> bool:
        """Validate that inferences are logically consistent with principles."""
        inferences_text = "\n".join([f"- {i}" for i in inferences])
        principles_text = "\n".join([f"- {p}" for p in principles])

        prompt = f"""Verify that these inferences are logically consistent with the fundamental principles.

Principles:
{principles_text}

Inferences:
{inferences_text}

Are all inferences logically consistent with the principles? Respond with YES or NO."""

        try:
            response = await self.client.generate(prompt, temperature=0.1, max_tokens=50)
            return "yes" in response.lower()
        except Exception as e:
            logger.error("absolute_zero.validation_failed", error=str(e))
            return False

    async def _synthesize_solution(
        self, context: ReasoningContext, inferences: list[str], principles: list[str]
    ) -> str:
        """Synthesize final solution from verified inferences."""
        inferences_text = "\n".join([f"{i+1}. {inf}" for i, inf in enumerate(inferences)])
        principles_text = "\n".join([f"- {p}" for p in principles])

        prompt = f"""Using these verified inferences and fundamental principles, provide a comprehensive answer to the query.

Query: {context.query}

Fundamental Principles:
{principles_text}

Verified Inferences:
{inferences_text}

Provide a clear, detailed answer that builds from first principles."""

        try:
            solution: str = await self.client.generate(prompt, temperature=0.2, max_tokens=600)
            return solution
        except Exception as e:
            logger.error("absolute_zero.synthesis_failed", error=str(e))
            return "Unable to synthesize solution from first principles."
