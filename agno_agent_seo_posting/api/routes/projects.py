"""
Project Management Endpoints

CRUD operations for project configurations.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from api.models.schemas import (
    APIResponse,
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectDetailResponse,
    ProjectStats,
)
from api.core.security import verify_api_key
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.database import (
    create_project,
    get_project,
    update_project,
    delete_project,
    list_projects,
    get_publish_history,
)

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("", response_model=APIResponse, dependencies=[Depends(verify_api_key)])
async def create_new_project(project: ProjectCreate):
    """
    Create a new project configuration.

    Requires authentication via X-API-Key header.
    """
    try:
        # Convert Pydantic models to dicts
        html_configs = project.html_configs.dict() if project.html_configs else None
        image_configs = project.image_configs.dict() if project.image_configs else None

        # Create project in database
        result = create_project(
            project_id=project.project_id,
            project_name=project.project_name,
            wordpress_url=str(project.wordpress_url),
            wordpress_username=project.wordpress_username,
            wordpress_app_password=project.wordpress_app_password,
            html_configs=html_configs,
            image_configs=image_configs,
            notes=project.notes,
        )

        if not result:
            raise HTTPException(status_code=400, detail="Project creation failed. Project ID may already exist.")

        return APIResponse(
            success=True,
            data={"project_id": project.project_id, "message": "Project created successfully"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating project: {str(e)}")


@router.get("", response_model=APIResponse, dependencies=[Depends(verify_api_key)])
async def list_all_projects(
    status: Optional[str] = Query(None, description="Filter by status (active/inactive/all)"),
    limit: Optional[int] = Query(None, description="Limit number of results"),
):
    """
    List all projects.

    Optionally filter by status and limit results.
    """
    try:
        projects = list_projects(status=status or 'all')

        # Apply limit if specified
        if limit and limit > 0:
            projects = projects[:limit]

        # Convert to response format
        project_responses = []
        for proj in projects:
            project_responses.append(ProjectResponse(
                project_id=proj['project_id'],
                project_name=proj['project_name'],
                wordpress_url=proj['wordpress_url'],
                wordpress_username=proj['wordpress_username'],
                html_patterns_count=len(proj.get('html_configs', {}).get('patterns', [])) if proj.get('html_configs') else 0,
                image_width=proj.get('image_configs', {}).get('target_width') if proj.get('image_configs') else None,
                status=proj['status'],
                created_at=proj.get('created_at'),
                updated_at=proj.get('updated_at'),
                last_published_at=proj.get('last_published_at'),
                notes=proj.get('notes'),
            ))

        return APIResponse(success=True, data={"projects": [p.dict() for p in project_responses], "count": len(project_responses)})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing projects: {str(e)}")


@router.get("/{project_id}", response_model=APIResponse, dependencies=[Depends(verify_api_key)])
async def get_project_detail(project_id: str):
    """
    Get detailed information for a specific project.

    Includes full HTML and image configurations.
    """
    try:
        project = get_project(project_id)

        if not project:
            raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found")

        # Convert to detailed response format
        response = ProjectDetailResponse(
            project_id=project['project_id'],
            project_name=project['project_name'],
            wordpress_url=project['wordpress_url'],
            wordpress_username=project['wordpress_username'],
            html_patterns_count=len(project.get('html_configs', {}).get('patterns', [])) if project.get('html_configs') else 0,
            image_width=project.get('image_configs', {}).get('target_width') if project.get('image_configs') else None,
            status=project['status'],
            created_at=project.get('created_at'),
            updated_at=project.get('updated_at'),
            last_published_at=project.get('last_published_at'),
            notes=project.get('notes'),
            html_configs=project.get('html_configs'),
            image_configs=project.get('image_configs'),
        )

        return APIResponse(success=True, data=response.dict())

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving project: {str(e)}")


@router.put("/{project_id}", response_model=APIResponse, dependencies=[Depends(verify_api_key)])
async def update_existing_project(project_id: str, updates: ProjectUpdate):
    """
    Update an existing project configuration.

    Only specified fields will be updated.
    """
    try:
        # Check if project exists
        existing = get_project(project_id)
        if not existing:
            raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found")

        # Build update dict (only include non-None fields)
        update_data = {}
        if updates.project_name is not None:
            update_data['project_name'] = updates.project_name
        if updates.wordpress_url is not None:
            update_data['wordpress_url'] = str(updates.wordpress_url)
        if updates.wordpress_username is not None:
            update_data['wordpress_username'] = updates.wordpress_username
        if updates.wordpress_app_password is not None:
            update_data['wordpress_app_password'] = updates.wordpress_app_password
        if updates.html_configs is not None:
            update_data['html_configs'] = updates.html_configs.dict()
        if updates.image_configs is not None:
            update_data['image_configs'] = updates.image_configs.dict()
        if updates.status is not None:
            update_data['status'] = updates.status
        if updates.notes is not None:
            update_data['notes'] = updates.notes

        # Update project
        result = update_project(project_id, **update_data)

        if not result:
            raise HTTPException(status_code=500, detail="Project update failed")

        return APIResponse(
            success=True,
            data={"project_id": project_id, "message": "Project updated successfully"}
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating project: {str(e)}")


@router.delete("/{project_id}", response_model=APIResponse, dependencies=[Depends(verify_api_key)])
async def delete_existing_project(project_id: str):
    """
    Delete a project configuration.

    Warning: This action cannot be undone.
    """
    try:
        # Check if project exists
        existing = get_project(project_id)
        if not existing:
            raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found")

        # Delete project
        result = delete_project(project_id)

        if not result:
            raise HTTPException(status_code=500, detail="Project deletion failed")

        return APIResponse(
            success=True,
            data={"project_id": project_id, "message": "Project deleted successfully"}
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting project: {str(e)}")


@router.get("/{project_id}/stats", response_model=APIResponse, dependencies=[Depends(verify_api_key)])
async def get_project_statistics(project_id: str):
    """
    Get publishing statistics for a project.

    Returns success rate, average execution time, and other metrics.
    """
    try:
        # Check if project exists
        project = get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found")

        # Get publishing history
        history = get_publish_history(project_id=project_id)

        # Calculate statistics
        total = len(history)
        successful = sum(1 for h in history if h['success'])
        failed = total - successful
        success_rate = (successful / total * 100) if total > 0 else 0.0

        # Calculate average execution time (only successful)
        successful_times = [h['execution_time_seconds'] for h in history if h['success'] and h.get('execution_time_seconds')]
        avg_time = sum(successful_times) / len(successful_times) if successful_times else 0.0

        # Get last publish date
        last_publish = history[0]['published_at'] if history else None

        stats = ProjectStats(
            project_id=project_id,
            project_name=project['project_name'],
            total_publishes=total,
            successful_publishes=successful,
            failed_publishes=failed,
            success_rate=success_rate,
            avg_execution_time=avg_time,
            last_publish_date=last_publish,
        )

        return APIResponse(success=True, data=stats.dict())

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving statistics: {str(e)}")
