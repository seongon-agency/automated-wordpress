"""
SEO Blog Publishing - Deterministic Workflow
A reliable, non-agentic pipeline that executes all steps sequentially

This workflow replaces the agent-based approach which was stopping after 3 tool calls.
Instead of trying to force an agent to call 6 tools, we orchestrate the tools directly.

Version: 1.0.0
"""

import os
import dotenv
from typing import Dict, Any, Optional

# Import tools directly
from tools.google_docs_converter import google_docs_to_html
from tools.image_processor import process_images
from tools.html_formatter import format_html_with_template
from tools.wordpress_publisher import publish_to_wordpress
from utils.html_extractor import extract_title_from_content

# Load environment variables
dotenv.load_dotenv()


class SEOPublishingPipeline:
    """
    Deterministic pipeline for SEO blog publishing.
    Executes all 6 steps reliably without agent intervention.
    """

    def __init__(self, wordpress_url: Optional[str] = None, target_width: int = 800):
        """
        Initialize the pipeline.

        Args:
            wordpress_url: WordPress site URL (defaults to WP_BASE_URL env var)
            target_width: Target width for image processing (default: 800px)
        """
        self.wordpress_url = wordpress_url or os.getenv("WP_BASE_URL")
        self.target_width = target_width
        self.results = {}

        if not self.wordpress_url:
            raise ValueError("WordPress URL not configured. Set WP_BASE_URL in .env or pass wordpress_url parameter.")

    def execute(
        self,
        content_url: str,
        template_url: str,
        post_status: str = "draft"
    ) -> Dict[str, Any]:
        """
        Execute the complete 6-step workflow.

        Args:
            content_url: Google Docs URL for content
            template_url: Google Docs URL for HTML template
            post_status: WordPress post status ('draft' or 'publish')

        Returns:
            Dictionary with complete workflow results and post URL
        """
        print("\n" + "="*80)
        print("🚀 STARTING SEO PUBLISHING PIPELINE")
        print("="*80)

        try:
            # STEP 1: Convert content from Google Docs to HTML
            print("\n[1/6] 📄 Converting content Google Docs to HTML...")
            content_result = google_docs_to_html(content_url)

            if not content_result.get('raw_html'):
                raise Exception(f"Failed to convert content: {content_result.get('error', 'Unknown error')}")

            self.results['content_html'] = content_result['raw_html']
            print(f"✓ Content converted ({len(self.results['content_html'])} chars)")

            # STEP 2: Convert template from Google Docs to HTML
            print("\n[2/6] 📄 Converting template Google Docs to HTML...")
            template_result = google_docs_to_html(template_url)

            if not template_result.get('raw_html'):
                raise Exception(f"Failed to convert template: {template_result.get('error', 'Unknown error')}")

            self.results['template_html'] = template_result['raw_html']
            print(f"✓ Template converted ({len(self.results['template_html'])} chars)")

            # STEP 3: Extract title from content
            print("\n[3/6] 📝 Extracting title from content...")
            post_title = extract_title_from_content(self.results['content_html'])

            if not post_title:
                raise Exception("Failed to extract title from content (no <h1> found)")

            self.results['post_title'] = post_title
            print(f"✓ Title extracted: '{post_title}'")

            # STEP 4: Process images
            print(f"\n[4/6] 🖼️  Processing images (target width: {self.target_width}px)...")
            image_result = process_images(
                html_content=self.results['content_html'],
                target_width=self.target_width
            )

            if not image_result.get('success'):
                raise Exception(f"Image processing failed: {image_result.get('error', 'Unknown error')}")

            self.results['processed_html'] = image_result['processed_html']
            self.results['image_metadata'] = image_result.get('image_metadata', [])
            print(f"✓ Images processed: {len(self.results['image_metadata'])} images")

            # STEP 5: Apply template formatting
            print("\n[5/6] ✨ Applying template formatting...")
            format_result = format_html_with_template(
                content_html=self.results['processed_html'],
                template_html=self.results['template_html']
            )

            if not format_result.get('success'):
                raise Exception(f"Template formatting failed: {format_result.get('error', 'Unknown error')}")

            self.results['formatted_html'] = format_result['formatted_html']
            print(f"✓ Template applied ({len(self.results['formatted_html'])} chars)")

            # STEP 6: Publish to WordPress
            print(f"\n[6/6] 🚀 Publishing to WordPress ({self.wordpress_url})...")

            # Extract image paths from metadata
            image_paths = [img['resized_path'] for img in self.results['image_metadata']]

            publish_result = publish_to_wordpress(
                formatted_html=self.results['formatted_html'],
                post_title=self.results['post_title'],
                wordpress_site_url=self.wordpress_url,
                post_status=post_status,
                image_paths=image_paths,
                image_metadata=self.results['image_metadata']
            )

            if not publish_result.get('success'):
                raise Exception(f"WordPress publishing failed: {publish_result.get('error', 'Unknown error')}")

            self.results['post_url'] = publish_result['post_url']
            self.results['post_id'] = publish_result['post_id']
            self.results['status'] = publish_result['status']

            print(f"✓ Published successfully!")

            # SUCCESS SUMMARY
            print("\n" + "="*80)
            print("✅ PIPELINE COMPLETED SUCCESSFULLY")
            print("="*80)
            print(f"📝 Title: {self.results['post_title']}")
            print(f"🔗 URL: {self.results['post_url']}")
            print(f"🖼️  Images: {len(self.results['image_metadata'])}")
            print(f"📊 Status: {self.results['status']}")
            print("="*80 + "\n")

            return {
                "success": True,
                "post_title": self.results['post_title'],
                "post_url": self.results['post_url'],
                "post_id": self.results['post_id'],
                "status": self.results['status'],
                "images_processed": len(self.results['image_metadata']),
                "results": self.results
            }

        except Exception as e:
            print(f"\n❌ PIPELINE FAILED: {str(e)}")
            print("="*80 + "\n")

            return {
                "success": False,
                "error": str(e),
                "completed_steps": list(self.results.keys()),
                "results": self.results
            }


def publish_blog_post(
    content_url: str,
    template_url: str,
    wordpress_url: Optional[str] = None,
    post_status: str = "draft",
    target_width: int = 800
) -> Dict[str, Any]:
    """
    Convenience function to execute the complete SEO publishing pipeline.

    Args:
        content_url: Google Docs URL for content
        template_url: Google Docs URL for HTML template
        wordpress_url: WordPress site URL (defaults to WP_BASE_URL env var)
        post_status: WordPress post status ('draft' or 'publish')
        target_width: Target width for image processing (default: 800px)

    Returns:
        Dictionary with complete workflow results and post URL

    Example:
        result = publish_blog_post(
            content_url="https://docs.google.com/document/d/e/2PACX-xxx/pub",
            template_url="https://docs.google.com/document/d/e/2PACX-yyy/pub",
            post_status="draft"
        )
        print(f"Published to: {result['post_url']}")
    """
    pipeline = SEOPublishingPipeline(
        wordpress_url=wordpress_url,
        target_width=target_width
    )

    return pipeline.execute(
        content_url=content_url,
        template_url=template_url,
        post_status=post_status
    )


if __name__ == "__main__":
    """
    Test the deterministic pipeline.

    Usage:
        python seo_workflow_deterministic.py
    """
    print("\n" + "="*80)
    print("SEO BLOG PUBLISHING - DETERMINISTIC PIPELINE")
    print("="*80)
    print("\nThis is a non-agentic, reliable workflow that executes all 6 steps.")
    print("Unlike the agent-based approach, this NEVER stops early.\n")

    # Example usage (replace with your URLs)
    content_url = "https://docs.google.com/document/d/e/2PACX-YOUR_CONTENT_DOC/pub"
    template_url = "https://docs.google.com/document/d/e/2PACX-YOUR_TEMPLATE_DOC/pub"

    print(f"Content URL: {content_url}")
    print(f"Template URL: {template_url}")
    print(f"WordPress: {os.getenv('WP_BASE_URL', 'Not configured')}")
    print("\nReady to publish? Update the URLs above and run again.\n")

    # Uncomment to run:
    # result = publish_blog_post(
    #     content_url=content_url,
    #     template_url=template_url,
    #     post_status="draft"
    # )
    #
    # if result['success']:
    #     print(f"\n🎉 Success! View your post: {result['post_url']}")
    # else:
    #     print(f"\n❌ Failed: {result['error']}")
