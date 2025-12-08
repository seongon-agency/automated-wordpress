"""
Publishing Workflow

End-to-end workflow for publishing Google Docs to WordPress.
Coordinates all steps: conversion, transformation, image processing, and publishing.
"""

import os
import time
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from database import get_project, log_publish
from .google_docs import google_docs_to_html
from .image_processor import process_images_from_html
from .html_transformer import transform_html
from .wordpress import (
    upload_images_batch,
    create_wordpress_post,
    replace_image_urls_in_html,
    extract_image_metadata_from_html,
    replace_images_with_wordpress_captions
)
from utils.html_extractor import extract_title_from_html, clean_html_for_wordpress


def get_secret(key: str, default=None):
    """Get secret from environment."""
    return os.getenv(key, default)


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
        project_id: Project ID (None = use default WordPress credentials)
        main_keyword: Optional main keyword for image naming

    Returns:
        Dict with workflow results
    """
    start_time = time.time()
    project = None
    html_configs = None
    image_configs = None
    wordpress_url = None
    username = None
    app_password = None

    print("\n" + "="*80)
    print("STARTING PUBLISHING WORKFLOW")
    print("="*80)

    try:
        # Load project configuration if provided
        if project_id:
            print(f"\nLoading project: {project_id}")
            try:
                project = get_project(project_id)
                html_configs = project.get('html_configs')
                image_configs = project.get('image_configs')
                wordpress_url = project['wordpress_url']
                username = project['wordpress_username']
                app_password = project['wordpress_app_password']
                print(f"   Project loaded: {project['project_name']}")
            except ValueError as e:
                return {
                    "success": False,
                    "error": f"Project not found: {str(e)}",
                    "step_failed": "project_loading"
                }
        else:
            print("\nNo project selected - using defaults")
            wordpress_url = get_secret('WP_BASE_URL')
            username = get_secret('WP_USERNAME')
            app_password = get_secret('WP_APP_PASS')

            if not all([wordpress_url, username, app_password]):
                return {
                    "success": False,
                    "error": "WordPress credentials not configured. Set WP_BASE_URL, WP_USERNAME, WP_APP_PASS in environment",
                    "step_failed": "configuration"
                }

        # STEP 1: Convert Google Docs to HTML
        print("\n[1/6] Converting Google Docs to HTML...")
        docs_result = google_docs_to_html(google_docs_url)

        if not docs_result['success']:
            return {
                "success": False,
                "error": f"Failed to convert Google Docs: {docs_result.get('error')}",
                "step_failed": "docs_conversion"
            }

        raw_html = docs_result['raw_html']
        document_name = docs_result.get('document_name', 'Untitled')
        print(f"   Converted ({len(raw_html)} characters)")
        print(f"   Document: {document_name}")

        # STEP 2: Extract title and clean HTML
        print("\n[2/6] Extracting post title and cleaning HTML...")
        post_title = extract_title_from_html(raw_html)
        if not post_title:
            post_title = document_name
        print(f"   Title: {post_title}")

        cleaned_html = clean_html_for_wordpress(raw_html)
        print(f"   Cleaned HTML: {len(cleaned_html)} characters")

        # STEP 3: Process images
        print("\n[3/6] Processing images...")

        original_image_metadata = extract_image_metadata_from_html(cleaned_html)
        print(f"   Extracted metadata for {len(original_image_metadata)} image(s)")

        if not image_configs:
            image_configs = {
                "target_width": 800,
                "image_quality": 92,
                "image_format": "JPEG"
            }

        image_result = process_images_from_html(
            cleaned_html,
            image_config=image_configs,
            base_name=project_id or "image",
            main_keyword=main_keyword or ""
        )

        processed_images = image_result.get('processed_images', [])
        print(f"   Processed {len(processed_images)} image(s)")

        # STEP 4: Upload images to WordPress
        print("\n[4/6] Uploading images to WordPress...")
        url_mapping = {}
        enriched_metadata = []

        if processed_images:
            resized_paths = [img['resized_path'] for img in processed_images]
            print(f"   Found {len(resized_paths)} resized image(s) to upload")

            upload_result = upload_images_batch(
                resized_paths,
                wordpress_url,
                username,
                app_password
            )

            uploaded_count = len(upload_result['uploaded'])
            failed_count = len(upload_result['failed'])

            if upload_result['success']:
                print(f"   Uploaded {uploaded_count} image(s)")
            else:
                print(f"   Uploaded {uploaded_count} image(s), {failed_count} failed")

            if upload_result['uploaded']:
                resized_to_original_url = {}
                resized_to_dimensions = {}
                for processed_img in processed_images:
                    resized_path = processed_img['resized_path']
                    original_url = processed_img['original_url']
                    dimensions = processed_img.get('dimensions', (image_configs.get('target_width', 800), 800))
                    resized_to_original_url[resized_path] = original_url
                    resized_to_dimensions[resized_path] = dimensions

                for uploaded_img in upload_result['uploaded']:
                    resized_path = uploaded_img['image_path']
                    original_url = resized_to_original_url.get(resized_path, '')
                    dimensions = resized_to_dimensions.get(resized_path, (800, 800))

                    if original_url:
                        url_mapping[original_url] = uploaded_img['url']

                    original_meta = original_image_metadata.get(original_url, {})
                    if not original_meta:
                        for meta_url, meta_data in original_image_metadata.items():
                            if meta_url in original_url or original_url in meta_url:
                                original_meta = meta_data
                                break

                    enriched_metadata.append({
                        'media_id': uploaded_img['media_id'],
                        'url': uploaded_img['url'],
                        'alt': original_meta.get('alt', ''),
                        'width': dimensions[0],
                        'height': dimensions[1],
                        'original_filename': Path(resized_path).name
                    })

                print(f"   Enriched metadata for {len(enriched_metadata)} image(s)")
        else:
            print("   No images to upload")

        # STEP 5: Apply HTML transformations
        print("\n[5/6] Applying HTML transformations...")

        if html_configs and html_configs.get('patterns'):
            transform_result = transform_html(cleaned_html, html_configs)
            if transform_result['success']:
                transformed_html = transform_result['transformed_html']
                patterns_applied = transform_result.get('patterns_applied', 0)
                print(f"   Applied {patterns_applied} transformation pattern(s)")
            else:
                print(f"   Transformation failed, using cleaned HTML")
                transformed_html = cleaned_html
        else:
            print("   No transformations configured - using cleaned HTML")
            transformed_html = cleaned_html

        if url_mapping:
            print("   Replacing image URLs with WordPress media URLs...")
            transformed_html = replace_image_urls_in_html(transformed_html, url_mapping)
            print(f"   Replaced {len(url_mapping)} image URL(s)")

        enable_auto_captions = image_configs.get('enable_auto_captions', True)

        if enriched_metadata and enable_auto_captions:
            print("   Generating WordPress caption shortcodes...")
            final_html = replace_images_with_wordpress_captions(
                transformed_html,
                enriched_metadata,
                target_width=image_configs.get('target_width', 1200),
                max_caption_width=image_configs.get('max_caption_width')
            )
            print(f"   Generated {len(enriched_metadata)} caption shortcode(s)")
        else:
            final_html = transformed_html

        # STEP 6: Create WordPress post
        print("\n[6/6] Creating WordPress post...")
        post_result = create_wordpress_post(
            title=post_title,
            content=final_html,
            wordpress_url=wordpress_url,
            username=username,
            app_password=app_password,
            status="draft"
        )

        if not post_result['success']:
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

        print(f"   Post created: {post_result['post_id']}")
        print(f"   Status: {post_result['status']}")

        execution_time = time.time() - start_time

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
        print("WORKFLOW COMPLETED SUCCESSFULLY")
        print("="*80)
        print(f"\nPost Title: {post_title}")
        print(f"Post URL: {post_result['post_url']}")
        print(f"Images: {len(processed_images)} processed")
        print(f"Time: {execution_time:.2f}s")
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

        log_publish(
            google_docs_url=google_docs_url,
            success=False,
            project_id=project_id,
            error_message=str(e),
            execution_time_seconds=execution_time
        )

        print("\n" + "="*80)
        print("WORKFLOW FAILED")
        print("="*80)
        print(f"\nError: {str(e)}")
        print("\n" + "="*80 + "\n")

        return {
            "success": False,
            "error": str(e),
            "step_failed": "unexpected_error",
            "execution_time": execution_time
        }
