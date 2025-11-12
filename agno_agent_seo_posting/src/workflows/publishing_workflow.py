"""
Publishing Workflow

End-to-end workflow for publishing Google Docs to WordPress.
Coordinates all steps: conversion, transformation, image processing, and publishing.
"""

import os
import sys
import time
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_project, log_publish
from tools.google_docs_converter import google_docs_to_html
from tools.image_processor import process_images_from_html
from tools.html_transformer import transform_html
from tools.wordpress_uploader import (
    upload_images_batch,
    create_wordpress_post,
    replace_image_urls_in_html
)
from utils.html_extractor import extract_title_from_html, clean_html_for_wordpress


def execute_publishing_workflow(
    google_docs_url: str,
    project_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Execute the complete publishing workflow.

    Steps:
    1. Convert Google Docs to HTML
    2. Extract title and images
    3. Process and upload images to WordPress
    4. Apply HTML transformations (if project selected)
    5. Create WordPress post
    6. Log to history

    Args:
        google_docs_url: Published Google Docs URL
        project_id: Project ID (None = "no-project" mode, skip transformations)

    Returns:
        Dict with workflow results:
        - success: bool
        - post_url: str (WordPress post URL)
        - post_id: int
        - post_title: str
        - images_processed: int
        - execution_time: float
        - error: str (if failed)
        - step_failed: str (which step failed)
    """
    start_time = time.time()
    project = None
    html_configs = None
    image_configs = None
    wordpress_url = None
    username = None
    app_password = None

    print("\n" + "="*80)
    print("🚀 STARTING PUBLISHING WORKFLOW")
    print("="*80)

    try:
        # Load project configuration if provided
        if project_id:
            print(f"\n📁 Loading project: {project_id}")
            try:
                project = get_project(project_id)
                html_configs = project['html_configs']
                image_configs = project['image_configs']
                wordpress_url = project['wordpress_url']
                username = project['wordpress_username']
                app_password = project['wordpress_app_password']
                print(f"   ✓ Project loaded: {project['project_name']}")
            except ValueError as e:
                return {
                    "success": False,
                    "error": f"Project not found: {str(e)}",
                    "step_failed": "project_loading"
                }
        else:
            print("\n📁 No project selected - using defaults")
            # Get WordPress credentials from environment
            wordpress_url = os.getenv('WP_BASE_URL')
            username = os.getenv('WP_USERNAME')
            app_password = os.getenv('WP_APP_PASS')

            if not all([wordpress_url, username, app_password]):
                return {
                    "success": False,
                    "error": "WordPress credentials not configured. Set WP_BASE_URL, WP_USERNAME, WP_APP_PASS in .env",
                    "step_failed": "configuration"
                }

        # STEP 1: Convert Google Docs to HTML
        print("\n[1/6] 📄 Converting Google Docs to HTML...")
        docs_result = google_docs_to_html(google_docs_url)

        if not docs_result['success']:
            return {
                "success": False,
                "error": f"Failed to convert Google Docs: {docs_result.get('error')}",
                "step_failed": "docs_conversion"
            }

        raw_html = docs_result['raw_html']
        document_name = docs_result.get('document_name', 'Untitled')
        print(f"   ✓ Converted ({len(raw_html)} characters)")
        print(f"   ✓ Document: {document_name}")

        # STEP 2: Extract title and clean HTML
        print("\n[2/6] 📝 Extracting post title and cleaning HTML...")
        post_title = extract_title_from_html(raw_html)
        if not post_title:
            post_title = document_name
        print(f"   ✓ Title: {post_title}")

        # Apply universal cleaning: remove everything before and including H1
        # This applies to ALL clients - the H1 is used as the post title
        cleaned_html = clean_html_for_wordpress(raw_html)
        print(f"   ✓ Removed H1 and content before it")
        print(f"   ✓ Cleaned HTML: {len(cleaned_html)} characters (was {len(raw_html)})")

        # STEP 3: Process images
        print("\n[3/6] 🖼️  Processing images...")

        # Use project image config or defaults
        if not image_configs:
            image_configs = {
                "target_width": 800,
                "image_quality": 92,
                "image_format": "JPEG"
            }

        # Process images (download and resize) from cleaned HTML
        image_result = process_images_from_html(
            cleaned_html,
            image_config=image_configs,
            base_name=project_id or "image"
        )

        if not image_result['success']:
            print(f"   ⚠️  Image processing had issues")

        processed_images = image_result.get('processed_images', [])
        print(f"   ✓ Processed {len(processed_images)} image(s)")

        # STEP 4: Upload images to WordPress
        print("\n[4/6] ⬆️  Uploading images to WordPress...")
        url_mapping = {}

        if processed_images:
            resized_paths = [img['resized_path'] for img in processed_images]
            print(f"   Found {len(resized_paths)} resized image(s) to upload")
            print(f"   WordPress URL: {wordpress_url}")
            print(f"   Uploading to: {wordpress_url}/wp-json/wp/v2/media")

            upload_result = upload_images_batch(
                resized_paths,
                wordpress_url,
                username,
                app_password
            )

            if upload_result['success']:
                print(f"   ✓ Uploaded {len(upload_result['uploaded'])} image(s)")
                url_mapping = upload_result['url_mapping']
            else:
                print(f"   ⚠️  Some images failed to upload: {len(upload_result['failed'])}")
                # Continue anyway with successful uploads
                url_mapping = upload_result['url_mapping']

                # Print failed uploads for debugging
                for failure in upload_result['failed']:
                    print(f"   ✗ Failed: {failure['image_path']}")
                    print(f"     Error: {failure['error']}")
        else:
            print("   ℹ️  No images to upload")

        # STEP 5: Apply HTML transformations
        print("\n[5/6] 🔄 Applying HTML transformations...")

        if html_configs and html_configs.get('patterns'):
            transform_result = transform_html(cleaned_html, html_configs)
            if transform_result['success']:
                transformed_html = transform_result['transformed_html']
                patterns_applied = transform_result.get('patterns_applied', 0)
                print(f"   ✓ Applied {patterns_applied} transformation pattern(s)")
            else:
                print(f"   ⚠️  Transformation failed, using cleaned HTML")
                transformed_html = cleaned_html
        else:
            print("   ℹ️  No transformations configured - using cleaned HTML")
            transformed_html = cleaned_html

        # Replace image URLs with WordPress URLs
        if url_mapping:
            print("   🔗 Replacing image URLs with WordPress media URLs...")
            final_html = replace_image_urls_in_html(transformed_html, url_mapping)
            print(f"   ✓ Replaced {len(url_mapping)} image URL(s)")
        else:
            final_html = transformed_html

        # STEP 6: Create WordPress post
        print("\n[6/6] 📤 Creating WordPress post...")
        post_result = create_wordpress_post(
            title=post_title,
            content=final_html,
            wordpress_url=wordpress_url,
            username=username,
            app_password=app_password,
            status="draft"  # Always create as draft for safety
        )

        if not post_result['success']:
            # Log failure
            execution_time = time.time() - start_time
            log_publish(
                google_docs_url=google_docs_url,
                success=False,
                project_id=project_id,
                post_title=post_title,
                images_processed=len(processed_images),
                error_message=post_result.get('error'),
                execution_time_seconds=execution_time
            )

            return {
                "success": False,
                "error": f"Failed to create WordPress post: {post_result.get('error')}",
                "step_failed": "wordpress_publish"
            }

        # Success!
        execution_time = time.time() - start_time

        print(f"   ✓ Post created: {post_result['post_id']}")
        print(f"   ✓ Status: {post_result['status']}")

        # Log success
        log_publish(
            google_docs_url=google_docs_url,
            success=True,
            project_id=project_id,
            wordpress_post_id=post_result['post_id'],
            wordpress_post_url=post_result['post_url'],
            post_title=post_title,
            post_status=post_result['status'],
            images_processed=len(processed_images),
            execution_time_seconds=execution_time
        )

        print("\n" + "="*80)
        print("✅ WORKFLOW COMPLETED SUCCESSFULLY")
        print("="*80)
        print(f"\n📌 Post Title: {post_title}")
        print(f"🔗 Post URL: {post_result['post_url']}")
        print(f"🖼️  Images: {len(processed_images)} processed")
        print(f"⏱️  Time: {execution_time:.2f}s")
        print("\n" + "="*80 + "\n")

        return {
            "success": True,
            "post_url": post_result['post_url'],
            "edit_url": post_result.get('edit_url'),
            "post_id": post_result['post_id'],
            "post_title": post_title,
            "post_status": post_result['status'],
            "images_processed": len(processed_images),
            "execution_time": execution_time
        }

    except Exception as e:
        execution_time = time.time() - start_time

        # Log failure
        log_publish(
            google_docs_url=google_docs_url,
            success=False,
            project_id=project_id,
            error_message=str(e),
            execution_time_seconds=execution_time
        )

        print("\n" + "="*80)
        print("❌ WORKFLOW FAILED")
        print("="*80)
        print(f"\nError: {str(e)}")
        print("\n" + "="*80 + "\n")

        return {
            "success": False,
            "error": str(e),
            "step_failed": "unexpected_error",
            "execution_time": execution_time
        }


# Make available as Agno tool
execute_publishing_workflow.__annotations__ = {
    'google_docs_url': str,
    'project_id': Optional[str],
    'return': Dict[str, Any]
}
