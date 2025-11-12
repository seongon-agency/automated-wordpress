"""
HTML Transformer

Applies project-specific HTML transformation patterns to content.
Uses the pattern engine for regex-based transformations.
"""

from typing import Dict, Optional, Any
import sys
import os

# Add parent directory to path to import utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.pattern_engine import transform_html_with_config


def transform_html(
    html: str,
    html_configs: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Transform HTML using project's HTML configuration patterns.

    Args:
        html: Source HTML content
        html_configs: Project's html_configs dict (from database)

    Returns:
        Dict containing:
        - success: bool
        - transformed_html: str
        - patterns_applied: int
        - error: str (if failed)

    Example:
        result = transform_html(
            html="<p>Hello</p>",
            html_configs={
                "patterns": [
                    {
                        "element_type": "p",
                        "source_pattern": "<p[^>]*>(.*?)</p>",
                        "target_pattern": "<p class=\"article\">\\1</p>"
                    }
                ]
            }
        )
    """
    try:
        if not html_configs:
            # No transformation needed
            return {
                "success": True,
                "transformed_html": html,
                "patterns_applied": 0,
                "message": "No HTML configuration provided - skipped transformation"
            }

        patterns = html_configs.get('patterns', [])

        if not patterns:
            return {
                "success": True,
                "transformed_html": html,
                "patterns_applied": 0,
                "message": "No patterns in configuration - skipped transformation"
            }

        # Apply transformations
        transformed_html = transform_html_with_config(html, html_configs)

        return {
            "success": True,
            "transformed_html": transformed_html,
            "patterns_applied": len(patterns)
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"HTML transformation failed: {str(e)}",
            "transformed_html": html  # Return original on failure
        }


# Make available as Agno tool
transform_html.__annotations__ = {
    'html': str,
    'html_configs': Optional[Dict[str, Any]],
    'return': Dict[str, Any]
}
