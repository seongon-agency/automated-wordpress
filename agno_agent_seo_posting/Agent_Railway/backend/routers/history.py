"""
History Router - Publishing history endpoints.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException

from database import get_publish_history


router = APIRouter()


@router.get("")
async def get_history(project_id: Optional[str] = None, limit: int = 50):
    """
    Get publishing history.

    Args:
        project_id: Filter by project (optional)
        limit: Maximum number of records (default 50)
    """
    try:
        history = get_publish_history(project_id=project_id, limit=limit)
        return {
            "success": True,
            "history": history,
            "count": len(history)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_id}")
async def get_project_history(project_id: str, limit: int = 50):
    """
    Get publishing history for a specific project.
    """
    try:
        history = get_publish_history(project_id=project_id, limit=limit)
        return {
            "success": True,
            "project_id": project_id,
            "history": history,
            "count": len(history)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
