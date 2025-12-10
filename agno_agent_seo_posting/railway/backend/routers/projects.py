"""Projects API Router"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
from typing import Optional, Dict, Any, List
import re

from database.db import (
    list_projects as db_list_projects,
    get_project as db_get_project,
    create_project as db_create_project,
    update_project as db_update_project,
    delete_project as db_delete_project
)

logger = logging.getLogger(__name__)

router = APIRouter()


class ProjectCreate(BaseModel):
    project_id: str
    project_name: str
    wordpress_url: str
    wordpress_username: str
    wordpress_app_password: str
    html_configs: Optional[Dict[str, Any]] = None
    image_configs: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None

    @field_validator('project_id')
    @classmethod
    def validate_project_id(cls, v: str) -> str:
        if not v or len(v) < 1:
            raise ValueError('Project ID is required')
        if len(v) > 100:
            raise ValueError('Project ID must be 100 characters or less')
        if not re.match(r'^[a-z0-9_]+$', v):
            raise ValueError('Project ID must contain only lowercase letters, numbers, and underscores')
        return v

    @field_validator('project_name')
    @classmethod
    def validate_project_name(cls, v: str) -> str:
        if not v or len(v.strip()) < 1:
            raise ValueError('Project name is required')
        if len(v) > 255:
            raise ValueError('Project name must be 255 characters or less')
        return v.strip()

    @field_validator('wordpress_url')
    @classmethod
    def validate_wordpress_url(cls, v: str) -> str:
        if not v or len(v.strip()) < 1:
            raise ValueError('WordPress URL is required')
        if len(v) > 500:
            raise ValueError('WordPress URL must be 500 characters or less')
        # Basic URL validation
        if not re.match(r'^https?://', v):
            raise ValueError('WordPress URL must start with http:// or https://')
        return v.strip().rstrip('/')

    @field_validator('wordpress_username')
    @classmethod
    def validate_wordpress_username(cls, v: str) -> str:
        if not v or len(v.strip()) < 1:
            raise ValueError('WordPress username is required')
        if len(v) > 255:
            raise ValueError('WordPress username must be 255 characters or less')
        return v.strip()

    @field_validator('wordpress_app_password')
    @classmethod
    def validate_wordpress_app_password(cls, v: str) -> str:
        if not v or len(v.strip()) < 1:
            raise ValueError('WordPress app password is required')
        if len(v) > 255:
            raise ValueError('WordPress app password must be 255 characters or less')
        return v.strip()


class ProjectUpdate(BaseModel):
    project_name: Optional[str] = None
    wordpress_url: Optional[str] = None
    wordpress_username: Optional[str] = None
    wordpress_app_password: Optional[str] = None
    html_configs: Optional[Dict[str, Any]] = None
    image_configs: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    status: Optional[str] = None

    @field_validator('project_name')
    @classmethod
    def validate_project_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if len(v.strip()) < 1:
            raise ValueError('Project name cannot be empty')
        if len(v) > 255:
            raise ValueError('Project name must be 255 characters or less')
        return v.strip()

    @field_validator('wordpress_url')
    @classmethod
    def validate_wordpress_url(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if len(v) > 500:
            raise ValueError('WordPress URL must be 500 characters or less')
        if not re.match(r'^https?://', v):
            raise ValueError('WordPress URL must start with http:// or https://')
        return v.strip().rstrip('/')

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        allowed_statuses = {'active', 'inactive', 'paused'}
        if v not in allowed_statuses:
            raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v


def serialize_project(project: Dict[str, Any]) -> Dict[str, Any]:
    """Serialize project for JSON response"""
    if project is None:
        return None

    result = dict(project)

    # Convert datetime objects to ISO strings
    for key in ['created_at', 'updated_at', 'last_published_at']:
        if key in result and result[key] is not None:
            result[key] = result[key].isoformat() if hasattr(result[key], 'isoformat') else str(result[key])

    return result


@router.get("/")
async def list_projects(status: str = "all"):
    """List all projects"""
    try:
        projects = db_list_projects(status=status)
        return {
            "success": True,
            "projects": [serialize_project(p) for p in projects],
            "count": len(projects)
        }
    except Exception as e:
        logger.error(f"Failed to list projects: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve projects")


@router.get("/{project_id}")
async def get_project(project_id: str):
    """Get project by ID"""
    try:
        project = db_get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        return {
            "success": True,
            "project": serialize_project(project)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get project {project_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve project")


@router.post("/")
async def create_project(project: ProjectCreate):
    """Create a new project"""
    try:
        # Check if project already exists
        existing = db_get_project(project.project_id)
        if existing:
            raise HTTPException(
                status_code=400,
                detail="A project with this ID already exists"
            )

        new_project = db_create_project(
            project_id=project.project_id,
            project_name=project.project_name,
            wordpress_url=project.wordpress_url,
            wordpress_username=project.wordpress_username,
            wordpress_app_password=project.wordpress_app_password,
            html_configs=project.html_configs,
            image_configs=project.image_configs,
            notes=project.notes
        )

        return {
            "success": True,
            "project": serialize_project(new_project)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create project: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create project")


@router.put("/{project_id}")
async def update_project(project_id: str, updates: ProjectUpdate):
    """Update a project"""
    try:
        # Check if project exists
        existing = db_get_project(project_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Project not found")

        # Build update dict from non-None values
        update_data = {}
        if updates.project_name is not None:
            update_data['project_name'] = updates.project_name
        if updates.wordpress_url is not None:
            update_data['wordpress_url'] = updates.wordpress_url
        if updates.wordpress_username is not None:
            update_data['wordpress_username'] = updates.wordpress_username
        if updates.wordpress_app_password is not None:
            update_data['wordpress_app_password'] = updates.wordpress_app_password
        if updates.html_configs is not None:
            update_data['html_configs'] = updates.html_configs
        if updates.image_configs is not None:
            update_data['image_configs'] = updates.image_configs
        if updates.notes is not None:
            update_data['notes'] = updates.notes
        if updates.status is not None:
            update_data['status'] = updates.status

        updated_project = db_update_project(project_id, **update_data)

        return {
            "success": True,
            "project": serialize_project(updated_project)
        }
    except HTTPException:
        raise
    except ValueError as e:
        # Handle invalid field errors from db layer
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update project {project_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update project")


@router.delete("/{project_id}")
async def delete_project(project_id: str):
    """Delete a project"""
    try:
        # Check if project exists
        existing = db_get_project(project_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Project not found")

        success = db_delete_project(project_id)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete project")

        return {
            "success": True,
            "message": "Project deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete project {project_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete project")
