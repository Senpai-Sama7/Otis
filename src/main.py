"""Main FastAPI application."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from src.api import agent, auth, health, ingest
from src.core.config import get_settings
from src.core.logging import configure_logging, get_logger
from src.core.tracing import configure_tracing
from src.database import init_db

settings = get_settings()
configure_logging(settings.log_level)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting Otis", version=settings.app_version)

    # Initialize database
    try:
        init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error("Failed to initialize database", error=str(e))

    # Configure distributed tracing
    try:
        configure_tracing(app)
        logger.info("Distributed tracing configured")
    except Exception as e:
        logger.warning("Failed to configure tracing", error=str(e))

    yield

    logger.info("Shutting down Otis")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Autonomous Cybersecurity AI Coding Agent with A+ Security",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix=settings.api_prefix)
app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(agent.router, prefix=settings.api_prefix)
app.include_router(ingest.router, prefix=settings.api_prefix)

# Serve static files
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/")
async def root():
    """Serve the main GUI."""
    static_file = static_dir / "app.html"
    if static_file.exists():
        return FileResponse(static_file)
    return {"message": "Otis API", "docs": "/docs", "gui": "GUI not found"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
