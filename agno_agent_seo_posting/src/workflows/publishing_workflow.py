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

# Add project root to path for consistent imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.database import get_project, log_publish
from src.config.settings import get_secret
from src.tools.google_docs_converter import google_docs_to_html
from src.tools.image_processor import process_images_from_html
from src.tools.html_transformer import transform_html
from src.tools.wordpress_uploader import (
    upload_images_batch,
    create_wordpress_post,
    replace_image_urls_in_html,
    extract_image_metadata_from_html,
    replace_images_with_wordpress_captions
)
from src.tools.google_drive_uploader import upload_images_to_google_drive
from src.utils.html_extractor import extract_title_from_html, clean_html_for_wordpress


def execute_publishing_workflow(
    google_docs_url: str,
    project_id: Optional[str] = None,
    main_keyword: Optional[str] = None
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
        main_keyword: Optional main keyword for image naming (if naming_method is "main_keyword")

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
            # Get WordPress credentials from secrets/environment
            wordpress_url = get_secret('WP_BASE_URL')
            username = get_secret('WP_USERNAME')
            app_password = get_secret('WP_APP_PASS')

            if not all([wordpress_url, username, app_password]):
                return {
                    "success": False,
                    "error": "WordPress credentials not configured. Set WP_BASE_URL, WP_USERNAME, WP_APP_PASS in .streamlit/secrets.toml or .env",
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

        # Extract original image metadata (alt, width, height) from cleaned HTML
        # This MUST happen BEFORE image processing, so we preserve Google Docs metadata
        print("   📊 Extracting original image metadata from HTML...")
        original_image_metadata = extract_image_metadata_from_html(cleaned_html)
        print(f"   ✓ Extracted metadata for {len(original_image_metadata)} image(s)")

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
            base_name=project_id or "image",
            main_keyword=main_keyword or ""
        )

        if not image_result['success']:
            print(f"   ⚠️  Image processing had issues")

        processed_images = image_result.get('processed_images', [])
        print(f"   ✓ Processed {len(processed_images)} image(s)")

        # STEP 3.5: Upload images to Google Drive (optional, non-blocking)
        google_drive_folder = image_configs.get('google_drive_folder_url', '')
        google_drive_result = None

        if google_drive_folder and processed_images:
            print("\n[3.5/7] 📁 Uploading images to Google Drive...")

            try:
                # Get resized image paths and filenames
                resized_paths = [img['resized_path'] for img in processed_images]
                image_filenames = [img['filename'] for img in processed_images]

                google_drive_result = upload_images_to_google_drive(
                    parent_folder_url=google_drive_folder,
                    post_title=post_title,
                    image_paths=resized_paths,
                    image_filenames=image_filenames
                )

                if google_drive_result['success']:
                    print(f"   ✓ Uploaded {google_drive_result['total_uploaded']} image(s) to Google Drive")
                    print(f"   🔗 Folder: {google_drive_result.get('folder_url', 'N/A')}")
                else:
                    print(f"   ⚠️  Google Drive upload had issues: {google_drive_result.get('error', 'Unknown error')}")
                    if google_drive_result.get('total_uploaded', 0) > 0:
                        print(f"   ✓ Partially uploaded: {google_drive_result['total_uploaded']} image(s)")

            except Exception as gdrive_error:
                # Google Drive failure should NOT block the workflow
                print(f"   ⚠️  Google Drive backup failed: {str(gdrive_error)}")
                print(f"   ℹ️  Continuing with WordPress upload...")
                google_drive_result = {
                    'success': False,
                    'error': str(gdrive_error)
                }

        elif google_drive_folder and not processed_images:
            print("\n[3.5/7] 📁 Google Drive backup skipped (no images)")
        # If google_drive_folder is not set, silently skip

        # STEP 4: Upload images to WordPress
        print("\n[4/7] ⬆️  Uploading images to WordPress...")
        url_mapping = {}
        enriched_metadata = []

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

            # Report upload status
            uploaded_count = len(upload_result['uploaded'])
            failed_count = len(upload_result['failed'])

            if upload_result['success']:
                print(f"   ✓ Uploaded {uploaded_count} image(s)")
            else:
                print(f"   ⚠️  Uploaded {uploaded_count} image(s), {failed_count} failed")
                for failure in upload_result['failed']:
                    print(f"   ✗ Failed: {failure['image_path']}")
                    print(f"     Error: {failure['error']}")

            # ALWAYS create URL mapping and enriched metadata for successful uploads
            # This ensures captions work even when some images fail
            if upload_result['uploaded']:
                # CRITICAL: Create URL mapping from ORIGINAL URLs (Google Docs) to WordPress URLs
                print("   🔗 Creating URL mapping from original URLs to WordPress URLs...")

                # First, create reverse mappings: resized_path -> original_url and resized_path -> dimensions
                resized_to_original_url = {}
                resized_to_dimensions = {}
                for processed_img in processed_images:
                    resized_path = processed_img['resized_path']
                    original_url = processed_img['original_url']
                    dimensions = processed_img.get('dimensions', (image_configs.get('target_width', 800), 800))
                    resized_to_original_url[resized_path] = original_url
                    resized_to_dimensions[resized_path] = dimensions

                # Process each uploaded image
                print("   🔗 Enriching image metadata with WordPress data...")
                for uploaded_img in upload_result['uploaded']:
                    resized_path = uploaded_img['image_path']
                    original_url = resized_to_original_url.get(resized_path, '')
                    dimensions = resized_to_dimensions.get(resized_path, (image_configs.get('target_width', 800), 800))

                    # Add to URL mapping
                    if original_url:
                        url_mapping[original_url] = uploaded_img['url']
                        print(f"      {original_url[:60]}... → {uploaded_img['url']}")

                    # Match metadata by original URL using PARTIAL matching
                    original_meta = {}
                    if original_url:
                        # First try exact match
                        original_meta = original_image_metadata.get(original_url, {})

                        # If exact match fails, try partial matching
                        if not original_meta:
                            for meta_url, meta_data in original_image_metadata.items():
                                if meta_url in original_url or original_url in meta_url:
                                    original_meta = meta_data
                                    print(f"      ✓ Partial URL match: {meta_url[:60]}...")
                                    break

                    if original_meta:
                        print(f"      ✓ Matched metadata for: {original_url[:80]}...")
                        print(f"         Alt text: '{original_meta.get('alt', '')[:80]}...'")
                    else:
                        print(f"      ⚠️  No metadata found for: {original_url[:80] if original_url else Path(resized_path).name}")

                    # Create enriched metadata with WordPress data, original metadata, and ACTUAL resized dimensions
                    enriched_metadata.append({
                        'media_id': uploaded_img['media_id'],
                        'url': uploaded_img['url'],
                        'alt': original_meta.get('alt', ''),
                        'width': dimensions[0],
                        'height': dimensions[1],
                        'original_filename': Path(resized_path).name
                    })

                print(f"   ✓ Enriched metadata for {len(enriched_metadata)} image(s)")
        else:
            print("   ℹ️  No images to upload")

        # STEP 5: Apply HTML transformations
        print("\n[5/7] 🔄 Applying HTML transformations...")

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

        # CRITICAL: Replace image URLs FIRST (before caption generation)
        # This is necessary because the HTML still has Google Docs URLs,
        # but the caption generator needs WordPress URLs to match images
        if url_mapping:
            print("   🔗 Replacing image URLs with WordPress media URLs...")
            transformed_html = replace_image_urls_in_html(transformed_html, url_mapping)
            print(f"   ✓ Replaced {len(url_mapping)} image URL(s)")

        # Now generate captions (if enabled) on the HTML with updated URLs
        enable_auto_captions = image_configs.get('enable_auto_captions', True)

        if enriched_metadata and enable_auto_captions:
            print("   🎨 Generating WordPress caption shortcodes for images...")
            final_html = replace_images_with_wordpress_captions(
                transformed_html,
                enriched_metadata,
                target_width=image_configs.get('target_width', 1200),
                max_caption_width=image_configs.get('max_caption_width')
            )
            print(f"   ✓ Generated {len(enriched_metadata)} caption shortcode(s)")
        else:
            if not enable_auto_captions:
                print("   ℹ️  Auto-captions disabled - images will use simple format")
            final_html = transformed_html

        # STEP 6: Create WordPress post
        print("\n[6/7] 📤 Creating WordPress post...")
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
        print(f"   ✓ Post created: {post_result['post_id']}")
        print(f"   ✓ Status: {post_result['status']}")

        execution_time = time.time() - start_time

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
        if google_drive_result and google_drive_result.get('folder_url'):
            print(f"📁 Google Drive: {google_drive_result['folder_url']}")
        print(f"⏱️  Time: {execution_time:.2f}s")
        print("\n" + "="*80 + "\n")

        result = {
            "success": True,
            "post_url": post_result['post_url'],
            "edit_url": post_result.get('edit_url'),
            "post_id": post_result['post_id'],
            "post_title": post_title,
            "post_status": post_result['status'],
            "images_processed": len(processed_images),
            "execution_time": execution_time
        }

        # Add Google Drive info if available
        if google_drive_result and google_drive_result.get('folder_url'):
            result['google_drive_folder_url'] = google_drive_result['folder_url']
            result['google_drive_folder_name'] = google_drive_result.get('folder_name', '')

        return result

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
    'main_keyword': Optional[str],
    'return': Dict[str, Any]
}
