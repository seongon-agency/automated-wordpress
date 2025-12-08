"""
AI Pattern Services - Claude-powered HTML pattern generation and modification.

Provides two main features:
1. Generate patterns from HTML template
2. Modify patterns with natural language instructions
"""

import os
import json
from typing import Dict, List, Any, Optional
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


def get_api_key() -> str:
    """Get Anthropic API key from environment."""
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        raise ValueError("ANTHROPIC_API_KEY not found in environment")
    return key


def modify_patterns_with_ai(
    current_patterns: List[Dict[str, str]],
    instruction: str,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Modify HTML patterns using natural language instructions.

    Args:
        current_patterns: List of existing patterns
        instruction: Natural language description of changes
        api_key: Anthropic API key (optional)

    Returns:
        Dict with:
        - success: bool
        - patterns: List[Dict] - modified patterns
        - changes_made: str - description of changes
        - error: str (if failed)
    """
    api_key = api_key or get_api_key()

    try:
        client = Anthropic(api_key=api_key)

        current_patterns_json = json.dumps(current_patterns, indent=2)

        prompt = f"""You are an HTML pattern modification assistant. You help modify HTML transformation patterns based on user instructions.

Current Patterns:
```json
{current_patterns_json}
```

User Instruction:
"{instruction}"

Your task:
1. Analyze the user's instruction
2. Modify, add, or delete patterns as needed
3. Return the updated patterns

Rules:
- Preserve existing patterns unless instruction says to change/remove them
- When modifying a pattern, update only what the instruction specifies
- Use proper regex patterns with (.*?) for content capture
- Use \\\\1, \\\\2, etc. for capture group references (double backslash for JSON)
- For styles, add them to existing style attributes or create new ones
- For classes, add to existing class list or create new class attribute
- Preserve all unmodified attributes

Return ONLY valid JSON in this format (no markdown, no explanation):
{{
  "changes_made": "Brief description of changes",
  "patterns": [
    {{
      "element_type": "element_name",
      "source_pattern": "regex pattern",
      "target_pattern": "replacement pattern"
    }}
  ]
}}"""

        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text.strip()

        # Remove markdown code blocks if present
        if response_text.startswith('```'):
            lines = response_text.split('\n')
            response_text = '\n'.join(lines[1:-1]) if len(lines) > 2 else response_text

        result = json.loads(response_text)

        if 'patterns' not in result:
            return {
                "success": False,
                "error": "AI response missing 'patterns' field"
            }

        return {
            "success": True,
            "patterns": result['patterns'],
            "changes_made": result.get('changes_made', 'Patterns modified')
        }

    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": f"Failed to parse AI response: {e}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"AI modification failed: {e}"
        }


def generate_patterns_from_template(
    source_html: str,
    target_html: str,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate HTML transformation patterns by analyzing source and target HTML.

    Args:
        source_html: Original HTML (e.g., from Google Docs)
        target_html: Desired HTML format (template)
        api_key: Anthropic API key (optional)

    Returns:
        Dict with:
        - success: bool
        - patterns: List[Dict] - generated patterns
        - analysis: str - description of patterns
        - error: str (if failed)
    """
    api_key = api_key or get_api_key()

    try:
        client = Anthropic(api_key=api_key)

        prompt = f"""You are an HTML pattern generator. Analyze the source and target HTML to create transformation patterns.

SOURCE HTML (original format):
```html
{source_html[:5000]}
```

TARGET HTML (desired format):
```html
{target_html[:5000]}
```

Your task:
1. Identify all HTML elements in the source that need transformation
2. Compare them with the target format
3. Create regex patterns to transform source into target

Rules:
- Create patterns for: p, h1, h2, h3, h4, h5, h6, ul, ol, li, a, img, table, tr, td, th, blockquote
- Use (.*?) to capture content between tags
- Use \\\\1, \\\\2 for capture group references in target_pattern
- Handle both class and style attributes
- Preserve content while changing structure

Return ONLY valid JSON:
{{
  "analysis": "Brief description of what patterns do",
  "patterns": [
    {{
      "element_type": "p",
      "source_pattern": "<p[^>]*>(.*?)</p>",
      "target_pattern": "<p class=\\"article\\">\\\\1</p>"
    }}
  ]
}}"""

        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text.strip()

        # Remove markdown code blocks if present
        if response_text.startswith('```'):
            lines = response_text.split('\n')
            response_text = '\n'.join(lines[1:-1]) if len(lines) > 2 else response_text

        result = json.loads(response_text)

        if 'patterns' not in result:
            return {
                "success": False,
                "error": "AI response missing 'patterns' field"
            }

        return {
            "success": True,
            "patterns": result['patterns'],
            "analysis": result.get('analysis', 'Patterns generated')
        }

    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": f"Failed to parse AI response: {e}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Pattern generation failed: {e}"
        }
