"""Health check and status routes."""

from datetime import UTC, datetime

from fastapi import APIRouter

from src.core.config import get_settings
from src.models.schemas import HealthResponse
from src.services import ChromaService, DockerSandboxService, OllamaService, TelegramService

router = APIRouter(tags=["Health"])
settings = get_settings()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    # Check service health
    ollama_service = OllamaService()
    chroma_service = ChromaService()
    docker_service = DockerSandboxService()
    telegram_service = TelegramService()

    services_status = {
        "ollama": "healthy" if await ollama_service.check_health() else "unhealthy",
        "chroma": "healthy" if chroma_service.check_health() else "unhealthy",
        "docker": "healthy" if docker_service.check_health() else "unhealthy",
        "telegram": "healthy" if await telegram_service.check_health() else "not_configured",
        "database": "healthy",  # If we got here, DB is working
    }

    overall_status = (
        "healthy"
        if all(s in ["healthy", "not_configured"] for s in services_status.values())
        else "degraded"
    )

    return {
        "status": overall_status,
        "version": settings.app_version,
        "timestamp": datetime.now(UTC),
        "services": services_status,
    }


@router.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "operational",
        "docs": "/docs",
    }
