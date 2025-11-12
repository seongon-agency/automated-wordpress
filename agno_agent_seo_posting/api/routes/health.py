"""
Health Check and Utility Endpoints
"""

from fastapi import APIRouter
from api.models.schemas import HealthCheck, APIResponse
from api.core.config import get_settings
import sys
import os

router = APIRouter(tags=["Health"])
settings = get_settings()


@router.get("/health", response_model=HealthCheck)
async def health_check():
    """
    Health check endpoint.

    Returns system status and version information.
    """
    return HealthCheck(
        status="healthy",
        version=settings.API_VERSION
    )


@router.get("/info", response_model=APIResponse)
async def system_info():
    """
    Get system information.

    Returns detailed system information including:
    - API version
    - Python version
    - Database status
    - Configuration status
    """
    # Add src to path for imports
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

    try:
        from src.database import get_project
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    info = {
        "api_version": settings.API_VERSION,
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.patch}",
        "database_status": db_status,
        "anthropic_api_configured": bool(settings.ANTHROPIC_API_KEY),
        "lark_configured": bool(settings.LARK_APP_ID and settings.LARK_APP_SECRET),
    }

    return APIResponse(success=True, data=info)
