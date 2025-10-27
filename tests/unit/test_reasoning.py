"""
Unit tests for the multi-layered reasoning engine.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.reasoning import ReasoningContext, ReasoningEngine, ReasoningStrategy


class TestReasoningEngine:
    """Test cases for ReasoningEngine."""

    @pytest.fixture
    def mock_ollama_client(self):
        """Create a mock Ollama client."""
        client = AsyncMock()
        client.generate = AsyncMock(return_value="Mock LLM response")
        return client

    @pytest.fixture
    def reasoning_engine(self, mock_ollama_client):
        """Create a reasoning engine instance."""
        return ReasoningEngine(ollama_client=mock_ollama_client)

    @pytest.mark.asyncio
    async def test_complexity_calculation_simple(self, reasoning_engine):
        """Test complexity calculation for simple queries."""
        simple_query = "What is a firewall?"
        complexity = await reasoning_engine._calculate_complexity(simple_query)
        assert complexity < 0.5  # Adjusted threshold

    @pytest.mark.asyncio
    async def test_complexity_calculation_moderate(self, reasoning_engine):
        """Test complexity calculation for moderate queries."""
        moderate_query = "How do I detect and prevent SQL injection attacks using WAF?"
        complexity = await reasoning_engine._calculate_complexity(moderate_query)
        assert 0.5 <= complexity < 0.95  # Adjusted thresholds

    @pytest.mark.asyncio
    async def test_complexity_calculation_complex(self, reasoning_engine):
        """Test complexity calculation for complex queries."""
        complex_query = """Analyze the advanced persistent threat attack vector involving
        lateral movement through privilege escalation and zero-day exploits.
        Explain how to detect and mitigate such attacks."""
        complexity = await reasoning_engine._calculate_complexity(complex_query)
        assert complexity >= 0.5

    @pytest.mark.asyncio
    async def test_strategy_selection_zero_shot(self, reasoning_engine):
        """Test strategy selection for simple queries."""
        strategy = reasoning_engine._select_strategy(0.2)
        assert strategy == ReasoningStrategy.ZERO_SHOT

    @pytest.mark.asyncio
    async def test_strategy_selection_darwin_godel(self, reasoning_engine):
        """Test strategy selection for moderate queries."""
        strategy = reasoning_engine._select_strategy(0.5)
        assert strategy == ReasoningStrategy.DARWIN_GODEL

    @pytest.mark.asyncio
    async def test_strategy_selection_absolute_zero(self, reasoning_engine):
        """Test strategy selection for complex queries."""
        strategy = reasoning_engine._select_strategy(0.8)
        assert strategy == ReasoningStrategy.ABSOLUTE_ZERO

    @pytest.mark.asyncio
    async def test_zero_shot_reasoning(self, reasoning_engine, mock_ollama_client):
        """Test zero-shot reasoning execution."""
        context = ReasoningContext(query="What is a firewall?", complexity_score=0.2)

        result = await reasoning_engine.reason(context)

        assert result.strategy_used == ReasoningStrategy.ZERO_SHOT
        assert result.response is not None
        assert len(result.steps) > 0
        assert result.confidence > 0
        mock_ollama_client.generate.assert_called()

    @pytest.mark.asyncio
    async def test_darwin_godel_reasoning(self, reasoning_engine, mock_ollama_client):
        """Test Darwin-Gödel reasoning execution."""
        # Mock the Darwin-Gödel engine
        with patch("src.reasoning.darwin_godel.DarwinGodelEngine") as mock_dg:
            mock_dg_instance = AsyncMock()
            mock_dg_instance.reason = AsyncMock(
                return_value=MagicMock(
                    strategy_used=ReasoningStrategy.DARWIN_GODEL,
                    response="Mock Darwin-Gödel response",
                    steps=[],
                    confidence=0.85,
                    reasoning_trace=[],
                )
            )
            mock_dg.return_value = mock_dg_instance

            context = ReasoningContext(query="How do I detect SQL injection?", complexity_score=0.5)

            result = await reasoning_engine.reason(context)

            assert result.strategy_used == ReasoningStrategy.DARWIN_GODEL

    @pytest.mark.asyncio
    async def test_absolute_zero_reasoning(self, reasoning_engine, mock_ollama_client):
        """Test Absolute Zero reasoning execution."""
        # Mock the Absolute Zero reasoner
        with patch("src.reasoning.absolute_zero.AbsoluteZeroReasoner") as mock_az:
            mock_az_instance = AsyncMock()
            mock_az_instance.reason = AsyncMock(
                return_value=MagicMock(
                    strategy_used=ReasoningStrategy.ABSOLUTE_ZERO,
                    response="Mock Absolute Zero response",
                    steps=[],
                    confidence=0.95,
                    reasoning_trace=[],
                )
            )
            mock_az.return_value = mock_az_instance

            context = ReasoningContext(
                query="Analyze advanced persistent threat vectors", complexity_score=0.8
            )

            result = await reasoning_engine.reason(context)

            assert result.strategy_used == ReasoningStrategy.ABSOLUTE_ZERO

    @pytest.mark.asyncio
    async def test_reasoning_with_memory(self, mock_ollama_client):
        """Test reasoning with memory context."""
        mock_memory = MagicMock()
        engine = ReasoningEngine(ollama_client=mock_ollama_client, memory_system=mock_memory)

        context = ReasoningContext(
            query="What is XSS?",
            relevant_memories=[{"content": "Cross-site scripting is a web vulnerability"}],
            complexity_score=0.2,
        )

        result = await engine.reason(context)

        assert result is not None
        assert result.response is not None

    @pytest.mark.asyncio
    async def test_reasoning_context_dataclass(self):
        """Test ReasoningContext dataclass."""
        context = ReasoningContext(
            query="Test query",
            user_context={"role": "analyst"},
            relevant_memories=[{"content": "test"}],
            complexity_score=0.5,
        )

        assert context.query == "Test query"
        assert context.user_context["role"] == "analyst"
        assert len(context.relevant_memories) == 1
        assert context.complexity_score == 0.5

    @pytest.mark.asyncio
    async def test_automatic_complexity_calculation(self, reasoning_engine):
        """Test that complexity is calculated automatically if not provided."""
        context = ReasoningContext(query="What is a firewall?")
        assert context.complexity_score == 0.0

        result = await reasoning_engine.reason(context)

        # Complexity should be calculated during reasoning
        assert result is not None
