"""
Publish Router - Publishing workflow endpoints.
"""

from typing import Optional, List
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from services.workflow import execute_publishing_workflow
from services.google_docs import google_docs_to_html


router = APIRouter()


class PublishRequest(BaseModel):
    google_docs_url: str
    project_id: Optional[str] = None
    main_keyword: Optional[str] = None


class BatchPublishItem(BaseModel):
    google_docs_url: str
    main_keyword: Optional[str] = None


class BatchPublishRequest(BaseModel):
    project_id: str
    items: List[BatchPublishItem]


class GoogleDocsConvertRequest(BaseModel):
    google_docs_url: str


@router.post("")
async def publish_content(request: PublishRequest):
    """
    Execute the publishing workflow for a single Google Docs URL.

    Returns:
        - success: bool
        - post_url: str
        - post_id: int
        - post_title: str
        - images_processed: int
        - execution_time: float
        - error: str (if failed)
    """
    try:
        result = execute_publishing_workflow(
            google_docs_url=request.google_docs_url,
            project_id=request.project_id,
            main_keyword=request.main_keyword
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch")
async def batch_publish(request: BatchPublishRequest):
    """
    Execute the publishing workflow for multiple Google Docs URLs.

    Processes items sequentially and returns results for each.
    """
    results = []

    for item in request.items:
        try:
            result = execute_publishing_workflow(
                google_docs_url=item.google_docs_url,
                project_id=request.project_id,
                main_keyword=item.main_keyword
            )
            results.append({
                "google_docs_url": item.google_docs_url,
                **result
            })
        except Exception as e:
            results.append({
                "google_docs_url": item.google_docs_url,
                "success": False,
                "error": str(e)
            })

    success_count = sum(1 for r in results if r.get('success'))
    failed_count = len(results) - success_count

    return {
        "success": failed_count == 0,
        "total": len(results),
        "success_count": success_count,
        "failed_count": failed_count,
        "results": results
    }


@router.post("/convert")
async def convert_google_docs(request: GoogleDocsConvertRequest):
    """
    Convert a Google Docs URL to HTML (test conversion).

    Useful for testing before publishing.
    """
    try:
        result = google_docs_to_html(request.google_docs_url)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
