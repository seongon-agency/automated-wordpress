"""
Automatic Client Configuration Generator

Analyzes example HTML (before/after) and generates client transformation rules.
This uses AI once to create the config, then all future posts use the config (no tokens).
"""

from bs4 import BeautifulSoup, Tag
import re
from typing import Dict, List, Tuple, Any
import json


def analyze_html_differences(original_html: str, desired_html: str) -> Dict[str, Any]:
    """
    Analyze differences between original and desired HTML.

    Args:
        original_html: HTML from Google Docs (before transformation)
        desired_html: HTML the client needs (after transformation)

    Returns:
        Dictionary with detected transformation patterns
    """
    orig_soup = BeautifulSoup(original_html, 'html.parser')
    desired_soup = BeautifulSoup(desired_html, 'html.parser')

    transformations = {
        "tag_replacements": {},
        "attribute_rules": {},
        "style_injections": {},
        "class_mappings": {},
        "custom_wrappers": []
    }

    # Analyze tag replacements
    tag_replacements = _analyze_tag_replacements(orig_soup, desired_soup)
    transformations["tag_replacements"] = tag_replacements

    # Analyze attribute changes
    attribute_rules = _analyze_attribute_changes(orig_soup, desired_soup)
    transformations["attribute_rules"] = attribute_rules

    # Analyze class mappings
    class_mappings = _analyze_class_mappings(orig_soup, desired_soup)
    transformations["class_mappings"] = class_mappings

    # Analyze wrappers
    wrappers = _analyze_wrappers(orig_soup, desired_soup)
    transformations["custom_wrappers"] = wrappers

    return transformations


def _analyze_tag_replacements(orig_soup: BeautifulSoup, desired_soup: BeautifulSoup) -> Dict:
    """Detect tag name changes."""
    replacements = {}

    # Get all original tags
    orig_tags = {}
    for tag in orig_soup.find_all(True):
        content = tag.get_text(strip=True)
        if content:
            if tag.name not in orig_tags:
                orig_tags[tag.name] = []
            orig_tags[tag.name].append({
                'content': content,
                'tag': tag
            })

    # Match with desired tags
    desired_tags = {}
    for tag in desired_soup.find_all(True):
        content = tag.get_text(strip=True)
        if content:
            if tag.name not in desired_tags:
                desired_tags[tag.name] = []
            desired_tags[tag.name].append({
                'content': content,
                'tag': tag
            })

    # Find tag replacements by matching content
    for orig_name, orig_items in orig_tags.items():
        for orig_item in orig_items:
            content = orig_item['content']

            # Look for this content in desired HTML
            for desired_name, desired_items in desired_tags.items():
                for desired_item in desired_items:
                    if desired_item['content'] == content and orig_name != desired_name:
                        # Tag was replaced
                        if orig_name not in replacements:
                            replacements[orig_name] = {
                                "new_tag": desired_name,
                                "preserve_content": True
                            }

                            # Check if classes were added
                            desired_classes = desired_item['tag'].get('class', [])
                            if desired_classes:
                                replacements[orig_name]["add_class"] = " ".join(desired_classes)

    return replacements


def _analyze_attribute_changes(orig_soup: BeautifulSoup, desired_soup: BeautifulSoup) -> Dict:
    """Detect attribute additions/changes."""
    rules = {}

    # Match tags by content
    for orig_tag in orig_soup.find_all(True):
        content = orig_tag.get_text(strip=True)
        if not content:
            continue

        # Find matching tag in desired HTML (same content, same tag name)
        for desired_tag in desired_soup.find_all(orig_tag.name):
            if desired_tag.get_text(strip=True) == content:
                # Compare attributes
                orig_classes = set(orig_tag.get('class', []))
                desired_classes = set(desired_tag.get('class', []))
                new_classes = desired_classes - orig_classes

                orig_style = orig_tag.get('style', '')
                desired_style = desired_tag.get('style', '')

                if new_classes or (desired_style and desired_style != orig_style):
                    if orig_tag.name not in rules:
                        rules[orig_tag.name] = {}

                    if new_classes:
                        rules[orig_tag.name]["add_class"] = " ".join(new_classes)

                    if desired_style and desired_style != orig_style:
                        # Extract new styles
                        rules[orig_tag.name]["add_style"] = desired_style

                # Check for other attributes
                for attr, value in desired_tag.attrs.items():
                    if attr not in ['class', 'style'] and attr not in orig_tag.attrs:
                        if orig_tag.name not in rules:
                            rules[orig_tag.name] = {}
                        if "add_attribute" not in rules[orig_tag.name]:
                            rules[orig_tag.name]["add_attribute"] = {}
                        rules[orig_tag.name]["add_attribute"][attr] = value

                break

    return rules


def _analyze_class_mappings(orig_soup: BeautifulSoup, desired_soup: BeautifulSoup) -> Dict:
    """Detect class name replacements."""
    mappings = {}

    for orig_tag in orig_soup.find_all(class_=True):
        content = orig_tag.get_text(strip=True)
        if not content:
            continue

        orig_classes = set(orig_tag.get('class', []))

        # Find matching tag in desired HTML
        for desired_tag in desired_soup.find_all(orig_tag.name):
            if desired_tag.get_text(strip=True) == content:
                desired_classes = set(desired_tag.get('class', []))

                # Check if classes were replaced (not just added)
                if orig_classes and desired_classes and orig_classes != desired_classes:
                    # Classes that disappeared
                    removed_classes = orig_classes - desired_classes
                    # Classes that appeared
                    new_classes = desired_classes - orig_classes

                    # If there's a 1-to-1 or 1-to-many mapping
                    if removed_classes and new_classes:
                        for old_class in removed_classes:
                            mappings[old_class] = " ".join(new_classes)

                break

    return mappings


def _analyze_wrappers(orig_soup: BeautifulSoup, desired_soup: BeautifulSoup) -> List[Dict]:
    """Detect custom wrapper structures."""
    wrappers = []

    # Look for tags that are wrapped in additional HTML in desired version
    for orig_tag in orig_soup.find_all(True):
        content = orig_tag.get_text(strip=True)
        if not content:
            continue

        # Find this content in desired HTML
        for desired_tag in desired_soup.find_all(True):
            if desired_tag.get_text(strip=True) == content:
                # Check if it's wrapped in a parent that doesn't exist in original
                desired_parent = desired_tag.parent

                if desired_parent and desired_parent.name != orig_tag.parent.name:
                    # This tag is wrapped in something new
                    wrapper_config = {
                        "wrap_tag": orig_tag.name,
                        "wrapper": f"<{desired_parent.name}>" + "{content}" + f"</{desired_parent.name}>"
                    }

                    # Add wrapper classes if any
                    if desired_parent.get('class'):
                        wrapper_config["wrapper"] = f"<{desired_parent.name} class='{' '.join(desired_parent.get('class'))}'>" + "{content}" + f"</{desired_parent.name}>"

                    # Only add if not duplicate
                    if wrapper_config not in wrappers:
                        wrappers.append(wrapper_config)

                break

    return wrappers


def generate_client_config(
    client_name: str,
    client_id: str,
    description: str,
    original_html: str,
    desired_html: str
) -> str:
    """
    Generate a complete client configuration from HTML examples.

    Args:
        client_name: Display name for the client
        client_id: Unique identifier (e.g., 'client-xyz')
        description: Description of what this client needs
        original_html: HTML from Google Docs
        desired_html: HTML the client needs

    Returns:
        Python code string to add to client_configs.py
    """
    # Analyze differences
    transformations = analyze_html_differences(original_html, desired_html)

    # Generate Python code
    config_code = f'''
# Auto-generated configuration for {client_name}
CLIENT_{client_id.upper().replace('-', '_')} = {{
    "name": "{client_name}",
    "description": "{description}",
    "transformations": {json.dumps(transformations, indent=8)}
}}

# Add to registry
CLIENT_REGISTRY["{client_id}"] = CLIENT_{client_id.upper().replace('-', '_')}
'''

    return config_code


def save_client_config(config_code: str) -> bool:
    """
    Append generated config to client_configs.py

    Args:
        config_code: Python code to append

    Returns:
        True if successful
    """
    try:
        config_file = "client_configs.py"

        with open(config_file, 'a', encoding='utf-8') as f:
            f.write('\n\n')
            f.write(config_code)

        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False


# For agent to use
def create_client_from_examples(
    client_name: str,
    client_id: str,
    description: str,
    original_html: str,
    desired_html: str
) -> dict:
    """
    Main function for agent to create a new client configuration.

    Args:
        client_name: Display name (e.g., "ABC Company")
        client_id: Unique ID (e.g., "abc-company")
        description: What customizations are needed
        original_html: Example HTML from Google Docs
        desired_html: Example HTML the client wants

    Returns:
        dict with success status and generated config
    """
    try:
        # Generate config
        config_code = generate_client_config(
            client_name,
            client_id,
            description,
            original_html,
            desired_html
        )

        # Save to file
        success = save_client_config(config_code)

        if success:
            return {
                "success": True,
                "client_id": client_id,
                "client_name": client_name,
                "message": f"Client '{client_name}' created successfully! Use client_id '{client_id}' when publishing.",
                "config_preview": config_code
            }
        else:
            return {
                "success": False,
                "error": "Failed to save configuration file"
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# Test function
if __name__ == "__main__":
    # Example usage
    original = """
    <h2>Heading</h2>
    <p>Text with <strong>bold</strong> word.</p>
    """

    desired = """
    <h2 class="custom-heading" style="color: red;">Heading</h2>
    <p class="content">Text with <b class="fw-bold">bold</b> word.</p>
    """

    result = create_client_from_examples(
        client_name="Test Client",
        client_id="test-client",
        description="Test configuration",
        original_html=original,
        desired_html=desired
    )

    print(json.dumps(result, indent=2))
