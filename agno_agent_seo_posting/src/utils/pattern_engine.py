"""
Pattern Engine

Core regex-based HTML transformation logic.
Applies transformation patterns from project configurations.
"""

import re
from typing import Dict, List, Any


def apply_pattern(html: str, pattern: Dict[str, str]) -> str:
    """
    Apply a single transformation pattern to HTML.

    Args:
        html: HTML content
        pattern: Dict with element_type, source_pattern, target_pattern

    Returns:
        Transformed HTML
    """
    source_pattern = pattern.get('source_pattern', '')
    target_pattern = pattern.get('target_pattern', '')

    if not source_pattern or not target_pattern:
        return html

    try:
        # Apply regex substitution
        transformed = re.sub(
            source_pattern,
            target_pattern,
            html,
            flags=re.IGNORECASE | re.DOTALL
        )
        return transformed

    except re.error as e:
        # If regex is invalid, return original HTML
        print(f"⚠️  Invalid regex pattern for {pattern.get('element_type', 'unknown')}: {e}")
        return html


def apply_all_patterns(html: str, patterns: List[Dict[str, str]]) -> str:
    """
    Apply all transformation patterns sequentially.

    Args:
        html: HTML content
        patterns: List of pattern dicts from html_configs

    Returns:
        Fully transformed HTML
    """
    transformed_html = html

    for pattern in patterns:
        transformed_html = apply_pattern(transformed_html, pattern)

    return transformed_html


def transform_html_with_config(html: str, html_configs: Dict[str, Any]) -> str:
    """
    Transform HTML using project's html_configs.

    Args:
        html: Source HTML content
        html_configs: Dict from projects.html_configs (contains 'patterns' list)

    Returns:
        Transformed HTML

    Example html_configs:
        {
            "patterns": [
                {
                    "element_type": "p",
                    "source_pattern": "<p[^>]*>(.*?)</p>",
                    "target_pattern": "<p class=\"article\">\\1</p>"
                }
            ]
        }
    """
    if not html_configs:
        return html

    patterns = html_configs.get('patterns', [])

    if not patterns:
        return html

    return apply_all_patterns(html, patterns)
