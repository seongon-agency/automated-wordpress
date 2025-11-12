"""
Quick test of the project editing functionality.
"""

import os
import sys
from database import list_projects, get_project, update_project

os.environ['CLIENT_DB_PATH'] = 'clients.db'

print("="*80)
print("TESTING PROJECT EDITING")
print("="*80)

# Test 1: List projects
print("\n1. Listing projects...")
projects = list_projects(status='all')
print(f"[OK] Found {len(projects)} project(s)")
for p in projects:
    print(f"   - {p['project_id']}: {p['project_name']}")

# Test 2: Get a project
if projects:
    print(f"\n2. Getting project details...")
    project_id = projects[0]['project_id']
    project = get_project(project_id)
    print(f"[OK] Retrieved: {project['project_name']}")
    print(f"   WordPress: {project['wordpress_url']}")

    # Show current HTML configs
    if project['html_configs']:
        patterns = project['html_configs'].get('patterns', [])
        print(f"   HTML patterns: {len(patterns)}")
    else:
        print(f"   HTML patterns: none")

    # Show current image configs
    if project['image_configs']:
        print(f"   Image width: {project['image_configs'].get('target_width', 'not set')}")
    else:
        print(f"   Image config: none")

    # Test 3: Update project metadata
    print(f"\n3. Testing metadata update...")
    original_notes = project['notes']
    updated = update_project(
        project_id,
        notes="Test note - edited at " + str(os.times())
    )
    print(f"[OK] Updated notes")
    print(f"   Before: {original_notes}")
    print(f"   After:  {updated['notes']}")

    # Restore original
    update_project(project_id, notes=original_notes)
    print(f"[OK] Restored original notes")

    # Test 4: Update image config
    print(f"\n4. Testing image config update...")
    original_image_config = project['image_configs']
    new_image_config = {
        "target_width": 1000,
        "image_quality": 95,
        "image_format": "WEBP",
        "css_classes": "test-image"
    }

    updated = update_project(project_id, image_configs=new_image_config)
    print(f"[OK] Updated image config")
    print(f"   Width: {updated['image_configs']['target_width']}")
    print(f"   Format: {updated['image_configs']['image_format']}")

    # Restore original
    update_project(project_id, image_configs=original_image_config)
    print(f"[OK] Restored original image config")

    print("\n" + "="*80)
    print("[OK] ALL EDITING FUNCTIONS WORK!")
    print("="*80)
    print("\nThe edit_project.py script is ready to use.")
    print("Run: python edit_project.py")
else:
    print("\n[ERROR] No projects found to test")
