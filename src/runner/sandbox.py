"""Docker sandbox for secure code execution."""

import json
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

import docker
from docker.errors import ContainerError, ImageNotFound

from src.core.logging import get_logger

logger = get_logger(__name__)


def exec_in_sandbox(
    code: str,
    lang: str = "python",
    timeout: int = 20,
    net: bool = False,
) -> dict:
    """
    Execute code in a Docker sandbox with security constraints.
    
    Args:
        code: Code to execute
        lang: Programming language (default: "python")
        timeout: Execution timeout in seconds (default: 20)
        net: Allow network access (default: False, requires approval)
    
    Returns:
        Dictionary with execution results:
        - success: bool
        - output: str (stdout)
        - error: str (stderr, if any)
        - exit_code: int
    
    Security:
        - Read-only root filesystem
        - tmpfs for /tmp
        - Memory and CPU limits
        - Network disabled by default (net=none)
        - No privileged mode
        - Enforces denylist for dangerous operations
    """
    logger.info(
        "Executing code in sandbox",
        lang=lang,
        timeout=timeout,
        net=net,
        code_len=len(code),
    )

    # Validate and sanitize input
    if not code or not code.strip():
        return {
            "success": False,
            "error": "Empty code provided",
            "exit_code": 1,
        }

    # Check denylist for dangerous operations
    denylist_patterns = [
        "privileged",
        "--privileged",
        "cap-add",
        "device",
        "/dev/",
    ]

    code_lower = code.lower()
    for pattern in denylist_patterns:
        if pattern in code_lower:
            logger.warning("Denylist violation detected", pattern=pattern)
            return {
                "success": False,
                "error": f"Operation blocked by security policy: {pattern}",
                "exit_code": 1,
            }

    try:
        client = docker.from_env()

        # Select appropriate image based on language
        images = {
            "python": "python:3.11-slim",
            "node": "node:18-slim",
            "bash": "bash:5",
        }
        image = images.get(lang, "python:3.11-slim")

        # Ensure image is available
        try:
            client.images.get(image)
        except ImageNotFound:
            logger.info("Pulling image", image=image)
            client.images.pull(image)

        # Create temporary file for code
        with tempfile.NamedTemporaryFile(mode="w", suffix=f".{lang}", delete=False) as f:
            f.write(code)
            code_file = f.name

        # Prepare execution command
        if lang == "python":
            cmd = ["python", "/tmp/code.py"]
        elif lang == "node":
            cmd = ["node", "/tmp/code.js"]
        elif lang == "bash":
            cmd = ["bash", "/tmp/code.sh"]
        else:
            return {
                "success": False,
                "error": f"Unsupported language: {lang}",
                "exit_code": 1,
            }

        # Configure network mode
        network_mode = "host" if net else "none"

        # Run container with security constraints
        result = client.containers.run(
            image=image,
            command=cmd,
            # Security settings
            read_only=True,  # Read-only root filesystem
            network_mode=network_mode,  # Network disabled by default
            mem_limit="512m",  # Memory limit
            nano_cpus=int(1.0 * 1e9),  # CPU limit (1.0 CPU)
            # Mount code file
            volumes={
                code_file: {"bind": f"/tmp/code.{lang}", "mode": "ro"}
            },
            # Tmpfs for temporary files
            tmpfs={
                "/tmp": "size=100M,mode=1777",
            },
            # Remove container after execution
            remove=True,
            # Timeout
            timeout=timeout,
            # Capture output
            stdout=True,
            stderr=True,
            detach=False,
        )

        # Clean up temporary file
        Path(code_file).unlink(missing_ok=True)

        # Decode output
        if isinstance(result, bytes):
            output = result.decode("utf-8")
        else:
            output = str(result)

        logger.info("Sandbox execution completed", output_len=len(output))

        return {
            "success": True,
            "output": output,
            "error": "",
            "exit_code": 0,
        }

    except ContainerError as e:
        # Container execution failed
        logger.error("Sandbox execution failed", error=str(e))

        # Clean up temporary file
        if "code_file" in locals():
            Path(code_file).unlink(missing_ok=True)

        return {
            "success": False,
            "output": e.stdout.decode("utf-8") if e.stdout else "",
            "error": e.stderr.decode("utf-8") if e.stderr else str(e),
            "exit_code": e.exit_status,
        }

    except Exception as e:
        logger.error("Sandbox execution error", error=str(e), error_type=type(e).__name__)

        # Clean up temporary file
        if "code_file" in locals():
            Path(code_file).unlink(missing_ok=True)

        return {
            "success": False,
            "output": "",
            "error": str(e),
            "exit_code": 1,
        }


class SandboxExecutor:
    """
    Class-based wrapper for sandbox execution with additional features.
    """

    def __init__(
        self,
        default_lang: str = "python",
        default_timeout: int = 20,
        allow_net_by_default: bool = False,
    ):
        self.default_lang = default_lang
        self.default_timeout = default_timeout
        self.allow_net_by_default = allow_net_by_default

    def execute(
        self,
        code: str,
        lang: Optional[str] = None,
        timeout: Optional[int] = None,
        net: Optional[bool] = None,
    ) -> dict:
        """Execute code with instance defaults."""
        return exec_in_sandbox(
            code=code,
            lang=lang or self.default_lang,
            timeout=timeout or self.default_timeout,
            net=net if net is not None else self.allow_net_by_default,
        )

    async def execute_async(
        self,
        code: str,
        lang: Optional[str] = None,
        timeout: Optional[int] = None,
        net: Optional[bool] = None,
    ) -> dict:
        """Async wrapper for execute."""
        import asyncio

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.execute,
            code,
            lang or self.default_lang,
            timeout or self.default_timeout,
            net if net is not None else self.allow_net_by_default,
        )
