"""
Pattern Analyzer Tool

AI-powered tool for analyzing HTML templates and generating transformation patterns.
This is designed to be used by an Agno agent (Claude) to extract patterns from sample HTML.
"""

from typing import Dict, Any
import json


def analyze_html_template_for_patterns(sample_html: str) -> str:
    """
    Analyze a sample HTML template to extract transformation patterns.

    This function returns instructions for an AI agent (Claude) to analyze the HTML.
    The agent will identify patterns and return them in the required JSON format.

    Args:
        sample_html: Sample HTML from the project's desired output format

    Returns:
        Formatted instruction string for the AI agent

    Note: This is a placeholder that will be called by the Configuration Agent.
    The actual analysis will be done by Claude using reasoning.
    """
    instruction = f"""
You are analyzing an HTML template to extract transformation patterns.

**Your Task:**
Examine the following HTML sample and identify patterns for these element types:
- Paragraphs (<p>)
- Headings (<h2>, <h3>, <h4>)
- Bold/Strong (<b>, <strong>)
- Emphasis (<em>, <i>)
- Lists (<ul>, <ol>, <li>)
- Tables (<table>, <tr>, <td>)
- Images (<img>)
- Links (<a>)

**HTML Sample:**
```html
{sample_html}
```

**Instructions:**
1. For each element type found in the sample, identify:
   - The complete HTML pattern (including all attributes and classes)
   - Common attributes (class, style, dir, etc.)

2. Generate regex patterns that will transform plain Google Docs HTML into this format.

3. Return a JSON object with this structure:
```json
{{
  "patterns": [
    {{
      "element_type": "p",
      "source_pattern": "<p[^>]*>(.*?)</p>",
      "target_pattern": "<p class=\\"found-class\\" style=\\"found-style\\">\\\\1</p>"
    }}
  ]
}}
```

**Important:**
- Use double backslashes (\\\\1) for regex capture groups in JSON
- Preserve content with capture group (.*?)
- Include all discovered attributes in target_pattern
- Be thorough - analyze ALL element types present

Return ONLY the JSON object, nothing else.
    """

    return instruction


def create_image_config_from_preferences(
    target_width: int = 800,
    image_quality: int = 92,
    image_format: str = "JPEG",
    css_classes: str = "",
    alignment: str = "center"
) -> Dict[str, Any]:
    """
    Create image_configs JSON from user preferences.

    Args:
        target_width: Target image width in pixels
        image_quality: JPEG quality 1-100
        image_format: Image format (JPEG, PNG, WEBP)
        css_classes: CSS classes to add to <img> tags
        alignment: Image alignment (left, center, right)

    Returns:
        Dict ready to be stored as image_configs JSON
    """
    return {
        "target_width": target_width,
        "target_height": None,  # Maintain aspect ratio
        "image_quality": image_quality,
        "image_format": image_format,
        "css_classes": css_classes,
        "alignment": alignment,
        "additional_attributes": {
            "loading": "lazy"  # Default to lazy loading
        }
    }


# Make available as Agno tools
analyze_html_template_for_patterns.__annotations__ = {
    'sample_html': str,
    'return': str
}

create_image_config_from_preferences.__annotations__ = {
    'target_width': int,
    'image_quality': int,
    'image_format': str,
    'css_classes': str,
    'alignment': str,
    'return': Dict[str, Any]
}
