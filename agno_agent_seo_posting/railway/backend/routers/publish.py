"""Publishing API Router"""

import logging
import asyncio
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
from typing import Optional, List
from urllib.parse import urlparse
import re

from services.workflow import execute_publishing_workflow
from database.db import get_project as db_get_project, log_publishing

logger = logging.getLogger(__name__)
router = APIRouter()

# Timeout constants
SINGLE_PUBLISH_TIMEOUT = 180  # 3 minutes for single publish
BATCH_ITEM_TIMEOUT = 180  # 3 minutes per batch item


def validate_wordpress_url(url: str) -> bool:
    """Validate WordPress URL to prevent SSRF attacks"""
    if not url:
        return False
    try:
        parsed = urlparse(url)
        # Must be http or https
        if parsed.scheme not in ('http', 'https'):
            return False
        # Must have a valid hostname
        if not parsed.netloc:
            return False
        # Block private/internal addresses
        hostname = parsed.hostname or ''
        blocked_hosts = ['localhost', '127.0.0.1', '0.0.0.0', '::1']
        if hostname in blocked_hosts:
            return False
        # Block private IP ranges
        if hostname.startswith('10.') or hostname.startswith('192.168.') or hostname.startswith('172.'):
            return False
        return True
    except Exception:
        return False


class PublishRequest(BaseModel):
    google_docs_url: str
    project_id: Optional[str] = None
    main_keyword: Optional[str] = None

    @field_validator('google_docs_url')
    @classmethod
    def validate_google_docs_url(cls, v: str) -> str:
        if not v or len(v.strip()) < 1:
            raise ValueError('Google Docs URL is required')
        if len(v) > 1000:
            raise ValueError('URL is too long')
        # Basic validation - must be a Google Docs URL
        if 'docs.google.com' not in v and 'drive.google.com' not in v:
            raise ValueError('Must be a valid Google Docs or Drive URL')
        return v.strip()


class BatchItem(BaseModel):
    url: str
    keyword: Optional[str] = None


class BatchPublishRequest(BaseModel):
    project_id: str
    items: List[BatchItem]

    @field_validator('items')
    @classmethod
    def validate_items(cls, v: List[BatchItem]) -> List[BatchItem]:
        if not v or len(v) == 0:
            raise ValueError('At least one item is required')
        if len(v) > 50:
            raise ValueError('Maximum 50 items per batch')
        return v


class PublishResponse(BaseModel):
    success: bool
    post_url: Optional[str] = None
    edit_url: Optional[str] = None
    post_id: Optional[int] = None
    post_title: Optional[str] = None
    post_status: Optional[str] = None
    images_processed: Optional[int] = None
    execution_time: Optional[float] = None
    error: Optional[str] = None
    step_failed: Optional[str] = None


class BatchItemResult(BaseModel):
    url: str
    success: bool
    post_url: Optional[str] = None
    post_title: Optional[str] = None
    error: Optional[str] = None


class BatchPublishResponse(BaseModel):
    success: bool
    total: int
    completed: int
    failed: int
    results: List[BatchItemResult]


@router.post("/single", response_model=PublishResponse)
async def publish_single(request: PublishRequest):
    """
    Execute the complete publishing workflow for a single document.

    Steps:
    1. Convert Google Docs to HTML
    2. Extract title and clean HTML
    3. Process images (download & resize)
    4. Upload images to WordPress
    5. Apply HTML transformations
    6. Create WordPress post
    """
    try:
        # Get project configuration if project_id provided
        project = None
        if request.project_id:
            project = db_get_project(request.project_id)
            if not project:
                return PublishResponse(
                    success=False,
                    error="Project not found",
                    step_failed="project_lookup"
                )

            # Validate WordPress URL to prevent SSRF
            if not validate_wordpress_url(project['wordpress_url']):
                logger.warning(f"Invalid WordPress URL for project {request.project_id}")
                return PublishResponse(
                    success=False,
                    error="Invalid WordPress URL configuration",
                    step_failed="url_validation"
                )

        # Execute workflow with timeout
        try:
            result = await asyncio.wait_for(
                execute_publishing_workflow(
                    google_docs_url=request.google_docs_url,
                    wordpress_url=project['wordpress_url'] if project else None,
                    wordpress_username=project['wordpress_username'] if project else None,
                    wordpress_app_password=project['wordpress_app_password'] if project else None,
                    html_configs=project.get('html_configs') if project else None,
                    image_configs=project.get('image_configs') if project else None,
                    main_keyword=request.main_keyword,
                    project_id=request.project_id
                ),
                timeout=SINGLE_PUBLISH_TIMEOUT
            )
        except asyncio.TimeoutError:
            logger.error(f"Publishing timeout for project {request.project_id}")
            return PublishResponse(
                success=False,
                error="Publishing operation timed out. Please try again.",
                step_failed="timeout"
            )

        # Log to publishing history
        try:
            log_publishing(
                project_id=request.project_id,
                google_docs_url=request.google_docs_url,
                success=result.get('success', False),
                wordpress_post_id=result.get('post_id'),
                wordpress_post_url=result.get('post_url'),
                post_title=result.get('post_title'),
                post_status=result.get('post_status'),
                images_processed=result.get('images_processed', 0),
                error_message=result.get('error'),
                execution_time_seconds=result.get('execution_time')
            )
        except Exception as log_error:
            logger.warning(f"Failed to log publishing history: {log_error}")

        return PublishResponse(**{k: v for k, v in result.items() if k in PublishResponse.model_fields})

    except Exception as e:
        logger.error(f"Publishing failed: {e}", exc_info=True)
        return PublishResponse(
            success=False,
            error="An unexpected error occurred during publishing",
            step_failed="unexpected_error"
        )


@router.post("/batch", response_model=BatchPublishResponse)
async def batch_publish(request: BatchPublishRequest):
    """Publish multiple documents sequentially"""
    try:
        # Validate project exists
        project = db_get_project(request.project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Validate WordPress URL to prevent SSRF
        if not validate_wordpress_url(project['wordpress_url']):
            logger.warning(f"Invalid WordPress URL for project {request.project_id}")
            raise HTTPException(status_code=400, detail="Invalid WordPress URL configuration")

        results: List[BatchItemResult] = []
        completed = 0
        failed = 0

        for item in request.items:
            try:
                # Execute with timeout per item
                try:
                    result = await asyncio.wait_for(
                        execute_publishing_workflow(
                            google_docs_url=item.url,
                            wordpress_url=project['wordpress_url'],
                            wordpress_username=project['wordpress_username'],
                            wordpress_app_password=project['wordpress_app_password'],
                            html_configs=project.get('html_configs'),
                            image_configs=project.get('image_configs'),
                            main_keyword=item.keyword,
                            project_id=request.project_id
                        ),
                        timeout=BATCH_ITEM_TIMEOUT
                    )
                except asyncio.TimeoutError:
                    logger.error(f"Batch item timeout for URL: {item.url[:50]}...")
                    failed += 1
                    results.append(BatchItemResult(
                        url=item.url,
                        success=False,
                        error="Processing timed out"
                    ))
                    continue

                # Log to history
                try:
                    log_publishing(
                        project_id=request.project_id,
                        google_docs_url=item.url,
                        success=result.get('success', False),
                        wordpress_post_id=result.get('post_id'),
                        wordpress_post_url=result.get('post_url'),
                        post_title=result.get('post_title'),
                        post_status=result.get('post_status'),
                        images_processed=result.get('images_processed', 0),
                        error_message=result.get('error'),
                        execution_time_seconds=result.get('execution_time')
                    )
                except Exception as log_error:
                    logger.warning(f"Failed to log publishing history: {log_error}")

                if result.get('success'):
                    completed += 1
                    results.append(BatchItemResult(
                        url=item.url,
                        success=True,
                        post_url=result.get('post_url'),
                        post_title=result.get('post_title')
                    ))
                else:
                    failed += 1
                    results.append(BatchItemResult(
                        url=item.url,
                        success=False,
                        error=result.get('error', 'Unknown error')
                    ))

            except Exception as item_error:
                logger.error(f"Batch item failed: {item_error}", exc_info=True)
                failed += 1
                results.append(BatchItemResult(
                    url=item.url,
                    success=False,
                    error="Processing failed"
                ))

        return BatchPublishResponse(
            success=failed == 0,
            total=len(request.items),
            completed=completed,
            failed=failed,
            results=results
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch publishing failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Batch publishing failed")
