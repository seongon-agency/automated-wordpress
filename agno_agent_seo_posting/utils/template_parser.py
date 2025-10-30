"""
Template Parser Utility
Extracts formatting rules from HTML template documents

Version 2.0: Extracts ALL unique valid forms for each tag type,
then selects the most appropriate form for each context
"""

import re
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup, NavigableString
from collections import defaultdict


class TemplateParser:
    """Parse HTML template and extract ALL valid formatting forms for each tag type."""

    def __init__(self, template_html: str):
        """
        Initialize the template parser.

        Args:
            template_html: HTML content from the template Google Doc
        """
        self.template_html = template_html
        self.soup = BeautifulSoup(template_html, "html.parser")
        self.rules = {}

    def parse(self) -> Dict[str, Any]:
        """
        Parse the template and extract all formatting rules.

        Returns:
            Dictionary mapping tag names to their formatting rules.
            Each tag has:
            - 'default': Most common/default form
            - 'variants': List of all unique forms with their usage context
        """
        # Extract rules for each tag type found in the template
        self.rules = {
            'p': self._extract_p_rules(),
            'img': self._extract_img_rules(),
            'h1': self._extract_heading_rules('h1'),
            'h2': self._extract_heading_rules('h2'),
            'h3': self._extract_heading_rules('h3'),
            'h4': self._extract_heading_rules('h4'),
            'h5': self._extract_heading_rules('h5'),
            'h6': self._extract_heading_rules('h6'),
            'ul': self._extract_list_rules('ul'),
            'ol': self._extract_list_rules('ol'),
            'li': self._extract_li_rules(),
            'table': self._extract_table_rules(),
            'tr': self._extract_tr_rules(),
            'td': self._extract_td_rules(),
            'th': self._extract_th_rules(),
            'strong': self._extract_inline_rules('strong'),
            'em': self._extract_inline_rules('em'),
            'span': self._extract_inline_rules('span'),
            'b': self._extract_inline_rules('b'),
            'i': self._extract_inline_rules('i'),
            'u': self._extract_inline_rules('u'),
            'a': self._extract_link_rules(),
            'div': self._extract_block_rules('div'),
            'blockquote': self._extract_block_rules('blockquote'),
        }

        return self.rules

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

    def _extract_all_unique_forms(self, tags: List) -> Dict[str, Any]:
        """
        Extract ALL unique forms of a tag type from the template.

        Returns:
            Dictionary with:
            - 'default': Most common form (used most frequently)
            - 'variants': List of all unique forms with their attributes and count
        """
        if not tags:
            return {'default': {}, 'variants': []}

        # Track all unique attribute combinations
        form_signatures = defaultdict(lambda: {'attrs': {}, 'count': 0})

        for tag in tags:
            # Create a signature for this tag form
            attrs = {}
            for attr, value in tag.attrs.items():
                if isinstance(value, list):
                    attrs[attr] = ' '.join(sorted(value))
                else:
                    attrs[attr] = value

            # Create hashable signature
            signature = self._attrs_to_signature(attrs)
            form_signatures[signature]['attrs'] = attrs
            form_signatures[signature]['count'] += 1

        # Convert to sorted list (most common first)
        variants = sorted(
            [{'attrs': data['attrs'], 'count': data['count']}
             for data in form_signatures.values()],
            key=lambda x: x['count'],
            reverse=True
        )

        # Most common form is the default
        default_attrs = variants[0]['attrs'] if variants else {}

        return {
            'default': default_attrs,
            'variants': variants
        }

    def _attrs_to_signature(self, attrs: Dict[str, Any]) -> str:
        """Convert attributes dict to a hashable signature string."""
        items = sorted(attrs.items())
        return '|'.join(f"{k}={v}" for k, v in items)

    def _extract_common_attributes(self, tags: List) -> Dict[str, Any]:
        """Extract common attributes from a list of tags."""
        if not tags:
            return {}

        # Collect all attributes from all tags
        attr_freq = defaultdict(lambda: defaultdict(int))

        for tag in tags:
            for attr, value in tag.attrs.items():
                if attr == 'style':
                    # Parse style into individual properties
                    styles = self._parse_style(value)
                    for prop, prop_value in styles.items():
                        attr_freq[f'style_{prop}'][prop_value] += 1
                elif isinstance(value, list):
                    for v in value:
                        attr_freq[attr][v] += 1
                else:
                    attr_freq[attr][value] += 1

        # Extract most common values
        common_attrs = {}
        style_props = {}

        for attr, values in attr_freq.items():
            if attr.startswith('style_'):
                # Style property
                prop_name = attr[6:]  # Remove 'style_' prefix
                most_common_value = max(values.items(), key=lambda x: x[1])[0]
                style_props[prop_name] = most_common_value
            else:
                # Regular attribute
                most_common_value = max(values.items(), key=lambda x: x[1])[0]
                common_attrs[attr] = most_common_value

        if style_props:
            common_attrs['style'] = self._style_to_str(style_props)

        return common_attrs

    def _extract_p_rules(self) -> Dict[str, Any]:
        """
        Extract paragraph formatting rules - ALL unique forms.

        Analyzes template to find:
        - Default form (most common)
        - Center-aligned form (for images)
        - Justify/left-aligned form (for text)
        """
        p_tags = self.soup.find_all('p')
        if not p_tags:
            return {
                'default': {'dir': 'ltr', 'style': 'text-align: justify;'},
                'variants': [],
                'center': {'dir': 'ltr', 'style': 'text-align: center;'},
                'justify': {'dir': 'ltr', 'style': 'text-align: justify;'}
            }

        # Extract all unique forms
        forms_data = self._extract_all_unique_forms(p_tags)

        # Analyze variants to identify center vs justify forms
        center_form = None
        justify_form = None

        for variant in forms_data['variants']:
            attrs = variant['attrs']
            style_str = attrs.get('style', '')
            styles = self._parse_style(style_str)
            text_align = styles.get('text-align', '')

            if text_align == 'center' and not center_form:
                center_form = attrs
            elif text_align in ['justify', 'left'] and not justify_form:
                justify_form = attrs

        # Set defaults if not found
        if not center_form:
            center_form = {'dir': 'ltr', 'style': 'text-align: center;'}
        if not justify_form:
            justify_form = forms_data['default'] or {'dir': 'ltr', 'style': 'text-align: justify;'}

        return {
            'default': forms_data['default'],
            'variants': forms_data['variants'],
            'center': center_form,
            'justify': justify_form
        }

    def _extract_img_rules(self) -> Dict[str, Any]:
        """Extract image formatting rules - all unique forms."""
        img_tags = self.soup.find_all('img')
        if not img_tags:
            return {
                'default': {'class': 'aligncenter'},
                'variants': []
            }

        forms_data = self._extract_all_unique_forms(img_tags)

        # Ensure default has at least a class
        if not forms_data['default']:
            forms_data['default'] = {'class': 'aligncenter'}
        elif 'class' not in forms_data['default']:
            forms_data['default']['class'] = 'aligncenter'

        return forms_data

    def _extract_heading_rules(self, tag_name: str) -> Dict[str, Any]:
        """Extract heading formatting rules - all unique forms."""
        tags = self.soup.find_all(tag_name)
        if not tags:
            return {'default': {}, 'variants': []}

        return self._extract_all_unique_forms(tags)

    def _extract_list_rules(self, tag_name: str) -> Dict[str, Any]:
        """Extract list (ul/ol) formatting rules - all unique forms."""
        tags = self.soup.find_all(tag_name)
        if not tags:
            return {'default': {}, 'variants': []}

        return self._extract_all_unique_forms(tags)

    def _extract_li_rules(self) -> Dict[str, Any]:
        """Extract list item formatting rules - all unique forms."""
        li_tags = self.soup.find_all('li')
        if not li_tags:
            return {'default': {}, 'variants': []}

        return self._extract_all_unique_forms(li_tags)

    def _extract_table_rules(self) -> Dict[str, Any]:
        """Extract table formatting rules - all unique forms."""
        tables = self.soup.find_all('table')
        if not tables:
            return {
                'default': {'style': 'width: 100%;'},
                'variants': []
            }

        forms_data = self._extract_all_unique_forms(tables)

        # Ensure width is set in default
        if forms_data['default']:
            default_style = forms_data['default'].get('style', '')
            styles = self._parse_style(default_style)
            if 'width' not in styles:
                styles['width'] = '100%'
            forms_data['default']['style'] = self._style_to_str(styles)
        else:
            forms_data['default'] = {'style': 'width: 100%;'}

        return forms_data

    def _extract_tr_rules(self) -> Dict[str, Any]:
        """Extract table row formatting rules - all unique forms."""
        tr_tags = self.soup.find_all('tr')
        if not tr_tags:
            return {'default': {}, 'variants': []}

        return self._extract_all_unique_forms(tr_tags)

    def _extract_td_rules(self) -> Dict[str, Any]:
        """Extract table cell formatting rules - all unique forms."""
        td_tags = self.soup.find_all('td')
        if not td_tags:
            return {'default': {}, 'variants': []}

        return self._extract_all_unique_forms(td_tags)

    def _extract_th_rules(self) -> Dict[str, Any]:
        """Extract table header formatting rules - all unique forms."""
        th_tags = self.soup.find_all('th')
        if not th_tags:
            return {'default': {}, 'variants': []}

        return self._extract_all_unique_forms(th_tags)

    def _extract_inline_rules(self, tag_name: str) -> Dict[str, Any]:
        """Extract inline element formatting rules - all unique forms."""
        tags = self.soup.find_all(tag_name)
        if not tags:
            return {'default': {}, 'variants': []}

        return self._extract_all_unique_forms(tags)

    def _extract_link_rules(self) -> Dict[str, Any]:
        """Extract link formatting rules - all unique forms (excluding href)."""
        a_tags = self.soup.find_all('a')
        if not a_tags:
            return {'default': {}, 'variants': []}

        # Extract all forms but exclude href from the signature
        form_signatures = defaultdict(lambda: {'attrs': {}, 'count': 0})

        for tag in a_tags:
            attrs = {}
            for attr, value in tag.attrs.items():
                if attr != 'href':  # Exclude href as it's content-specific
                    if isinstance(value, list):
                        attrs[attr] = ' '.join(sorted(value))
                    else:
                        attrs[attr] = value

            if attrs:  # Only track if there are non-href attributes
                signature = self._attrs_to_signature(attrs)
                form_signatures[signature]['attrs'] = attrs
                form_signatures[signature]['count'] += 1

        # Convert to sorted list
        variants = sorted(
            [{'attrs': data['attrs'], 'count': data['count']}
             for data in form_signatures.values()],
            key=lambda x: x['count'],
            reverse=True
        )

        default_attrs = variants[0]['attrs'] if variants else {}

        return {
            'default': default_attrs,
            'variants': variants
        }

    def _extract_block_rules(self, tag_name: str) -> Dict[str, Any]:
        """Extract block element formatting rules - all unique forms."""
        tags = self.soup.find_all(tag_name)
        if not tags:
            return {'default': {}, 'variants': []}

        return self._extract_all_unique_forms(tags)


def extract_template_rules(template_html: str) -> Dict[str, Any]:
    """
    Helper function to extract template rules from HTML.

    Args:
        template_html: HTML content from template Google Doc

    Returns:
        Dictionary of formatting rules for each tag type
    """
    parser = TemplateParser(template_html)
    return parser.parse()


if __name__ == "__main__":
    # Test the parser
    test_html = '''
    <html>
        <body>
            <p dir="ltr" style="text-align: justify;">Sample paragraph 1</p>
            <p dir="ltr" style="text-align: justify;">Sample paragraph 2</p>
            <img class="aligncenter" src="test.jpg" alt="Test" />
            <h2 style="color: blue;">Heading</h2>
        </body>
    </html>
    '''

    rules = extract_template_rules(test_html)
    print("Extracted rules:")
    for tag, attrs in rules.items():
        if attrs:
            print(f"  {tag}: {attrs}")
