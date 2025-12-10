"""
HTML Transformer Service

Applies project-specific HTML transformation patterns to content.
"""

import re
from typing import Dict, Optional, Any, List


def apply_pattern(html: str, pattern: Dict[str, str]) -> str:
    """
    Apply a single transformation pattern to HTML.

    Args:
        html: Source HTML
        pattern: Dict with source_pattern and target_pattern

    Returns:
        Transformed HTML
    """
    source_pattern = pattern.get('source_pattern', '')
    target_pattern = pattern.get('target_pattern', '')

    if not source_pattern or not target_pattern:
        return html

    try:
        return re.sub(source_pattern, target_pattern, html, flags=re.DOTALL | re.IGNORECASE)
    except re.error:
        return html


def transform_html_with_config(html: str, html_configs: Dict[str, Any]) -> str:
    """
    Apply all transformation patterns from config to HTML.

    Args:
        html: Source HTML
        html_configs: Config dict with 'patterns' list

    Returns:
        Transformed HTML
    """
    patterns = html_configs.get('patterns', [])

    result = html
    for pattern in patterns:
        result = apply_pattern(result, pattern)

    return result


async def transform_html(
    html: str,
    html_configs: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Transform HTML using project's HTML configuration patterns.

    Args:
        html: Source HTML content
        html_configs: Project's html_configs dict (from database)

    Returns:
        Dict with success, transformed_html, patterns_applied, or error
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


def extract_title_from_html(html: str) -> Optional[str]:
    """
    Extract title (first H1) from HTML content.

    Args:
        html: HTML content

    Returns:
        Title text or None
    """
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, 'lxml')
    h1 = soup.find('h1')

    if h1:
        return h1.get_text(strip=True)

    return None


def remove_title_from_html(html: str) -> str:
    """
    Remove the first H1 tag from HTML (since it becomes the post title).

    Args:
        html: HTML content

    Returns:
        HTML with first H1 removed
    """
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, 'lxml')
    h1 = soup.find('h1')

    if h1:
        # Remove the H1 and its parent if it's a wrapper div/p
        parent = h1.parent
        if parent and parent.name in ['div', 'p'] and len(parent.contents) == 1:
            parent.decompose()
        else:
            h1.decompose()

    return str(soup)
