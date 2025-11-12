"""
Project Configuration Agent

AI agent that helps users configure new projects by analyzing HTML templates
and generating transformation patterns automatically.
"""

import os
import sys
import json
from agno.agent import Agent
from agno.models.anthropic import Claude

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import create_project
from tools.pattern_analyzer import (
    create_image_config_from_preferences,
    analyze_html_template_for_patterns
)


def save_project_configuration(
    project_id: str,
    project_name: str,
    wordpress_url: str,
    wordpress_username: str,
    wordpress_app_password: str,
    html_configs: dict,
    image_configs: dict,
    notes: str = ""
) -> dict:
    """
    Save a new project configuration to the database.

    Args:
        project_id: Unique project identifier (slug format)
        project_name: Display name for the project
        wordpress_url: WordPress site URL
        wordpress_username: WordPress admin username
        wordpress_app_password: WordPress application password
        html_configs: Dict with transformation patterns
        image_configs: Dict with image settings
        notes: Optional notes

    Returns:
        Dict with success status and message
    """
    try:
        create_project(
            project_id=project_id,
            project_name=project_name,
            wordpress_url=wordpress_url,
            wordpress_username=wordpress_username,
            wordpress_app_password=wordpress_app_password,
            html_configs=html_configs,
            image_configs=image_configs,
            notes=notes
        )

        return {
            "success": True,
            "message": f"Project '{project_name}' saved successfully!",
            "project_id": project_id
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to save project: {str(e)}",
            "error": str(e)
        }


def create_configuration_agent() -> Agent:
    """
    Create the Project Configuration Agent.

    This agent guides users through project setup and analyzes HTML templates.
    """
    agent = Agent(
        name="Project Configuration Specialist",
        role="Help users configure new projects for SEO publishing",
        model=Claude(
            id="claude-sonnet-4-5-20250929",
            api_key=os.getenv("ANTHROPIC_API_KEY")
        ),
        description=(
            "You are a project configuration specialist. You help users set up new projects "
            "by gathering their requirements and analyzing HTML templates to extract transformation patterns."
        ),
        tools=[
            create_image_config_from_preferences,
            save_project_configuration
        ],
        instructions=[
            "=== YOUR TASK ===",
            "Help the user configure a new project for SEO publishing. Follow these steps:",
            "",
            "STEP 1: Gather Basic Information",
            "Ask the user for:",
            "- Project ID (slug format, e.g., 'acme_corp_2025')",
            "- Project Name (display name)",
            "- WordPress site URL",
            "- WordPress username",
            "- WordPress application password",
            "- Any notes for future reference",
            "",
            "STEP 2: Image Configuration",
            "Ask the user for image preferences:",
            "- Target image width (default: 800px)",
            "- Image quality 1-100 (default: 92)",
            "- Image format: JPEG, PNG, or WEBP (default: JPEG)",
            "- CSS classes for images (e.g., 'wp-image aligncenter')",
            "- Image alignment: left, center, right (default: center)",
            "",
            "STEP 3: HTML Template Analysis",
            "Ask the user to paste a sample of their desired HTML output.",
            "Then analyze it to extract patterns:",
            "",
            "For each HTML element type you find (p, h2, h3, strong, em, ul, ol, li, table, img, a):",
            "1. Identify the complete pattern with all attributes",
            "2. Note any CSS classes, styles, or other attributes",
            "3. Generate a regex pattern to transform plain HTML to this format",
            "",
            "Create transformation patterns in this format:",
            "```json",
            "{",
            '  "patterns": [',
            '    {',
            '      "element_type": "p",',
            '      "source_pattern": "<p[^>]*>(.*?)</p>",',
            '      "target_pattern": "<p class=\\"article-body\\" style=\\"text-align: justify;\\">\\\\1</p>"',
            '    },',
            '    {',
            '      "element_type": "strong",',
            '      "source_pattern": "<b>(.*?)</b>",',
            '      "target_pattern": "<strong>\\\\1</strong>"',
            '    }',
            '  ]',
            "}",
            "```",
            "",
            "STEP 4: Review and Confirmation",
            "Show the user:",
            "- All gathered information",
            "- Generated html_configs (the patterns JSON)",
            "- Generated image_configs (using create_image_config_from_preferences tool)",
            "",
            "Ask for confirmation before saving.",
            "",
            "STEP 5: Save Configuration",
            "Once user confirms:",
            "1. Use the create_image_config_from_preferences tool to create the image_configs dict",
            "2. Use the save_project_configuration tool to save everything to the database",
            "3. Confirm to the user that the project has been saved successfully",
            "",
            "=== IMPORTANT NOTES ===",
            "- Be thorough in HTML analysis - check ALL element types",
            "- Use double backslashes (\\\\1) for capture groups in JSON",
            "- Always preserve content with (.*?) capture group",
            "- Include ALL attributes found in the sample HTML",
            "- Provide clear before/after examples",
            "- Be patient and guide the user step by step"
        ],
        markdown=True,
        debug_mode=False,
        # show_tool_calls=True,
        reasoning=True  # Enable extended thinking for HTML analysis
    )

    return agent


def run_configuration_workflow(agent: Agent) -> dict:
    """
    Run the interactive configuration workflow with the agent.

    Returns:
        Dict with project configuration data
    """
    print("\n" + "="*80)
    print("🔧 PROJECT CONFIGURATION WIZARD")
    print("="*80)
    print("\nWelcome! I'll help you configure a new project.")
    print("This involves gathering your WordPress details and analyzing your HTML template.\n")

    # Run agent interactively
    response = agent.print_response(
        "Let's start configuring a new project. Please guide me through the 5 steps: gather basic info, image config, HTML analysis, review, and save using the tools.",
        stream=True
    )

    print("\n" + "="*80)
    print("✅ Configuration workflow completed!")
    print("="*80 + "\n")

    return response


# Add explicit annotations for Agno tools
save_project_configuration.__annotations__ = {
    'project_id': str,
    'project_name': str,
    'wordpress_url': str,
    'wordpress_username': str,
    'wordpress_app_password': str,
    'html_configs': dict,
    'image_configs': dict,
    'notes': str,
    'return': dict
}
