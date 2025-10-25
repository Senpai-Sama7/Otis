"""Security policy enforcement for risk assessment and approval gates."""

import re
from enum import Enum
from typing import Dict, List, Optional

from src.core.logging import get_logger

logger = get_logger(__name__)


class RiskLevel(str, Enum):
    """Risk levels for actions."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskPolicy:
    """
    Risk policy for cybersecurity operations.
    
    Risk Levels:
    - LOW: Read-only operations, logging, queries
    - MEDIUM: Active scanning, network changes (non-destructive)
    - HIGH: Offensive operations, code execution, destructive changes
    - CRITICAL: System-level changes, privileged operations
    """

    # Operations that require approval
    REQUIRES_APPROVAL = [RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]

    # Denylist patterns (blocked by default)
    DENYLIST = [
        r"wireless.*injection",
        r"traffic.*disruption",
        r"dos\s+attack",
        r"ddos",
        r"exploit.*kernel",
        r"privilege.*escalation",
        r"rm\s+-rf\s+/",
        r"format\s+/dev/",
        r"dd\s+if=/dev/zero",
        r":(){ :|:& };:",  # Fork bomb
    ]

    # Allowlist patterns (safe operations)
    ALLOWLIST = [
        r"port.*scan",
        r"nmap.*-sT",  # TCP connect scan
        r"vulnerability.*scan",
        r"log.*analysis",
        r"query.*database",
        r"read.*file",
        r"check.*status",
    ]

    @staticmethod
    def evaluate_risk(
        action_type: str,
        code: Optional[str] = None,
        description: Optional[str] = None,
    ) -> RiskLevel:
        """
        Evaluate the risk level of an action.

        Args:
            action_type: Type of action (scan, patch, configure, etc.)
            code: Optional code to execute
            description: Optional description

        Returns:
            Risk level (LOW, MEDIUM, HIGH, CRITICAL)
        """
        logger.info("Evaluating risk", action_type=action_type)

        # Check denylist first
        if code:
            for pattern in RiskPolicy.DENYLIST:
                if re.search(pattern, code, re.IGNORECASE):
                    logger.warning("Denylist pattern matched", pattern=pattern)
                    return RiskLevel.CRITICAL

        # Evaluate based on action type
        action_lower = action_type.lower()

        # Low-risk operations
        if any(
            term in action_lower
            for term in ["read", "query", "log", "check", "view", "list"]
        ):
            return RiskLevel.LOW

        # Medium-risk operations
        if any(
            term in action_lower
            for term in ["scan", "probe", "detect", "analyze", "monitor"]
        ):
            # Active scanning is medium risk
            if code and "active" in code.lower():
                return RiskLevel.MEDIUM
            return RiskLevel.LOW

        # High-risk operations
        if any(
            term in action_lower
            for term in [
                "patch",
                "configure",
                "modify",
                "update",
                "execute",
                "run",
                "deploy",
            ]
        ):
            return RiskLevel.HIGH

        # Critical operations
        if any(
            term in action_lower
            for term in [
                "delete",
                "remove",
                "destroy",
                "exploit",
                "attack",
                "inject",
                "escalate",
            ]
        ):
            return RiskLevel.CRITICAL

        # Default to high risk for unknown operations
        logger.warning("Unknown action type, defaulting to HIGH risk", action_type=action_type)
        return RiskLevel.HIGH

    @staticmethod
    def requires_approval(risk_level: RiskLevel) -> bool:
        """
        Check if an action requires human approval.

        Args:
            risk_level: Risk level

        Returns:
            True if approval required
        """
        return risk_level in RiskPolicy.REQUIRES_APPROVAL

    @staticmethod
    def is_allowed(code: str) -> bool:
        """
        Check if code is allowed by the allowlist.

        Args:
            code: Code to check

        Returns:
            True if allowed
        """
        # Check denylist first
        for pattern in RiskPolicy.DENYLIST:
            if re.search(pattern, code, re.IGNORECASE):
                logger.warning("Code blocked by denylist", pattern=pattern)
                return False

        # Check allowlist
        for pattern in RiskPolicy.ALLOWLIST:
            if re.search(pattern, code, re.IGNORECASE):
                return True

        # If not in allowlist, default to requiring approval
        return False

    @staticmethod
    def check_wireless_injection(code: str) -> bool:
        """
        Check if code contains wireless injection attempts.

        Args:
            code: Code to check

        Returns:
            True if wireless injection detected
        """
        wireless_patterns = [
            r"aircrack",
            r"aireplay",
            r"airodump",
            r"wireless.*injection",
            r"packet.*injection",
            r"monitor.*mode",
            r"iwconfig.*mode.*monitor",
        ]

        for pattern in wireless_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                logger.warning("Wireless injection detected", pattern=pattern)
                return True

        return False


def evaluate_risk(
    action_type: str,
    code: Optional[str] = None,
    description: Optional[str] = None,
) -> str:
    """
    Convenience function to evaluate risk.

    Args:
        action_type: Type of action
        code: Optional code
        description: Optional description

    Returns:
        Risk level as string
    """
    policy = RiskPolicy()
    risk_level = policy.evaluate_risk(action_type, code, description)
    return risk_level.value


def check_allowlist(code: str) -> bool:
    """
    Convenience function to check allowlist.

    Args:
        code: Code to check

    Returns:
        True if allowed
    """
    policy = RiskPolicy()
    return policy.is_allowed(code)


class ApprovalGate:
    """
    Approval gate for managing action approvals.
    """

    def __init__(self):
        self.pending_approvals: Dict[str, Dict] = {}

    def request_approval(
        self,
        action_id: str,
        action_type: str,
        risk_level: RiskLevel,
        code: Optional[str] = None,
        rationale: Optional[str] = None,
    ) -> None:
        """
        Request approval for an action.

        Args:
            action_id: Unique action ID
            action_type: Type of action
            risk_level: Risk level
            code: Optional code
            rationale: Optional rationale
        """
        self.pending_approvals[action_id] = {
            "action_type": action_type,
            "risk_level": risk_level,
            "code": code,
            "rationale": rationale,
            "status": "pending",
        }
        logger.info("Approval requested", action_id=action_id, risk_level=risk_level)

    def approve(self, action_id: str) -> bool:
        """
        Approve an action.

        Args:
            action_id: Action ID

        Returns:
            True if approved
        """
        if action_id in self.pending_approvals:
            self.pending_approvals[action_id]["status"] = "approved"
            logger.info("Action approved", action_id=action_id)
            return True
        return False

    def deny(self, action_id: str, reason: Optional[str] = None) -> bool:
        """
        Deny an action.

        Args:
            action_id: Action ID
            reason: Optional denial reason

        Returns:
            True if denied
        """
        if action_id in self.pending_approvals:
            self.pending_approvals[action_id]["status"] = "denied"
            self.pending_approvals[action_id]["denial_reason"] = reason
            logger.info("Action denied", action_id=action_id, reason=reason)
            return True
        return False

    def get_status(self, action_id: str) -> Optional[str]:
        """
        Get approval status.

        Args:
            action_id: Action ID

        Returns:
            Status or None
        """
        if action_id in self.pending_approvals:
            return self.pending_approvals[action_id]["status"]
        return None

    def list_pending(self) -> List[Dict]:
        """
        List all pending approvals.

        Returns:
            List of pending approval dictionaries
        """
        return [
            {"action_id": aid, **details}
            for aid, details in self.pending_approvals.items()
            if details["status"] == "pending"
        ]
