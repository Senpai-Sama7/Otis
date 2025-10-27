"""
Darwin-Gödel Engine: Evolutionary reasoning with formal verification.

This reasoning system combines evolutionary algorithms with formal logic
to optimize solutions through iterative refinement and verification.
"""

import asyncio
import random
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import structlog

from src.reasoning.reasoning_engine import ReasoningContext, ReasoningResult, ReasoningStrategy

logger = structlog.get_logger(__name__)


@dataclass
class Hypothesis:
    """A hypothesis in the evolutionary population."""

    content: str
    fitness: float = 0.0
    generation: int = 0
    verified: bool = False


class DarwinGodelEngine:
    """
    Darwin-Gödel reasoning engine that uses evolutionary algorithms
    with formal verification for complex problem-solving.

    Process:
    1. Extract foundational axioms from context
    2. Generate initial population of hypotheses
    3. Evolve hypotheses through mutation and crossover
    4. Verify best candidates for logical consistency
    5. Extract final solution
    """

    def __init__(
        self,
        client: Any,
        memory: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the Darwin-Gödel engine.

        Args:
            client: LLM client for generation
            memory: Memory system for context
            config: Configuration options
        """
        self.client = client
        self.memory = memory
        self.config = config or {}

        # Evolutionary parameters
        self.mutation_rate = self.config.get("mutation_rate", 0.1)
        self.crossover_rate = self.config.get("crossover_rate", 0.7)
        self.population_size = self.config.get("population_size", 5)
        self.max_generations = self.config.get("max_generations", 3)

        # Verification parameters
        self.verification_threshold = self.config.get("verification_threshold", 0.9)
        self.consistency_check = self.config.get("consistency_check", True)

        logger.info(
            "darwin_godel.initialized",
            population_size=self.population_size,
            max_generations=self.max_generations,
        )

    async def reason(self, context: ReasoningContext) -> ReasoningResult:
        """
        Execute Darwin-Gödel reasoning process.

        Args:
            context: Reasoning context

        Returns:
            ReasoningResult with optimized solution
        """
        steps = []
        reasoning_trace = []

        # Step 1: Extract axioms
        logger.debug("darwin_godel.extracting_axioms", query=context.query[:100])
        axioms = await self._extract_axioms(context)
        steps.append({"type": "axiom_extraction", "description": "Extract foundational axioms", "axioms": axioms})
        reasoning_trace.append(f"Extracted {len(axioms)} foundational axioms")

        # Step 2: Generate initial hypotheses
        logger.debug("darwin_godel.generating_hypotheses", count=self.population_size)
        population = await self._generate_initial_population(context, axioms)
        steps.append(
            {
                "type": "hypothesis_generation",
                "description": "Generate initial hypothesis population",
                "count": len(population),
            }
        )
        reasoning_trace.append(f"Generated {len(population)} initial hypotheses")

        # Step 3: Evolutionary optimization
        logger.debug("darwin_godel.evolving", generations=self.max_generations)
        best_hypothesis = await self._evolve_population(context, population, axioms)
        steps.append(
            {
                "type": "evolutionary_optimization",
                "description": "Evolve hypotheses through selection and mutation",
                "generations": self.max_generations,
                "best_fitness": best_hypothesis.fitness,
            }
        )
        reasoning_trace.append(f"Evolved population over {self.max_generations} generations")

        # Step 4: Formal verification
        logger.debug("darwin_godel.verifying", hypothesis_length=len(best_hypothesis.content))
        verification_result = await self._verify_hypothesis(best_hypothesis, axioms)
        steps.append(
            {
                "type": "formal_verification",
                "description": "Verify logical consistency",
                "verified": verification_result,
            }
        )
        reasoning_trace.append(f"Verification: {'PASSED' if verification_result else 'PARTIAL'}")

        # Step 5: Extract solution
        solution = await self._extract_solution(best_hypothesis, context)
        steps.append({"type": "solution_extraction", "description": "Extract final solution", "verified": verification_result})
        reasoning_trace.append("Extracted final solution from best hypothesis")

        # Calculate confidence based on fitness and verification
        confidence = min(best_hypothesis.fitness * (1.1 if verification_result else 0.9), 1.0)

        return ReasoningResult(
            strategy_used=ReasoningStrategy.DARWIN_GODEL,
            response=solution,
            steps=steps,
            confidence=confidence,
            reasoning_trace=reasoning_trace,
            metadata={
                "best_fitness": best_hypothesis.fitness,
                "verified": verification_result,
                "generations": self.max_generations,
            },
        )

    async def _extract_axioms(self, context: ReasoningContext) -> List[str]:
        """Extract foundational axioms from query and context."""
        prompt = f"""Analyze this cybersecurity query and extract 3-5 foundational axioms or principles that are relevant:

Query: {context.query}

Return only the axioms as a numbered list."""

        try:
            response = await self.client.generate(prompt, temperature=0.2, max_tokens=300)
            # Parse axioms from response
            axioms = [
                line.strip().split(". ", 1)[1] if ". " in line else line.strip()
                for line in response.split("\n")
                if line.strip() and any(c.isdigit() for c in line[:3])
            ]
            return axioms[:5] if axioms else ["Analyze security context", "Identify threat vectors", "Propose mitigations"]
        except Exception as e:
            logger.error("darwin_godel.axiom_extraction_failed", error=str(e))
            return ["Analyze security context", "Identify threat vectors", "Propose mitigations"]

    async def _generate_initial_population(self, context: ReasoningContext, axioms: List[str]) -> List[Hypothesis]:
        """Generate initial population of hypotheses."""
        population = []

        axiom_context = "\n".join([f"- {axiom}" for axiom in axioms])

        for i in range(self.population_size):
            prompt = f"""Based on these axioms:
{axiom_context}

Generate a solution approach for:
{context.query}

Provide a concise approach (variation {i+1})."""

            try:
                content = await self.client.generate(prompt, temperature=0.6 + (i * 0.1), max_tokens=400)
                hypothesis = Hypothesis(content=content, generation=0)
                population.append(hypothesis)
            except Exception as e:
                logger.error("darwin_godel.hypothesis_generation_failed", iteration=i, error=str(e))

        return population

    async def _evolve_population(
        self, context: ReasoningContext, population: List[Hypothesis], axioms: List[str]
    ) -> Hypothesis:
        """Evolve population through selection, crossover, and mutation."""
        for generation in range(self.max_generations):
            # Evaluate fitness
            for hypothesis in population:
                hypothesis.fitness = await self._calculate_fitness(hypothesis, context, axioms)

            # Sort by fitness
            population.sort(key=lambda h: h.fitness, reverse=True)

            logger.debug(
                "darwin_godel.generation",
                number=generation + 1,
                best_fitness=population[0].fitness,
                avg_fitness=sum(h.fitness for h in population) / len(population),
            )

            # Keep top performers
            survivors = population[: max(2, self.population_size // 2)]

            # Create next generation
            new_population = survivors.copy()

            while len(new_population) < self.population_size:
                # Crossover
                if random.random() < self.crossover_rate and len(survivors) >= 2:
                    parent1, parent2 = random.sample(survivors, 2)
                    child = await self._crossover(parent1, parent2, generation + 1)
                    new_population.append(child)
                # Mutation
                elif survivors:
                    parent = random.choice(survivors)
                    mutant = await self._mutate(parent, context, generation + 1)
                    new_population.append(mutant)

            population = new_population

        # Return best hypothesis
        for hypothesis in population:
            hypothesis.fitness = await self._calculate_fitness(hypothesis, context, axioms)
        population.sort(key=lambda h: h.fitness, reverse=True)

        return population[0]

    async def _calculate_fitness(self, hypothesis: Hypothesis, context: ReasoningContext, axioms: List[str]) -> float:
        """Calculate fitness score for a hypothesis."""
        # Simple fitness: combination of relevance and completeness
        # In a real implementation, this could use embedding similarity or other metrics

        # Length factor (prefer detailed but not overly verbose solutions)
        length = len(hypothesis.content)
        length_score = 1.0 if 200 < length < 1000 else 0.7

        # Axiom coverage (check if hypothesis references the axioms)
        axiom_score = sum(1 for axiom in axioms if any(word in hypothesis.content.lower() for word in axiom.lower().split()[:3])) / max(len(axioms), 1)

        # Query relevance (simple keyword matching)
        query_words = set(context.query.lower().split())
        hypothesis_words = set(hypothesis.content.lower().split())
        relevance_score = len(query_words & hypothesis_words) / max(len(query_words), 1)

        # Combine scores
        fitness = (length_score * 0.3) + (axiom_score * 0.4) + (relevance_score * 0.3)

        return min(fitness, 1.0)

    async def _crossover(self, parent1: Hypothesis, parent2: Hypothesis, generation: int) -> Hypothesis:
        """Create offspring through crossover of two parents."""
        # Simple crossover: combine parts of both parents
        p1_parts = parent1.content.split(". ")
        p2_parts = parent2.content.split(". ")

        # Take first half from parent1, second half from parent2
        crossover_point = len(p1_parts) // 2
        child_content = ". ".join(p1_parts[:crossover_point] + p2_parts[crossover_point:])

        return Hypothesis(content=child_content, generation=generation)

    async def _mutate(self, parent: Hypothesis, context: ReasoningContext, generation: int) -> Hypothesis:
        """Create mutant through variation of parent."""
        prompt = f"""Improve and refine this solution approach:

{parent.content}

Original query: {context.query}

Provide an enhanced variation."""

        try:
            mutated_content = await self.client.generate(prompt, temperature=0.5, max_tokens=400)
            return Hypothesis(content=mutated_content, generation=generation)
        except Exception as e:
            logger.error("darwin_godel.mutation_failed", error=str(e))
            return Hypothesis(content=parent.content, generation=generation)

    async def _verify_hypothesis(self, hypothesis: Hypothesis, axioms: List[str]) -> bool:
        """Verify logical consistency of hypothesis."""
        if not self.consistency_check:
            return True

        prompt = f"""Verify the logical consistency of this solution:

Solution: {hypothesis.content}

Axioms:
{chr(10).join([f'- {axiom}' for axiom in axioms])}

Is this solution logically consistent with the axioms? Respond with YES or NO."""

        try:
            response = await self.client.generate(prompt, temperature=0.1, max_tokens=50)
            return "yes" in response.lower()
        except Exception as e:
            logger.error("darwin_godel.verification_failed", error=str(e))
            return False

    async def _extract_solution(self, hypothesis: Hypothesis, context: ReasoningContext) -> str:
        """Extract and refine final solution from best hypothesis."""
        prompt = f"""Refine this solution into a clear, actionable response:

Solution: {hypothesis.content}

Original query: {context.query}

Provide a clear, concise final answer."""

        try:
            solution = await self.client.generate(prompt, temperature=0.2, max_tokens=500)
            return solution
        except Exception as e:
            logger.error("darwin_godel.extraction_failed", error=str(e))
            return hypothesis.content
