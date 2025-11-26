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
    target_pattern = pattern.get('target_pattern')
    element_type = pattern.get('element_type', 'unknown')

    # Check if source_pattern exists (not empty)
    if not source_pattern:
        return html

    # Allow target_pattern to be empty string (for removal patterns)
    # Only skip if target_pattern is None (not provided)
    if target_pattern is None:
        return html

    try:
        # Apply regex substitution
        # target_pattern can be '' (empty string) to remove matched content
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


def sort_patterns_by_specificity(patterns: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Sort patterns by specificity (most specific first).

    This ensures that more specific patterns (like p_with_image) are applied
    before more general patterns (like p_justify), preventing conflicts.

    Specificity rules (higher score = more specific = applied first):
    1. Patterns matching elements with child elements (e.g., p with img) = priority 100
    2. Patterns matching specific attributes (e.g., text-align) = priority 50
    3. General patterns matching tag type only = priority 10

    Args:
        patterns: List of pattern dicts

    Returns:
        Sorted list with most specific patterns first
    """
    def get_priority(pattern: Dict[str, str]) -> int:
        source = pattern.get('source_pattern', '')
        element_type = pattern.get('element_type', '')

        # Check for patterns with child elements (highest priority)
        # e.g., <p[^>]*>.*?<img[^>]*>.*?</p>
        if '<img' in source or '<a' in source or '<span' in source:
            return 100

        # Check for patterns with specific attributes (medium priority)
        # e.g., <p[^>]*style="[^"]*text-align
        if 'style=' in source or 'class=' in source or 'id=' in source:
            return 50

        # General patterns (lowest priority)
        return 10

    # Sort by priority (descending - highest first)
    return sorted(patterns, key=get_priority, reverse=True)


def apply_all_patterns(html: str, patterns: List[Dict[str, str]]) -> str:
    """
    Apply all transformation patterns sequentially.

    Patterns are automatically sorted by specificity to ensure
    more specific patterns (e.g., p_with_image) are applied before
    more general patterns (e.g., p_justify).

    Args:
        html: HTML content
        patterns: List of pattern dicts from html_configs

    Returns:
        Fully transformed HTML
    """
    # Sort patterns by specificity (most specific first)
    sorted_patterns = sort_patterns_by_specificity(patterns)

    transformed_html = html

    for pattern in sorted_patterns:
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
