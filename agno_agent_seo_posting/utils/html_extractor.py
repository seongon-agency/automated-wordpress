"""
HTML Content Extractor Utility
Extracts useful information from HTML content
"""

import re
from typing import Optional
from bs4 import BeautifulSoup


def extract_first_heading(html_content: str) -> Optional[str]:
    """
    Extract the first h1 heading from HTML content.
    This is typically the main title of the document.

    Args:
        html_content: HTML content to extract from

    Returns:
        The text of the first h1 heading, or None if not found
    """
    if not html_content:
        return None

    try:
        soup = BeautifulSoup(html_content, "html.parser")

        # Find the first h1 tag
        h1_tag = soup.find('h1')

        if h1_tag:
            # Get the text content and clean it up
            title = h1_tag.get_text(strip=True)
            return title if title else None

        return None

    except Exception as e:
        print(f"⚠️  Error extracting heading: {e}")
        return None


def extract_title_from_content(html_content: str, fallback: Optional[str] = None) -> Optional[str]:
    """
    Extract the document title from HTML content.
    Tries multiple methods in order:
    1. First h1 heading
    2. First h2 heading if no h1
    3. Fallback value if provided

    Args:
        html_content: HTML content to extract from
        fallback: Fallback title if extraction fails

    Returns:
        Extracted title or fallback value
    """
    if not html_content:
        return fallback

    try:
        soup = BeautifulSoup(html_content, "html.parser")

        # Try h1 first
        h1_tag = soup.find('h1')
        if h1_tag:
            title = h1_tag.get_text(strip=True)
            if title:
                return title

        # Fallback to h2
        h2_tag = soup.find('h2')
        if h2_tag:
            title = h2_tag.get_text(strip=True)
            if title:
                return title

        return fallback

    except Exception as e:
        print(f"⚠️  Error extracting title: {e}")
        return fallback


def remove_first_heading(html_content: str) -> str:
    """
    Remove the first h1 heading from HTML content.
    Useful when the h1 is extracted as the post title and shouldn't be duplicated in content.

    Args:
        html_content: HTML content to process

    Returns:
        HTML content with first h1 removed
    """
    if not html_content:
        return html_content

    try:
        soup = BeautifulSoup(html_content, "html.parser")

        # Find and remove the first h1 tag
        h1_tag = soup.find('h1')
        if h1_tag:
            h1_tag.decompose()

        return str(soup)

    except Exception as e:
        print(f"⚠️  Error removing heading: {e}")
        return html_content


if __name__ == "__main__":
    # Test the extractor
    test_html = '''
    <html>
        <body>
            <h1>This is the Main Title</h1>
            <p>Some content here</p>
            <h2>A subheading</h2>
        </body>
    </html>
    '''

    title = extract_first_heading(test_html)
    print(f"Extracted title: {title}")

    html_without_h1 = remove_first_heading(test_html)
    print(f"\nHTML without h1:\n{html_without_h1}")
