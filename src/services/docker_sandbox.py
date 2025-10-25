"""Docker sandbox service for safe code execution."""

import asyncio

import docker
from docker.errors import APIError, ContainerError, ImageNotFound

from src.core.config import get_settings
from src.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class DockerSandboxService:
    """Service for executing code in Docker sandbox."""

    def __init__(self):
        self.client = docker.from_env()
        self.image = settings.docker_sandbox_image
        self.timeout = settings.docker_sandbox_timeout
        self.memory_limit = settings.docker_sandbox_memory_limit
        self.cpu_limit = settings.docker_sandbox_cpu_limit

    def ensure_image(self) -> None:
        """Ensure the sandbox image is available."""
        try:
            self.client.images.get(self.image)
            logger.info("Sandbox image found", image=self.image)
        except ImageNotFound:
            logger.info("Pulling sandbox image", image=self.image)
            self.client.images.pull(self.image)

    async def execute_code(
        self, code: str, language: str = "python", timeout: int | None = None
    ) -> dict:
        """Execute code in a sandboxed container."""
        if not settings.enable_code_execution:
            logger.warning("Code execution is disabled")
            return {"success": False, "error": "Code execution is disabled"}

        timeout = timeout or self.timeout
        logger.info("Executing code in sandbox", language=language, code_length=len(code))

        try:
            self.ensure_image()

            # Prepare the command based on language
            if language == "python":
                command = ["python", "-c", code]
            elif language == "bash":
                command = ["bash", "-c", code]
            else:
                return {"success": False, "error": f"Unsupported language: {language}"}

            # Run in a thread to not block
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self._run_container, command, timeout)

            return result

        except ContainerError as e:
            logger.error("Container execution error", error=str(e))
            return {
                "success": False,
                "error": f"Container error: {e.stderr.decode() if e.stderr else str(e)}",
            }
        except APIError as e:
            logger.error("Docker API error", error=str(e))
            return {"success": False, "error": f"Docker API error: {str(e)}"}
        except Exception as e:
            logger.error("Unexpected error during code execution", error=str(e))
            return {"success": False, "error": f"Unexpected error: {str(e)}"}

    def _run_container(self, command: list, timeout: int) -> dict:
        """Run container synchronously."""
        container = None
        try:
            container = self.client.containers.run(
                self.image,
                command=command,
                mem_limit=self.memory_limit,
                nano_cpus=int(self.cpu_limit * 1e9),
                network_disabled=True,
                remove=True,
                detach=False,
                stdout=True,
                stderr=True,
                timeout=timeout,
            )

            output = container.decode("utf-8") if isinstance(container, bytes) else str(container)

            logger.info("Code executed successfully", output_length=len(output))
            return {"success": True, "output": output}

        except Exception as e:
            raise e

    def check_health(self) -> bool:
        """Check if Docker service is available."""
        try:
            self.client.ping()
            return True
        except Exception as e:
            logger.error("Docker health check failed", error=str(e))
            return False
