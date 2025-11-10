"""
C2 (Command & Control) Framework Manager.

Integrates with professional C2 frameworks (Havoc, Sliver, Merlin).
"""

from typing import Any

import httpx
import structlog

from src.core.config import get_settings
from src.tools.base import BaseTool

logger = structlog.get_logger(__name__)
settings = get_settings()


class C2ManagerTool(BaseTool):
    """
    Manages C2 framework operations.
    
    Integrates with professional C2 frameworks for post-exploitation.
    """

    def __init__(self):
        super().__init__(
            name="c2_manager",
            description="Manage C2 framework (create listeners, generate payloads, task agents)",
        )
        self.c2_url = getattr(settings, "c2_api_url", "http://localhost:40056")
        self.c2_token = getattr(settings, "c2_api_token", "")

    async def execute(
        self,
        operation: str,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Execute C2 operation.
        
        Args:
            operation: Operation type (create_listener, generate_payload, list_agents, task_agent)
            **kwargs: Operation-specific parameters
            
        Returns:
            Operation result
        """
        logger.info("c2_manager.executing", operation=operation)

        try:
            if operation == "create_listener":
                return await self._create_listener(**kwargs)
            elif operation == "generate_payload":
                return await self._generate_payload(**kwargs)
            elif operation == "list_agents":
                return await self._list_agents()
            elif operation == "task_agent":
                return await self._task_agent(**kwargs)
            else:
                return {"success": False, "error": f"Unknown operation: {operation}"}

        except Exception as e:
            logger.error("c2_manager.failed", error=str(e))
            return {"success": False, "error": str(e)}

    async def _create_listener(
        self,
        protocol: str = "https",
        host: str = "0.0.0.0",
        port: int = 443,
        **kwargs,
    ) -> dict[str, Any]:
        """Create C2 listener."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.c2_url}/api/listeners",
                headers={"Authorization": f"Bearer {self.c2_token}"},
                json={
                    "protocol": protocol,
                    "host": host,
                    "port": port,
                    **kwargs,
                },
                timeout=30,
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "listener_id": data.get("id"),
                    "protocol": protocol,
                    "host": host,
                    "port": port,
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to create listener: {response.text}",
                }

    async def _generate_payload(
        self,
        listener_id: str,
        os: str = "windows",
        arch: str = "x64",
        format: str = "exe",
        **kwargs,
    ) -> dict[str, Any]:
        """Generate C2 payload."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.c2_url}/api/payloads",
                headers={"Authorization": f"Bearer {self.c2_token}"},
                json={
                    "listener_id": listener_id,
                    "os": os,
                    "arch": arch,
                    "format": format,
                    **kwargs,
                },
                timeout=60,
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "payload_id": data.get("id"),
                    "download_url": data.get("download_url"),
                    "os": os,
                    "arch": arch,
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to generate payload: {response.text}",
                }

    async def _list_agents(self) -> dict[str, Any]:
        """List active C2 agents."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.c2_url}/api/agents",
                headers={"Authorization": f"Bearer {self.c2_token}"},
                timeout=30,
            )
            
            if response.status_code == 200:
                agents = response.json()
                return {
                    "success": True,
                    "agents": agents,
                    "count": len(agents),
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to list agents: {response.text}",
                }

    async def _task_agent(
        self,
        agent_id: str,
        command: str,
        **kwargs,
    ) -> dict[str, Any]:
        """Task C2 agent with command."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.c2_url}/api/agents/{agent_id}/tasks",
                headers={"Authorization": f"Bearer {self.c2_token}"},
                json={
                    "command": command,
                    **kwargs,
                },
                timeout=30,
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "task_id": data.get("id"),
                    "agent_id": agent_id,
                    "command": command,
                    "status": "queued",
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to task agent: {response.text}",
                }

    def get_parameters(self) -> dict[str, Any]:
        """Get tool parameters schema."""
        return {
            "operation": {
                "type": "string",
                "enum": ["create_listener", "generate_payload", "list_agents", "task_agent"],
                "description": "C2 operation to perform",
            },
            "protocol": {
                "type": "string",
                "description": "Listener protocol (for create_listener)",
            },
            "listener_id": {
                "type": "string",
                "description": "Listener ID (for generate_payload)",
            },
            "agent_id": {
                "type": "string",
                "description": "Agent ID (for task_agent)",
            },
            "command": {
                "type": "string",
                "description": "Command to execute (for task_agent)",
            },
        }
