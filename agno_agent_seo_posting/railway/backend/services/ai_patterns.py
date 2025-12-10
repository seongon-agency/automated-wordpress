"""
AI Pattern Services

Uses Claude AI for pattern modification and HTML scanning.
"""

import os
import re
import json
import asyncio
import logging
from typing import Dict, Any, List

import anthropic

logger = logging.getLogger(__name__)

# Constants
AI_TIMEOUT_SECONDS = 60
MAX_HTML_LENGTH = 10000
MAX_INSTRUCTION_LENGTH = 500

# Dangerous regex patterns that can cause ReDoS
REDOS_PATTERNS = [
    r'\([^)]*\+[^)]*\)\+',  # Nested quantifiers: (a+)+
    r'\([^)]*\*[^)]*\)\*',  # Nested quantifiers: (a*)*
    r'\([^)]*\+[^)]*\)\*',  # Nested quantifiers: (a+)*
    r'\([^)]*\*[^)]*\)\+',  # Nested quantifiers: (a*)+
    r'(\.\*){3,}',          # Multiple greedy wildcards
    r'(\.\+){3,}',          # Multiple one-or-more wildcards
]


def validate_regex_pattern(pattern: str) -> tuple[bool, str]:
    """
    Validate a regex pattern for safety and correctness.

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not pattern or len(pattern) > 2000:
        return False, "Pattern is empty or too long"

    try:
        # Test if it's valid regex
        re.compile(pattern)
    except re.error as e:
        return False, f"Invalid regex: {e}"

    # Check for ReDoS patterns
    for dangerous in REDOS_PATTERNS:
        if re.search(dangerous, pattern, re.IGNORECASE):
            return False, "Pattern contains potentially dangerous nested quantifiers"

    return True, ""


def validate_patterns_list(patterns: List[Dict[str, Any]]) -> tuple[bool, str]:
    """
    Validate a list of patterns from AI response.

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(patterns, list):
        return False, "Patterns must be a list"

    if len(patterns) > 50:
        return False, "Too many patterns (max 50)"

    valid_element_types = {
        'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'div', 'span', 'a', 'img', 'ul', 'ol', 'li',
        'table', 'tr', 'td', 'th', 'thead', 'tbody',
        'blockquote', 'pre', 'code', 'strong', 'em',
        'b', 'i', 'u', 'br', 'hr', 'figure', 'figcaption',
        'section', 'article', 'header', 'footer', 'nav',
        'video', 'audio', 'iframe', 'form', 'input', 'button'
    }

    for i, pattern in enumerate(patterns):
        if not isinstance(pattern, dict):
            return False, f"Pattern {i} is not a dictionary"

        # Check required fields
        for field in ['element_type', 'source_pattern', 'target_pattern']:
            if field not in pattern:
                return False, f"Pattern {i} missing required field: {field}"
            if not isinstance(pattern[field], str):
                return False, f"Pattern {i} field '{field}' must be a string"

        # Validate element type
        element_type = pattern['element_type'].lower().strip()
        if element_type not in valid_element_types:
            return False, f"Pattern {i} has invalid element type: {element_type}"

        # Validate regex patterns
        is_valid, error = validate_regex_pattern(pattern['source_pattern'])
        if not is_valid:
            return False, f"Pattern {i} source_pattern: {error}"

        # Target pattern doesn't need regex validation but check for basic sanity
        if len(pattern['target_pattern']) > 5000:
            return False, f"Pattern {i} target_pattern is too long"

    return True, ""


def sanitize_instruction(instruction: str) -> str:
    """
    Sanitize user instruction to prevent prompt injection.
    """
    if not instruction:
        return ""

    # Truncate to max length
    instruction = instruction[:MAX_INSTRUCTION_LENGTH]

    # Remove potential prompt injection markers
    injection_markers = [
        'ignore previous',
        'ignore all previous',
        'disregard previous',
        'forget previous',
        'new instructions',
        'system:',
        'assistant:',
        'human:',
    ]

    instruction_lower = instruction.lower()
    for marker in injection_markers:
        if marker in instruction_lower:
            logger.warning(f"Potential prompt injection detected: {marker}")
            # Don't block, just log - the instruction context is limited anyway

    return instruction.strip()


async def modify_patterns_with_ai(
    current_patterns: List[Dict[str, str]],
    instruction: str
) -> Dict[str, Any]:
    """
    Modify HTML patterns using AI based on natural language instruction.

    Args:
        current_patterns: List of current patterns
        instruction: Natural language instruction

    Returns:
        Dict with modified patterns or error
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return {
            "success": False,
            "error": "ANTHROPIC_API_KEY not configured"
        }

    # Sanitize instruction
    instruction = sanitize_instruction(instruction)
    if not instruction:
        return {
            "success": False,
            "error": "Instruction is empty after sanitization"
        }

    try:
        client = anthropic.Anthropic(api_key=api_key)

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
- Only use valid HTML element types (p, h1-h6, div, span, a, img, ul, ol, li, table, etc.)
- Keep patterns simple and safe - avoid complex nested quantifiers

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
}}

Examples of modifications:

Instruction: "Make h2 headings blue"
Result: Modify h2 target_pattern to include style="color: blue;"

Instruction: "Add class 'highlight' to paragraphs"
Result: Modify p target_pattern to add or append "highlight" to class attribute

Instruction: "Remove all styling from images"
Result: Modify img target_pattern to remove style attributes

Instruction: "Make links open in new tab"
Result: Modify a target_pattern to add target="_blank"

Now process the user's instruction and return the updated patterns."""

        # Execute with timeout
        message = await asyncio.wait_for(
            asyncio.to_thread(
                client.messages.create,
                model="claude-sonnet-4-5-20250929",
                max_tokens=3000,
                messages=[{"role": "user", "content": prompt}]
            ),
            timeout=AI_TIMEOUT_SECONDS
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

        # Validate AI-generated patterns
        is_valid, error = validate_patterns_list(result['patterns'])
        if not is_valid:
            logger.warning(f"AI generated invalid patterns: {error}")
            return {
                "success": False,
                "error": f"AI generated invalid patterns: {error}"
            }

        return {
            "success": True,
            "patterns": result['patterns'],
            "changes_made": result.get('changes_made', 'Patterns modified')
        }

    except asyncio.TimeoutError:
        logger.error("AI pattern modification timed out")
        return {
            "success": False,
            "error": "AI request timed out. Please try again."
        }
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse AI response: {e}")
        return {
            "success": False,
            "error": "Failed to parse AI response"
        }
    except Exception as e:
        logger.error(f"AI modification failed: {e}", exc_info=True)
        return {
            "success": False,
            "error": "AI modification failed. Please try again."
        }


async def scan_html_for_patterns(html_content: str) -> Dict[str, Any]:
    """
    Scan HTML content and extract transformation patterns using AI.

    Args:
        html_content: Sample HTML to analyze

    Returns:
        Dict with extracted patterns or error
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return {
            "success": False,
            "error": "ANTHROPIC_API_KEY not configured"
        }

    try:
        client = anthropic.Anthropic(api_key=api_key)

        # Truncate HTML if too long
        truncated = False
        if len(html_content) > MAX_HTML_LENGTH:
            html_content = html_content[:MAX_HTML_LENGTH]
            truncated = True

        prompt = f"""You are an HTML pattern analysis expert. Analyze this HTML content and extract transformation patterns that can be used to apply similar styling to other content.

HTML Content to Analyze:
```html
{html_content}
```

Your task:
1. Identify all HTML element types used (p, h1, h2, h3, img, a, ul, ol, li, table, etc.)
2. Extract styling patterns (classes, inline styles, attributes)
3. Create regex-based transformation patterns

For each element type found, create a pattern that:
- Captures the content between tags
- Preserves the styling from the sample
- Uses regex capture groups properly

Return ONLY valid JSON in this format:
{{
  "elements_found": ["list", "of", "element", "types"],
  "patterns": [
    {{
      "element_type": "p",
      "source_pattern": "<p[^>]*>(.*?)</p>",
      "target_pattern": "<p class=\\"extracted-class\\" style=\\"extracted-style\\">\\\\1</p>",
      "description": "Paragraph with specific styling"
    }}
  ],
  "notes": "Any observations about the HTML structure"
}}

Rules:
- Use (.*?) for content capture (non-greedy)
- Use \\\\1 for replacement references (double backslash for JSON)
- Extract actual classes and styles from the HTML
- Create patterns for all significant element types
- Preserve complex attributes (data-*, custom attributes)
- Only use valid HTML element types
- Keep patterns simple - avoid complex nested quantifiers like (a+)+ or (.*)*"""

        # Execute with timeout
        message = await asyncio.wait_for(
            asyncio.to_thread(
                client.messages.create,
                model="claude-sonnet-4-5-20250929",
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            ),
            timeout=AI_TIMEOUT_SECONDS
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

        # Validate AI-generated patterns
        is_valid, error = validate_patterns_list(result['patterns'])
        if not is_valid:
            logger.warning(f"AI generated invalid patterns: {error}")
            return {
                "success": False,
                "error": f"AI generated invalid patterns: {error}"
            }

        notes = result.get('notes', '')
        if truncated:
            notes = f"HTML content was truncated to {MAX_HTML_LENGTH} characters. {notes}"

        return {
            "success": True,
            "patterns": result['patterns'],
            "elements_found": result.get('elements_found', []),
            "notes": notes
        }

    except asyncio.TimeoutError:
        logger.error("AI HTML scanning timed out")
        return {
            "success": False,
            "error": "AI request timed out. Please try again."
        }
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse AI response: {e}")
        return {
            "success": False,
            "error": "Failed to parse AI response"
        }
    except Exception as e:
        logger.error(f"AI scanning failed: {e}", exc_info=True)
        return {
            "success": False,
            "error": "AI scanning failed. Please try again."
        }
