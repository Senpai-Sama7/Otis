"""
Policy Enforcement Point (PEP) for hard-coded security rules.

This replaces "policy-by-prompt" with actual code-enforced policies.
"""

from enum import Enum
from typing import Any

import structlog

from src.models.schemas import AgentRequest

logger = structlog.get_logger(__name__)


class PolicyDecision(Enum):
    """Policy decision outcomes."""

    PERMIT = "PERMIT"
    DENY = "DENY"
    REQUIRES_APPROVAL = "REQUIRES_APPROVAL"


def trace_policy_validation(func):
    """Decorator to trace policy validation."""
    import functools
    try:
        from opentelemetry import trace
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            tracer = trace.get_tracer(__name__)
            with tracer.start_as_current_span("policy.validate") as span:
                tool_name = kwargs.get("tool_name", args[1] if len(args) > 1 else "unknown")
                span.set_attribute("policy.tool", tool_name)
                
                try:
                    decision = func(*args, **kwargs)
                    span.set_attribute("policy.decision", decision.value)
                    return decision
                except Exception as e:
                    span.record_exception(e)
                    raise
        return wrapper
    except ImportError:
        return func


class PolicyEngine:
    """
    Hard-coded policy enforcement for agent actions.
    
    This is the critical security layer that prevents LLM prompt injection
    from bypassing security controls.
    """

    # Sensitive network ranges requiring approval
    SENSITIVE_NETWORKS = [
        "10.0.1.",
        "192.168.1.",
        "172.16.",
        "prod-",
        "production",
    ]

    # High-risk tool operations
    HIGH_RISK_TOOLS = [
        "exec_in_sandbox",
        "propose_action",
        "execute_code",
    ]

    def __init__(self, user: Any, request: AgentRequest):
        """
        Initialize policy engine.
        
        Args:
            user: Authenticated user with role attribute
            request: Original agent request
        """
        self.user = user
        self.request = request
        self.mode = request.mode if hasattr(request, "mode") else "passive"

    @trace_policy_validation
    def validate(self, tool_name: str, tool_params: dict[str, Any]) -> PolicyDecision:
        """
        Validate a proposed tool call against hard-coded security policies.
        
        Args:
            tool_name: Name of the tool to execute
            tool_params: Parameters for the tool
            
        Returns:
            PolicyDecision (PERMIT, DENY, or REQUIRES_APPROVAL)
        """
        logger.info(
            "policy_engine.validating",
            tool=tool_name,
            user_role=self.user.role,
            mode=self.mode,
        )

        # Rule 1: Role-Based Access Control (RBAC)
        rbac_decision = self._check_rbac(tool_name)
        if rbac_decision == PolicyDecision.DENY:
            logger.warning(
                "policy_engine.rbac_denied",
                tool=tool_name,
                user_role=self.user.role,
            )
            return PolicyDecision.DENY

        # Rule 2: Risk-Based Approval Gate
        risk_decision = self._check_risk_level(tool_name, tool_params)
        if risk_decision == PolicyDecision.REQUIRES_APPROVAL:
            logger.info(
                "policy_engine.approval_required",
                tool=tool_name,
                reason="high_risk_operation",
            )
            return PolicyDecision.REQUIRES_APPROVAL

        # Rule 3: Target-Based Restrictions
        target_decision = self._check_target_restrictions(tool_name, tool_params)
        if target_decision != PolicyDecision.PERMIT:
            return target_decision

        # Rule 4: Mode-Based Restrictions
        if self.mode == "passive" and tool_name in ["exec_in_sandbox", "propose_action"]:
            logger.warning(
                "policy_engine.mode_violation",
                tool=tool_name,
                mode=self.mode,
            )
            return PolicyDecision.DENY

        # Default: Permit
        logger.info("policy_engine.permitted", tool=tool_name)
        return PolicyDecision.PERMIT

    def _check_rbac(self, tool_name: str) -> PolicyDecision:
        """Check role-based access control."""
        user_role = self.user.role.lower()

        # Viewers can only query threat intel
        if user_role == "viewer":
            if tool_name != "query_threat_intel":
                return PolicyDecision.DENY

        # Analysts can scan and query, but not execute code
        if user_role == "analyst":
            if tool_name in ["exec_in_sandbox", "execute_code"]:
                return PolicyDecision.DENY

        # Admins can do everything (but still subject to approval gates)
        return PolicyDecision.PERMIT

    def _check_risk_level(self, tool_name: str, tool_params: dict[str, Any]) -> PolicyDecision:
        """Check if operation requires approval based on risk."""
        # All code execution requires approval
        if tool_name in self.HIGH_RISK_TOOLS:
            return PolicyDecision.REQUIRES_APPROVAL

        # Active scans on production systems require approval
        if tool_name == "scan_environment":
            scan_type = tool_params.get("scan_type", "")
            if scan_type in ["active", "intrusive", "exploit"]:
                return PolicyDecision.REQUIRES_APPROVAL

        return PolicyDecision.PERMIT

    def _check_target_restrictions(
        self, tool_name: str, tool_params: dict[str, Any]
    ) -> PolicyDecision:
        """Check if target is in sensitive network range."""
        if tool_name not in ["scan_environment", "query_threat_intel"]:
            return PolicyDecision.PERMIT

        target = tool_params.get("target", "").lower()

        # Check if target is in sensitive network
        for sensitive in self.SENSITIVE_NETWORKS:
            if sensitive in target:
                logger.warning(
                    "policy_engine.sensitive_target",
                    tool=tool_name,
                    target=target,
                )
                return PolicyDecision.REQUIRES_APPROVAL

        return PolicyDecision.PERMIT

    def get_denial_reason(self, tool_name: str, tool_params: dict[str, Any]) -> str:
        """Get human-readable reason for policy denial."""
        user_role = self.user.role.lower()

        if user_role == "viewer" and tool_name != "query_threat_intel":
            return f"Role '{user_role}' is not authorized to use tool '{tool_name}'"

        if user_role == "analyst" and tool_name in ["exec_in_sandbox", "execute_code"]:
            return f"Role '{user_role}' cannot execute code. Admin role required."

        if self.mode == "passive" and tool_name in ["exec_in_sandbox", "propose_action"]:
            return f"Tool '{tool_name}' not allowed in passive mode"

        return f"Policy denied tool '{tool_name}'"
