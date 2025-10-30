"""
Tool 3: HTML Template Formatter
Applies HTML template styling rules to content

Version 4.0: INTELLIGENT CONTEXT-AWARE FORMATTING
- CRITICAL FIX: Completely REPLACES Google Docs attributes instead of merging
- Intelligently chooses template variants based on content context
- Paragraphs with images use 'center' template variant
- Paragraphs with text use 'justify' template variant
- Removes ALL Google Docs inline styles (padding-top, margin, orphans, widows, etc.)
- Produces clean HTML with only template formatting
"""

import re
from typing import Dict, Any
from bs4 import BeautifulSoup, NavigableString
import sys
sys.path.append('..')
from utils.template_parser import extract_template_rules


class HTMLFormatter:
    """
    Apply template formatting rules to content HTML.

    Version 4.0: Intelligent context-aware formatting
    - Completely replaces Google Docs attributes with template attributes
    - Intelligently chooses correct template variant based on content
    - Produces clean, minimal HTML matching template exactly
    """

    def __init__(self, template_rules: Dict[str, Any]):
        """
        Initialize the formatter with template rules.

        Args:
            template_rules: Dictionary of formatting rules from template parser.
                           Each tag has 'default' form which contains the most common
                           attributes from the template.
        """
        self.rules = template_rules

    def _parse_style(self, style_str: str) -> Dict[str, str]:
        """Parse inline style string into dictionary."""
        if not style_str:
            return {}

        styles = {}
        for declaration in style_str.split(';'):
            declaration = declaration.strip()
            if ':' in declaration:
                prop, value = declaration.split(':', 1)
                styles[prop.strip().lower()] = value.strip()

        return styles

    def _style_to_str(self, style_dict: Dict[str, str]) -> str:
        """Convert style dictionary back to string."""
        if not style_dict:
            return ""
        return "; ".join(f"{k}: {v}" for k, v in style_dict.items())

    def _get_default_attrs(self, rule: Any) -> Dict[str, Any]:
        """
        Get default attributes from a rule.

        Args:
            rule: Rule dict that may have 'default' key or be a flat dict

        Returns:
            Dictionary of attributes
        """
        if not rule:
            return {}

        # New format: has 'default' key
        if isinstance(rule, dict) and 'default' in rule:
            return rule.get('default', {})

        # Old format: flat dict
        if isinstance(rule, dict):
            return rule

        return {}

    def _merge_styles(self, original_style: str, template_style: str) -> str:
        """
        Merge original and template styles, with template taking precedence.

        Args:
            original_style: Original inline style string
            template_style: Template inline style string

        Returns:
            Merged style string
        """
        original = self._parse_style(original_style)
        template = self._parse_style(template_style)

        # Template overrides original
        merged = {**original, **template}

        return self._style_to_str(merged)

    def _apply_attributes(self, tag, rule: Dict[str, Any], preserve_content_attrs: list = None):
        """
        Apply template attributes to a tag by COMPLETELY REPLACING original attributes.

        This ensures clean HTML output with only template formatting, removing all
        Google Docs inline styles (padding-top, margin, orphans, widows, etc.)

        Args:
            tag: BeautifulSoup tag object
            rule: Template rule dictionary containing attributes to apply
            preserve_content_attrs: List of attribute names to preserve from content (not overwrite)
        """
        if not rule:
            return

        # Default attributes to preserve from content
        if preserve_content_attrs is None:
            preserve_content_attrs = []

        # First, save attributes we want to preserve
        attrs_to_keep = {}
        for attr in preserve_content_attrs:
            if attr in tag.attrs:
                attrs_to_keep[attr] = tag.attrs[attr]

        # Clear ALL existing attributes
        tag.attrs = {}

        # Restore preserved attributes
        for attr, value in attrs_to_keep.items():
            tag[attr] = value

        # Now apply template attributes (completely fresh, no merging)
        for attr, value in rule.items():
            # Skip if this attribute should be preserved from content
            if attr in preserve_content_attrs:
                continue

            if attr == 'class':
                # Apply class from template
                if isinstance(value, list):
                    tag['class'] = value
                else:
                    tag['class'] = value.split() if ' ' in value else [value]
            else:
                # Apply all other attributes from template (including style)
                tag[attr] = value

    def format_html(self, content_html: str) -> str:
        """
        Apply template formatting to content HTML.

        Args:
            content_html: Raw HTML content to format

        Returns:
            Formatted HTML with template rules applied
        """
        soup = BeautifulSoup(content_html, "html.parser")

        # Apply rules for each tag type
        self._format_paragraphs(soup)
        self._format_images(soup)
        self._format_headings(soup)
        self._format_lists(soup)
        self._format_tables(soup)
        self._format_inline_elements(soup)
        self._format_links(soup)

        return str(soup)

    def _format_paragraphs(self, soup: BeautifulSoup):
        """
        Apply paragraph formatting from template - INTELLIGENTLY choosing variant.

        Strategy:
        - Paragraphs containing images → use 'center' template variant
        - Paragraphs with text content → use 'justify' or 'default' template variant

        This preserves the semantic meaning of the content while applying clean template styles.
        """
        if 'p' not in self.rules or not self.rules['p']:
            return

        p_rule = self.rules['p']

        # Get template variants
        default_attrs = self._get_default_attrs(p_rule)
        center_attrs = p_rule.get('center', default_attrs)
        justify_attrs = p_rule.get('justify', default_attrs)

        for p in soup.find_all('p'):
            # Check if paragraph contains an image
            if p.find('img'):
                # Use center template for image paragraphs
                self._apply_attributes(p, center_attrs)
            else:
                # Use justify template for text paragraphs
                self._apply_attributes(p, justify_attrs)

    def _format_images(self, soup: BeautifulSoup):
        """
        Apply image formatting from template.

        Applies template classes/styles while preserving content-specific attributes.
        """
        if 'img' not in self.rules or not self.rules['img']:
            return

        img_attrs = self._get_default_attrs(self.rules['img'])

        for img in soup.find_all('img'):
            # Preserve content-specific image attributes
            self._apply_attributes(img, img_attrs,
                                 preserve_content_attrs=['src', 'alt', 'width', 'height', 'title'])

    def _format_headings(self, soup: BeautifulSoup):
        """
        Apply heading formatting from template.

        Uses default form from template for each heading level.
        """
        for level in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            if level not in self.rules or not self.rules[level]:
                continue

            heading_attrs = self._get_default_attrs(self.rules[level])

            for tag in soup.find_all(level):
                # Apply all template attributes to headings
                self._apply_attributes(tag, heading_attrs)

    def _format_lists(self, soup: BeautifulSoup):
        """
        Apply list formatting from template.

        Uses default form from template for ul, ol, and li tags.
        """
        # Format ul and ol
        for list_type in ['ul', 'ol']:
            if list_type not in self.rules or not self.rules[list_type]:
                continue

            list_attrs = self._get_default_attrs(self.rules[list_type])

            for tag in soup.find_all(list_type):
                # Apply all template attributes
                self._apply_attributes(tag, list_attrs)

        # Format li
        if 'li' in self.rules and self.rules['li']:
            li_attrs = self._get_default_attrs(self.rules['li'])
            for li in soup.find_all('li'):
                # Apply all template attributes
                self._apply_attributes(li, li_attrs)

    def _format_tables(self, soup: BeautifulSoup):
        """
        Apply table formatting from template.

        Uses default form from template for table, tr, td, th tags.
        """
        # Format tables
        if 'table' in self.rules and self.rules['table']:
            table_attrs = self._get_default_attrs(self.rules['table'])
            for table in soup.find_all('table'):
                # Apply all template attributes
                self._apply_attributes(table, table_attrs)

        # Format tr
        if 'tr' in self.rules and self.rules['tr']:
            tr_attrs = self._get_default_attrs(self.rules['tr'])
            for tr in soup.find_all('tr'):
                # Apply all template attributes
                self._apply_attributes(tr, tr_attrs)

        # Format td
        if 'td' in self.rules and self.rules['td']:
            td_attrs = self._get_default_attrs(self.rules['td'])
            for td in soup.find_all('td'):
                # Apply all template attributes
                self._apply_attributes(td, td_attrs)

        # Format th
        if 'th' in self.rules and self.rules['th']:
            th_attrs = self._get_default_attrs(self.rules['th'])
            for th in soup.find_all('th'):
                # Apply all template attributes
                self._apply_attributes(th, th_attrs)

    def _format_inline_elements(self, soup: BeautifulSoup):
        """
        Apply inline element formatting from template.

        Uses default form from template for strong, em, span, b, i, u tags.
        """
        for tag_name in ['strong', 'em', 'span', 'b', 'i', 'u']:
            if tag_name not in self.rules or not self.rules[tag_name]:
                continue

            inline_attrs = self._get_default_attrs(self.rules[tag_name])

            for tag in soup.find_all(tag_name):
                # Apply all template attributes
                self._apply_attributes(tag, inline_attrs)

    def _format_links(self, soup: BeautifulSoup):
        """
        Apply link formatting from template.

        Applies template styles while preserving href from content.
        """
        if 'a' not in self.rules or not self.rules['a']:
            return

        link_attrs = self._get_default_attrs(self.rules['a'])

        for a in soup.find_all('a'):
            # Preserve href from content (link destination)
            self._apply_attributes(a, link_attrs,
                                 preserve_content_attrs=['href'])


def format_html_with_template(content_html: str, template_html: str) -> Dict[str, Any]:
    """
    Apply HTML template formatting to content.

    Args:
        content_html: Raw or processed HTML content
        template_html: HTML extracted from the template Google Doc

    Returns:
        Dictionary containing:
        - formatted_html: Content HTML formatted according to template rules
        - template_rules: The extracted template rules used
        - success: Boolean indicating success
        - error: Error message if failed
    """
    try:
        # Extract template rules
        template_rules = extract_template_rules(template_html)

        # Create formatter
        formatter = HTMLFormatter(template_rules)

        # Apply formatting
        formatted_html = formatter.format_html(content_html)

        return {
            "success": True,
            "formatted_html": formatted_html,
            "template_rules": template_rules,
            "error": None
        }

    except Exception as e:
        return {
            "success": False,
            "formatted_html": content_html,
            "template_rules": {},
            "error": str(e)
        }


if __name__ == "__main__":
    # Test the formatter
    content = '''
    <html>
        <body>
            <p>This is a test paragraph.</p>
            <img src="test.jpg" alt="Test image" />
            <h2>Test Heading</h2>
        </body>
    </html>
    '''

    template = '''
    <html>
        <body>
            <p dir="ltr" style="text-align: justify; font-size: 16px;">Template paragraph</p>
            <img class="aligncenter size-full" alt="Template" />
            <h2 style="color: #333; font-weight: bold;">Template heading</h2>
        </body>
    </html>
    '''

    result = format_html_with_template(content, template)
    print(f"Success: {result['success']}")
    if result['success']:
        print("\nFormatted HTML:")
        print(result['formatted_html'][:500])
