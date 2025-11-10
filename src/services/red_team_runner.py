"""
Red Team Runner Service - Orchestrates professional security tools.

Executes real tools (nmap, sqlmap, metasploit) in isolated container.
"""

import asyncio
from typing import Any

import structlog

import docker
from src.core.config import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()


class RedTeamRunnerService:
    """
    Orchestrates professional Red Team tools in dedicated container.

    Executes real tools instead of reimplementing them in Python.
    """

    def __init__(self):
        self.client = docker.from_env()
        self.image = "otis-red-team:latest"
        self.timeout = 300  # 5 minutes default

    async def run_command(
        self,
        command: str,
        timeout: int | None = None,
        use_proxy: bool = False,
    ) -> dict[str, Any]:
        """
        Execute command in Red Team container.

        Args:
            command: Shell command to execute
            timeout: Execution timeout in seconds
            use_proxy: Route through Tor proxy

        Returns:
            Dict with stdout, stderr, exit_code, artifacts
        """
        timeout = timeout or self.timeout

        # Wrap with proxychains if proxy requested
        if use_proxy:
            command = f"proxychains4 -q {command}"

        logger.info(
            "red_team_runner.executing",
            command=command[:100],
            use_proxy=use_proxy,
        )

        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, self._run_container, command, timeout
            )

            logger.info(
                "red_team_runner.completed",
                exit_code=result["exit_code"],
                output_length=len(result["stdout"]),
            )

            return result

        except Exception as e:
            logger.error("red_team_runner.failed", error=str(e))
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "exit_code": 1,
                "artifacts": [],
            }

    def _run_container(self, command: str, timeout: int) -> dict[str, Any]:
        """Execute command in container synchronously."""
        try:
            container = self.client.containers.run(
                self.image,
                command=["bash", "-c", command],
                detach=False,
                remove=True,
                network_mode="bridge",  # Or service:tor-proxy
                mem_limit="2g",
                nano_cpus=int(2.0 * 1e9),
                volumes={
                    "/tmp/otis-artifacts": {"bind": "/artifacts", "mode": "rw"}
                },
                stdout=True,
                stderr=True,
                timeout=timeout,
            )

            # Parse output
            if isinstance(container, bytes):
                output = container.decode("utf-8", errors="replace")
                stdout = output
                stderr = ""
                exit_code = 0
            else:
                stdout = container
                stderr = ""
                exit_code = 0

            return {
                "success": True,
                "stdout": stdout,
                "stderr": stderr,
                "exit_code": exit_code,
                "artifacts": self._collect_artifacts(),
            }

        except docker.errors.ContainerError as e:
            return {
                "success": False,
                "stdout": e.stdout.decode() if e.stdout else "",
                "stderr": e.stderr.decode() if e.stderr else str(e),
                "exit_code": e.exit_status,
                "artifacts": [],
            }

    def _collect_artifacts(self) -> list[str]:
        """Collect artifacts from /artifacts volume."""
        import os
        artifacts = []
        artifact_dir = "/tmp/otis-artifacts"

        if os.path.exists(artifact_dir):
            for file in os.listdir(artifact_dir):
                artifacts.append(os.path.join(artifact_dir, file))

        return artifacts

    # Tool-specific methods
    async def nmap_scan(
        self,
        target: str,
        flags: str = "-sV -sC",
        use_proxy: bool = False,
    ) -> dict[str, Any]:
        """Execute nmap scan."""
        command = f"nmap {flags} {target} -oN /artifacts/nmap-{target}.txt"
        return await self.run_command(command, use_proxy=use_proxy)

    async def sqlmap_scan(
        self,
        url: str,
        flags: str = "--batch --level=1 --risk=1",
        use_proxy: bool = False,
    ) -> dict[str, Any]:
        """Execute sqlmap scan."""
        command = f'sqlmap -u "{url}" {flags} --output-dir=/artifacts'
        return await self.run_command(command, timeout=600, use_proxy=use_proxy)

    async def gobuster_scan(
        self,
        url: str,
        wordlist: str = "/usr/share/wordlists/dirb/common.txt",
        use_proxy: bool = False,
    ) -> dict[str, Any]:
        """Execute gobuster directory scan."""
        command = f"gobuster dir -u {url} -w {wordlist} -o /artifacts/gobuster.txt"
        return await self.run_command(command, use_proxy=use_proxy)

    async def metasploit_exploit(
        self,
        module: str,
        options: dict[str, str],
    ) -> dict[str, Any]:
        """Execute Metasploit module."""
        # Build msfconsole command
        opts = " ".join([f"set {k} {v}" for k, v in options.items()])
        command = f'msfconsole -q -x "use {module}; {opts}; run; exit"'
        return await self.run_command(command, timeout=600)
