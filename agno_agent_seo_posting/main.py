"""
SEO Publishing System - Main Entry Point

Multi-project SEO publishing system with AI-powered HTML configuration.
Publishes Google Docs to WordPress with project-specific transformations.
"""

import os
import sys
import dotenv

# Load environment variables
dotenv.load_dotenv()

from database import init_database, list_projects
# Agents removed - using direct workflow execution instead to avoid httpx errors
# from agents.orchestrator import create_orchestrator_agent, run_orchestrator
# from agents.configuration_agent import create_configuration_agent, run_configuration_workflow
from simple_configuration import run_simple_configuration


def display_banner():
    """Display application banner."""
    print("\n" + "="*80)
    print("🚀 SEO PUBLISHING SYSTEM - MVP v1.0")
    print("="*80)
    print("\nAutomated Google Docs → WordPress Publishing")
    print("with AI-Powered Project Configuration\n")
    print("="*80 + "\n")


def display_menu():
    """Display main menu."""
    print("\n📋 MAIN MENU")
    print("-" * 40)
    print("1. 📤 Publish Google Docs to WordPress")
    print("2. 🔧 Configure New Project")
    print("3. 📁 List All Projects")
    print("4. 🚪 Exit")
    print("-" * 40)


def list_all_projects():
    """List all configured projects."""
    print("\n📁 CONFIGURED PROJECTS")
    print("="*80)

    projects = list_projects(status='all')

    if not projects:
        print("\nNo projects configured yet.")
        print("Use 'Configure New Project' to add one.\n")
        return

    for project in projects:
        print(f"\n🔸 {project['project_name']}")
        print(f"   ID: {project['project_id']}")
        print(f"   WordPress: {project['wordpress_url']}")
        print(f"   Status: {project['status']}")
        print(f"   HTML Patterns: {len(project.get('html_configs', {}).get('patterns', [])) if project.get('html_configs') else 0}")
        print(f"   Image Width: {project.get('image_configs', {}).get('target_width', 'default') if project.get('image_configs') else 'default'}")

    print("\n" + "="*80)


def main():
    """Main application entry point."""
    display_banner()

    # Initialize database
    print("Initializing database...")
    init_database()
    print("✓ Database ready\n")

    # Don't create agents at startup - create them when needed to avoid httpx errors
    orchestrator = None

    while True:
        display_menu()

        try:
            choice = input("\nSelect an option (1-4): ").strip()

            if choice == '1':
                # Publish workflow
                print("\n" + "="*80)
                print("📤 PUBLISH WORKFLOW")
                print("="*80 + "\n")

                # First, show available projects
                projects = list_projects(status='active')

                if projects:
                    print("Available projects:")
                    for idx, project in enumerate(projects, 1):
                        print(f"  {idx}. {project['project_name']} ({project['project_id']})")
                    print(f"  {len(projects) + 1}. No project (skip transformations)")
                else:
                    print("No projects configured. You can still publish without transformations.")

                # Get project selection
                print("\nSelect project number (or press Enter for no project):")
                project_choice = input("> ").strip()

                project_id = None
                if project_choice and project_choice.isdigit():
                    idx = int(project_choice) - 1
                    if 0 <= idx < len(projects):
                        project_id = projects[idx]['project_id']
                        print(f"✓ Selected: {projects[idx]['project_name']}")

                if not project_id:
                    print("✓ No project selected - will use default settings")

                # Get Google Docs URL
                print("\nEnter Google Docs URL:")
                docs_url = input("> ").strip()

                if not docs_url:
                    print("❌ No URL provided. Cancelled.\n")
                    continue

                # Execute workflow directly without agent
                print("\n" + "="*80)
                print("EXECUTING PUBLISHING WORKFLOW")
                print("="*80)

                try:
                    from workflows.publishing_workflow import execute_publishing_workflow

                    result = execute_publishing_workflow(
                        google_docs_url=docs_url,
                        project_id=project_id
                    )

                    if result['success']:
                        print("\n" + "="*80)
                        print("✅ PUBLISHING COMPLETED SUCCESSFULLY!")
                        print("="*80)
                        print(f"\n📌 Post Title: {result['post_title']}")
                        print(f"🔗 Post URL: {result['post_url']}")
                        print(f"🖼️  Images: {result['images_processed']}")
                        print(f"⏱️  Time: {result['execution_time']:.2f}s\n")
                    else:
                        print("\n" + "="*80)
                        print("❌ PUBLISHING FAILED")
                        print("="*80)
                        print(f"\nError: {result.get('error', 'Unknown error')}")
                        print(f"Failed at: {result.get('step_failed', 'Unknown step')}\n")

                except Exception as e:
                    print("\n" + "="*80)
                    print("❌ EXCEPTION OCCURRED")
                    print("="*80)
                    print(f"\nError: {str(e)}\n")
                    import traceback
                    traceback.print_exc()

            elif choice == '2':
                # Configuration workflow
                run_simple_configuration()

            elif choice == '3':
                # List projects
                list_all_projects()

            elif choice == '4':
                # Exit
                print("\n👋 Goodbye!\n")
                break

            else:
                print("\n❌ Invalid option. Please select 1-4.\n")

        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
