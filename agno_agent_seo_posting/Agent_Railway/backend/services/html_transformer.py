"""
HTML Transformer

Applies project-specific HTML transformation patterns to content.
Uses the pattern engine for regex-based transformations.
"""

from typing import Dict, Optional, Any
from ..utils.pattern_engine import transform_html_with_config


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
    """
    try:
        if not html_configs:
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
            "transformed_html": html
        }
