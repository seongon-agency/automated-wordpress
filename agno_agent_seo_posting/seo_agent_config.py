"""
SEO Blog Publishing Agent Configuration
Restructured for easy deployment following Agno framework patterns
Author: Based on original seo_agent.py
Version: 2.0.0
"""

import os
import dotenv
from typing import Dict, Any, Optional

# Agno framework imports
from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.db.sqlite import SqliteDb
from agno.os import AgentOS

# Import custom tools
from tools.google_docs_converter import google_docs_to_html
from tools.image_processor import process_images
from tools.html_formatter import format_html_with_template
from tools.wordpress_publisher import publish_to_wordpress
from utils.html_extractor import extract_title_from_content

# Load environment variables
dotenv.load_dotenv()


# Configure SQLite Database for SEO Agent
seo_db = SqliteDb(
    db_file="seo_agent.db",
    session_table="seo_sessions",
    memory_table="seo_memory",
    metrics_table="seo_metrics",
    eval_table="seo_evals",
    knowledge_table="seo_knowledge",
)


def create_seo_agent() -> Agent:
    """
    Create and configure the SEO Blog Publishing Agent.

    Returns:
        Configured Agent instance ready for deployment
    """
    seo_agent = Agent(
        name="SEO Blog Publishing Agent",
        role="Convert Google Docs to SEO-optimized HTML and publish to WordPress",
        model=Claude(
            id="claude-sonnet-4-5-20250929",
            api_key=os.getenv("ANTHROPIC_API_KEY")
        ),
        description=(
            "You are an expert SEO blog publishing assistant. "
            "You help users convert Google Docs into beautifully formatted, "
            "SEO-optimized HTML and optionally publish to WordPress. "
            "You can process images, apply HTML templates, and extract titles automatically."
        ),
        instructions=[
            "Always be friendly, professional, and clear in your communication.",
            "Guide users step-by-step through the blog publishing workflow.",
            "Explain what you're doing at each stage of the process.",
            "TWO Google Docs are required: one for content and one for the HTML template.",
            "The template Google Doc defines the formatting rules (paragraph styles, image classes, etc.).",
            "Automatically extract the first h1 heading from content as the post title.",
            "Provide helpful tips about SEO and blog formatting when appropriate.",
            "Always show a preview or summary before finalizing.",
            "Ask for confirmation before publishing to WordPress.",
            "Be proactive in identifying potential issues (missing images, broken links, etc.).",
            "Provide the final HTML in a format that's easy to copy and use.",
            "When publishing is successful, ALWAYS prominently display the WordPress post URL.",
            "Never use emojis unless explicitly requested by the user."
        ],

        # Tools - None here as we'll use direct function calls
        tools=[],

        # Database configuration
        db=seo_db,

        # History and context management
        add_history_to_context=True,
        read_chat_history=True,
        num_history_runs=3,
        search_session_history=True,

        # Session management
        cache_session=True,

        # Output configuration
        markdown=True,
        debug_mode=False
    )

    return seo_agent


def process_blog_workflow(
    content_url: str,
    template_url: str,
    post_title: Optional[str] = None,
    process_images_flag: bool = True,
    target_width: int = 800,
    publish_to_wp: bool = False,
    wordpress_site_url: Optional[str] = None,
    wp_post_title: Optional[str] = None,
    wp_status: str = "draft",
    categories: Optional[list] = None,
    tags: Optional[list] = None
) -> Dict[str, Any]:
    """
    Execute the complete blog publishing workflow.

    This function can be called directly or through the agent.

    Args:
        content_url: URL of the content Google Doc
        template_url: URL of the template Google Doc
        post_title: Optional post title override
        process_images_flag: Whether to process and resize images
        target_width: Target width for image resizing
        publish_to_wp: Whether to publish to WordPress
        wordpress_site_url: WordPress site URL
        wp_post_title: WordPress post title
        wp_status: Post status (draft/publish)
        categories: Category IDs
        tags: Tag names

    Returns:
        Dictionary with workflow results
    """
    results = {
        "success": False,
        "stage": None,
        "content_html": None,
        "template_html": None,
        "formatted_html": None,
        "final_html": None,
        "image_metadata": [],
        "errors": [],
        "extracted_title": None,
        "wordpress_url": None,
        "wordpress_post_id": None
    }

    try:
        # Step 1: Convert content Google Doc to HTML
        print("📄 Step 1: Converting content Google Doc to HTML...")
        content_result = google_docs_to_html(content_url)

        if not content_result['success']:
            results['errors'].append(f"Content conversion failed: {content_result['error']}")
            results['stage'] = "content_conversion"
            return results

        results['content_html'] = content_result['raw_html']
        print(f"✅ Content converted: {content_result['name']}")

        # Extract title from content
        extracted_title = extract_title_from_content(
            content_result['raw_html'],
            fallback=post_title
        )
        if extracted_title:
            results['extracted_title'] = extracted_title
            print(f"📝 Extracted title: \"{extracted_title}\"")

        # Step 2: Convert template Google Doc to HTML
        print("\n📐 Step 2: Converting template Google Doc to HTML...")
        template_result = google_docs_to_html(template_url)

        if not template_result['success']:
            results['errors'].append(f"Template conversion failed: {template_result['error']}")
            results['stage'] = "template_conversion"
            return results

        results['template_html'] = template_result['raw_html']
        print(f"✅ Template converted: {template_result['name']}")

        # Step 3: Process images (if requested)
        current_html = results['content_html']

        if process_images_flag:
            print(f"\n🖼️  Step 3: Processing images (target width: {target_width}px)...")
            image_result = process_images(
                html_content=current_html,
                target_width=target_width
            )

            if image_result['success']:
                current_html = image_result['processed_html']
                results['image_metadata'] = image_result['image_metadata']
                print(f"✅ Processed {len(image_result['image_metadata'])} images")
            else:
                results['errors'].append(f"Image processing warning: {image_result['error']}")
                print(f"⚠️  Image processing had issues: {image_result['error']}")

        # Step 4: Apply template formatting
        print("\n✨ Step 4: Applying template formatting to content...")
        format_result = format_html_with_template(
            content_html=current_html,
            template_html=results['template_html']
        )

        if not format_result['success']:
            results['errors'].append(f"Formatting failed: {format_result['error']}")
            results['stage'] = "formatting"
            return results

        results['formatted_html'] = format_result['formatted_html']
        results['final_html'] = format_result['formatted_html']
        print("✅ Template formatting applied successfully")

        # Step 5: Publish to WordPress (if requested)
        if publish_to_wp and wordpress_site_url:
            print("\n🚀 Step 5: Publishing to WordPress...")

            # Use extracted title if no WordPress title provided
            final_wp_title = wp_post_title or results['extracted_title'] or post_title or "Untitled Post"

            # Get image paths for upload
            image_paths = []
            image_metadata = []

            for img in results['image_metadata']:
                if 'local_path' in img and img['local_path']:
                    image_paths.append(img['local_path'])
                    image_metadata.append({
                        'alt': img.get('alt', ''),
                        'title': img.get('alt', ''),
                        'description': img.get('alt', ''),
                        'caption': img.get('alt', '')
                    })

            # Publish
            wp_result = publish_to_wordpress(
                formatted_html=results['final_html'],
                wordpress_site_url=wordpress_site_url,
                post_title=final_wp_title,
                post_status=wp_status,
                categories=categories,
                tags=tags,
                image_paths=image_paths if image_paths else None,
                image_metadata=image_metadata if image_metadata else None
            )

            if wp_result['success']:
                results['wordpress_url'] = wp_result['post_url']
                results['wordpress_post_id'] = wp_result['post_id']
                print(f"✅ Published successfully!")
                print(f"🔗 Post URL: {wp_result['post_url']}")
            else:
                results['errors'].append(f"WordPress publishing failed: {wp_result['error']}")
                print(f"❌ Publishing failed: {wp_result['error']}")

        results['success'] = True
        results['stage'] = "complete"
        return results

    except Exception as e:
        results['errors'].append(f"Workflow error: {str(e)}")
        results['stage'] = "error"
        return results


def create_seo_agent_os() -> AgentOS:
    """
    Create an AgentOS instance with the SEO Blog Publishing Agent.

    Returns:
        AgentOS instance ready to serve
    """
    seo_agent = create_seo_agent()

    agent_os = AgentOS(
        id="seo-blog-publisher",
        description="SEO Blog Publishing System - Convert Google Docs to WordPress",
        agents=[seo_agent]
    )

    return agent_os


# Create the agent OS instance
seo_os_instance = create_seo_agent_os()
app = seo_os_instance.get_app()


if __name__ == "__main__":
    """
    Run the SEO Agent OS server.

    Usage:
        python seo_agent_config.py

    Or with custom settings:
        agno serve seo_agent_config:app --reload
    """
    print("\n" + "="*80)
    print("🚀 Starting SEO Blog Publishing Agent OS")
    print("="*80)
    print("\nAgent: SEO Blog Publishing Agent")
    print("Database: seo_agent.db")
    print("Model: Claude Sonnet 4.5")
    print("\nFeatures:")
    print("  ✓ Google Docs to HTML conversion")
    print("  ✓ Automatic title extraction from h1")
    print("  ✓ Image processing and resizing")
    print("  ✓ HTML template formatting")
    print("  ✓ WordPress publishing")
    print("  ✓ Session history and memory")
    print("\n" + "="*80 + "\n")

    seo_os_instance.serve(app="seo_agent_config:app", reload=False)
