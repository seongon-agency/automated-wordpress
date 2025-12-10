"""
Database Connection Module

Uses Railway PostgreSQL database with raw SQL queries.
"""

import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from contextlib import contextmanager
import psycopg2
from psycopg2.extras import RealDictCursor


def get_database_url() -> str:
    """Get database URL from environment"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError(
            "DATABASE_URL not found. "
            "Please set DATABASE_URL in environment variables."
        )
    return database_url


@contextmanager
def get_db_connection():
    """Get database connection as context manager"""
    database_url = get_database_url()
    conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_database():
    """Initialize database - create tables if not exist"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Create projects table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    project_id VARCHAR(255) PRIMARY KEY,
                    project_name VARCHAR(255) NOT NULL,
                    wordpress_url VARCHAR(500) NOT NULL,
                    wordpress_username VARCHAR(255) NOT NULL,
                    wordpress_app_password VARCHAR(255) NOT NULL,
                    html_configs JSONB,
                    image_configs JSONB,
                    status VARCHAR(50) DEFAULT 'active',
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_published_at TIMESTAMP
                )
            """)

            # Create publishing_history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS publishing_history (
                    id SERIAL PRIMARY KEY,
                    project_id VARCHAR(255) REFERENCES projects(project_id) ON DELETE SET NULL,
                    google_docs_url TEXT NOT NULL,
                    wordpress_post_id INTEGER,
                    wordpress_post_url TEXT,
                    post_title TEXT,
                    post_status VARCHAR(50),
                    images_processed INTEGER DEFAULT 0,
                    success BOOLEAN NOT NULL,
                    error_message TEXT,
                    execution_time_seconds FLOAT,
                    published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            print("[OK] Database tables initialized")

    except Exception as e:
        print(f"[ERROR] Failed to initialize database: {e}")
        raise


# ============================================
# Project CRUD Operations
# ============================================

def list_projects(status: str = "active") -> List[Dict[str, Any]]:
    """List all projects with optional status filter"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        if status == "all":
            cursor.execute("""
                SELECT * FROM projects
                ORDER BY created_at DESC
            """)
        else:
            cursor.execute("""
                SELECT * FROM projects
                WHERE status = %s
                ORDER BY created_at DESC
            """, (status,))

        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_project(project_id: str) -> Optional[Dict[str, Any]]:
    """Get a single project by ID"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM projects WHERE project_id = %s
        """, (project_id,))

        row = cursor.fetchone()
        return dict(row) if row else None


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
    """Create a new project"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO projects (
                project_id, project_name, wordpress_url,
                wordpress_username, wordpress_app_password,
                html_configs, image_configs, notes
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """, (
            project_id, project_name, wordpress_url,
            wordpress_username, wordpress_app_password,
            json.dumps(html_configs) if html_configs else None,
            json.dumps(image_configs) if image_configs else None,
            notes
        ))

        row = cursor.fetchone()
        return dict(row)


# Whitelist of allowed fields for update_project to prevent SQL injection
ALLOWED_UPDATE_FIELDS = {
    'project_name',
    'wordpress_url',
    'wordpress_username',
    'wordpress_app_password',
    'html_configs',
    'image_configs',
    'notes',
    'status'
}


def update_project(project_id: str, **updates) -> Optional[Dict[str, Any]]:
    """Update a project"""
    if not updates:
        return get_project(project_id)

    # Validate all fields against whitelist to prevent SQL injection
    invalid_fields = set(updates.keys()) - ALLOWED_UPDATE_FIELDS
    if invalid_fields:
        raise ValueError(f"Invalid fields: {', '.join(invalid_fields)}")

    # Build dynamic update query
    set_clauses = []
    values = []

    for key, value in updates.items():
        if key in ['html_configs', 'image_configs']:
            set_clauses.append(f"{key} = %s")
            values.append(json.dumps(value) if value else None)
        else:
            set_clauses.append(f"{key} = %s")
            values.append(value)

    # Add updated_at
    set_clauses.append("updated_at = CURRENT_TIMESTAMP")

    values.append(project_id)

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            UPDATE projects
            SET {', '.join(set_clauses)}
            WHERE project_id = %s
            RETURNING *
        """, values)

        row = cursor.fetchone()
        return dict(row) if row else None


def delete_project(project_id: str) -> bool:
    """Delete a project"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM projects WHERE project_id = %s
        """, (project_id,))

        return cursor.rowcount > 0


def update_last_published(project_id: str):
    """Update the last_published_at timestamp"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE projects
            SET last_published_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE project_id = %s
        """, (project_id,))


# ============================================
# Publishing History Operations
# ============================================

def log_publishing(
    project_id: Optional[str],
    google_docs_url: str,
    success: bool,
    wordpress_post_id: Optional[int] = None,
    wordpress_post_url: Optional[str] = None,
    post_title: Optional[str] = None,
    post_status: Optional[str] = None,
    images_processed: int = 0,
    error_message: Optional[str] = None,
    execution_time_seconds: Optional[float] = None
) -> Dict[str, Any]:
    """Log a publishing attempt"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO publishing_history (
                project_id, google_docs_url, wordpress_post_id,
                wordpress_post_url, post_title, post_status,
                images_processed, success, error_message, execution_time_seconds
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """, (
            project_id, google_docs_url, wordpress_post_id,
            wordpress_post_url, post_title, post_status,
            images_processed, success, error_message, execution_time_seconds
        ))

        row = cursor.fetchone()

        # Update project's last_published_at if project_id provided
        if project_id and success:
            update_last_published(project_id)

        return dict(row)


def get_publishing_history(
    project_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """Get publishing history with optional project filter"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        if project_id:
            cursor.execute("""
                SELECT h.*, p.project_name
                FROM publishing_history h
                LEFT JOIN projects p ON h.project_id = p.project_id
                WHERE h.project_id = %s
                ORDER BY h.published_at DESC
                LIMIT %s OFFSET %s
            """, (project_id, limit, offset))
        else:
            cursor.execute("""
                SELECT h.*, p.project_name
                FROM publishing_history h
                LEFT JOIN projects p ON h.project_id = p.project_id
                ORDER BY h.published_at DESC
                LIMIT %s OFFSET %s
            """, (limit, offset))

        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_failed_publishes(limit: int = 20) -> List[Dict[str, Any]]:
    """Get recent failed publishing attempts"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT h.*, p.project_name
            FROM publishing_history h
            LEFT JOIN projects p ON h.project_id = p.project_id
            WHERE h.success = FALSE
            ORDER BY h.published_at DESC
            LIMIT %s
        """, (limit,))

        rows = cursor.fetchall()
        return [dict(row) for row in rows]
