"""History API Router"""

import logging
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from database.db import get_publishing_history, get_failed_publishes

logger = logging.getLogger(__name__)
router = APIRouter()


class HistoryEntry(BaseModel):
    id: int
    project_id: Optional[str]
    project_name: Optional[str]
    google_docs_url: str
    wordpress_post_id: Optional[int]
    wordpress_post_url: Optional[str]
    post_title: Optional[str]
    post_status: Optional[str]
    images_processed: int
    success: bool
    error_message: Optional[str]
    execution_time_seconds: Optional[float]
    published_at: datetime


class HistoryResponse(BaseModel):
    success: bool
    history: List[HistoryEntry]
    count: int


class HistoryStatsResponse(BaseModel):
    success: bool
    total: int
    successful: int
    failed: int
    success_rate: float


def serialize_history_entry(entry: dict) -> dict:
    """Serialize history entry for JSON response"""
    result = dict(entry)
    # Convert datetime to ISO string if needed
    if 'published_at' in result and result['published_at'] is not None:
        if hasattr(result['published_at'], 'isoformat'):
            result['published_at'] = result['published_at'].isoformat()
    return result


@router.get("/", response_model=HistoryResponse)
async def get_history(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    limit: int = Query(50, ge=1, le=200, description="Maximum entries to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """Get publishing history with optional project filter"""
    try:
        entries = get_publishing_history(
            project_id=project_id,
            limit=limit,
            offset=offset
        )

        return HistoryResponse(
            success=True,
            history=[serialize_history_entry(e) for e in entries],
            count=len(entries)
        )
    except Exception as e:
        logger.error(f"Failed to get history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve history")


@router.get("/failed", response_model=HistoryResponse)
async def get_failed_history(
    limit: int = Query(20, ge=1, le=100, description="Maximum entries to return")
):
    """Get recent failed publishing attempts"""
    try:
        entries = get_failed_publishes(limit=limit)

        return HistoryResponse(
            success=True,
            history=[serialize_history_entry(e) for e in entries],
            count=len(entries)
        )
    except Exception as e:
        logger.error(f"Failed to get failed history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve failed history")


@router.get("/stats", response_model=HistoryStatsResponse)
async def get_history_stats(
    project_id: Optional[str] = Query(None, description="Filter by project ID")
):
    """Get publishing statistics"""
    try:
        # Get all entries for the project (or all)
        all_entries = get_publishing_history(project_id=project_id, limit=10000)

        total = len(all_entries)
        successful = sum(1 for e in all_entries if e.get('success'))
        failed = total - successful
        success_rate = (successful / total * 100) if total > 0 else 0.0

        return HistoryStatsResponse(
            success=True,
            total=total,
            successful=successful,
            failed=failed,
            success_rate=round(success_rate, 1)
        )
    except Exception as e:
        logger.error(f"Failed to get stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve statistics")
