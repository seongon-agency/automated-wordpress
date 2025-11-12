"""
HTML Extractor Utilities

Helper functions to extract specific elements from HTML content.
"""

import re
from bs4 import BeautifulSoup
from typing import Optional, List


def extract_title_from_html(html: str) -> Optional[str]:
    """
    Extract the main title (H1) from HTML content.

    Args:
        html: HTML content

    Returns:
        Title text or None if not found
    """
    soup = BeautifulSoup(html, 'html.parser')

    # Look for H1 tag
    h1 = soup.find('h1')
    if h1:
        return h1.get_text().strip()

    # Fallback: look for first H2
    h2 = soup.find('h2')
    if h2:
        return h2.get_text().strip()

    return None


def extract_images_from_html(html: str) -> List[str]:
    """
    Extract all image URLs from HTML.

    Args:
        html: HTML content

    Returns:
        List of image URLs
    """
    soup = BeautifulSoup(html, 'html.parser')

    image_urls = []
    for img in soup.find_all('img'):
        src = img.get('src')
        if src and (src.startswith('http://') or src.startswith('https://')):
            image_urls.append(src)

    return image_urls


def remove_content_before_h1(html: str) -> str:
    """
    Remove all content before and including the first H1 tag.

    This is a universal cleaning step that applies to all clients:
    1. Find the first H1 tag
    2. Remove everything before it
    3. Remove the H1 itself
    4. Return the cleaned HTML

    The H1 is used as the WordPress post title, so it should not
    appear in the content body.

    Args:
        html: HTML content

    Returns:
        Cleaned HTML with H1 and everything before it removed
    """
    # Use regex to find the H1 and remove everything before and including it
    # This handles nested structures better than BeautifulSoup navigation

    # Find the closing tag of the first H1
    h1_pattern = r'<h1[^>]*>.*?</h1>'
    match = re.search(h1_pattern, html, flags=re.IGNORECASE | re.DOTALL)

    if not match:
        # No H1 found, return original HTML
        return html

    # Get the position after the closing </h1> tag
    end_pos = match.end()

    # Return everything after the H1 (removing everything before and including H1)
    cleaned_html = html[end_pos:]

    return cleaned_html.strip()


def clean_html_for_wordpress(html: str) -> str:
    """
    Apply all universal HTML cleaning rules.

    This function applies cleaning rules that should be used for ALL clients:
    1. Remove everything before and including the first H1

    Args:
        html: Raw HTML content

    Returns:
        Cleaned HTML ready for WordPress
    """
    # Apply universal cleaning: remove content before H1 and remove H1
    html = remove_content_before_h1(html)

    return html
