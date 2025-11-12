"""
Project Manager - Database operations for multi-project SEO publishing system.

Provides CRUD operations for projects and publishing history tracking.
Uses JSON columns for flexible configuration storage.
"""

import sqlite3
import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path


# Database path - defaults to data/clients.db in project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
DEFAULT_DB_PATH = PROJECT_ROOT / 'data' / 'clients.db'
DB_PATH = os.getenv('CLIENT_DB_PATH', str(DEFAULT_DB_PATH))


def get_connection() -> sqlite3.Connection:
    """Get database connection with JSON support."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn


def init_database() -> None:
    """Initialize database with schema."""
    schema_path = Path(__file__).parent / 'schema.sql'

    with open(schema_path, 'r') as f:
        schema_sql = f.read()

    conn = get_connection()
    try:
        conn.executescript(schema_sql)
        conn.commit()
        print(f"[OK] Database initialized: {DB_PATH}")
    except Exception as e:
        print(f"[ERROR] Failed to initialize database: {e}")
        raise
    finally:
        conn.close()


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
        html_configs: Dict with HTML transformation patterns (will be stored as JSON)
        image_configs: Dict with image processing settings (will be stored as JSON)
        notes: Optional notes for agent

    Returns:
        Dict with created project data

    Example html_configs:
        {
            "patterns": [
                {
                    "element_type": "p",
                    "source_pattern": "<p[^>]*>(.*?)</p>",
                    "target_pattern": "<p class=\"article-body\">\\1</p>"
                }
            ]
        }

    Example image_configs:
        {
            "target_width": 800,
            "image_quality": 92,
            "image_format": "JPEG",
            "css_classes": "wp-image aligncenter"
        }
    """
    conn = get_connection()

    try:
        conn.execute('''
            INSERT INTO projects (
                project_id, project_name, wordpress_url,
                wordpress_username, wordpress_app_password,
                html_configs, image_configs, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            project_id,
            project_name,
            wordpress_url,
            wordpress_username,
            wordpress_app_password,
            json.dumps(html_configs) if html_configs else None,
            json.dumps(image_configs) if image_configs else None,
            notes
        ))
        conn.commit()

        return get_project(project_id)

    except sqlite3.IntegrityError:
        raise ValueError(f"Project with ID '{project_id}' already exists")
    except Exception as e:
        conn.rollback()
        raise Exception(f"Failed to create project: {e}")
    finally:
        conn.close()


def get_project(project_id: str) -> Dict[str, Any]:
    """
    Get project by ID.

    Args:
        project_id: Project identifier

    Returns:
        Dict with project data (html_configs and image_configs parsed from JSON)

    Raises:
        ValueError: If project not found
    """
    conn = get_connection()

    try:
        cursor = conn.execute(
            'SELECT * FROM projects WHERE project_id = ?',
            (project_id,)
        )
        row = cursor.fetchone()

        if not row:
            raise ValueError(f"Project '{project_id}' not found")

        # Convert row to dict and parse JSON fields
        project = dict(row)
        project['html_configs'] = json.loads(project['html_configs']) if project['html_configs'] else None
        project['image_configs'] = json.loads(project['image_configs']) if project['image_configs'] else None

        return project

    finally:
        conn.close()


def update_project(project_id: str, **kwargs) -> Dict[str, Any]:
    """
    Update project fields.

    Args:
        project_id: Project identifier
        **kwargs: Fields to update (html_configs and image_configs will be JSON-encoded)

    Returns:
        Dict with updated project data

    Example:
        update_project('acme_corp', wordpress_url='https://newsite.com')
        update_project('acme_corp', html_configs={'patterns': [...]})
    """
    conn = get_connection()

    # Verify project exists
    try:
        get_project(project_id)
    except ValueError:
        conn.close()
        raise

    # Build update query dynamically
    allowed_fields = {
        'project_name', 'wordpress_url', 'wordpress_username',
        'wordpress_app_password', 'html_configs', 'image_configs',
        'status', 'notes'
    }

    updates = {}
    for key, value in kwargs.items():
        if key in allowed_fields:
            # JSON-encode dict fields
            if key in ('html_configs', 'image_configs') and isinstance(value, dict):
                updates[key] = json.dumps(value)
            else:
                updates[key] = value

    if not updates:
        conn.close()
        return get_project(project_id)

    # Add updated_at timestamp
    updates['updated_at'] = datetime.now().isoformat()

    set_clause = ', '.join([f'{key} = ?' for key in updates.keys()])
    values = list(updates.values()) + [project_id]

    try:
        conn.execute(
            f'UPDATE projects SET {set_clause} WHERE project_id = ?',
            values
        )
        conn.commit()

        return get_project(project_id)

    except Exception as e:
        conn.rollback()
        raise Exception(f"Failed to update project: {e}")
    finally:
        conn.close()


def delete_project(project_id: str) -> bool:
    """
    Delete project by ID.

    Args:
        project_id: Project identifier

    Returns:
        True if deleted, False if not found
    """
    conn = get_connection()

    try:
        cursor = conn.execute(
            'DELETE FROM projects WHERE project_id = ?',
            (project_id,)
        )
        conn.commit()

        return cursor.rowcount > 0

    finally:
        conn.close()


def list_projects(status: str = 'active') -> List[Dict[str, Any]]:
    """
    List all projects with given status.

    Args:
        status: Filter by status ('active', 'inactive', 'testing', or 'all')

    Returns:
        List of project dicts (html_configs and image_configs parsed from JSON)
    """
    conn = get_connection()

    try:
        if status == 'all':
            cursor = conn.execute('SELECT * FROM projects ORDER BY project_name')
        else:
            cursor = conn.execute(
                'SELECT * FROM projects WHERE status = ? ORDER BY project_name',
                (status,)
            )

        rows = cursor.fetchall()

        # Convert rows to dicts and parse JSON fields
        projects = []
        for row in rows:
            project = dict(row)
            project['html_configs'] = json.loads(project['html_configs']) if project['html_configs'] else None
            project['image_configs'] = json.loads(project['image_configs']) if project['image_configs'] else None
            projects.append(project)

        return projects

    finally:
        conn.close()


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
    conn = get_connection()

    try:
        cursor = conn.execute('''
            INSERT INTO publishing_history (
                project_id, google_docs_url, wordpress_post_id,
                wordpress_post_url, post_title, post_status,
                images_processed, success, error_message, execution_time_seconds
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            project_id,
            google_docs_url,
            wordpress_post_id,
            wordpress_post_url,
            post_title,
            post_status,
            images_processed,
            success,
            error_message,
            execution_time_seconds
        ))
        conn.commit()

        # Update last_published_at for project if successful
        if success and project_id:
            conn.execute(
                'UPDATE projects SET last_published_at = ? WHERE project_id = ?',
                (datetime.now().isoformat(), project_id)
            )
            conn.commit()

        return cursor.lastrowid

    except Exception as e:
        conn.rollback()
        raise Exception(f"Failed to log publish: {e}")
    finally:
        conn.close()


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
    conn = get_connection()

    try:
        if project_id:
            cursor = conn.execute('''
                SELECT * FROM publishing_history
                WHERE project_id = ?
                ORDER BY published_at DESC
                LIMIT ?
            ''', (project_id, limit))
        else:
            cursor = conn.execute('''
                SELECT * FROM publishing_history
                ORDER BY published_at DESC
                LIMIT ?
            ''', (limit,))

        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    finally:
        conn.close()
