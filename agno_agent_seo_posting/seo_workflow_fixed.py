"""
SEO Blog Publishing Workflow - Using Agno Workflow Pattern
This approach chains tool calls as explicit workflow steps to avoid agent stopping issues.

Version: 1.0.0
Author: Fixed version addressing stopping-after-3-calls issue
"""

import os
import dotenv
from typing import Dict, Any

# Agno framework imports
from agno.workflow import Step, Workflow

# Import custom tools
from tools.google_docs_converter import google_docs_to_html
from tools.image_processor import process_images
from tools.html_formatter import format_html_with_template
from tools.wordpress_publisher import publish_to_wordpress
from utils.html_extractor import extract_title_from_content

# Load environment variables
dotenv.load_dotenv()


def step_1_convert_docs(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Step 1: Convert both Google Docs to HTML."""
    print("📄 Step 1: Converting Google Docs to HTML...")

    content_url = input_data['content_url']
    template_url = input_data['template_url']

    content_result = google_docs_to_html(content_url)
    template_result = google_docs_to_html(template_url)

    if not content_result['success'] or not template_result['success']:
        raise Exception(f"Failed to convert docs: content={content_result['success']}, template={template_result['success']}")

    return {
        **input_data,  # Pass through original input
        'content_html': content_result['raw_html'],
        'template_html': template_result['raw_html']
    }


def step_2_extract_title(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Step 2: Extract title from content."""
    print("📝 Step 2: Extracting title...")

    title = extract_title_from_content(input_data['content_html'])

    if not title:
        raise Exception("Failed to extract title from content")

    return {
        **input_data,
        'post_title': title
    }


def step_3_process_images(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Step 3: Process and resize images."""
    print(f"🖼️  Step 3: Processing images (target width: {input_data.get('target_width', 800)}px)...")

    result = process_images(
        html_content=input_data['content_html'],
        target_width=input_data.get('target_width', 800)
    )

    if not result['success']:
        raise Exception("Failed to process images")

    print(f"   Processed {len(result.get('image_metadata', []))} images")

    return {
        **input_data,
        'processed_html': result['processed_html'],
        'image_metadata': result.get('image_metadata', [])
    }


def step_4_format_html(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Step 4: Apply template formatting."""
    print("✨ Step 4: Applying template formatting...")

    result = format_html_with_template(
        content_html=input_data['processed_html'],
        template_html=input_data['template_html']
    )

    if not result['success']:
        raise Exception("Failed to format HTML")

    return {
        **input_data,
        'formatted_html': result['formatted_html']
    }


def step_5_publish_wordpress(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Step 5: Publish to WordPress."""
    print("🚀 Step 5: Publishing to WordPress...")

    # Extract image paths from metadata
    image_paths = [m['resized_path'] for m in input_data.get('image_metadata', [])]

    result = publish_to_wordpress(
        formatted_html=input_data['formatted_html'],
        post_title=input_data['post_title'],
        wordpress_site_url=input_data.get('wordpress_site_url', os.getenv('WP_BASE_URL')),
        post_status=input_data.get('post_status', 'draft'),
        image_paths=image_paths,
        image_metadata=input_data.get('image_metadata', [])
    )

    if not result['success']:
        raise Exception(f"Failed to publish to WordPress: {result.get('error')}")

    print(f"\n✅ SUCCESS! Published to: {result.get('post_url')}")

    return {
        **input_data,
        'post_url': result.get('post_url'),
        'post_id': result.get('post_id'),
        'status': result.get('status')
    }


# Create the workflow
seo_publishing_workflow = Workflow(
    name="SEO Blog Publishing Workflow",
    steps=[
        Step(name="Convert Google Docs to HTML", executor=step_1_convert_docs),
        Step(name="Extract title from content", executor=step_2_extract_title),
        Step(name="Process and resize images", executor=step_3_process_images),
        Step(name="Apply template formatting", executor=step_4_format_html),
        Step(name="Publish to WordPress", executor=step_5_publish_wordpress),
    ]
)

def run_seo_workflow(
    content_url: str,
    template_url: str,
    target_width: int = 800,
    post_status: str = "draft"
) -> Dict[str, Any]:
    """
    Run the complete SEO publishing workflow.

    Args:
        content_url: Google Docs URL for the blog content
        template_url: Google Docs URL for the HTML template
        target_width: Target width for image resizing (default: 800)
        post_status: WordPress post status (default: "draft")

    Returns:
        Dict containing the workflow results including post_url
    """
    print("\n" + "="*80)
    print("🚀 SEO BLOG PUBLISHING WORKFLOW")
    print("="*80)
    print(f"Content URL: {content_url}")
    print(f"Template URL: {template_url}")
    print(f"Target Image Width: {target_width}px")
    print(f"Post Status: {post_status}")
    print("="*80 + "\n")

    # Prepare input data
    input_data = {
        'content_url': content_url,
        'template_url': template_url,
        'target_width': target_width,
        'post_status': post_status,
        'wordpress_site_url': os.getenv('WP_BASE_URL')
    }

    # Run the workflow
    result = seo_publishing_workflow.print_response(input_data)

    return result


if __name__ == "__main__":
    """
    Example usage:
    """
    # Example URLs (replace with your actual URLs)
    CONTENT_URL = "https://docs.google.com/document/d/e/2PACX-1vTDCwHgnP-VTBgggyE8z8fjBQMblE_clLwRQah2GTdLcnCcetiWNGfQgHaEg05fMg7b7OrJsYSRXGw2/pub"
    TEMPLATE_URL = "https://docs.google.com/document/d/e/2PACX-1vR9CcRP5KuvtD6GLAujQriz_QxllaEw3emzcwZrpOpnWhHG82aTY7te7biPo1FSB6fo472D4ZjqYd_l/pub"

    print("\n" + "="*80)
    print("SEO BLOG PUBLISHING WORKFLOW - EXAMPLE")
    print("="*80)
    print("\nTo use this workflow, replace the URLs below with your actual Google Docs URLs:")
    print(f"  CONTENT_URL = '{CONTENT_URL}'")
    print(f"  TEMPLATE_URL = '{TEMPLATE_URL}'")
    print("\nThen run:")
    print("  result = run_seo_workflow(")
    print("      content_url=CONTENT_URL,")
    print("      template_url=TEMPLATE_URL,")
    print("      target_width=800,")
    print("      post_status='draft'")
    print("  )")
    print("\n" + "="*80 + "\n")

    # Uncomment below to run with actual URLs:
    # result = run_seo_workflow(
    #     content_url=CONTENT_URL,
    #     template_url=TEMPLATE_URL,
    #     target_width=800,
    #     post_status='draft'
    # )
    # print(f"\nFinal result: {result}")
