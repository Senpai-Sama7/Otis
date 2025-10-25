"""Propose action tool for ReAct agent."""
from typing import Any, Dict

from sqlalchemy.orm import Session

from src.core.logging import get_logger
from src.database.repository import BaseRepository
from src.models.database import ActionStatus, AgentAction
from src.services.telegram import TelegramService
from src.tools.base import BaseTool

logger = get_logger(__name__)


class ProposeActionTool(BaseTool):
    """Tool for proposing actions that require approval."""

    def __init__(self, telegram_service: TelegramService):
        super().__init__(
            name="propose_action",
            description="Propose an action for approval before execution (code changes, configuration updates, etc.)",
        )
        self.telegram_service = telegram_service

    def get_parameters(self) -> Dict[str, Any]:
        """Get parameter schema."""
        return {
            "type": "object",
            "properties": {
                "action_type": {
                    "type": "string",
                    "description": "Type of action (patch, configure, scan, block)",
                },
                "description": {
                    "type": "string",
                    "description": "Detailed description of the proposed action",
                },
                "proposed_code": {
                    "type": "string",
                    "description": "Code or configuration to execute (if applicable)",
                },
                "reasoning": {
                    "type": "string",
                    "description": "Reasoning and justification for this action",
                },
                "risk_level": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "critical"],
                    "description": "Risk level assessment",
                },
            },
            "required": ["action_type", "description", "reasoning", "risk_level"],
        }

    async def execute(self, db: Session, **kwargs) -> Dict[str, Any]:
        """Execute action proposal."""
        action_type = kwargs.get("action_type", "")
        description = kwargs.get("description", "")
        proposed_code = kwargs.get("proposed_code")
        reasoning = kwargs.get("reasoning", "")
        risk_level = kwargs.get("risk_level", "medium")

        logger.info(
            "Proposing action",
            action_type=action_type,
            risk_level=risk_level,
        )

        try:
            # Create action record in database
            repo = BaseRepository(AgentAction, db)
            action = repo.create(
                action_type=action_type,
                description=description,
                proposed_code=proposed_code,
                reasoning=reasoning,
                risk_level=risk_level,
                status=ActionStatus.PENDING,
            )

            # Request approval via Telegram
            approval_requested = await self.telegram_service.request_approval(
                action_description=f"{action_type}: {description}\n\nReasoning: {reasoning}",
                risk_level=risk_level,
                action_id=action.id,
            )

            result = {
                "success": True,
                "action_id": action.id,
                "status": "pending_approval",
                "approval_requested": approval_requested is not None,
            }

            if approval_requested is True:
                result["status"] = "auto_approved"
                result["message"] = "Action auto-approved (approval gate disabled)"

            logger.info("Action proposed", action_id=action.id, status=result["status"])

            return result

        except Exception as e:
            logger.error("Failed to propose action", error=str(e))
            return {
                "success": False,
                "error": str(e),
            }
