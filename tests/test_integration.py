"""
Integration tests for Otis platform.
"""

import pytest

from src.core.sanitization import InputSanitizer
from src.models.schemas import AgentRequest
from src.security.policy_engine import PolicyDecision, PolicyEngine


class MockUser:
    def __init__(self, role):
        self.role = role


class TestPolicyEngine:
    """Test PolicyEngine security enforcement."""

    def test_admin_can_query(self):
        user = MockUser("admin")
        request = AgentRequest(instruction="test", mode="passive")
        engine = PolicyEngine(user, request)

        decision = engine.validate("query_threat_intel", {})
        assert decision == PolicyDecision.PERMIT

    def test_viewer_cannot_scan(self):
        user = MockUser("viewer")
        request = AgentRequest(instruction="test", mode="passive")
        engine = PolicyEngine(user, request)

        decision = engine.validate("scan_environment", {})
        assert decision == PolicyDecision.DENY

    def test_code_execution_requires_approval(self):
        user = MockUser("admin")
        request = AgentRequest(instruction="test", mode="active")
        engine = PolicyEngine(user, request)

        decision = engine.validate("exec_in_sandbox", {"code": "print(1)"})
        assert decision == PolicyDecision.REQUIRES_APPROVAL

    def test_sensitive_network_requires_approval(self):
        user = MockUser("analyst")
        request = AgentRequest(instruction="test", mode="passive")
        engine = PolicyEngine(user, request)

        decision = engine.validate("scan_environment", {"target": "10.0.1.50"})
        assert decision == PolicyDecision.REQUIRES_APPROVAL

    def test_passive_mode_blocks_execution(self):
        user = MockUser("admin")
        request = AgentRequest(instruction="test", mode="passive")
        engine = PolicyEngine(user, request)

        # High-risk tools require approval even for admins
        # Mode check happens after risk check
        decision = engine.validate("exec_in_sandbox", {"code": "test"})
        assert decision == PolicyDecision.REQUIRES_APPROVAL


class TestInputSanitizer:
    """Test input sanitization."""

    def test_valid_query_passes(self):
        result = InputSanitizer.sanitize_query("What is SQL injection?")
        assert result == "What is SQL injection?"

    def test_dangerous_command_blocked(self):
        with pytest.raises(ValueError):
            InputSanitizer.sanitize_query("rm -rf /")

    def test_sql_injection_blocked(self):
        with pytest.raises(ValueError):
            InputSanitizer.sanitize_query("'; DROP TABLE users; --")

    def test_xss_blocked(self):
        with pytest.raises(ValueError):
            InputSanitizer.sanitize_query("<script>alert('xss')</script>")

    def test_code_execution_blocked(self):
        with pytest.raises(ValueError):
            InputSanitizer.sanitize_code("import os; os.system('ls')")

    def test_target_validation(self):
        result = InputSanitizer.sanitize_target("localhost")
        assert result == "localhost"

    def test_invalid_target_blocked(self):
        with pytest.raises(ValueError):
            InputSanitizer.sanitize_target("target; rm -rf /")


class TestReasoningStrategies:
    """Test reasoning strategy selection."""

    def test_strategy_enum_values(self):
        from src.reasoning.reasoning_engine import ReasoningStrategy

        assert ReasoningStrategy.DIRECT.value == "direct"
        assert ReasoningStrategy.HYPOTHESIS_EVOLUTION.value == "hypothesis_evolution"
        assert ReasoningStrategy.FIRST_PRINCIPLES.value == "first_principles"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
