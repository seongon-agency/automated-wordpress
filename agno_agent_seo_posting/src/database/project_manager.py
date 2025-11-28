"""
Project Manager - Database operations for multi-project SEO publishing system.

Uses Supabase for cloud database storage (works with Streamlit Cloud deployment).
Provides CRUD operations for projects and publishing history tracking.
"""

import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from supabase import create_client, Client


def get_secret(key: str, default=None):
    """
    Get a secret value with fallback chain:
    1. Streamlit secrets (st.secrets) - for Streamlit Cloud deployment
    2. Environment variable (os.getenv) - for local development
    3. Default value
    """
    # Try Streamlit secrets first
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass

    # Fall back to environment variable
    env_value = os.getenv(key)
    if env_value is not None:
        return env_value

    return default


def get_supabase_client() -> Client:
    """Get Supabase client instance."""
    url = get_secret("SUPABASE_URL")
    key = get_secret("SUPABASE_KEY")

    if not url or not key:
        raise ValueError(
            "Supabase credentials not found. "
            "Please set SUPABASE_URL and SUPABASE_KEY in .streamlit/secrets.toml or environment variables."
        )

    return create_client(url, key)


def init_database() -> None:
    """
    Initialize database - verify connection to Supabase.
    Tables should be created in Supabase dashboard using the SQL provided in schema.sql
    """
    try:
        client = get_supabase_client()
        # Test connection by fetching projects
        client.table("projects").select("project_id").limit(1).execute()
        print("[OK] Connected to Supabase database")
    except Exception as e:
        print(f"[ERROR] Failed to connect to Supabase: {e}")
        raise


# ============================================================================
# PROJECT CRUD OPERATIONS
# ============================================================================

def create_project(
    project_id: str,
    project_name: str,
    wordpress_url: str,
    wordpress_username: str,
    wordpress_app_password: str,
    html_configs: Optional[Dict] = None,
    image_configs: Optional[Dict] = None,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new project.

    Args:
        project_id: Unique identifier (slug format: e.g., "acme_corp")
        project_name: Display name
        wordpress_url: WordPress site URL
        wordpress_username: WP username
        wordpress_app_password: WP application password
        html_configs: Dict with HTML transformation patterns
        image_configs: Dict with image processing settings
        notes: Optional notes for agent

    Returns:
        Dict with created project data
    """
    client = get_supabase_client()

    try:
        data = {
            "project_id": project_id,
            "project_name": project_name,
            "wordpress_url": wordpress_url,
            "wordpress_username": wordpress_username,
            "wordpress_app_password": wordpress_app_password,
            "html_configs": html_configs,
            "image_configs": image_configs,
            "notes": notes,
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        result = client.table("projects").insert(data).execute()

        if result.data:
            return result.data[0]
        else:
            raise Exception("Failed to create project - no data returned")

    except Exception as e:
        if "duplicate key" in str(e).lower() or "unique constraint" in str(e).lower():
            raise ValueError(f"Project with ID '{project_id}' already exists")
        raise Exception(f"Failed to create project: {e}")


def get_project(project_id: str) -> Dict[str, Any]:
    """
    Get project by ID.

    Args:
        project_id: Project identifier

    Returns:
        Dict with project data

    Raises:
        ValueError: If project not found
    """
    client = get_supabase_client()

    result = client.table("projects").select("*").eq("project_id", project_id).execute()

    if not result.data:
        raise ValueError(f"Project '{project_id}' not found")

    return result.data[0]


def update_project(project_id: str, **kwargs) -> Dict[str, Any]:
    """
    Update project fields.

    Args:
        project_id: Project identifier
        **kwargs: Fields to update

    Returns:
        Dict with updated project data
    """
    client = get_supabase_client()

    # Verify project exists
    get_project(project_id)

    # Build update data
    allowed_fields = {
        'project_name', 'wordpress_url', 'wordpress_username',
        'wordpress_app_password', 'html_configs', 'image_configs',
        'status', 'notes'
    }

    updates = {}
    for key, value in kwargs.items():
        if key in allowed_fields:
            updates[key] = value

    if not updates:
        return get_project(project_id)

    # Add updated_at timestamp
    updates['updated_at'] = datetime.now().isoformat()

    try:
        result = client.table("projects").update(updates).eq("project_id", project_id).execute()

        if result.data:
            return result.data[0]
        else:
            return get_project(project_id)

    except Exception as e:
        raise Exception(f"Failed to update project: {e}")


def delete_project(project_id: str) -> bool:
    """
    Delete project by ID.

    Args:
        project_id: Project identifier

    Returns:
        True if deleted, False if not found
    """
    client = get_supabase_client()

    try:
        result = client.table("projects").delete().eq("project_id", project_id).execute()
        return len(result.data) > 0 if result.data else False
    except Exception:
        return False


def list_projects(status: str = 'active') -> List[Dict[str, Any]]:
    """
    List all projects with given status.

    Args:
        status: Filter by status ('active', 'inactive', 'testing', or 'all')

    Returns:
        List of project dicts
    """
    client = get_supabase_client()

    try:
        if status == 'all':
            result = client.table("projects").select("*").order("project_name").execute()
        else:
            result = client.table("projects").select("*").eq("status", status).order("project_name").execute()

        return result.data if result.data else []

    except Exception as e:
        print(f"Error listing projects: {e}")
        return []


# ============================================================================
# PUBLISHING HISTORY OPERATIONS
# ============================================================================

def log_publish(
    google_docs_url: str,
    success: bool,
    project_id: Optional[str] = None,
    wordpress_post_id: Optional[int] = None,
    wordpress_post_url: Optional[str] = None,
    post_title: Optional[str] = None,
    post_status: Optional[str] = None,
    images_processed: int = 0,
    error_message: Optional[str] = None,
    execution_time_seconds: Optional[float] = None
) -> int:
    """
    Log a publishing attempt to history.

    Args:
        google_docs_url: Source Google Docs URL
        success: Whether publish was successful
        project_id: Project ID (None if "no-project" option)
        wordpress_post_id: WP post ID if successful
        wordpress_post_url: Full URL to published post
        post_title: Post title
        post_status: draft or publish
        images_processed: Number of images processed
        error_message: Error message if failed
        execution_time_seconds: Total execution time

    Returns:
        publish_id of created record
    """
    client = get_supabase_client()

    try:
        data = {
            "project_id": project_id,
            "google_docs_url": google_docs_url,
            "wordpress_post_id": wordpress_post_id,
            "wordpress_post_url": wordpress_post_url,
            "post_title": post_title,
            "post_status": post_status,
            "images_processed": images_processed,
            "success": success,
            "error_message": error_message,
            "execution_time_seconds": execution_time_seconds,
            "published_at": datetime.now().isoformat()
        }

        result = client.table("publishing_history").insert(data).execute()

        # Update last_published_at for project if successful
        if success and project_id:
            client.table("projects").update({
                "last_published_at": datetime.now().isoformat()
            }).eq("project_id", project_id).execute()

        if result.data:
            return result.data[0].get('publish_id', 0)
        return 0

    except Exception as e:
        print(f"Failed to log publish: {e}")
        return 0


def get_publish_history(
    project_id: Optional[str] = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Get publishing history.

    Args:
        project_id: Filter by project (None = all projects)
        limit: Maximum number of records to return

    Returns:
        List of publishing history records (newest first)
    """
    client = get_supabase_client()

    try:
        query = client.table("publishing_history").select("*")

        if project_id:
            query = query.eq("project_id", project_id)

        result = query.order("published_at", desc=True).limit(limit).execute()

        return result.data if result.data else []

    except Exception as e:
        print(f"Error getting publish history: {e}")
        return []
