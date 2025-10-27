"""Tests for security policy."""

import pytest

from src.security.policy import (
    ApprovalGate,
    RiskLevel,
    RiskPolicy,
    check_allowlist,
    evaluate_risk,
)


class TestRiskPolicy:
    """Test risk policy enforcement."""

    def test_evaluate_risk_low(self):
        """Test low-risk operations."""
        risk = RiskPolicy.evaluate_risk(action_type="read_log")
        assert risk == RiskLevel.LOW

        risk = RiskPolicy.evaluate_risk(action_type="query_database")
        assert risk == RiskLevel.LOW

    def test_evaluate_risk_medium(self):
        """Test medium-risk operations."""
        risk = RiskPolicy.evaluate_risk(
            action_type="scan_network", code="nmap -sT localhost"
        )
        assert risk in [RiskLevel.LOW, RiskLevel.MEDIUM]

    def test_evaluate_risk_high(self):
        """Test high-risk operations."""
        risk = RiskPolicy.evaluate_risk(action_type="patch_system")
        assert risk == RiskLevel.HIGH

        risk = RiskPolicy.evaluate_risk(action_type="modify_config")
        assert risk == RiskLevel.HIGH

    def test_evaluate_risk_critical(self):
        """Test critical-risk operations."""
        risk = RiskPolicy.evaluate_risk(action_type="delete_files")
        assert risk == RiskLevel.CRITICAL

        risk = RiskPolicy.evaluate_risk(action_type="exploit_vulnerability")
        assert risk == RiskLevel.CRITICAL

    def test_denylist_blocks_dangerous_operations(self):
        """Test denylist blocks dangerous operations."""
        risk = RiskPolicy.evaluate_risk(
            action_type="scan", code="wireless injection attack"
        )
        assert risk == RiskLevel.CRITICAL

        risk = RiskPolicy.evaluate_risk(
            action_type="network", code="traffic disruption ddos"
        )
        assert risk == RiskLevel.CRITICAL

    def test_requires_approval(self):
        """Test approval requirements."""
        assert not RiskPolicy.requires_approval(RiskLevel.LOW)
        assert RiskPolicy.requires_approval(RiskLevel.MEDIUM)
        assert RiskPolicy.requires_approval(RiskLevel.HIGH)
        assert RiskPolicy.requires_approval(RiskLevel.CRITICAL)

    def test_allowlist_permits_safe_operations(self):
        """Test allowlist permits safe operations."""
        assert RiskPolicy.is_allowed("port scan localhost")
        assert RiskPolicy.is_allowed("nmap -sT 192.168.1.1")
        assert RiskPolicy.is_allowed("vulnerability scan target")

    def test_wireless_injection_detection(self):
        """Test wireless injection detection."""
        assert RiskPolicy.check_wireless_injection("aircrack-ng wlan0")
        assert RiskPolicy.check_wireless_injection("aireplay-ng --deauth")
        assert not RiskPolicy.check_wireless_injection("nmap -sT localhost")

    def test_evaluate_risk_convenience_function(self):
        """Test convenience function."""
        risk = evaluate_risk(action_type="read", code="cat /etc/passwd")
        assert risk in ["low", "medium", "high", "critical"]

    def test_check_allowlist_convenience_function(self):
        """Test allowlist convenience function."""
        assert check_allowlist("port scan") is True or check_allowlist("port scan") is False


class TestApprovalGate:
    """Test approval gate functionality."""

    def test_request_approval(self):
        """Test approval request."""
        gate = ApprovalGate()
        gate.request_approval(
            action_id="test_123",
            action_type="patch",
            risk_level=RiskLevel.HIGH,
            code="apt-get update",
            rationale="Security update required",
        )

        assert "test_123" in gate.pending_approvals
        assert gate.pending_approvals["test_123"]["status"] == "pending"

    def test_approve_action(self):
        """Test approving an action."""
        gate = ApprovalGate()
        gate.request_approval(
            action_id="test_123",
            action_type="patch",
            risk_level=RiskLevel.HIGH,
        )

        success = gate.approve("test_123")

        assert success is True
        assert gate.pending_approvals["test_123"]["status"] == "approved"

    def test_deny_action(self):
        """Test denying an action."""
        gate = ApprovalGate()
        gate.request_approval(
            action_id="test_123",
            action_type="patch",
            risk_level=RiskLevel.HIGH,
        )

        success = gate.deny("test_123", reason="Not authorized")

        assert success is True
        assert gate.pending_approvals["test_123"]["status"] == "denied"
        assert gate.pending_approvals["test_123"]["denial_reason"] == "Not authorized"

    def test_get_status(self):
        """Test getting approval status."""
        gate = ApprovalGate()
        gate.request_approval(
            action_id="test_123",
            action_type="patch",
            risk_level=RiskLevel.HIGH,
        )

        status = gate.get_status("test_123")
        assert status == "pending"

        gate.approve("test_123")
        status = gate.get_status("test_123")
        assert status == "approved"

    def test_list_pending(self):
        """Test listing pending approvals."""
        gate = ApprovalGate()
        gate.request_approval(
            action_id="test_1",
            action_type="patch",
            risk_level=RiskLevel.HIGH,
        )
        gate.request_approval(
            action_id="test_2",
            action_type="scan",
            risk_level=RiskLevel.MEDIUM,
        )
        gate.approve("test_1")

        pending = gate.list_pending()

        assert len(pending) == 1
        assert pending[0]["action_id"] == "test_2"

    def test_approve_nonexistent_action(self):
        """Test approving nonexistent action returns False."""
        gate = ApprovalGate()
        success = gate.approve("nonexistent")
        assert success is False

    def test_deny_nonexistent_action(self):
        """Test denying nonexistent action returns False."""
        gate = ApprovalGate()
        success = gate.deny("nonexistent")
        assert success is False

    def test_get_status_nonexistent(self):
        """Test getting status of nonexistent action returns None."""
        gate = ApprovalGate()
        status = gate.get_status("nonexistent")
        assert status is None
