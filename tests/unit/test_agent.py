"""Tests for ReAct agent."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.agent.model import OllamaModel
from src.agent.react_agent import ReactAgent
from src.models.schemas import AgentRequest, AgentResponse


@pytest.fixture
def mock_model():
    """Create a mock Ollama model."""
    model = AsyncMock(spec=OllamaModel)
    model.infer = AsyncMock(
        return_value='Thought: Test thought\nAction: scan_environment\nAction Input: {"scan_type": "ports", "target": "localhost"}'
    )
    model.close = AsyncMock()
    return model


@pytest.fixture
def mock_tools():
    """Create mock tools."""
    scan_tool = MagicMock()
    scan_tool.execute = AsyncMock(
        return_value={
            "success": True,
            "findings": [{"port": 80, "status": "open"}],
            "vulnerabilities_count": 1,
            "risk_score": 0.1,
        }
    )
    scan_tool.description = "Scan environment"
    scan_tool.get_parameters = MagicMock(return_value={})

    threat_tool = MagicMock()
    threat_tool.execute = AsyncMock(
        return_value={
            "success": True,
            "results": [{"content": "Test threat", "source": "MITRE"}],
        }
    )
    threat_tool.description = "Query threat intel"
    threat_tool.get_parameters = MagicMock(return_value={})

    propose_tool = MagicMock()
    propose_tool.execute = AsyncMock(
        return_value={
            "success": True,
            "action_id": "test_123",
            "status": "pending_approval",
        }
    )
    propose_tool.description = "Propose action"
    propose_tool.get_parameters = MagicMock(return_value={})

    return {
        "scan_environment": scan_tool,
        "query_threat_intel": threat_tool,
        "propose_action": propose_tool,
    }


class TestReactAgent:
    """Test ReAct agent functionality."""

    @pytest.mark.asyncio
    async def test_agent_initialization(self, mock_model, mock_tools):
        """Test agent can be initialized."""
        agent = ReactAgent(mock_model, mock_tools)
        assert agent.model == mock_model
        assert agent.tools == mock_tools
        assert agent.max_iterations == 2
        assert agent.max_exec_time == 45

    @pytest.mark.asyncio
    async def test_agent_run_success(self, mock_model, mock_tools):
        """Test successful agent execution."""
        agent = ReactAgent(mock_model, mock_tools, max_iterations=1)
        request = AgentRequest(
            instruction="Scan localhost for open ports",
            mode="passive",
            scan_duration=10,
        )

        result = await agent.run(request)

        assert isinstance(result, AgentResponse)
        assert len(result.steps) > 0
        assert result.confidence > 0

    @pytest.mark.asyncio
    async def test_agent_passive_mode_default(self, mock_model, mock_tools):
        """Test agent defaults to passive mode."""
        _ = ReactAgent(mock_model, mock_tools)
        request = AgentRequest(
            instruction="Test instruction",
            scan_duration=10,
        )

        # The request should default to passive mode
        assert request.mode == "passive"

    @pytest.mark.asyncio
    async def test_agent_max_iterations(self, mock_model, mock_tools):
        """Test agent respects max iterations."""
        agent = ReactAgent(mock_model, mock_tools, max_iterations=2)
        request = AgentRequest(
            instruction="Test",
            mode="passive",
        )

        result = await agent.run(request)

        # Should not exceed max iterations
        assert len(result.steps) <= 2

    @pytest.mark.asyncio
    async def test_agent_handles_errors(self, mock_model, mock_tools):
        """Test agent handles errors gracefully."""
        mock_model.infer = AsyncMock(side_effect=Exception("Test error"))
        agent = ReactAgent(mock_model, mock_tools)
        request = AgentRequest(
            instruction="Test",
            mode="passive",
        )

        result = await agent.run(request)

        assert "failed" in result.summary.lower()
        assert result.confidence == 0.0

    def test_parse_response_valid(self, mock_model, mock_tools):
        """Test parsing valid response."""
        agent = ReactAgent(mock_model, mock_tools)
        response = 'Thought: Test\nAction: scan_environment\nAction Input: {"target": "localhost"}'

        thought, action, action_input = agent._parse_response(response)

        assert thought == "Test"
        assert action == "scan_environment"
        assert isinstance(action_input, dict)

    def test_parse_response_final_answer(self, mock_model, mock_tools):
        """Test parsing final answer response."""
        agent = ReactAgent(mock_model, mock_tools)
        response = "Thought: Complete\nAnswer: All done"

        thought, action, action_input = agent._parse_response(response)

        assert thought == "Complete"
        assert action is None


class TestAgentModel:
    """Test Ollama model wrapper."""

    @pytest.mark.asyncio
    async def test_model_initialization(self):
        """Test model can be initialized."""
        with patch("src.agent.model.httpx.AsyncClient"):
            model = OllamaModel()
            assert model.base_url is not None
            assert model.model is not None
            assert model.timeout == 300

    @pytest.mark.asyncio
    async def test_model_infer_with_params(self):
        """Test inference with custom parameters."""
        with patch("src.agent.model.httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = {"response": "Test response", "done": True}
            mock_client.return_value.post = AsyncMock(return_value=mock_response)

            model = OllamaModel()
            result = await model.infer(
                prompt="Test",
                temperature=0.1,
                top_p=0.9,
                num_ctx=1536,
            )

            assert result == "Test response"
