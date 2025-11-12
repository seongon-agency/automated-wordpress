"""
Publishing Workflow Endpoints

Handles content publishing from Google Docs to WordPress.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from api.models.schemas import (
    APIResponse,
    PublishRequest,
    PublishResponse,
    PublishHistoryItem,
    BatchPublishRequest,
    BatchPublishResponse,
    BatchPublishItemResult,
    HTMLAnalysisRequest,
    HTMLAnalysisResponse,
    PatternModifyRequest,
    PatternModifyResponse,
)
from api.core.security import verify_api_key
import sys
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.workflows.publishing_workflow import execute_publishing_workflow
from src.database import get_publish_history, get_project
from src.utils.pattern_modifier import modify_patterns_with_ai

router = APIRouter(prefix="/publish", tags=["Publishing"])


# Thread pool for background tasks
executor = ThreadPoolExecutor(max_workers=10)


@router.post("", response_model=APIResponse, dependencies=[Depends(verify_api_key)])
async def publish_content(request: PublishRequest):
    """
    Publish content from Google Docs to WordPress.

    This endpoint:
    1. Converts Google Docs to HTML
    2. Processes images
    3. Applies project-specific transformations (if project_id provided)
    4. Publishes to WordPress

    Returns the WordPress post URL and publishing details.
    """
    try:
        # Execute publishing workflow
        result = execute_publishing_workflow(
            google_docs_url=str(request.google_docs_url),
            project_id=request.project_id
        )

        # Convert to response format
        response = PublishResponse(
            success=result['success'],
            post_title=result.get('post_title'),
            post_url=result.get('post_url'),
            wordpress_post_id=result.get('wordpress_post_id'),
            images_processed=result.get('images_processed', 0),
            execution_time=result.get('execution_time', 0.0),
            error=result.get('error'),
            step_failed=result.get('step_failed'),
        )

        return APIResponse(success=result['success'], data=response.dict())

    except Exception as e:
        return APIResponse(
            success=False,
            error=f"Publishing failed: {str(e)}"
        )


async def publish_single_item(item: dict) -> dict:
    """Helper function to publish a single item"""
    try:
        result = await asyncio.get_event_loop().run_in_executor(
            executor,
            execute_publishing_workflow,
            item['google_docs_url'],
            item.get('project_id')
        )

        return {
            'item_id': item.get('item_id'),
            'google_docs_url': item['google_docs_url'],
            'success': result['success'],
            'post_url': result.get('post_url'),
            'error': result.get('error'),
        }
    except Exception as e:
        return {
            'item_id': item.get('item_id'),
            'google_docs_url': item['google_docs_url'],
            'success': False,
            'post_url': None,
            'error': str(e),
        }


@router.post("/batch", response_model=APIResponse, dependencies=[Depends(verify_api_key)])
async def batch_publish(request: BatchPublishRequest):
    """
    Publish multiple pieces of content in parallel.

    This is the key endpoint for Lark Base integration, enabling:
    - Bulk processing of content queue
    - Parallel execution for speed
    - Individual result tracking per item

    Maximum 50 items per batch.
    """
    try:
        # Convert items to dicts
        items = [
            {
                'google_docs_url': str(item.google_docs_url),
                'project_id': item.project_id,
                'item_id': item.item_id,
            }
            for item in request.items
        ]

        # Execute all publishes in parallel
        tasks = [publish_single_item(item) for item in items]
        results = await asyncio.gather(*tasks)

        # Count successes and failures
        successful = sum(1 for r in results if r['success'])
        failed = len(results) - successful

        # Convert to response format
        item_results = [BatchPublishItemResult(**r) for r in results]

        batch_response = BatchPublishResponse(
            total=len(results),
            successful=successful,
            failed=failed,
            results=item_results,
        )

        return APIResponse(success=True, data=batch_response.dict())

    except Exception as e:
        return APIResponse(
            success=False,
            error=f"Batch publishing failed: {str(e)}"
        )


@router.get("/history", response_model=APIResponse, dependencies=[Depends(verify_api_key)])
async def get_publishing_history(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    limit: Optional[int] = Query(50, description="Limit number of results"),
    offset: Optional[int] = Query(0, description="Offset for pagination"),
):
    """
    Get publishing history.

    Returns a list of all publishing attempts with results.
    Optionally filter by project and paginate results.
    """
    try:
        # Get history from database
        history = get_publish_history(project_id=project_id, limit=limit)

        # Apply offset if specified
        if offset > 0:
            history = history[offset:]

        # Convert to response format
        history_items = []
        for h in history:
            # Get project name if project_id exists
            project_name = None
            if h.get('project_id'):
                proj = get_project(h['project_id'])
                project_name = proj['project_name'] if proj else None

            history_items.append(PublishHistoryItem(
                id=h['id'],
                google_docs_url=h['google_docs_url'],
                project_id=h.get('project_id'),
                project_name=project_name,
                success=h['success'],
                post_title=h.get('post_title'),
                post_url=h.get('wordpress_post_url'),
                wordpress_post_id=h.get('wordpress_post_id'),
                images_processed=h.get('images_processed', 0),
                execution_time=h.get('execution_time_seconds', 0.0),
                error_message=h.get('error_message'),
                published_at=h['published_at'],
            ))

        return APIResponse(
            success=True,
            data={
                "history": [h.dict() for h in history_items],
                "count": len(history_items),
                "offset": offset,
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving history: {str(e)}")


@router.post("/analyze-html", response_model=APIResponse, dependencies=[Depends(verify_api_key)])
async def analyze_html_sample(request: HTMLAnalysisRequest):
    """
    Analyze HTML sample and extract patterns.

    Uses AI to identify HTML elements and generate transformation patterns.
    Useful for project configuration via API.
    """
    try:
        # Import the AI analysis function
        from app.configure import analyze_html_sample_with_ai

        # Analyze HTML
        html_configs = analyze_html_sample_with_ai(request.html_sample)

        if not html_configs:
            return APIResponse(
                success=False,
                error="Failed to analyze HTML. Check ANTHROPIC_API_KEY configuration."
            )

        patterns_found = len(html_configs.get('patterns', []))

        response = HTMLAnalysisResponse(
            success=True,
            html_configs=html_configs,
            patterns_found=patterns_found,
        )

        return APIResponse(success=True, data=response.dict())

    except Exception as e:
        return APIResponse(
            success=False,
            error=f"HTML analysis failed: {str(e)}"
        )


@router.post("/modify-patterns", response_model=APIResponse, dependencies=[Depends(verify_api_key)])
async def modify_patterns_natural_language(request: PatternModifyRequest):
    """
    Modify HTML patterns using natural language.

    Example: "Make all h2 headings blue"

    Returns a preview of changes before applying them.
    Use the PUT /projects/{project_id} endpoint to save the changes.
    """
    try:
        # Get current project
        project = get_project(request.project_id)
        if not project:
            raise HTTPException(status_code=404, detail=f"Project '{request.project_id}' not found")

        current_configs = project.get('html_configs')
        if not current_configs or not current_configs.get('patterns'):
            return APIResponse(
                success=False,
                error="Project has no HTML patterns to modify"
            )

        # Modify patterns with AI
        modified_configs = modify_patterns_with_ai(current_configs, request.instruction)

        if not modified_configs:
            return APIResponse(
                success=False,
                error="Failed to modify patterns. Check instruction and try again."
            )

        # Generate previews
        previews = []
        current_patterns = {p['element_type']: p for p in current_configs.get('patterns', [])}
        modified_patterns = {p['element_type']: p for p in modified_configs.get('patterns', [])}

        for element_type, modified in modified_patterns.items():
            current = current_patterns.get(element_type, {})
            if modified['target_pattern'] != current.get('target_pattern'):
                previews.append({
                    'element_type': element_type,
                    'current_pattern': current.get('target_pattern', 'N/A'),
                    'modified_pattern': modified['target_pattern'],
                    'changes_description': f"Modified {element_type} pattern",
                })

        response = PatternModifyResponse(
            success=True,
            previews=previews,
        )

        # Include modified configs in response for saving
        return APIResponse(
            success=True,
            data={
                **response.dict(),
                "modified_html_configs": modified_configs,
                "message": "Preview generated. Use PUT /projects/{project_id} to save changes."
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        return APIResponse(
            success=False,
            error=f"Pattern modification failed: {str(e)}"
        )
