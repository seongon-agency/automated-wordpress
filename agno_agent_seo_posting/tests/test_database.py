"""
Test script for database operations.
"""

import os
import sys
from database import (
    init_database,
    create_project,
    get_project,
    update_project,
    list_projects,
    log_publish,
    get_publish_history,
)

# Use a test database
os.environ['CLIENT_DB_PATH'] = 'test_clients.db'


def test_database():
    """Test all database operations."""
    print("="*80)
    print("TESTING DATABASE OPERATIONS")
    print("="*80)

    # Clean up test database if it exists
    test_db_path = 'test_clients.db'
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
        print(f"[OK] Cleaned up old test database\n")

    # Initialize database
    print("1. Initializing database...")
    init_database()

    # Create a test project
    print("\n2. Creating test project...")
    html_configs = {
        "patterns": [
            {
                "element_type": "p",
                "source_pattern": "<p[^>]*>(.*?)</p>",
                "target_pattern": "<p class=\"test-paragraph\">\\1</p>"
            },
            {
                "element_type": "strong",
                "source_pattern": "<b>(.*?)</b>",
                "target_pattern": "<strong>\\1</strong>"
            }
        ]
    }

    image_configs = {
        "target_width": 800,
        "image_quality": 92,
        "image_format": "JPEG",
        "css_classes": "wp-image aligncenter"
    }

    project = create_project(
        project_id="test_project",
        project_name="Test Project",
        wordpress_url="https://test.wordpress.com",
        wordpress_username="admin",
        wordpress_app_password="test pass word 1234",
        html_configs=html_configs,
        image_configs=image_configs,
        notes="This is a test project"
    )

    print(f"[OK] Created project: {project['project_id']}")
    print(f"   HTML patterns: {len(project['html_configs']['patterns'])} patterns")
    print(f"   Image config: {project['image_configs']['target_width']}px width")

    # Get project
    print("\n3. Getting project...")
    retrieved = get_project("test_project")
    print(f"[OK] Retrieved project: {retrieved['project_name']}")

    # List projects
    print("\n4. Listing all projects...")
    projects = list_projects(status='all')
    print(f"[OK] Found {len(projects)} project(s)")
    for p in projects:
        print(f"   - {p['project_id']}: {p['project_name']}")

    # Update project
    print("\n5. Updating project...")
    updated = update_project(
        "test_project",
        wordpress_url="https://updated.wordpress.com"
    )
    print(f"[OK] Updated WordPress URL: {updated['wordpress_url']}")

    # Log a successful publish
    print("\n6. Logging successful publish...")
    publish_id = log_publish(
        google_docs_url="https://docs.google.com/document/d/test/pub",
        success=True,
        project_id="test_project",
        wordpress_post_id=123,
        wordpress_post_url="https://test.wordpress.com/post-123",
        post_title="Test Post",
        post_status="draft",
        images_processed=3,
        execution_time_seconds=15.5
    )
    print(f"[OK] Logged publish with ID: {publish_id}")

    # Get publish history
    print("\n7. Getting publish history...")
    history = get_publish_history(project_id="test_project", limit=5)
    print(f"[OK] Found {len(history)} publish record(s)")
    for record in history:
        status_icon = "[OK]" if record['success'] else "[X]"
        print(f"   {status_icon} {record['post_title']} - {record['published_at']}")

    print("\n" + "="*80)
    print("[OK] ALL TESTS PASSED!")
    print("="*80)


if __name__ == "__main__":
    try:
        test_database()
    except Exception as e:
        print(f"\n[ERROR] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
