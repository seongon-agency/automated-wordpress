"""
Main Orchestrator Agent

Coordinates the entire publishing system - handles project selection and workflow execution.
"""

import os
import sys
from agno.agent import Agent
from agno.models.anthropic import Claude

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import list_projects
from workflows import execute_publishing_workflow


def create_orchestrator_agent() -> Agent:
    """
    Create the main SEO Publishing Orchestrator agent.

    This agent:
    - Presents project selection interface
    - Coordinates workflow execution
    - Reports results to user
    """
    agent = Agent(
        name="SEO Publishing Orchestrator",
        role="Coordinate Google Docs to WordPress publishing workflow",
        model=Claude(
            id="claude-sonnet-4-5-20250929",
            api_key=os.getenv("ANTHROPIC_API_KEY")
        ),
        description=(
            "You coordinate the complete SEO publishing workflow. "
            "You help users select projects and execute the publishing pipeline from Google Docs to WordPress."
        ),
        instructions=[
            "=== YOUR TASK ===",
            "Help the user publish a Google Docs document to WordPress.",
            "",
            "STEP 1: Project Selection",
            "Ask the user which project they want to use:",
            "- List all active projects from the database",
            "- Allow the user to select a project by name or ID",
            "- Offer 'no-project' option (this skips HTML transformations)",
            "",
            "STEP 2: Get Google Docs URL",
            "Ask for the Google Docs URL to publish.",
            "Remind them the document must be published to web (URL should end in /pub).",
            "",
            "STEP 3: Execute Workflow",
            "Call the publishing workflow with:",
            "- google_docs_url",
            "- project_id (or None for 'no-project')",
            "",
            "The workflow will automatically:",
            "1. Convert Google Docs to HTML",
            "2. Extract title and images",
            "3. Download and resize images",
            "4. Upload images to WordPress",
            "5. Apply HTML transformations (if project selected)",
            "6. Create WordPress post as draft",
            "",
            "STEP 4: Report Results",
            "Show the user:",
            "✅ Post title",
            "🔗 WordPress post URL (clickable link)",
            "🖼️  Number of images processed",
            "⏱️  Execution time",
            "📝 Post status (draft/publish)",
            "",
            "If there were errors, explain clearly what went wrong and suggest solutions.",
            "",
            "=== IMPORTANT ===",
            "- Be concise and clear",
            "- Always provide clickable WordPress URLs",
            "- If workflow fails, suggest troubleshooting steps",
            "- Remind users posts are created as drafts by default"
        ],
        tools=[execute_publishing_workflow],
        markdown=True,
        debug_mode=False,
        # show_tool_calls=True
    )

    return agent


def run_orchestrator(agent: Agent, initial_message: str = None) -> None:
    """
    Run the orchestrator agent interactively.

    Args:
        agent: The orchestrator agent
        initial_message: Optional initial message (defaults to prompt for action)
    """
    if not initial_message:
        initial_message = "Welcome! I can help you publish Google Docs to WordPress. Would you like to publish a document?"

    agent.print_response(initial_message, stream=True)
