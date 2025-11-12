"""
Simple Configuration Wizard (Non-Agent Based)

A straightforward CLI wizard for configuring new projects without AI agent complexity.
"""

import os
import sys
import json
from dotenv import load_dotenv

load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import create_project


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


def analyze_html_sample_with_ai(html_sample):
    """
    Use AI (one-shot call, no streaming) to analyze HTML and extract patterns.
    Falls back to simple analysis if AI fails.
    """
    import anthropic

    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("   ⚠️  No ANTHROPIC_API_KEY found - using simple analysis")
        return analyze_html_sample_simple(html_sample)

    try:
        print("   🤖 Using AI to analyze HTML patterns...")

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
- Use double backslashes (\\\\1) for capture groups
- Preserve content with (.*?) in source_pattern
- Include ALL attributes found in the sample in target_pattern
- Return valid JSON only"""

        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text.strip()

        # Try to parse JSON
        import json

        # Remove markdown code blocks if present
        if response_text.startswith('```'):
            lines = response_text.split('\n')
            response_text = '\n'.join(lines[1:-1]) if len(lines) > 2 else response_text

        patterns_data = json.loads(response_text)

        if 'patterns' in patterns_data and len(patterns_data['patterns']) > 0:
            print(f"   ✅ AI generated {len(patterns_data['patterns'])} patterns")
            for pattern in patterns_data['patterns']:
                print(f"      - {pattern['element_type']}")
            return patterns_data
        else:
            print("   ⚠️  AI returned empty patterns - using simple analysis")
            return analyze_html_sample_simple(html_sample)

    except Exception as e:
        print(f"   ⚠️  AI analysis failed ({str(e)}) - using simple analysis")
        return analyze_html_sample_simple(html_sample)


def analyze_html_sample_simple(html_sample):
    """
    Simple HTML analysis to extract patterns (fallback when AI not available).
    """
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html_sample, 'html.parser')
    patterns = []

    # Find all unique tags
    tags_found = set()
    for tag in soup.find_all():
        tags_found.add(tag.name)

    print(f"\n   Found these HTML elements: {', '.join(sorted(tags_found))}")

    # Generate basic patterns for common elements
    element_mapping = {
        'p': ('paragraph', '<p[^>]*>(.*?)</p>'),
        'h2': ('heading 2', '<h2[^>]*>(.*?)</h2>'),
        'h3': ('heading 3', '<h3[^>]*>(.*?)</h3>'),
        'h4': ('heading 4', '<h4[^>]*>(.*?)</h4>'),
        'strong': ('bold/strong', '<(b|strong)[^>]*>(.*?)</(b|strong)>'),
        'em': ('italic/emphasis', '<(em|i)[^>]*>(.*?)</(em|i)>'),
        'ul': ('unordered list', '<ul[^>]*>(.*?)</ul>'),
        'ol': ('ordered list', '<ol[^>]*>(.*?)</ol>'),
        'li': ('list item', '<li[^>]*>(.*?)</li>'),
        'a': ('link', '<a[^>]*>(.*?)</a>'),
        'img': ('image', '<img[^>]*>'),
        'table': ('table', '<table[^>]*>(.*?)</table>'),
    }

    for tag in sorted(tags_found):
        if tag in element_mapping:
            # Find first occurrence to get attributes
            first_tag = soup.find(tag)
            if first_tag:
                # Get all attributes as string
                attrs = []
                for key, value in first_tag.attrs.items():
                    if isinstance(value, list):
                        value = ' '.join(value)
                    attrs.append(f'{key}="{value}"')

                attr_string = ' ' + ' '.join(attrs) if attrs else ''

                # For self-closing tags like img
                if tag == 'img':
                    target_pattern = f'<{tag}{attr_string}>'
                else:
                    target_pattern = f'<{tag}{attr_string}>\\1</{tag}>'

                patterns.append({
                    "element_type": tag,
                    "source_pattern": element_mapping[tag][1],
                    "target_pattern": target_pattern
                })

                print(f"   ✓ Pattern for {element_mapping[tag][0]}: {tag}{attr_string}")

    return {"patterns": patterns}


def run_simple_configuration():
    """Run the simple configuration wizard."""
    print("\n" + "="*80)
    print("🔧 PROJECT CONFIGURATION WIZARD (SIMPLE MODE)")
    print("="*80)
    print("\nThis wizard will help you configure a new project.")
    print("Press Ctrl+C at any time to cancel.\n")

    try:
        # STEP 1: Basic Information
        print("="*80)
        print("STEP 1: BASIC INFORMATION")
        print("="*80)

        project_id = get_input("\n1. Project ID (slug format, e.g., 'client_2025')")
        if not project_id:
            print("❌ Project ID is required.")
            return

        project_name = get_input("2. Project Name (e.g., 'Client Blog')")
        if not project_name:
            print("❌ Project Name is required.")
            return

        wordpress_url = get_input("3. WordPress URL", os.getenv('WP_BASE_URL', 'https://'))
        if not wordpress_url:
            print("❌ WordPress URL is required.")
            return

        wordpress_username = get_input("4. WordPress Username", os.getenv('WP_USERNAME', ''))
        if not wordpress_username:
            print("❌ WordPress Username is required.")
            return

        wordpress_app_password = get_input("5. WordPress Application Password", os.getenv('WP_APP_PASS', ''))
        if not wordpress_app_password:
            print("❌ WordPress Application Password is required.")
            return

        notes = get_input("6. Notes (optional)")

        # STEP 2: Image Configuration
        print("\n" + "="*80)
        print("STEP 2: IMAGE CONFIGURATION")
        print("="*80)

        target_width = int(get_input("\n1. Target image width in pixels", "800"))
        image_quality = int(get_input("2. Image quality (1-100)", "92"))
        image_format = get_input("3. Image format (JPEG/PNG/WEBP)", "JPEG").upper()
        css_classes = get_input("4. CSS classes for images", "wp-image aligncenter")
        alignment = get_input("5. Image alignment (left/center/right)", "center")

        image_configs = {
            "target_width": target_width,
            "target_height": None,
            "image_quality": image_quality,
            "image_format": image_format,
            "css_classes": css_classes,
            "alignment": alignment,
            "additional_attributes": {
                "loading": "lazy"
            }
        }

        # STEP 3: HTML Template Analysis
        print("\n" + "="*80)
        print("STEP 3: HTML TEMPLATE ANALYSIS")
        print("="*80)

        print("\nPaste a sample of your desired HTML output.")
        print("Include examples of paragraphs, headings, lists, etc.")
        print("(Press Enter twice when done, or type 'SKIP' to skip HTML patterns)\n")

        html_lines = []
        empty_count = 0
        while True:
            line = input()
            if line.strip().upper() == 'SKIP':
                html_lines = []
                break
            if not line:
                empty_count += 1
                if empty_count >= 2:
                    break
            else:
                empty_count = 0
                html_lines.append(line)

        html_configs = None
        if html_lines:
            html_sample = '\n'.join(html_lines)
            print("\n   Analyzing HTML sample...")
            html_configs = analyze_html_sample_with_ai(html_sample)
            print(f"\n   ✓ Generated {len(html_configs.get('patterns', []))} transformation patterns")
        else:
            print("\n   ⚠️  Skipped HTML analysis - no patterns will be applied")

        # STEP 4: Review
        print("\n" + "="*80)
        print("STEP 4: REVIEW CONFIGURATION")
        print("="*80)

        print(f"\n📋 Basic Information:")
        print(f"   Project ID: {project_id}")
        print(f"   Project Name: {project_name}")
        print(f"   WordPress URL: {wordpress_url}")
        print(f"   WordPress Username: {wordpress_username}")
        print(f"   WordPress App Password: {'*' * 20}")
        if notes:
            print(f"   Notes: {notes}")

        print(f"\n🖼️  Image Configuration:")
        print(f"   Target Width: {target_width}px")
        print(f"   Quality: {image_quality}")
        print(f"   Format: {image_format}")
        print(f"   CSS Classes: {css_classes}")
        print(f"   Alignment: {alignment}")

        print(f"\n🔄 HTML Configuration:")
        if html_configs:
            print(f"   Patterns: {len(html_configs.get('patterns', []))}")
            print(f"   Elements: {', '.join([p['element_type'] for p in html_configs.get('patterns', [])])}")
        else:
            print(f"   Patterns: None (will use default HTML)")

        # STEP 5: Confirmation and Save
        print("\n" + "="*80)
        print("STEP 5: SAVE CONFIGURATION")
        print("="*80)

        if not get_yes_no("\nSave this configuration?", 'y'):
            print("\n❌ Configuration cancelled.\n")
            return

        # Save to database
        print("\n   Saving to database...")

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

        print("\n" + "="*80)
        print("✅ PROJECT SAVED SUCCESSFULLY!")
        print("="*80)
        print(f"\n📌 Project ID: {project_id}")
        print(f"📌 Project Name: {project_name}")
        print("\nYou can now use this project when publishing Google Docs to WordPress.")
        print("Select 'Publish' from the main menu and choose this project.\n")
        print("="*80 + "\n")

    except KeyboardInterrupt:
        print("\n\n❌ Configuration cancelled.\n")
    except Exception as e:
        print(f"\n\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_simple_configuration()
