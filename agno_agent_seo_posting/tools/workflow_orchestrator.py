"""
Workflow Orchestrator Tool
Single tool that executes the complete 6-step SEO publishing workflow

This solves the "agent stops after 3 tools" problem by wrapping all steps into ONE tool call.
The agent calls this once, and internally it executes all 6 steps sequentially.

Version: 1.0.0
"""

import os
from typing import Dict, Any, Optional

from tools.google_docs_converter import google_docs_to_html
from tools.image_processor import process_images
from tools.html_formatter import format_html_with_template
from tools.wordpress_publisher import publish_to_wordpress
from utils.html_extractor import extract_title_from_content


def execute_complete_seo_workflow(
    content_url: str,
    template_url: str,
    wordpress_site_url: Optional[str] = None,
    post_status: str = "draft",
    target_width: int = 800
) -> Dict[str, Any]:
    """
    Execute the complete 6-step SEO publishing workflow in a single tool call.

    This tool orchestrates all steps internally:
    1. Convert content Google Docs to HTML
    2. Convert template Google Docs to HTML
    3. Extract title from content
    4. Process, resize, and upload images to WordPress
    5. Apply template formatting
    6. Publish post to WordPress (images already uploaded)

    Args:
        content_url: Google Docs URL for the blog post content (must be published)
        template_url: Google Docs URL for the HTML template (must be published)
        wordpress_site_url: WordPress site URL (optional, uses WP_BASE_URL env var if not provided)
        post_status: WordPress post status - 'draft' or 'publish' (default: 'draft')
        target_width: Target width for image resizing in pixels (default: 800)

    Returns:
        Dictionary containing:
        - success: Boolean indicating if workflow completed
        - post_title: Extracted post title
        - post_url: WordPress post URL (clickable link)
        - post_id: WordPress post ID
        - status: Post status (draft/publish)
        - images_processed: Number of images processed
        - error: Error message if failed
        - step_failed: Which step failed (if any)

    Example:
        result = execute_complete_seo_workflow(
            content_url="https://docs.google.com/document/d/e/2PACX-xxx/pub",
            template_url="https://docs.google.com/document/d/e/2PACX-yyy/pub",
            post_status="draft"
        )
    """
    workflow_data = {}

    try:
        # Use environment variable if wordpress_site_url not provided
        if not wordpress_site_url:
            wordpress_site_url = os.getenv("WP_BASE_URL")

        if not wordpress_site_url:
            return {
                "success": False,
                "error": "WordPress URL not configured. Set WP_BASE_URL in .env or provide wordpress_site_url parameter.",
                "step_failed": "configuration"
            }

        print("\n" + "="*80)
        print("🚀 EXECUTING COMPLETE SEO WORKFLOW")
        print("="*80)

        # STEP 1: Convert content Google Docs to HTML
        print("\n[1/6] 📄 Converting content from Google Docs...")
        content_result = google_docs_to_html(content_url)

        if not content_result.get('raw_html'):
            return {
                "success": False,
                "error": f"Failed to convert content: {content_result.get('error', 'Unknown error')}",
                "step_failed": "step_1_content_conversion"
            }

        workflow_data['content_html'] = content_result['raw_html']
        print(f"   ✓ Content converted ({len(workflow_data['content_html'])} characters)")

        # STEP 2: Convert template Google Docs to HTML
        print("\n[2/6] 📄 Converting template from Google Docs...")
        template_result = google_docs_to_html(template_url)

        if not template_result.get('raw_html'):
            return {
                "success": False,
                "error": f"Failed to convert template: {template_result.get('error', 'Unknown error')}",
                "step_failed": "step_2_template_conversion"
            }

        workflow_data['template_html'] = template_result['raw_html']
        print(f"   ✓ Template converted ({len(workflow_data['template_html'])} characters)")

        # STEP 3: Extract title from content
        print("\n[3/6] 📝 Extracting title from content...")
        post_title = extract_title_from_content(workflow_data['content_html'])

        if not post_title:
            return {
                "success": False,
                "error": "Failed to extract title from content (no <h1> tag found)",
                "step_failed": "step_3_title_extraction"
            }

        workflow_data['post_title'] = post_title
        print(f"   ✓ Title extracted: '{post_title}'")

        # STEP 4: Process images and upload to WordPress
        print(f"\n[4/6] 🖼️  Processing and uploading images (target width: {target_width}px)...")
        print(f"   - Downloading images from Google Docs")
        print(f"   - Resizing to target width: {target_width}px")
        print(f"   - Uploading to WordPress and getting WordPress URLs")
        print(f"   - Replacing <img> tags with WordPress URLs")

        image_result = process_images(
            html_content=workflow_data['content_html'],
            target_width=target_width,
            upload_to_wordpress=True,  # Enable WordPress upload during image processing
            wordpress_site_url=wordpress_site_url
        )

        if not image_result.get('success'):
            return {
                "success": False,
                "error": f"Image processing failed: {image_result.get('error', 'Unknown error')}",
                "step_failed": "step_4_image_processing"
            }

        workflow_data['processed_html'] = image_result['processed_html']
        workflow_data['image_metadata'] = image_result.get('image_metadata', [])

        # Count successfully uploaded images
        uploaded_count = sum(1 for img in workflow_data['image_metadata'] if img.get('wordpress_url'))
        total_count = len(workflow_data['image_metadata'])
        print(f"   ✓ Processed {total_count} images ({uploaded_count} uploaded to WordPress)")

        # Show sample WordPress URL
        if uploaded_count > 0:
            first_wp_url = next((img.get('wordpress_url') for img in workflow_data['image_metadata'] if img.get('wordpress_url')), None)
            if first_wp_url:
                print(f"   ✓ Sample WordPress URL: {first_wp_url[:80]}...")

        # STEP 5: Apply template formatting
        print("\n[5/6] ✨ Applying template formatting...")
        print(f"   - Extracting template rules for <p>, <img>, <h2>, <ol>, <ul>, etc.")
        print(f"   - Applying template classes and styles to content HTML")
        print(f"   - Preserving WordPress URLs, widths, heights, and alt text from Step 4")

        format_result = format_html_with_template(
            content_html=workflow_data['processed_html'],
            template_html=workflow_data['template_html']
        )

        if not format_result.get('success'):
            return {
                "success": False,
                "error": f"Template formatting failed: {format_result.get('error', 'Unknown error')}",
                "step_failed": "step_5_template_formatting"
            }

        workflow_data['formatted_html'] = format_result['formatted_html']
        template_rules = format_result.get('template_rules', {})
        applied_tags = [tag for tag, rules in template_rules.items() if rules]
        print(f"   ✓ Template applied to {len(applied_tags)} tag types: {', '.join(applied_tags[:8])}")
        print(f"   ✓ Final HTML: {len(workflow_data['formatted_html'])} characters")

        # STEP 6: Publish to WordPress
        print(f"\n[6/6] 🚀 Publishing to WordPress...")
        print(f"   Note: Images already uploaded in Step 4, skipping re-upload")

        # Images are already uploaded and HTML already contains WordPress URLs
        # Just create the post without uploading images again
        publish_result = publish_to_wordpress(
            formatted_html=workflow_data['formatted_html'],
            post_title=workflow_data['post_title'],
            wordpress_site_url=wordpress_site_url,
            post_status=post_status,
            image_paths=None,  # Don't upload images again
            image_metadata=workflow_data['image_metadata']
        )

        if not publish_result.get('success'):
            return {
                "success": False,
                "error": f"WordPress publishing failed: {publish_result.get('error', 'Unknown error')}",
                "step_failed": "step_6_wordpress_publishing"
            }

        workflow_data['post_url'] = publish_result['post_url']
        workflow_data['post_id'] = publish_result['post_id']
        workflow_data['status'] = publish_result['status']

        print(f"   ✓ Published successfully!")

        # SUCCESS SUMMARY
        print("\n" + "="*80)
        print("✅ WORKFLOW COMPLETED SUCCESSFULLY")
        print("="*80)
        print(f"📝 Title: {workflow_data['post_title']}")
        print(f"🔗 URL: {workflow_data['post_url']}")
        print(f"🖼️  Images: {len(workflow_data['image_metadata'])}")
        print(f"📊 Status: {workflow_data['status']}")
        print("="*80 + "\n")

        return {
            "success": True,
            "post_title": workflow_data['post_title'],
            "post_url": workflow_data['post_url'],
            "post_id": workflow_data['post_id'],
            "status": workflow_data['status'],
            "images_processed": len(workflow_data['image_metadata']),
            "workflow_data": workflow_data
        }

    except Exception as e:
        print(f"\n❌ WORKFLOW FAILED: {str(e)}")
        print("="*80 + "\n")

        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "step_failed": "unknown",
            "completed_data": workflow_data
        }
