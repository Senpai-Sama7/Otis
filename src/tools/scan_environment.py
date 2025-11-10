"""
Professional security scanning tool - orchestrates real tools.

Uses battle-tested tools (nmap, sqlmap, gobuster) instead of reimplementing.
"""

from typing import Any

import structlog

from src.services.red_team_runner import RedTeamRunnerService
from src.tools.base import BaseTool

logger = structlog.get_logger(__name__)


class ScanEnvironmentTool(BaseTool):
    """
    Orchestrates professional Red Team tools.
    
    Executes real tools (nmap, sqlmap, gobuster) in isolated container.
    """

    def __init__(self):
        super().__init__(
            name="scan_environment",
            description="Execute professional security scans using real tools (nmap, sqlmap, gobuster)",
        )
        self.runner = RedTeamRunnerService()

    async def execute(
        self,
        module: str,
        target: str,
        flags: str = "",
        use_proxy: bool = False,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Execute professional security tool.
        
        Args:
            module: Tool to use (nmap, sqlmap, gobuster, metasploit)
            target: Target host/URL
            flags: Tool-specific flags
            use_proxy: Route through Tor proxy
            
        Returns:
            Tool output and artifacts
        """
        logger.info(
            "scan_environment.executing",
            module=module,
            target=target,
            use_proxy=use_proxy,
        )

        try:
            # Route to appropriate tool
            if module == "nmap":
                result = await self.runner.nmap_scan(
                    target=target,
                    flags=flags or "-sV -sC",
                    use_proxy=use_proxy,
                )
            
            elif module == "sqlmap":
                result = await self.runner.sqlmap_scan(
                    url=target,
                    flags=flags or "--batch --level=1 --risk=1",
                    use_proxy=use_proxy,
                )
            
            elif module == "gobuster":
                result = await self.runner.gobuster_scan(
                    url=target,
                    wordlist=kwargs.get("wordlist", "/usr/share/wordlists/dirb/common.txt"),
                    use_proxy=use_proxy,
                )
            
            elif module == "metasploit":
                result = await self.runner.metasploit_exploit(
                    module=kwargs.get("msf_module", ""),
                    options=kwargs.get("options", {}),
                )
            
            else:
                return {
                    "success": False,
                    "error": f"Unknown module: {module}",
                }

            # Parse and return results
            return {
                "success": result["success"],
                "module": module,
                "target": target,
                "output": result["stdout"],
                "errors": result["stderr"],
                "exit_code": result["exit_code"],
                "artifacts": result.get("artifacts", []),
                "findings": self._parse_findings(module, result["stdout"]),
            }

        except Exception as e:
            logger.error("scan_environment.failed", error=str(e))
            return {
                "success": False,
                "error": str(e),
            }

    def _parse_findings(self, module: str, output: str) -> list[dict[str, Any]]:
        """Parse tool output into structured findings."""
        findings = []
        
        if module == "nmap":
            # Parse nmap output for open ports
            for line in output.split("\n"):
                if "/tcp" in line or "/udp" in line:
                    findings.append({"type": "open_port", "detail": line.strip()})
        
        elif module == "sqlmap":
            # Parse sqlmap output for vulnerabilities
            if "vulnerable" in output.lower():
                findings.append({"type": "sql_injection", "detail": "SQL injection detected"})
        
        elif module == "gobuster":
            # Parse gobuster output for discovered paths
            for line in output.split("\n"):
                if "Status: 200" in line:
                    findings.append({"type": "discovered_path", "detail": line.strip()})
        
        return findings

    def get_parameters(self) -> dict[str, Any]:
        """Get tool parameters schema."""
        return {
            "module": {
                "type": "string",
                "enum": ["nmap", "sqlmap", "gobuster", "metasploit"],
                "description": "Security tool to execute",
            },
            "target": {
                "type": "string",
                "description": "Target host or URL",
            },
            "flags": {
                "type": "string",
                "description": "Tool-specific command-line flags",
                "default": "",
            },
            "use_proxy": {
                "type": "boolean",
                "description": "Route through Tor proxy for anonymity",
                "default": False,
            },
        }
