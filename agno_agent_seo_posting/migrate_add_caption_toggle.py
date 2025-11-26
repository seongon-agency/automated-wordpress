"""
Migration script: Add enable_auto_captions to existing projects.

This script updates all existing projects to include the enable_auto_captions
setting in their image_configs, defaulting to true to preserve current behavior.
"""

import sys
sys.path.insert(0, 'src')

from database import list_projects, update_project
import json

print("="*80)
print("MIGRATION: Add enable_auto_captions to Projects")
print("="*80)

# Get all projects
projects = list_projects()

print(f"\nFound {len(projects)} project(s)\n")

updated_count = 0
skipped_count = 0

for project in projects:
    project_id = project['project_id']
    project_name = project['project_name']

    print(f"Processing: {project_name} ({project_id})")

    # Get current image_configs
    current_image_configs = project.get('image_configs') or {}

    # Check if enable_auto_captions already exists
    if 'enable_auto_captions' in current_image_configs:
        print(f"  ⏭️  Skipped - enable_auto_captions already exists (value: {current_image_configs['enable_auto_captions']})")
        skipped_count += 1
        continue

    # Add enable_auto_captions with default value true
    updated_image_configs = {**current_image_configs}
    updated_image_configs['enable_auto_captions'] = True

    # Update project
    try:
        update_project(project_id, image_configs=updated_image_configs)
        print(f"  ✓ Added enable_auto_captions: true (default)")
        updated_count += 1
    except Exception as e:
        print(f"  ✗ Error: {e}")

print("\n" + "="*80)
print("MIGRATION SUMMARY")
print("="*80)
print(f"Total projects: {len(projects)}")
print(f"Updated: {updated_count}")
print(f"Skipped: {skipped_count}")
print("\n✓ Migration complete!\n")

print("NOTE: All projects now have 'enable_auto_captions' set to true by default.")
print("You can change this per-project in the Streamlit UI or by calling update_project().\n")
