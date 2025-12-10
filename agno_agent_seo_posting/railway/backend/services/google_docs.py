"""
Google Docs to HTML Converter Service

Converts Google Docs to HTML using published URLs.
"""

import re
import requests
from typing import Dict, Any
from bs4 import BeautifulSoup


def convert_css_classes_to_inline_styles(html: str) -> str:
    """
    Convert CSS classes to inline styles in HTML.
    Handles Google Docs published format where styles are in <style> tags.
    """
    # Extract ALL CSS from style tags
    css_blocks = []
    style_regex = re.compile(r'<style[^>]*>([\s\S]*?)</style>', re.IGNORECASE)

    for match in style_regex.finditer(html):
        css_blocks.append(match.group(1))

    all_css = '\n\n'.join(css_blocks)

    # Parse all CSS class definitions
    class_styles = {}
    class_regex = re.compile(r'\.([a-z0-9_-]+)\s*\{([^}]+)\}', re.IGNORECASE | re.DOTALL)

    for match in class_regex.finditer(all_css):
        class_name = match.group(1)
        rules = match.group(2).replace('\n', ' ').replace(r'\s+', ' ').strip()
        class_styles[class_name] = rules

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
                colon_index = trimmed.find(':')
                if colon_index == -1:
                    continue
                prop = trimmed[:colon_index].strip()
                value = trimmed[colon_index + 1:].strip()
                if prop and value:
                    style_map[prop] = value
        if not style_map:
            return ''
        return '; '.join(f"{prop}: {val}" for prop, val in style_map.items())

    # Replace all class attributes with inline styles
    processed_html = html
    tag_regex = re.compile(r'<(\w+)([^>]*?)\sclass="([^"]+)"([^>]*?)>', re.IGNORECASE)

    def replace_class_with_style(match):
        tag_name = match.group(1)
        before_class = match.group(2)
        class_names = match.group(3)
        after_class = match.group(4)
        class_list = class_names.strip().split()
        inline_styles = get_styles_for_classes(class_list)
        new_tag = f"<{tag_name}{before_class}{after_class}"
        existing_style_regex = re.compile(r'\sstyle="([^"]*)"', re.IGNORECASE)
        existing_match = existing_style_regex.search(before_class + after_class)
        if existing_match:
            existing_style = existing_match.group(1)
            merged_style = f"{inline_styles}; {existing_style}" if inline_styles else existing_style
            new_tag = existing_style_regex.sub(f' style="{merged_style}"', new_tag)
        else:
            if inline_styles:
                new_tag += f' style="{inline_styles}"'
        new_tag += '>'
        return new_tag

    processed_html = tag_regex.sub(replace_class_with_style, processed_html)

    # Clean up
    processed_html = re.sub(r'<style[^>]*>[\s\S]*?</style>', '', processed_html, flags=re.IGNORECASE)
    processed_html = re.sub(r'\sclass="[^"]*"', '', processed_html, flags=re.IGNORECASE)
    processed_html = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', processed_html, flags=re.IGNORECASE)
    processed_html = re.sub(r'<noscript\b[^<]*(?:(?!<\/noscript>)<[^<]*)*<\/noscript>', '', processed_html, flags=re.IGNORECASE)

    return processed_html


def clean_published_html(html: str) -> str:
    """
    Clean published Google Docs HTML by extracting content from first H1 to last div.
    """
    h1_match = re.search(r'<h1\b', html, re.IGNORECASE)
    if not h1_match:
        return html

    start_index = h1_match.start()
    last_div_index = html.lower().rfind('</div>')

    if last_div_index == -1 or last_div_index <= start_index:
        return html[start_index:]

    return html[start_index:last_div_index + 6]


def extract_file_id(url: str) -> str:
    """Extract Google Drive file ID from URL."""
    # Published document pattern
    match = re.search(r"/document/d/e/([a-zA-Z0-9_-]+)/pub", url)
    if match:
        return match.group(1)

    # Regular document pattern
    match = re.search(r"/document/d/([a-zA-Z0-9_-]+)", url)
    if match:
        return match.group(1)

    raise ValueError(f"Could not extract file ID from URL: {url}")


async def google_docs_to_html(google_docs_url: str) -> Dict[str, Any]:
    """
    Convert a Google Docs URL to HTML.

    Only supports published URLs (ending with /pub).

    Args:
        google_docs_url: Published Google Docs URL

    Returns:
        Dict with success, raw_html, document_name, file_id, or error
    """
    try:
        if not google_docs_url.strip().endswith('/pub'):
            return {
                "success": False,
                "error": "URL must be a published Google Docs URL ending with /pub"
            }

        response = requests.get(google_docs_url, timeout=60)
        response.raise_for_status()
        html_text = response.text

        # Extract document title
        soup = BeautifulSoup(html_text, 'lxml')
        title_tag = soup.find('title')
        document_name = title_tag.get_text() if title_tag else "Untitled Document"

        # Extract file ID
        file_id = extract_file_id(google_docs_url)

        # Process HTML
        html_text = convert_css_classes_to_inline_styles(html_text)
        html_text = clean_published_html(html_text)

        return {
            "success": True,
            "raw_html": html_text,
            "document_name": document_name,
            "file_id": file_id
        }

    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Failed to fetch document: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Conversion failed: {str(e)}"
        }
