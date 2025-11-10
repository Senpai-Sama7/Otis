"""
Celery tasks for distributed execution.

Enables horizontal scaling of execution layer.
"""

from celery import Celery
from celery.utils.log import get_task_logger

from src.core.config import get_settings
from src.services.docker_sandbox import DockerSandboxService

settings = get_settings()
logger = get_task_logger(__name__)

# Initialize Celery app
celery_app = Celery(
    "otis",
    broker=(
        settings.celery_broker_url
        if hasattr(settings, "celery_broker_url")
        else "redis://localhost:6379/0"
    ),
    backend=(
        settings.celery_result_backend
        if hasattr(settings, "celery_result_backend")
        else "redis://localhost:6379/0"
    ),
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes hard limit
    task_soft_time_limit=240,  # 4 minutes soft limit
)


@celery_app.task(name="otis.run_sandbox_task", bind=True)
def run_sandbox_task(self, code: str, language: str = "python", timeout: int = 60) -> dict:
    """
    Execute code in Docker sandbox asynchronously.

    Args:
        code: Code to execute
        language: Programming language
        timeout: Execution timeout in seconds

    Returns:
        Execution result dictionary
    """
    logger.info(
        "sandbox_task.started",
        task_id=self.request.id,
        language=language,
        code_length=len(code),
    )

    try:
        sandbox = DockerSandboxService()

        # Run synchronously in worker
        import asyncio

        result = asyncio.run(sandbox.execute_code(code, language, timeout))

        logger.info(
            "sandbox_task.completed",
            task_id=self.request.id,
            success=result.get("success"),
        )

        return result

    except Exception as e:
        logger.error(
            "sandbox_task.failed",
            task_id=self.request.id,
            error=str(e),
        )
        return {
            "success": False,
            "error": f"Task execution failed: {str(e)}",
        }


@celery_app.task(name="otis.scan_environment_task", bind=True)
def scan_environment_task(self, target: str, scan_type: str = "ports", duration: int = 10) -> dict:
    """
    Execute environment scan asynchronously.

    Args:
        target: Target to scan
        scan_type: Type of scan
        duration: Scan duration in seconds

    Returns:
        Scan result dictionary
    """
    logger.info(
        "scan_task.started",
        task_id=self.request.id,
        target=target,
        scan_type=scan_type,
    )

    try:
        from src.tools.scan_environment import ScanEnvironmentTool

        tool = ScanEnvironmentTool()

        # Run synchronously in worker
        import asyncio

        result = asyncio.run(tool.execute(target=target, scan_type=scan_type, duration=duration))

        logger.info(
            "scan_task.completed",
            task_id=self.request.id,
            success=result.get("success"),
        )

        return result

    except Exception as e:
        logger.error(
            "scan_task.failed",
            task_id=self.request.id,
            error=str(e),
        )
        return {
            "success": False,
            "error": f"Scan task failed: {str(e)}",
        }


@celery_app.task(name="otis.query_threat_intel_task", bind=True)
def query_threat_intel_task(self, query: str, k: int = 3) -> dict:
    """
    Query threat intelligence asynchronously.

    Args:
        query: Query string
        k: Number of results

    Returns:
        Query result dictionary
    """
    logger.info(
        "threat_intel_task.started",
        task_id=self.request.id,
        query=query[:100],
    )

    try:
        from src.services.chroma import ChromaService
        from src.tools.query_threat_intel import QueryThreatIntelTool

        chroma = ChromaService()
        tool = QueryThreatIntelTool(chroma)

        # Run synchronously in worker
        import asyncio

        result = asyncio.run(tool.execute(query=query, k=k))

        logger.info(
            "threat_intel_task.completed",
            task_id=self.request.id,
            success=result.get("success"),
        )

        return result

    except Exception as e:
        logger.error(
            "threat_intel_task.failed",
            task_id=self.request.id,
            error=str(e),
        )
        return {
            "success": False,
            "error": f"Threat intel task failed: {str(e)}",
        }
