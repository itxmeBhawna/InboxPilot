"""FastAPI application entrypoint for InboxPilot service."""

import logging
import uvicorn
from fastapi import FastAPI
from src.config.settings import get_settings

# Configure basic application logging
settings = get_settings()
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    description="Autonomous AI agent for email triage, classification, drafting, and Notion synchronization.",
    version="0.1.0",
)


@app.get("/health", tags=["Health"])
async def health_check():
    """Service health check endpoint.

    Returns:
        JSON response confirming operational status and service name.
    """
    logger.info("Health check endpoint invoked")
    return {
        "status": "ok",
        "service": settings.app_name,
    }


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=(settings.app_env == "development"),
    )
