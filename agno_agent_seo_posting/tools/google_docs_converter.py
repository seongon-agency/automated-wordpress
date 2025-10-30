"""
Tool 1: Google Docs to HTML Converter
Converts published Google Docs content to raw HTML using HTTP GET requests

Updated to work with published Google Docs URLs (no API/OAuth needed)

Version: 3.0
CHANGELOG v3.0:
- Added process_html_styles() to convert CSS classes to inline styles
- Added extract_content_between_h1_and_last_div() for content extraction
- Processes <style> tags and converts all classes to inline styles
- Removes <style>, <script>, <noscript> tags and class attributes
- Extracts content between first <h1> and last </div>

CHANGELOG v2.0:
- Added extract_document_content() function to extract only document content
- Now removes Google Docs wrapper HTML (scripts, navigation, footer)
- Extracts content from div#contents or div#doc-content
- Returns clean HTML suitable for WordPress publishing
"""

import re
import requests
from typing import Dict, Any
from bs4 import BeautifulSoup


def extract_published_doc_id(url: str) -> str:
    """
    Extract document ID from published Google Docs URLs.

    Supports:
    - https://docs.google.com/document/d/e/2PACX-xxx/pub
    - https://docs.google.com/document/d/[DOC_ID]/edit
    - https://docs.google.com/document/d/[DOC_ID]/
    """
    # Published URL format: /d/e/2PACX-xxx/pub
    m = re.search(r"/d/e/([a-zA-Z0-9_-]+)/pub", url)
    if m:
        return f"e/{m.group(1)}"

    # Standard edit URL format: /d/[DOC_ID]/edit
    m = re.search(r"/d/([a-zA-Z0-9_-]+)", url)
    if m:
        return m.group(1)

    raise ValueError(f"Could not extract document ID from URL: {url}. Please use a published Google Docs URL.")


def convert_to_published_url(url: str) -> str:
    """
    Convert any Google Docs URL to its published format.

    If the URL is already published (/pub), return as-is.
    If it's an edit URL, convert to published format.
    """
    # If already a published URL, return as-is
    if "/pub" in url:
        return url

    # Extract doc ID and construct published URL
    doc_id = extract_published_doc_id(url)

    # If it's a standard doc ID (not starting with 'e/'), need to add /pub
    if not doc_id.startswith('e/'):
        return f"https://docs.google.com/document/d/{doc_id}/pub"
    else:
        return f"https://docs.google.com/document/d/{doc_id}/pub"


def extract_document_title(html_content: str) -> str:
    """Extract document title from Google Docs HTML."""
    soup = BeautifulSoup(html_content, 'html.parser')

    # Try to find title in <title> tag
    title_tag = soup.find('title')
    if title_tag and title_tag.string:
        return title_tag.string.strip()

    # Fallback: try to find h1 in body
    h1_tag = soup.find('h1')
    if h1_tag:
        return h1_tag.get_text().strip()

    return "Untitled Document"


def process_html_styles(html: str) -> str:
    """
    Convert CSS classes to inline styles and clean up HTML.

    This function:
    1. Extracts all CSS from <style> tags
    2. Parses CSS class definitions
    3. Replaces all class attributes with inline styles
    4. Removes <style>, <script>, <noscript> tags
    5. Removes class attributes

    Args:
        html: The HTML string to process

    Returns:
        Processed HTML with inline styles and cleaned tags
    """
    # Step 1: Extract all CSS from <style> tags
    css_blocks = []
    style_pattern = re.compile(r'<style[^>]*>([\s\S]*?)</style>', re.IGNORECASE)

    for match in style_pattern.finditer(html):
        css_blocks.append(match.group(1))

    all_css = '\n\n'.join(css_blocks)

    # Step 2: Parse all CSS class definitions
    class_styles = {}
    class_pattern = re.compile(r'\.([a-z0-9_-]+)\s*\{([^}]+)\}', re.IGNORECASE | re.DOTALL)

    for match in class_pattern.finditer(all_css):
        class_name = match.group(1)
        rules = match.group(2).replace('\n', ' ').strip()
        rules = re.sub(r'\s+', ' ', rules)  # Normalize whitespace
        class_styles[class_name] = rules

    print(f"Found {len(class_styles)} CSS classes")

    # Step 3: Function to get merged styles for multiple classes
    def get_styles_for_classes(class_list):
        style_map = {}

        for class_name in class_list:
            if class_name not in class_styles:
                continue

            rules = class_styles[class_name].split(';')

            for rule in rules:
                trimmed = rule.strip()
                if not trimmed:
                    continue

                if ':' not in trimmed:
                    continue

                prop, value = trimmed.split(':', 1)
                prop = prop.strip()
                value = value.strip()

                if prop and value:
                    style_map[prop] = value

        if not style_map:
            return ''

        return '; '.join(f'{prop}: {val}' for prop, val in style_map.items())

    # Step 4: Replace all class attributes with inline styles
    processed_html = html

    # Pattern to match tags with class attributes
    tag_pattern = re.compile(
        r'<(\w+)([^>]*?)\sclass="([^"]+)"([^>]*?)>',
        re.IGNORECASE
    )

    def replace_class_with_style(match):
        tag_name = match.group(1)
        before_class = match.group(2)
        class_names = match.group(3)
        after_class = match.group(4)

        class_list = class_names.strip().split()
        inline_styles = get_styles_for_classes(class_list)

        new_tag = f'<{tag_name}{before_class}{after_class}'

        # Check if there's already a style attribute
        existing_style_pattern = re.compile(r'\sstyle="([^"]*)"', re.IGNORECASE)
        existing_style_match = existing_style_pattern.search(before_class + after_class)

        if existing_style_match:
            # Merge with existing styles
            existing_style = existing_style_match.group(1)
            merged_style = f'{inline_styles}; {existing_style}' if inline_styles else existing_style
            new_tag = existing_style_pattern.sub(f' style="{merged_style}"', new_tag)
        else:
            # Add new style attribute
            if inline_styles:
                new_tag += f' style="{inline_styles}"'

        new_tag += '>'
        return new_tag

    processed_html = tag_pattern.sub(replace_class_with_style, processed_html)

    # Step 5: Clean up - Remove <style> tags
    processed_html = re.sub(r'<style[^>]*>[\s\S]*?</style>', '', processed_html, flags=re.IGNORECASE)

    # Step 6: Clean up - Remove class attributes
    processed_html = re.sub(r'\sclass="[^"]*"', '', processed_html, flags=re.IGNORECASE)

    # Step 7: Clean up - Remove scripts and unnecessary elements
    processed_html = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', processed_html, flags=re.IGNORECASE)
    processed_html = re.sub(r'<noscript\b[^<]*(?:(?!<\/noscript>)<[^<]*)*<\/noscript>', '', processed_html, flags=re.IGNORECASE)

    return processed_html


def extract_content_between_h1_and_last_div(html: str) -> str:
    """
    Extract content between the first <h1> tag and the last </div> tag.

    Args:
        html: The HTML string to process

    Returns:
        Extracted content between first <h1> and last </div> (inclusive)
    """
    # Find the position of the first <h1> tag
    h1_pattern = re.compile(r'<h1\b', re.IGNORECASE)
    h1_match = h1_pattern.search(html)

    if not h1_match:
        print("Warning: No <h1> tag found in HTML")
        return html

    start = h1_match.start()

    # Find the position of the last </div> tag
    html_lower = html.lower()
    end = html_lower.rfind('</div>')

    if end == -1:
        print("Warning: No </div> tag found in HTML")
        return html

    # Extract content (including the closing </div> tag)
    if start != -1 and end != -1 and end > start:
        cleaned = html[start:end + 6]  # +6 for length of '</div>'
        return cleaned

    print("Warning: Could not extract content between <h1> and </div>")
    return ""


def extract_document_content(full_html: str) -> str:
    """
    Extract only the document content from the full Google Docs published page.

    Google Docs published pages include wrapper HTML, navigation, scripts, etc.
    This function extracts just the actual document content.

    Args:
        full_html: The full HTML from the published Google Docs page

    Returns:
        Cleaned HTML containing only the document content
    """
    soup = BeautifulSoup(full_html, 'html.parser')

    # Try multiple selectors to find the content container
    # Google Docs uses different structures over time
    content = None

    # Method 1: Look for div with id="contents"
    content = soup.find('div', {'id': 'contents'})

    # Method 2: Look for div with id="doc-content"
    if not content:
        content = soup.find('div', {'id': 'doc-content'})

    # Method 3: Look for the main body content (skip header/footer)
    if not content:
        body = soup.find('body')
        if body:
            # Remove script tags, style tags, nav elements
            for tag in body.find_all(['script', 'style', 'nav', 'header', 'footer']):
                tag.decompose()
            content = body

    # Method 4: Fallback - return the whole body if nothing else found
    if not content:
        content = soup.find('body') or soup

    # Return the inner HTML of the content container
    return str(content)


def google_docs_to_html(google_docs_url: str) -> Dict[str, Any]:
    """
    Convert published Google Docs content to processed HTML using HTTP GET request.

    Processing pipeline:
    1. Fetch HTML from published Google Docs URL
    2. Extract document content (remove Google Docs wrapper)
    3. Convert CSS classes to inline styles
    4. Remove <style>, <script>, <noscript> tags and class attributes
    5. Extract content between first <h1> and last </div>

    Args:
        google_docs_url: The published Google Docs URL (must be published to the web)
                        Example: https://docs.google.com/document/d/e/2PACX-xxx/pub

    Returns:
        Dictionary containing:
        - raw_html: Processed HTML with inline styles, cleaned tags, content extracted
        - file_id: Document ID extracted from URL
        - name: Document title extracted from HTML
        - success: Boolean indicating success
        - error: Error message if failed

    Note:
        The document MUST be published to the web for this to work.
        Go to File > Share > Publish to web in Google Docs.
    """
    try:
        # Convert to published URL format if needed
        published_url = convert_to_published_url(google_docs_url)

        # Extract document ID for reference
        doc_id = extract_published_doc_id(google_docs_url)

        # Make GET request to fetch HTML
        response = requests.get(published_url, timeout=30)
        response.raise_for_status()  # Raise error for bad status codes

        # Get full page HTML
        full_page_html = response.text

        # Verify we got actual content (not an error page)
        if len(full_page_html) < 100 or "404" in full_page_html[:500]:
            return {
                "success": False,
                "error": "Document not found or not published. Please publish the document to the web (File > Share > Publish to web)",
                "raw_html": None,
                "file_id": doc_id,
                "name": None
            }

        # Extract document title from full page
        doc_title = extract_document_title(full_page_html)

        # Extract only the document content (not the full Google Docs page wrapper)
        content_html = extract_document_content(full_page_html)

        # Process HTML: Convert CSS classes to inline styles
        print("Processing HTML: Converting CSS classes to inline styles...")
        processed_html = process_html_styles(content_html)

        # Extract content between first <h1> and last </div>
        print("Extracting content between first <h1> and last </div>...")
        final_html = extract_content_between_h1_and_last_div(processed_html)

        return {
            "success": True,
            "raw_html": final_html,
            "file_id": doc_id,
            "name": doc_title,
            "error": None
        }

    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"HTTP request failed: {str(e)}. Make sure the document is published to the web.",
            "raw_html": None,
            "file_id": None,
            "name": None
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "raw_html": None,
            "file_id": None,
            "name": None
        }


if __name__ == "__main__":
    # Test the tool with a published Google Docs URL
    print("Testing Google Docs to HTML Converter (HTTP GET method)")
    print("=" * 70)

    # Example: Use your published Google Docs URL here
    test_url = "https://docs.google.com/document/d/e/2PACX-YOUR_PUBLISHED_DOC_ID/pub"

    print(f"\nFetching: {test_url}")
    print("Note: Document must be published to the web (File > Share > Publish to web)\n")

    result = google_docs_to_html(test_url)

    print(f"Success: {result['success']}")
    if result['success']:
        print(f"Document Title: {result['name']}")
        print(f"Document ID: {result['file_id']}")
        print(f"HTML Length: {len(result['raw_html'])} characters")
        print(f"\nFirst 200 characters of HTML:")
        print(result['raw_html'][:200])
    else:
        print(f"Error: {result['error']}")
        print("\nTroubleshooting:")
        print("1. Make sure the document is published to the web")
        print("2. In Google Docs: File > Share > Publish to web")
        print("3. Copy the published link (should contain /pub at the end)")
