"""
Publishing Workflow Service

End-to-end workflow for publishing Google Docs to WordPress.
"""

import time
from typing import Dict, Any, Optional

from .google_docs import google_docs_to_html
from .image_processor import process_images_from_html
from .wordpress import upload_images_batch, create_wordpress_post, replace_image_urls_in_html
from .html_transformer import transform_html, extract_title_from_html, remove_title_from_html


async def execute_publishing_workflow(
    google_docs_url: str,
    wordpress_url: str,
    wordpress_username: str,
    wordpress_app_password: str,
    html_configs: Optional[Dict[str, Any]] = None,
    image_configs: Optional[Dict[str, Any]] = None,
    main_keyword: Optional[str] = None,
    project_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Execute the complete publishing workflow.

    Steps:
    1. Convert Google Docs to HTML
    2. Extract title and clean HTML
    3. Process images (download & resize)
    4. Upload images to WordPress
    5. Apply HTML transformations
    6. Create WordPress post

    Args:
        google_docs_url: Published Google Docs URL
        wordpress_url: WordPress site URL
        wordpress_username: WordPress username
        wordpress_app_password: WordPress application password
        html_configs: HTML transformation patterns
        image_configs: Image processing settings
        main_keyword: Optional main keyword for image naming
        project_id: Project ID for logging

    Returns:
        Dict with workflow results
    """
    start_time = time.time()
    results = {
        "steps_completed": [],
        "project_id": project_id
    }

    try:
        # Step 1: Convert Google Docs to HTML
        step_start = time.time()
        docs_result = await google_docs_to_html(google_docs_url)

        if not docs_result.get("success"):
            return {
                "success": False,
                "error": docs_result.get("error", "Failed to convert Google Docs"),
                "step_failed": "google_docs_conversion",
                "execution_time": time.time() - start_time,
                **results
            }

        raw_html = docs_result["raw_html"]
        document_name = docs_result.get("document_name", "Untitled")
        results["steps_completed"].append({
            "step": "google_docs_conversion",
            "time": time.time() - step_start,
            "document_name": document_name
        })

        # Step 2: Extract title from HTML
        step_start = time.time()
        title = extract_title_from_html(raw_html)
        if not title:
            title = document_name

        # Remove title from content (it becomes post title)
        content_html = remove_title_from_html(raw_html)

        results["steps_completed"].append({
            "step": "title_extraction",
            "time": time.time() - step_start,
            "title": title
        })

        # Step 3: Process images
        step_start = time.time()
        images_result = await process_images_from_html(
            content_html,
            image_config=image_configs,
            main_keyword=main_keyword or ""
        )

        processed_images = images_result.get("processed_images", [])
        results["steps_completed"].append({
            "step": "image_processing",
            "time": time.time() - step_start,
            "images_processed": len(processed_images)
        })

        # Step 4: Upload images to WordPress
        url_mapping = {}
        if processed_images:
            step_start = time.time()
            image_paths = [img["resized_path"] for img in processed_images]

            upload_result = await upload_images_batch(
                image_paths,
                wordpress_url,
                wordpress_username,
                wordpress_app_password
            )

            if not upload_result.get("success") and not upload_result.get("uploaded"):
                return {
                    "success": False,
                    "error": "Failed to upload any images to WordPress",
                    "step_failed": "image_upload",
                    "execution_time": time.time() - start_time,
                    **results
                }

            url_mapping = upload_result.get("url_mapping", {})
            results["steps_completed"].append({
                "step": "image_upload",
                "time": time.time() - step_start,
                "images_uploaded": len(upload_result.get("uploaded", [])),
                "images_failed": len(upload_result.get("failed", []))
            })

            # Replace image URLs in HTML
            content_html = replace_image_urls_in_html(content_html, url_mapping)

        # Step 5: Apply HTML transformations
        step_start = time.time()
        transform_result = await transform_html(content_html, html_configs)

        if transform_result.get("success"):
            content_html = transform_result["transformed_html"]

        results["steps_completed"].append({
            "step": "html_transformation",
            "time": time.time() - step_start,
            "patterns_applied": transform_result.get("patterns_applied", 0)
        })

        # Step 6: Create WordPress post
        step_start = time.time()
        post_result = await create_wordpress_post(
            title=title,
            content=content_html,
            wordpress_url=wordpress_url,
            username=wordpress_username,
            app_password=wordpress_app_password,
            status="draft"
        )

        if not post_result.get("success"):
            return {
                "success": False,
                "error": post_result.get("error", "Failed to create WordPress post"),
                "step_failed": "post_creation",
                "execution_time": time.time() - start_time,
                **results
            }

        results["steps_completed"].append({
            "step": "post_creation",
            "time": time.time() - step_start
        })

        # Success!
        return {
            "success": True,
            "post_id": post_result["post_id"],
            "post_url": post_result["post_url"],
            "edit_url": post_result["edit_url"],
            "post_title": title,
            "post_status": post_result["status"],
            "images_processed": len(processed_images),
            "execution_time": time.time() - start_time,
            **results
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "step_failed": "unknown",
            "execution_time": time.time() - start_time,
            **results
        }
