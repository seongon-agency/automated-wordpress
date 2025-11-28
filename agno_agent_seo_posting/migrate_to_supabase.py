"""
Migration script to transfer data from SQLite to Supabase
Run this once to migrate existing projects.
"""

import json
import sqlite3
from pathlib import Path
from supabase import create_client

# Get secrets
def get_secret(key, default=None):
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass

    import os
    return os.getenv(key, default)

# Supabase credentials
SUPABASE_URL = get_secret("SUPABASE_URL")
SUPABASE_KEY = get_secret("SUPABASE_KEY")

# SQLite database path
SQLITE_DB = Path(__file__).parent / "data" / "clients.db"

def migrate_projects():
    """Migrate projects from SQLite to Supabase."""

    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Error: Supabase credentials not found!")
        print("Make sure SUPABASE_URL and SUPABASE_KEY are set in .streamlit/secrets.toml")
        return

    # Connect to SQLite
    print(f"Connecting to SQLite: {SQLITE_DB}")
    conn = sqlite3.connect(SQLITE_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Connect to Supabase
    print(f"Connecting to Supabase: {SUPABASE_URL}")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Fetch all projects from SQLite
    cursor.execute("SELECT * FROM projects")
    projects = cursor.fetchall()

    print(f"\nFound {len(projects)} projects to migrate:")

    for project in projects:
        project_dict = dict(project)
        project_id = project_dict['project_id']

        # Parse JSON fields
        html_configs = json.loads(project_dict['html_configs']) if project_dict['html_configs'] else None
        image_configs = json.loads(project_dict['image_configs']) if project_dict['image_configs'] else None

        # Prepare data for Supabase
        data = {
            "project_id": project_id,
            "project_name": project_dict['project_name'],
            "wordpress_url": project_dict['wordpress_url'],
            "wordpress_username": project_dict['wordpress_username'],
            "wordpress_app_password": project_dict['wordpress_app_password'],
            "html_configs": html_configs,
            "image_configs": image_configs,
            "status": project_dict['status'] or 'active',
            "created_at": project_dict['created_at'],
            "updated_at": project_dict['updated_at'],
            "last_published_at": project_dict['last_published_at'],
            "notes": project_dict['notes']
        }

        try:
            # Check if project already exists
            existing = supabase.table("projects").select("project_id").eq("project_id", project_id).execute()

            if existing.data:
                print(f"  - {project_id}: Already exists, skipping")
            else:
                # Insert into Supabase
                result = supabase.table("projects").insert(data).execute()
                print(f"  - {project_id}: Migrated successfully")
        except Exception as e:
            print(f"  - {project_id}: Error - {str(e)[:100]}")

    # Migrate publishing history (optional)
    cursor.execute("SELECT * FROM publishing_history ORDER BY published_at DESC LIMIT 100")
    history = cursor.fetchall()

    if history:
        print(f"\nMigrating {len(history)} publishing history records...")

        for record in history:
            record_dict = dict(record)

            data = {
                "project_id": record_dict['project_id'],
                "google_docs_url": record_dict['google_docs_url'],
                "wordpress_post_id": record_dict['wordpress_post_id'],
                "wordpress_post_url": record_dict['wordpress_post_url'],
                "post_title": record_dict['post_title'],
                "post_status": record_dict['post_status'],
                "images_processed": record_dict['images_processed'] or 0,
                "success": record_dict['success'],
                "error_message": record_dict['error_message'],
                "execution_time_seconds": record_dict['execution_time_seconds'],
                "published_at": record_dict['published_at']
            }

            try:
                supabase.table("publishing_history").insert(data).execute()
            except Exception as e:
                print(f"  History record error: {str(e)[:50]}")

        print("  Publishing history migrated.")

    conn.close()
    print("\nMigration complete!")

if __name__ == "__main__":
    migrate_projects()
