"""
Project Configuration Editor

Edit existing project configurations:
- Update HTML transformation patterns
- Update image processing settings
- Update WordPress credentials
- Update project metadata
"""

import os
import sys
import json
from dotenv import load_dotenv

# Add parent directory to path to import src modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables from parent directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from src.database import list_projects, get_project, update_project
from src.utils.pattern_modifier import modify_patterns_with_ai


def get_input(prompt, default=None):
    """Get user input with optional default."""
    if default:
        result = input(f"{prompt} [{default}]: ").strip()
        return result if result else default
    else:
        return input(f"{prompt}: ").strip()


def get_yes_no(prompt, default='y'):
    """Get yes/no input from user."""
    result = input(f"{prompt} [{'Y/n' if default == 'y' else 'y/N'}]: ").strip().lower()
    if not result:
        return default == 'y'
    return result in ['y', 'yes']


def analyze_html_with_ai(html_sample):
    """
    Use AI to analyze HTML and extract patterns.
    Returns html_configs dict or None if failed.
    """
    import anthropic

    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("   [ERROR] No ANTHROPIC_API_KEY found")
        return None

    try:
        print("   [AI] Analyzing HTML patterns...")

        client = anthropic.Anthropic(api_key=api_key)

        prompt = f"""Analyze this HTML sample and generate transformation patterns.

HTML Sample:
```html
{html_sample}
```

For each HTML element type you find (p, h2, h3, h4, strong, em, ul, ol, li, a, img, table), generate a transformation pattern.

Return ONLY a valid JSON object in this exact format (no markdown, no explanation):
{{
  "patterns": [
    {{
      "element_type": "p",
      "source_pattern": "<p[^>]*>(.*?)</p>",
      "target_pattern": "<p class=\\"found-class\\" style=\\"found-style\\">\\\\1</p>"
    }}
  ]
}}

Important:
- Use double backslashes (\\\\1) for capture groups in JSON
- Preserve content with (.*?) in source_pattern
- Include ALL attributes found in the sample in target_pattern
- Return valid JSON only"""

        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text.strip()

        # Remove markdown code blocks if present
        if response_text.startswith('```'):
            lines = response_text.split('\n')
            response_text = '\n'.join(lines[1:-1]) if len(lines) > 2 else response_text

        patterns_data = json.loads(response_text)

        if 'patterns' in patterns_data and len(patterns_data['patterns']) > 0:
            print(f"   [OK] AI generated {len(patterns_data['patterns'])} patterns")
            return patterns_data
        else:
            print("   [ERROR] AI response missing patterns")
            return None

    except Exception as e:
        print(f"   [ERROR] AI analysis failed: {e}")
        return None


def display_html_configs(html_configs):
    """Display current HTML configurations."""
    if not html_configs or not html_configs.get('patterns'):
        print("   No HTML patterns configured")
        return

    patterns = html_configs['patterns']
    print(f"\n   Current HTML Patterns ({len(patterns)} total):")
    print("   " + "="*70)
    for i, pattern in enumerate(patterns, 1):
        print(f"\n   Pattern {i}: {pattern.get('element_type', 'unknown')}")
        print(f"   Source:  {pattern.get('source_pattern', '')[:60]}...")
        print(f"   Target:  {pattern.get('target_pattern', '')[:60]}...")
    print("\n   " + "="*70)


def display_image_configs(image_configs):
    """Display current image configurations."""
    if not image_configs:
        print("   No image configuration")
        return

    print("\n   Current Image Configuration:")
    print("   " + "="*70)
    print(f"   Width:       {image_configs.get('target_width', 'not set')}")
    print(f"   Quality:     {image_configs.get('image_quality', 'not set')}")
    print(f"   Format:      {image_configs.get('image_format', 'not set')}")
    print(f"   CSS Classes: {image_configs.get('css_classes', 'not set')}")
    print("   " + "="*70)


def edit_html_configs(project):
    """Edit HTML transformation patterns."""
    print("\n" + "="*80)
    print("EDIT HTML TRANSFORMATION PATTERNS")
    print("="*80)

    # Display current patterns
    display_html_configs(project['html_configs'])

    print("\nOptions:")
    print("  1. Modify with natural language (e.g., 'make h2 headings blue')")
    print("  2. Re-analyze HTML sample (paste new HTML)")
    print("  3. Keep current patterns (no changes)")
    print("  4. Clear all patterns")

    choice = get_input("\nSelect option (1-4)", "3")

    if choice == "1":
        # Natural language modification
        print("\n" + "-"*80)
        print("NATURAL LANGUAGE PATTERN MODIFICATION")
        print("-"*80)
        print("\nDescribe the changes you want to make. Examples:")
        print("  - 'Make all h2 headings blue'")
        print("  - 'Add class highlight to all paragraphs'")
        print("  - 'Remove styling from images'")
        print("  - 'Make links open in new tab'")
        print("  - 'Add margin-bottom: 20px to all paragraphs'")
        print("-"*80)

        instruction = get_input("\nYour instruction")

        if not instruction:
            print("[ERROR] No instruction provided, keeping current patterns")
            return None

        print(f"\n[AI] Processing instruction: '{instruction}'")

        current_patterns = project['html_configs'].get('patterns', []) if project['html_configs'] else []

        result = modify_patterns_with_ai(current_patterns, instruction)

        if result['success']:
            new_html_configs = {"patterns": result['patterns']}

            print(f"\n[OK] {result['changes_made']}")
            print("\nUpdated patterns:")
            display_html_configs(new_html_configs)

            if get_yes_no("\nSave these modified patterns?", 'y'):
                return new_html_configs
            else:
                print("[INFO] Keeping current patterns")
                return None
        else:
            print(f"[ERROR] Modification failed: {result.get('error', 'Unknown error')}")
            return None

    elif choice == "2":
        print("\n" + "-"*80)
        print("Paste your HTML sample below.")
        print("This should be an example of your target WordPress HTML structure.")
        print("Press Ctrl+Z (Windows) or Ctrl+D (Unix) then Enter when done:")
        print("-"*80)

        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            pass

        html_sample = '\n'.join(lines).strip()

        if not html_sample:
            print("[ERROR] No HTML provided, keeping current patterns")
            return None

        # Analyze with AI
        new_html_configs = analyze_html_with_ai(html_sample)

        if new_html_configs:
            print("\n[OK] New patterns generated:")
            display_html_configs(new_html_configs)

            if get_yes_no("\nSave these new patterns?", 'y'):
                return new_html_configs
            else:
                print("[INFO] Keeping current patterns")
                return None
        else:
            print("[ERROR] Failed to generate patterns, keeping current patterns")
            return None

    elif choice == "3":
        print("[INFO] No changes to HTML patterns")
        return None

    elif choice == "4":
        if get_yes_no("\nAre you sure you want to clear all patterns?", 'n'):
            return {"patterns": []}
        else:
            return None
    else:
        print("[INFO] Invalid option, no changes made")
        return None


def edit_image_configs(project):
    """Edit image processing settings."""
    print("\n" + "="*80)
    print("EDIT IMAGE PROCESSING SETTINGS")
    print("="*80)

    # Display current config
    display_image_configs(project['image_configs'])

    if not get_yes_no("\nDo you want to update image settings?", 'n'):
        return None

    current = project['image_configs'] or {}

    print("\nEnter new values (press Enter to keep current):\n")

    new_config = {}

    # Target width
    width = get_input(
        "  Target width (pixels)",
        str(current.get('target_width', 800))
    )
    try:
        new_config['target_width'] = int(width)
    except:
        new_config['target_width'] = 800

    # Image quality
    quality = get_input(
        "  Image quality (1-100)",
        str(current.get('image_quality', 92))
    )
    try:
        new_config['image_quality'] = int(quality)
    except:
        new_config['image_quality'] = 92

    # Image format
    format_choice = get_input(
        "  Image format (JPEG/PNG/WEBP)",
        current.get('image_format', 'JPEG')
    )
    new_config['image_format'] = format_choice.upper()

    # CSS classes
    css_classes = get_input(
        "  CSS classes for images",
        current.get('css_classes', 'wp-image aligncenter')
    )
    new_config['css_classes'] = css_classes

    print("\n[OK] New image configuration:")
    display_image_configs(new_config)

    if get_yes_no("\nSave these settings?", 'y'):
        return new_config
    else:
        print("[INFO] Keeping current settings")
        return None


def edit_wordpress_credentials(project):
    """Edit WordPress credentials."""
    print("\n" + "="*80)
    print("EDIT WORDPRESS CREDENTIALS")
    print("="*80)

    print(f"\nCurrent WordPress Configuration:")
    print(f"  URL:      {project['wordpress_url']}")
    print(f"  Username: {project['wordpress_username']}")
    print(f"  Password: {'*' * 20}")

    if not get_yes_no("\nDo you want to update WordPress credentials?", 'n'):
        return {}

    updates = {}

    print("\nEnter new values (press Enter to keep current):\n")

    # WordPress URL
    url = get_input("  WordPress URL", project['wordpress_url'])
    if url != project['wordpress_url']:
        updates['wordpress_url'] = url

    # Username
    username = get_input("  Username", project['wordpress_username'])
    if username != project['wordpress_username']:
        updates['wordpress_username'] = username

    # Password
    if get_yes_no("  Update password?", 'n'):
        password = get_input("  New app password")
        if password:
            updates['wordpress_app_password'] = password

    if updates:
        print(f"\n[OK] Will update {len(updates)} field(s)")
        return updates
    else:
        print("[INFO] No changes to WordPress credentials")
        return {}


def edit_project_metadata(project):
    """Edit project name and notes."""
    print("\n" + "="*80)
    print("EDIT PROJECT METADATA")
    print("="*80)

    print(f"\nCurrent:")
    print(f"  Project ID:   {project['project_id']} (cannot change)")
    print(f"  Project Name: {project['project_name']}")
    print(f"  Notes:        {project['notes'] or '(none)'}")

    if not get_yes_no("\nDo you want to update project metadata?", 'n'):
        return {}

    updates = {}

    print("\nEnter new values (press Enter to keep current):\n")

    # Project name
    name = get_input("  Project name", project['project_name'])
    if name != project['project_name']:
        updates['project_name'] = name

    # Notes
    notes = get_input("  Notes", project['notes'] or '')
    if notes != (project['notes'] or ''):
        updates['notes'] = notes

    if updates:
        print(f"\n[OK] Will update {len(updates)} field(s)")
        return updates
    else:
        print("[INFO] No changes to metadata")
        return {}


def main():
    """Main editing workflow."""
    print("="*80)
    print("PROJECT CONFIGURATION EDITOR")
    print("="*80)

    # List all projects
    print("\nLoading projects...")
    projects = list_projects(status='all')

    if not projects:
        print("\n[ERROR] No projects found. Create a project first using simple_configuration.py")
        return

    print(f"\nFound {len(projects)} project(s):")
    print("-"*80)
    for i, p in enumerate(projects, 1):
        status_icon = "[ACTIVE]" if p['status'] == 'active' else "[INACTIVE]"
        print(f"  {i}. {status_icon} {p['project_id']} - {p['project_name']}")
    print("-"*80)

    # Select project
    try:
        selection = int(get_input(f"\nSelect project number (1-{len(projects)})", "1"))
        if selection < 1 or selection > len(projects):
            print("[ERROR] Invalid selection")
            return
        selected_project_id = projects[selection - 1]['project_id']
    except ValueError:
        print("[ERROR] Invalid input")
        return

    # Load full project
    project = get_project(selected_project_id)

    print(f"\n[OK] Loaded project: {project['project_name']}")

    # Main editing loop
    while True:
        print("\n" + "="*80)
        print(f"EDITING: {project['project_name']} ({project['project_id']})")
        print("="*80)

        print("\nWhat would you like to edit?")
        print("  1. HTML transformation patterns")
        print("  2. Image processing settings")
        print("  3. WordPress credentials")
        print("  4. Project metadata (name, notes)")
        print("  5. View current configuration")
        print("  6. Done (save and exit)")
        print("  0. Cancel (exit without saving)")

        choice = get_input("\nSelect option (0-6)", "6")

        if choice == "1":
            new_html_configs = edit_html_configs(project)
            if new_html_configs is not None:
                print("\n[OK] Updating HTML patterns in database...")
                project = update_project(project['project_id'], html_configs=new_html_configs)
                print("[OK] HTML patterns updated successfully")

        elif choice == "2":
            new_image_configs = edit_image_configs(project)
            if new_image_configs:
                print("\n[OK] Updating image settings in database...")
                project = update_project(project['project_id'], image_configs=new_image_configs)
                print("[OK] Image settings updated successfully")

        elif choice == "3":
            updates = edit_wordpress_credentials(project)
            if updates:
                print("\n[OK] Updating WordPress credentials in database...")
                project = update_project(project['project_id'], **updates)
                print("[OK] WordPress credentials updated successfully")

        elif choice == "4":
            updates = edit_project_metadata(project)
            if updates:
                print("\n[OK] Updating project metadata in database...")
                project = update_project(project['project_id'], **updates)
                print("[OK] Project metadata updated successfully")

        elif choice == "5":
            print("\n" + "="*80)
            print("CURRENT CONFIGURATION")
            print("="*80)
            print(f"\nProject: {project['project_name']} ({project['project_id']})")
            print(f"Status: {project['status']}")
            print(f"WordPress: {project['wordpress_url']}")
            display_html_configs(project['html_configs'])
            display_image_configs(project['image_configs'])
            print(f"\nNotes: {project['notes'] or '(none)'}")
            print("\n" + "="*80)
            input("\nPress Enter to continue...")

        elif choice == "6":
            print("\n[OK] All changes saved!")
            break

        elif choice == "0":
            print("\n[INFO] Exiting without additional changes")
            break

        else:
            print("[ERROR] Invalid option")

    print("\n" + "="*80)
    print("EDIT COMPLETE")
    print("="*80)
    print(f"\nProject '{project['project_name']}' is ready to use.")
    print("Run test_full_workflow.py or main.py to publish content.\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INFO] Editing cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
