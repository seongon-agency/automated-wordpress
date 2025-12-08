"""
Projects Router - CRUD operations for projects.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from database import (
    create_project,
    get_project,
    update_project,
    delete_project,
    list_projects
)


router = APIRouter()


# Pydantic models for request/response
class ImageConfig(BaseModel):
    resize_method: str = "fixed_width"
    target_width: int = 800
    target_height: Optional[int] = None
    image_quality: int = 92
    image_format: str = "JPEG"
    enable_auto_captions: bool = True
    naming_method: str = "default"
    alt_text_words: int = 5
    google_drive_folder_url: Optional[str] = None


class HtmlPattern(BaseModel):
    element_type: str
    source_pattern: str
    target_pattern: str


class HtmlConfig(BaseModel):
    patterns: List[HtmlPattern] = []


class ProjectCreate(BaseModel):
    project_id: str
    project_name: str
    wordpress_url: str
    wordpress_username: str
    wordpress_app_password: str
    html_configs: Optional[HtmlConfig] = None
    image_configs: Optional[ImageConfig] = None
    notes: Optional[str] = None


class ProjectUpdate(BaseModel):
    project_name: Optional[str] = None
    wordpress_url: Optional[str] = None
    wordpress_username: Optional[str] = None
    wordpress_app_password: Optional[str] = None
    html_configs: Optional[HtmlConfig] = None
    image_configs: Optional[ImageConfig] = None
    status: Optional[str] = None
    notes: Optional[str] = None


@router.get("")
async def get_projects(status: str = "active"):
    """
    Get all projects.

    Args:
        status: Filter by status ('active', 'inactive', 'all')
    """
    try:
        projects = list_projects(status=status)
        return {"success": True, "projects": projects}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("")
async def create_new_project(project: ProjectCreate):
    """Create a new project."""
    try:
        result = create_project(
            project_id=project.project_id,
            project_name=project.project_name,
            wordpress_url=project.wordpress_url,
            wordpress_username=project.wordpress_username,
            wordpress_app_password=project.wordpress_app_password,
            html_configs=project.html_configs.dict() if project.html_configs else None,
            image_configs=project.image_configs.dict() if project.image_configs else None,
            notes=project.notes
        )
        return {"success": True, "project": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_id}")
async def get_single_project(project_id: str):
    """Get a single project by ID."""
    try:
        project = get_project(project_id)
        return {"success": True, "project": project}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{project_id}")
async def update_existing_project(project_id: str, project: ProjectUpdate):
    """Update an existing project."""
    try:
        update_data = project.dict(exclude_unset=True)

        # Convert Pydantic models to dicts
        if 'html_configs' in update_data and update_data['html_configs']:
            update_data['html_configs'] = update_data['html_configs'].dict() if hasattr(update_data['html_configs'], 'dict') else update_data['html_configs']
        if 'image_configs' in update_data and update_data['image_configs']:
            update_data['image_configs'] = update_data['image_configs'].dict() if hasattr(update_data['image_configs'], 'dict') else update_data['image_configs']

        result = update_project(project_id, **update_data)
        return {"success": True, "project": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{project_id}")
async def delete_existing_project(project_id: str):
    """Delete a project by ID."""
    try:
        success = delete_project(project_id)
        if success:
            return {"success": True, "message": f"Project '{project_id}' deleted"}
        else:
            raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
