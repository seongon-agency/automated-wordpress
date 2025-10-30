"""
SEO Blog Publishing Agents - Deployable Configuration
Following the Agno framework pattern for easy deployment

Author: Based on original seo_agent.py
Version: 3.1.0

CHANGELOG v3.1.0:
- CRITICAL FIX: Template attributes now consistently applied to ALL tag types
- Fixed html_formatter.py to always use default template form (no more "smart" logic)
- Paragraphs, headings, lists, tables, links, etc. now get exact attributes from template
- Example: <p dir="ltr" style="text-align: justify;"> from template is now applied to all <p> tags
- Added support for additional tag types: b, i, u, div, blockquote, h1
- Simplified _apply_attributes() method for clearer attribute preservation logic
- Updated HTMLFormatter to Version 3.0 with consistent template application

CHANGELOG v3.0.0:
- ARCHITECTURAL FIX: Created workflow orchestrator tool to solve "stops after 3 tools" problem
- Agent now has ONE tool (execute_complete_seo_workflow) that internally runs all 6 steps
- This solves Claude's natural tendency to stop and report after 3-5 tool calls
- Drastically simplified agent instructions (no more multi-tool chaining logic needed)
- Agent simply calls one tool with content_url and template_url parameters
- Workflow tool handles all orchestration internally and returns complete result
- More reliable: Workflow either fully completes or returns specific failure point

CHANGELOG v2.3.0:
- CRITICAL FIX: Agent now properly executes all tools in single response
- Completely rewrote instructions to be more directive and action-oriented
- Added explicit "MULTI-TOOL EXECUTION REQUIRED" directive
- Removed verbose explanations, replaced with concrete execution pattern
- Changed from "what to do" to "how to execute" instruction format
- Re-enabled search_session_history to track multi-step progress
- Increased num_history_runs from 1 to 2 for better workflow context
- Added FORBIDDEN BEHAVIORS section to prevent premature stopping
- Instructions now total ~35 lines (down from 50+) for better clarity

CHANGELOG v2.2.0:
- CRITICAL FIX: google_docs_to_html() now extracts only document content
- Previously extracted entire Google Docs page (wrapper, scripts, navigation)
- Now extracts only the content container (div#contents)
- Prevents Google wrapper HTML from being published to WordPress
- Improves content quality and WordPress post cleanliness

CHANGELOG v2.1.0:
- Fixed multi-step workflow execution issue
- Agent now executes all 5 steps continuously without stopping
- Improved instructions to emphasize automated pipeline behavior
- Agent no longer waits for user feedback between tool calls
"""

import os
import dotenv
from typing import Dict, Any, Optional

# Agno framework imports
from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.db.sqlite import SqliteDb
from agno.os import AgentOS

# Import custom tools as functions
from tools.google_docs_converter import google_docs_to_html
from tools.image_processor import process_images
from tools.html_formatter import format_html_with_template
from tools.wordpress_publisher import publish_to_wordpress
from utils.html_extractor import extract_title_from_content

# Import workflow orchestrator (solves "stops after 3 tools" problem)
from tools.workflow_orchestrator import execute_complete_seo_workflow

# Load environment variables
dotenv.load_dotenv()


# Configure SQLite Database
db = SqliteDb(
    db_file="seo_agent.db",
    session_table="seo_sessions",
    memory_table="seo_memory",
    metrics_table="seo_metrics",
    eval_table="seo_evals",
    knowledge_table="seo_knowledge",
)


def seo_publishing_system():
    """
    Create the SEO Blog Publishing System with agents.

    Returns:
        AgentOS instance with configured agents
    """

    # Main SEO Publishing Agent
    seo_publisher = Agent(
        name="SEO Blog Publisher",
        role="Convert Google Docs to SEO-optimized HTML and publish to WordPress",
        model=Claude(
            id="claude-sonnet-4-5-20250929",
            api_key=os.getenv("ANTHROPIC_API_KEY")
        ),
        description=(
            "You execute the complete SEO blog publishing workflow using a single orchestrator tool. "
            "When given Google Docs URLs, call execute_complete_seo_workflow() with content_url and template_url. "
            "The tool handles all 6 steps internally (convert, extract, process, format, publish) and returns the complete result. "
            f"WordPress: {os.getenv('WP_BASE_URL', 'Not configured')}"
        ),
        instructions=[
            "=== YOUR TASK ===",
            "When the user provides Google Docs URLs for content and template:",
            "",
            "1. Call execute_complete_seo_workflow() with these parameters:",
            "   - content_url: The Google Docs URL for blog content",
            "   - template_url: The Google Docs URL for HTML template",
            "   - post_status: 'draft' (default) or 'publish'",
            "   - target_width: 800 (default image width in pixels)",
            "",
            "2. The tool executes all 6 steps internally:",
            "   • Converts both Google Docs to HTML",
            "   • Extracts title from content",
            "   • Processes, resizes, and uploads images to WordPress",
            "   • Applies template formatting",
            "   • Publishes post to WordPress (images already uploaded)",
            "",
            "3. Report the result to the user:",
            "   ✓ Post title",
            "   ✓ WordPress URL (clickable)",
            "   ✓ Number of images processed",
            "   ✓ Status (draft/publish)",
            "",
            "=== ERROR HANDLING ===",
            "If the tool returns success=False:",
            "- Report which step failed (step_failed field)",
            "- Show the error message",
            "- Provide troubleshooting guidance",
            "",
            "=== IMPORTANT ===",
            "- You only need to call ONE tool: execute_complete_seo_workflow",
            "- The tool handles all workflow orchestration internally",
            "- Do not ask for confirmation - this is an automated pipeline",
            "- Report results concisely after the tool completes"
        ],
        tools=[
            execute_complete_seo_workflow  # Single orchestrator tool
        ],
        db=db,
        add_history_to_context=True,
        read_chat_history=True,
        num_history_runs=2,
        search_session_history=True,
        markdown=True,
        debug_mode=True,
        stream_intermediate_steps=True,
        cache_session=True
    )

    # Content Converter Agent (specialized for Google Docs conversion)
    content_converter = Agent(
        name="Content Converter",
        role="Convert Google Docs to HTML format",
        model=Claude(
            id="claude-sonnet-4-5-20250929",
            api_key=os.getenv("ANTHROPIC_API_KEY")
        ),
        description=(
            "You specialize in converting Google Docs content to clean HTML. "
            "You extract document structure, maintain formatting, and identify key elements like headings and images."
        ),
        instructions=[
            "Convert Google Docs URLs to HTML format.",
            "Extract and preserve document structure.",
            "Identify all images and their metadata.",
            "Extract the main title (h1) from the document.",
            "Report any conversion issues clearly."
        ],
        tools=[
            google_docs_to_html,
            extract_title_from_content
        ],
        db=db,
        add_history_to_context=True,
        read_chat_history=True,
        num_history_runs=2,
        search_session_history=True,
        markdown=True,
        debug_mode=False,
        cache_session=True
    )

    # HTML Formatter Agent (specialized for applying templates)
    html_formatter = Agent(
        name="HTML Formatter",
        role="Apply HTML templates and formatting rules to content",
        model=Claude(
            id="claude-sonnet-4-5-20250929",
            api_key=os.getenv("ANTHROPIC_API_KEY")
        ),
        description=(
            "You specialize in applying HTML template formatting to content. "
            "You analyze template rules and apply them consistently to ensure SEO-optimized, well-formatted HTML."
        ),
        instructions=[
            "Parse HTML template documents to extract formatting rules.",
            "Apply paragraph styles, heading styles, and image classes.",
            "Ensure all HTML is SEO-friendly and well-structured.",
            "Maintain semantic HTML for better search engine indexing.",
            "Report formatting statistics and any issues encountered."
        ],
        tools=[
            format_html_with_template,
            process_images
        ],
        db=db,
        add_history_to_context=True,
        read_chat_history=True,
        num_history_runs=2,
        search_session_history=True,
        markdown=True,
        debug_mode=False,
        cache_session=True
    )

    # WordPress Publisher Agent (specialized for WordPress)
    wordpress_publisher = Agent(
        name="WordPress Publisher",
        role="Publish content to WordPress sites",
        model=Claude(
            id="claude-sonnet-4-5-20250929",
            api_key=os.getenv("ANTHROPIC_API_KEY")
        ),
        description=(
            "You specialize in publishing content to WordPress via the REST API. "
            "You handle image uploads, post creation, and return the published post URL."
        ),
        instructions=[
            "Upload images to WordPress media library.",
            "Create posts with proper titles, content, and metadata.",
            "Set appropriate categories and tags.",
            "Handle draft and publish statuses correctly.",
            "Always return the complete post URL for easy access.",
            "Report upload statistics and any errors clearly."
        ],
        tools=[
            publish_to_wordpress
        ],
        db=db,
        add_history_to_context=True,
        read_chat_history=True,
        num_history_runs=2,
        search_session_history=True,
        markdown=True,
        debug_mode=False,
        cache_session=True
    )

    # Create AgentOS with all agents
    agent_os = AgentOS(
        id="seo-blog-publishing-system",
        description="Complete SEO Blog Publishing System with specialized agents",
        agents=[
            seo_publisher,
            content_converter,
            html_formatter,
            wordpress_publisher
        ]
    )

    return agent_os


# Workflow functions for direct execution
def convert_google_docs_step(content_url: str, template_url: str) -> Dict[str, Any]:
    """Step 1: Convert both Google Docs to HTML."""
    print("📄 Converting Google Docs to HTML...")

    content_result = google_docs_to_html(content_url)
    template_result = google_docs_to_html(template_url)

    return {
        "content_html": content_result.get('raw_html'),
        "template_html": template_result.get('raw_html'),
        "content_name": content_result.get('name'),
        "template_name": template_result.get('name'),
        "success": content_result['success'] and template_result['success']
    }


def extract_title_step(content_html: str) -> Dict[str, Any]:
    """Step 2: Extract title from content."""
    print("📝 Extracting title from content...")

    title = extract_title_from_content(content_html)

    return {
        "extracted_title": title,
        "success": title is not None
    }


def process_images_step(html_content: str, target_width: int = 800) -> Dict[str, Any]:
    """Step 3: Process and resize images."""
    print(f"🖼️  Processing images (target width: {target_width}px)...")

    result = process_images(html_content=html_content, target_width=target_width)

    return {
        "processed_html": result.get('processed_html', html_content),
        "image_metadata": result.get('image_metadata', []),
        "success": result['success']
    }


def format_html_step(content_html: str, template_html: str) -> Dict[str, Any]:
    """Step 4: Apply template formatting."""
    print("✨ Applying template formatting...")

    result = format_html_with_template(
        content_html=content_html,
        template_html=template_html
    )

    return {
        "formatted_html": result.get('formatted_html'),
        "template_rules": result.get('template_rules', {}),
        "success": result['success']
    }


def publish_wordpress_step(
    formatted_html: str,
    post_title: str,
    wordpress_site_url: Optional[str] = None,
    post_status: str = "draft",
    image_paths: Optional[list] = None,
    image_metadata: Optional[list] = None
) -> Dict[str, Any]:
    """Step 5: Publish to WordPress."""
    print("🚀 Publishing to WordPress...")

    # Use environment variable if wordpress_site_url not provided
    if not wordpress_site_url:
        wordpress_site_url = os.getenv("WP_BASE_URL")
        print(f"   Using WordPress URL from environment: {wordpress_site_url}")

    result = publish_to_wordpress(
        formatted_html=formatted_html,
        post_title=post_title,
        wordpress_site_url=wordpress_site_url,
        post_status=post_status,
        image_paths=image_paths,
        image_metadata=image_metadata
    )

    return {
        "post_url": result.get('post_url'),
        "post_id": result.get('post_id'),
        "status": result.get('status'),
        "success": result['success']
    }


# Create the OS instance
os_instance = seo_publishing_system()
app = os_instance.get_app()


if __name__ == "__main__":
    """
    Run the SEO Publishing System.

    Usage:
        python seo_agents.py

    Or with Agno CLI:
        agno serve seo_agents:app --reload
    """
    print("\n" + "="*80)
    print("🚀 SEO BLOG PUBLISHING SYSTEM v3.1")
    print("="*80)
    print("\n✨ NEW IN v3.1: Consistent Template Attribute Application")
    print("   All tags now receive exact attributes from template (dir, style, etc.)")
    print("   No more missing attributes - full template form applied to all tags.\n")
    print("Starting AgentOS with specialized agents:")
    print("  • SEO Blog Publisher (Uses workflow orchestrator)")
    print("  • Content Converter (Google Docs → HTML)")
    print("  • HTML Formatter (Template application)")
    print("  • WordPress Publisher (Content deployment)")
    print("\nDatabase: seo_agent.db")
    print("Model: Claude Sonnet 4.5")
    print("\nWorkflow (executed by orchestrator):")
    print("  1. Convert content Google Docs → HTML")
    print("  2. Convert template Google Docs → HTML")
    print("  3. Extract title from content (h1)")
    print("  4. Process, resize, and upload images to WordPress")
    print("  5. Apply template formatting")
    print("  6. Publish post to WordPress (images already uploaded)")
    print("\nFeatures:")
    print("  ✓ Reliable end-to-end workflow execution")
    print("  ✓ No more premature stopping issues")
    print("  ✓ Automatic error recovery and reporting")
    print("  ✓ Session history and memory")
    print("  ✓ Conversation context tracking")
    print("\n" + "="*80 + "\n")

    os_instance.serve(app="seo_agents:app", reload=False)
