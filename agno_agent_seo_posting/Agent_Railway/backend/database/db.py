"""
Database Connection - PostgreSQL via psycopg2

Provides connection pooling and query execution for Railway PostgreSQL.
"""

import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from contextlib import contextmanager
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import pool
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Connection pool (will be initialized on first use)
_connection_pool = None


def get_database_url() -> str:
    """Get DATABASE_URL from environment."""
    url = os.getenv("DATABASE_URL")
    if not url:
        raise ValueError(
            "DATABASE_URL not found. "
            "Please set DATABASE_URL in .env file."
        )
    return url


def init_pool():
    """Initialize the connection pool."""
    global _connection_pool
    if _connection_pool is None:
        database_url = get_database_url()
        _connection_pool = pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=10,
            dsn=database_url
        )
    return _connection_pool


@contextmanager
def get_connection():
    """Get a connection from the pool."""
    pool = init_pool()
    conn = pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        pool.putconn(conn)


@contextmanager
def get_cursor():
    """Get a cursor with dict results."""
    with get_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            yield cursor
        finally:
            cursor.close()


def init_database() -> bool:
    """
    Initialize database - create tables if they don't exist.

    Returns:
        True if successful
    """
    try:
        with get_cursor() as cursor:
            # Create projects table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    project_id TEXT PRIMARY KEY,
                    project_name TEXT NOT NULL,
                    wordpress_url TEXT NOT NULL,
                    wordpress_username TEXT NOT NULL,
                    wordpress_app_password TEXT NOT NULL,
                    html_configs JSONB,
                    image_configs JSONB,
                    status TEXT DEFAULT 'active',
                    notes TEXT,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW(),
                    last_published_at TIMESTAMPTZ
                );

                CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
            """)

            # Create publishing_history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS publishing_history (
                    publish_id SERIAL PRIMARY KEY,
                    project_id TEXT REFERENCES projects(project_id) ON DELETE SET NULL,
                    google_docs_url TEXT NOT NULL,
                    wordpress_post_id INTEGER,
                    wordpress_post_url TEXT,
                    post_title TEXT,
                    post_status TEXT,
                    images_processed INTEGER DEFAULT 0,
                    success BOOLEAN,
                    error_message TEXT,
                    execution_time_seconds REAL,
                    published_at TIMESTAMPTZ DEFAULT NOW()
                );

                CREATE INDEX IF NOT EXISTS idx_publishing_history_project_id
                    ON publishing_history(project_id);
                CREATE INDEX IF NOT EXISTS idx_publishing_history_published_at
                    ON publishing_history(published_at DESC);
            """)

        print("[OK] Database tables initialized")
        return True

    except Exception as e:
        print(f"[ERROR] Failed to initialize database: {e}")
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
    """Create a new project."""
    import json

    with get_cursor() as cursor:
        try:
            cursor.execute("""
                INSERT INTO projects (
                    project_id, project_name, wordpress_url,
                    wordpress_username, wordpress_app_password,
                    html_configs, image_configs, notes,
                    status, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'active', NOW(), NOW())
                RETURNING *
            """, (
                project_id, project_name, wordpress_url,
                wordpress_username, wordpress_app_password,
                json.dumps(html_configs) if html_configs else None,
                json.dumps(image_configs) if image_configs else None,
                notes
            ))

            result = cursor.fetchone()
            return dict(result) if result else None

        except psycopg2.IntegrityError:
            raise ValueError(f"Project with ID '{project_id}' already exists")


def get_project(project_id: str) -> Dict[str, Any]:
    """Get project by ID."""
    with get_cursor() as cursor:
        cursor.execute(
            "SELECT * FROM projects WHERE project_id = %s",
            (project_id,)
        )
        result = cursor.fetchone()

        if not result:
            raise ValueError(f"Project '{project_id}' not found")

        return dict(result)


def update_project(project_id: str, **kwargs) -> Dict[str, Any]:
    """Update project fields."""
    import json

    # Verify project exists
    get_project(project_id)

    allowed_fields = {
        'project_name', 'wordpress_url', 'wordpress_username',
        'wordpress_app_password', 'html_configs', 'image_configs',
        'status', 'notes'
    }

    updates = {}
    for key, value in kwargs.items():
        if key in allowed_fields:
            # Convert dicts to JSON for JSONB fields
            if key in ('html_configs', 'image_configs') and isinstance(value, dict):
                updates[key] = json.dumps(value)
            else:
                updates[key] = value

    if not updates:
        return get_project(project_id)

    # Build UPDATE query dynamically
    set_clause = ", ".join(f"{key} = %s" for key in updates.keys())
    set_clause += ", updated_at = NOW()"

    with get_cursor() as cursor:
        cursor.execute(
            f"UPDATE projects SET {set_clause} WHERE project_id = %s RETURNING *",
            (*updates.values(), project_id)
        )
        result = cursor.fetchone()
        return dict(result) if result else get_project(project_id)


def delete_project(project_id: str) -> bool:
    """Delete project by ID."""
    with get_cursor() as cursor:
        cursor.execute(
            "DELETE FROM projects WHERE project_id = %s RETURNING project_id",
            (project_id,)
        )
        result = cursor.fetchone()
        return result is not None


def list_projects(status: str = 'active') -> List[Dict[str, Any]]:
    """List all projects with given status."""
    with get_cursor() as cursor:
        if status == 'all':
            cursor.execute(
                "SELECT * FROM projects ORDER BY project_name"
            )
        else:
            cursor.execute(
                "SELECT * FROM projects WHERE status = %s ORDER BY project_name",
                (status,)
            )

        results = cursor.fetchall()
        return [dict(row) for row in results] if results else []


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
    """Log a publishing attempt to history."""
    with get_cursor() as cursor:
        cursor.execute("""
            INSERT INTO publishing_history (
                project_id, google_docs_url, wordpress_post_id,
                wordpress_post_url, post_title, post_status,
                images_processed, success, error_message,
                execution_time_seconds, published_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            RETURNING publish_id
        """, (
            project_id, google_docs_url, wordpress_post_id,
            wordpress_post_url, post_title, post_status,
            images_processed, success, error_message,
            execution_time_seconds
        ))

        result = cursor.fetchone()

        # Update last_published_at for project if successful
        if success and project_id:
            cursor.execute("""
                UPDATE projects
                SET last_published_at = NOW()
                WHERE project_id = %s
            """, (project_id,))

        return result['publish_id'] if result else 0


def get_publish_history(
    project_id: Optional[str] = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """Get publishing history."""
    with get_cursor() as cursor:
        if project_id:
            cursor.execute("""
                SELECT * FROM publishing_history
                WHERE project_id = %s
                ORDER BY published_at DESC
                LIMIT %s
            """, (project_id, limit))
        else:
            cursor.execute("""
                SELECT * FROM publishing_history
                ORDER BY published_at DESC
                LIMIT %s
            """, (limit,))

        results = cursor.fetchall()
        return [dict(row) for row in results] if results else []
