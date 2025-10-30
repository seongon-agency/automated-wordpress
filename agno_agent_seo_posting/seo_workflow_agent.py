"""
SEO Blog Publishing Workflow - AgentOS Deployment
Combines the Workflow pattern from seo_workflow_fixed.py with Agent deployment

Version: 3.0.0
Author: Deployment version with AgentOS integration
"""

import os
import dotenv
from typing import Dict, Any

# Agno framework imports
from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.db.sqlite import SqliteDb
from agno.workflow import Step, Workflow

# Import custom tools
from tools.google_docs_converter import google_docs_to_html
from tools.image_processor import process_images
from tools.html_formatter import format_html_with_template
from tools.wordpress_publisher import publish_to_wordpress
from utils.html_extractor import extract_title_from_content

# Load environment variables
dotenv.load_dotenv()


# Configure SQLite Database
db = SqliteDb(
    db_file="seo_agent.db",
    session_table="seo_workflow_sessions",
    memory_table="seo_workflow_memory",
    metrics_table="seo_workflow_metrics",
    eval_table="seo_workflow_evals",
    knowledge_table="seo_workflow_knowledge",
)


# ============================================================================
# WORKFLOW STEPS (from seo_workflow_fixed.py)
# ============================================================================

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


# ============================================================================
# WORKFLOW EXECUTOR FUNCTION (for Agent to call)
# ============================================================================

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


# ============================================================================
# AGENT CONFIGURATION (AgentOS Deployment)
# ============================================================================

def create_seo_workflow_agent():
    """
    Create the SEO Workflow Agent for AgentOS deployment.

    Returns:
        Agent instance configured with workflow tools
    """

    agent = Agent(
        name="SEO Workflow Publisher",
        role="Execute automated SEO blog publishing workflow from Google Docs to WordPress",
        model=Claude(
            id="claude-sonnet-4-5-20250929",
            api_key=os.getenv("ANTHROPIC_API_KEY")
        ),
        description=(
            "AUTOMATED WORKFLOW EXECUTOR. "
            "Executes a 5-step pipeline to convert Google Docs to SEO-optimized WordPress posts. "
            f"WordPress: {os.getenv('WP_BASE_URL', 'Not configured')}"
        ),
        instructions=[
            "=== YOUR PURPOSE ===",
            "You execute a complete automated workflow to publish blog posts from Google Docs to WordPress.",
            "",
            "=== WORKFLOW EXECUTION ===",
            "When user provides content_url and template_url:",
            "1. Call run_seo_workflow() with the provided URLs",
            "2. The workflow automatically executes all 5 steps:",
            "   - Convert Google Docs to HTML",
            "   - Extract post title",
            "   - Process and resize images",
            "   - Apply template formatting",
            "   - Publish to WordPress",
            "",
            "=== FUNCTION SIGNATURE ===",
            "run_seo_workflow(",
            "    content_url: str,      # Published Google Docs URL",
            "    template_url: str,     # Published template URL",
            "    target_width: int = 800,  # Image width",
            "    post_status: str = 'draft'  # WordPress status",
            ")",
            "",
            "=== WHAT YOU REPORT ===",
            "After workflow completes, report:",
            "✓ Post title (extracted from h1)",
            "✓ WordPress URL (clickable)",
            "✓ Number of images processed",
            "✓ Post status (draft/publish)",
            "",
            "=== ERROR HANDLING ===",
            "If workflow fails, report which step failed and the error message.",
            "",
            "=== EXAMPLE USAGE ===",
            "User: 'Publish this doc: [content_url] with template: [template_url]'",
            "You: Call run_seo_workflow(content_url, template_url) and report results."
        ],
        tools=[
            run_seo_workflow,
            google_docs_to_html,
            extract_title_from_content,
            process_images,
            format_html_with_template,
            publish_to_wordpress
        ],
        db=db,
        add_history_to_context=True,
        read_chat_history=True,
        num_history_runs=3,
        search_session_history=True,
        markdown=True,
        debug_mode=True,
        cache_session=True
    )

    return agent


# Create the agent instance
seo_workflow_agent = create_seo_workflow_agent()

# For AgentOS deployment, wrap in AgentOS
from agno.os import AgentOS

agent_os = AgentOS(
    id="seo-workflow-publishing",
    description="SEO Blog Publishing Workflow - Automated pipeline from Google Docs to WordPress",
    agents=[seo_workflow_agent]
)

app = agent_os.get_app()


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    """
    Run the SEO Workflow Agent with AgentOS.

    Usage:
        python seo_workflow_agent.py

    Or with Agno CLI:
        agno serve seo_workflow_agent:app --reload
    """
    print("\n" + "="*80)
    print("🚀 SEO WORKFLOW AGENT - AGENTOS DEPLOYMENT")
    print("="*80)
    print("\nAgent Configuration:")
    print(f"  • Name: {seo_workflow_agent.name}")
    print(f"  • Role: {seo_workflow_agent.role}")
    print(f"  • Model: Claude Sonnet 4.5")
    print(f"  • Database: seo_agent.db")
    print(f"  • WordPress: {os.getenv('WP_BASE_URL', 'Not configured')}")
    print("\nWorkflow Steps:")
    print("  1. Convert Google Docs to HTML")
    print("  2. Extract title from content")
    print("  3. Process and resize images")
    print("  4. Apply template formatting")
    print("  5. Publish to WordPress")
    print("\nFeatures:")
    print("  ✓ Automated 5-step workflow")
    print("  ✓ Automatic title extraction (h1)")
    print("  ✓ Image processing and optimization")
    print("  ✓ HTML template formatting")
    print("  ✓ WordPress REST API publishing")
    print("  ✓ Session history and memory")
    print("\nStarting agent server...")
    print("="*80 + "\n")

    # Start the agent server
    agent_os.serve(app="seo_workflow_agent:app", reload=False)
