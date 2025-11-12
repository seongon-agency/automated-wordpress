"""
Pattern Modifier - AI-powered HTML pattern modification.

Allows natural language instructions to modify existing HTML transformation patterns.
Examples:
- "Make all h2 headings blue"
- "Add a class 'highlight' to all paragraphs"
- "Remove styling from images"
- "Make links open in new tab"
"""

import os
import json
from typing import Dict, List, Any, Optional
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


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
        api_key: Anthropic API key (optional, will use env var if not provided)

    Returns:
        Dict with:
        - success: bool
        - patterns: List[Dict] - modified patterns
        - changes_made: str - description of changes
        - error: str (if failed)

    Examples:
        >>> result = modify_patterns_with_ai(
        ...     current_patterns=[...],
        ...     instruction="Make all h2 headings blue"
        ... )
        >>> print(result['changes_made'])
        "Modified h2 pattern to add color: blue style"
    """
    api_key = api_key or os.getenv('ANTHROPIC_API_KEY')

    if not api_key:
        return {
            "success": False,
            "error": "No ANTHROPIC_API_KEY found in environment"
        }

    try:
        client = Anthropic(api_key=api_key)

        # Build prompt
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

        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text.strip()

        # Remove markdown code blocks if present
        if response_text.startswith('```'):
            lines = response_text.split('\n')
            # Remove first and last lines (```json and ```)
            response_text = '\n'.join(lines[1:-1]) if len(lines) > 2 else response_text

        # Parse JSON response
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
            "error": f"Failed to parse AI response: {e}",
            "raw_response": response_text if 'response_text' in locals() else None
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"AI modification failed: {e}"
        }


def apply_instruction_to_patterns(
    html_configs: Dict[str, Any],
    instruction: str
) -> Dict[str, Any]:
    """
    High-level function to modify patterns based on instruction.

    Args:
        html_configs: Current html_configs dict with 'patterns' list
        instruction: Natural language instruction

    Returns:
        Dict with:
        - success: bool
        - html_configs: Dict - updated html_configs
        - changes_made: str
        - error: str (if failed)
    """
    if not html_configs:
        html_configs = {"patterns": []}

    current_patterns = html_configs.get('patterns', [])

    result = modify_patterns_with_ai(current_patterns, instruction)

    if not result['success']:
        return result

    # Return updated html_configs
    updated_html_configs = {
        "patterns": result['patterns']
    }

    return {
        "success": True,
        "html_configs": updated_html_configs,
        "changes_made": result['changes_made']
    }


if __name__ == "__main__":
    # Test the pattern modifier
    print("="*80)
    print("TESTING PATTERN MODIFIER")
    print("="*80)

    # Sample patterns
    test_patterns = [
        {
            "element_type": "p",
            "source_pattern": "<p[^>]*>(.*?)</p>",
            "target_pattern": "<p class=\"article-text\">\\1</p>"
        },
        {
            "element_type": "h2",
            "source_pattern": "<h2[^>]*>(.*?)</h2>",
            "target_pattern": "<h2 class=\"section-header\">\\1</h2>"
        }
    ]

    print("\nCurrent patterns:")
    print(json.dumps(test_patterns, indent=2))

    # Test instruction
    instruction = "Make all h2 headings blue"

    print(f"\nInstruction: '{instruction}'")
    print("\nProcessing with AI...")

    result = modify_patterns_with_ai(test_patterns, instruction)

    if result['success']:
        print("\n[OK] Modification successful!")
        print(f"\nChanges made: {result['changes_made']}")
        print("\nUpdated patterns:")
        print(json.dumps(result['patterns'], indent=2))
    else:
        print(f"\n[ERROR] Modification failed: {result['error']}")
