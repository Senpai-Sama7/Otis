"""
Advanced multi-layered reasoning engine for cybersecurity analysis.

This module provides three distinct reasoning strategies:
1. Zero-Shot: Simple, direct responses for straightforward queries
2. Darwin-Gödel: Evolutionary problem-solving with formal verification
3. Absolute Zero: First-principles reasoning from fundamental axioms
"""

from src.reasoning.reasoning_engine import (
    ReasoningContext,
    ReasoningEngine,
    ReasoningResult,
    ReasoningStrategy,
)

__all__ = [
    "ReasoningContext",
    "ReasoningEngine",
    "ReasoningResult",
    "ReasoningStrategy",
]
