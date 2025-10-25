"""Environment scanning tool for ReAct agent."""

import asyncio
import socket
from typing import Any

from src.core.logging import get_logger
from src.tools.base import BaseTool

logger = get_logger(__name__)


async def scan_environment(duration: int = 10) -> dict:
    """
    Scan environment for security issues (convenience function).
    
    Args:
        duration: Scan duration in seconds (default: 10)
    
    Returns:
        Dictionary with scan results
    """
    tool = ScanEnvironmentTool()
    return await tool.execute(duration=duration)


class ScanEnvironmentTool(BaseTool):
    """Tool for scanning the environment for security issues."""

    def __init__(self):
        super().__init__(
            name="scan_environment",
            description="Scan the environment for open ports, running services, and potential vulnerabilities",
        )

    def get_parameters(self) -> dict[str, Any]:
        """Get parameter schema."""
        return {
            "type": "object",
            "properties": {
                "scan_type": {
                    "type": "string",
                    "enum": ["ports", "services", "vulnerabilities", "config"],
                    "description": "Type of scan to perform",
                },
                "target": {
                    "type": "string",
                    "description": "Target to scan (hostname, IP, or 'localhost')",
                },
                "port_range": {
                    "type": "string",
                    "description": "Port range for port scanning (e.g., '1-1024')",
                    "default": "1-1024",
                },
            },
            "required": ["scan_type", "target"],
        }

    async def execute(self, duration: int = 10, **kwargs) -> dict[str, Any]:
        """
        Execute environment scan.
        
        Args:
            duration: Scan duration in seconds (default: 10)
            **kwargs: Additional scan parameters
        
        Returns:
            Dictionary with scan results
        """
        scan_type = kwargs.get("scan_type", "ports")
        target = kwargs.get("target", "localhost")

        logger.info("Starting environment scan", scan_type=scan_type, target=target, duration=duration)

        try:
            if scan_type == "ports":
                result = await self._scan_ports(target, kwargs.get("port_range", "1-1024"))
            elif scan_type == "services":
                result = await self._scan_services(target)
            elif scan_type == "vulnerabilities":
                result = await self._scan_vulnerabilities(target)
            elif scan_type == "config":
                result = await self._scan_config(target)
            else:
                result = {"error": f"Unknown scan type: {scan_type}"}

            logger.info(
                "Scan completed",
                scan_type=scan_type,
                findings_count=len(result.get("findings", [])),
            )
            return {"success": True, "scan_type": scan_type, "target": target, "duration": duration, **result}

        except Exception as e:
            logger.error("Scan failed", error=str(e))
            return {"success": False, "error": str(e)}

    async def _scan_ports(self, target: str, port_range: str) -> dict[str, Any]:
        """Scan for open ports."""
        start_port, end_port = map(int, port_range.split("-"))
        open_ports = []

        # Limit scan to prevent abuse
        if end_port - start_port > 1000:
            return {"error": "Port range too large (max 1000 ports)"}

        async def check_port(port: int) -> bool:
            try:
                # Use asyncio to check port with timeout
                _, writer = await asyncio.wait_for(
                    asyncio.open_connection(target, port), timeout=0.5
                )
                writer.close()
                await writer.wait_closed()
                return True
            except (TimeoutError, ConnectionRefusedError, OSError):
                return False

        # Check ports with limited concurrency
        tasks = [
            check_port(port) for port in range(start_port, end_port + 1)
        ]
        results = await asyncio.gather(*tasks)

        open_ports = [
            {"port": port, "status": "open"}
            for port, is_open in zip(
                range(start_port, end_port + 1), results, strict=True
            )
            if is_open
        ]

        return {
            "findings": open_ports,
            "vulnerabilities_count": len(open_ports),
            "risk_score": min(len(open_ports) * 0.1, 1.0),
        }

    async def _scan_services(self, target: str) -> dict[str, Any]:
        """Scan for running services."""
        # Simplified service detection
        findings = []
        common_ports = {
            22: "SSH",
            80: "HTTP",
            443: "HTTPS",
            3306: "MySQL",
            5432: "PostgreSQL",
            6379: "Redis",
            27017: "MongoDB",
        }

        for port, service in common_ports.items():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                result = sock.connect_ex((target, port))
                sock.close()

                if result == 0:
                    findings.append(
                        {
                            "port": port,
                            "service": service,
                            "status": "running",
                        }
                    )
            except Exception:
                pass

        return {
            "findings": findings,
            "vulnerabilities_count": 0,
            "risk_score": 0.0,
        }

    async def _scan_vulnerabilities(self, target: str) -> dict[str, Any]:
        """Scan for known vulnerabilities."""
        # This is a simplified placeholder
        # In production, integrate with actual vulnerability scanners
        return {
            "findings": [
                {
                    "type": "info",
                    "message": "Vulnerability scanning requires integration with external tools",
                    "recommendation": "Consider integrating Nessus, OpenVAS, or similar scanners",
                }
            ],
            "vulnerabilities_count": 0,
            "risk_score": 0.0,
        }

    async def _scan_config(self, target: str) -> dict[str, Any]:
        """Scan configuration for security issues."""
        # Simplified configuration check
        findings = []

        # Check basic system information
        try:
            import platform

            findings.append(
                {
                    "type": "system_info",
                    "platform": platform.system(),
                    "version": platform.version(),
                    "machine": platform.machine(),
                }
            )
        except Exception as e:
            findings.append({"error": str(e)})

        return {
            "findings": findings,
            "vulnerabilities_count": 0,
            "risk_score": 0.0,
        }
