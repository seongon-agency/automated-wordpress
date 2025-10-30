"""
Efficient HTML Transformer for Client-Specific Customizations

This module applies client-specific HTML transformations programmatically,
without consuming AI tokens. Uses BeautifulSoup for efficient DOM manipulation.
"""

from bs4 import BeautifulSoup, NavigableString, Tag
import re
from typing import Dict, List, Any


class HTMLTransformer:
    """
    Applies client-specific HTML transformations efficiently.
    """

    def __init__(self, config: dict):
        """
        Initialize transformer with client configuration.

        Args:
            config: Client configuration dictionary from client_configs.py
        """
        self.config = config
        self.transformations = config.get("transformations", {})

    def transform(self, html: str) -> str:
        """
        Apply all transformations to HTML content.

        Args:
            html: Input HTML string

        Returns:
            Transformed HTML string
        """
        soup = BeautifulSoup(html, 'html.parser')

        # Apply transformations in order
        self._apply_tag_replacements(soup)
        self._apply_attribute_rules(soup)
        self._apply_style_injections(soup)
        self._apply_class_mappings(soup)
        self._apply_custom_wrappers(soup)

        return str(soup)

    def _apply_tag_replacements(self, soup: BeautifulSoup):
        """Replace HTML tags according to configuration."""
        replacements = self.transformations.get("tag_replacements", {})

        for old_tag, rules in replacements.items():
            new_tag_name = rules.get("new_tag")
            preserve_content = rules.get("preserve_content", True)
            add_class = rules.get("add_class")

            # Find all instances of the old tag
            for tag in soup.find_all(old_tag):
                # Create new tag
                new_tag = soup.new_tag(new_tag_name)

                # Preserve content
                if preserve_content:
                    for child in tag.children:
                        new_tag.append(child)

                # Copy attributes (optional)
                if rules.get("copy_attributes", False):
                    new_tag.attrs = tag.attrs.copy()

                # Add class if specified
                if add_class:
                    existing_classes = new_tag.get("class", [])
                    if isinstance(existing_classes, str):
                        existing_classes = [existing_classes]
                    existing_classes.append(add_class)
                    new_tag["class"] = existing_classes

                # Replace old tag with new tag
                tag.replace_with(new_tag)

    def _apply_attribute_rules(self, soup: BeautifulSoup):
        """Modify tag attributes according to configuration."""
        attribute_rules = self.transformations.get("attribute_rules", {})

        for tag_name, rules in attribute_rules.items():
            for tag in soup.find_all(tag_name):
                # Add class
                if "add_class" in rules:
                    existing_classes = tag.get("class", [])
                    if isinstance(existing_classes, str):
                        existing_classes = [existing_classes]
                    new_classes = rules["add_class"].split()
                    for cls in new_classes:
                        if cls not in existing_classes:
                            existing_classes.append(cls)
                    tag["class"] = existing_classes

                # Add or modify style
                if "add_style" in rules:
                    existing_style = tag.get("style", "")
                    new_style = rules["add_style"]

                    if existing_style:
                        # Merge styles (new style takes precedence)
                        tag["style"] = f"{existing_style}; {new_style}"
                    else:
                        tag["style"] = new_style

                # Remove style
                if rules.get("remove_style", False):
                    if "style" in tag.attrs:
                        del tag.attrs["style"]

                # Add custom attributes
                if "add_attribute" in rules:
                    for attr, value in rules["add_attribute"].items():
                        tag[attr] = value

                # Remove attributes
                if "remove_attribute" in rules:
                    attrs_to_remove = rules["remove_attribute"]
                    if isinstance(attrs_to_remove, str):
                        attrs_to_remove = [attrs_to_remove]
                    for attr in attrs_to_remove:
                        if attr in tag.attrs:
                            del tag.attrs[attr]

    def _apply_style_injections(self, soup: BeautifulSoup):
        """Inject inline styles to specific tags."""
        style_injections = self.transformations.get("style_injections", {})

        for tag_name, style in style_injections.items():
            for tag in soup.find_all(tag_name):
                existing_style = tag.get("style", "")

                if existing_style:
                    tag["style"] = f"{existing_style}; {style}"
                else:
                    tag["style"] = style

    def _apply_class_mappings(self, soup: BeautifulSoup):
        """Replace class names according to mappings."""
        class_mappings = self.transformations.get("class_mappings", {})

        for tag in soup.find_all(class_=True):
            classes = tag.get("class", [])
            if isinstance(classes, str):
                classes = [classes]

            new_classes = []
            for cls in classes:
                # Check if this class should be mapped
                if cls in class_mappings:
                    # Replace with new class(es)
                    mapped = class_mappings[cls]
                    if isinstance(mapped, str):
                        new_classes.extend(mapped.split())
                    else:
                        new_classes.extend(mapped)
                else:
                    # Keep original class
                    new_classes.append(cls)

            tag["class"] = new_classes

    def _apply_custom_wrappers(self, soup: BeautifulSoup):
        """Wrap specific tags in custom HTML structures."""
        custom_wrappers = self.transformations.get("custom_wrappers", [])

        for wrapper_config in custom_wrappers:
            wrap_tag = wrapper_config.get("wrap_tag")
            wrapper_html = wrapper_config.get("wrapper")

            for tag in soup.find_all(wrap_tag):
                # Create wrapper structure
                wrapper_soup = BeautifulSoup(wrapper_html, 'html.parser')

                # Find {content} placeholder and replace with actual tag
                wrapper_root = wrapper_soup.contents[0]

                # Convert tag to string and replace placeholder
                tag_html = str(tag)
                wrapper_str = str(wrapper_soup).replace("{content}", tag_html)

                # Parse wrapped content
                wrapped = BeautifulSoup(wrapper_str, 'html.parser')

                # Replace original tag with wrapped version
                tag.replace_with(wrapped)


def transform_html_for_client(html: str, client_config: dict) -> str:
    """
    Convenience function to transform HTML with a client configuration.

    Args:
        html: Input HTML string
        client_config: Client configuration dictionary

    Returns:
        Transformed HTML string
    """
    transformer = HTMLTransformer(client_config)
    return transformer.transform(html)


# Example usage
if __name__ == "__main__":
    # Test with sample HTML
    test_html = """
    <h2>This is a heading</h2>
    <p>This is a paragraph with <strong>bold text</strong> and <em>italic text</em>.</p>
    <ul>
        <li>List item 1</li>
        <li>List item 2</li>
    </ul>
    """

    from client_configs import CLIENT_CUSTOM_BOLD

    transformer = HTMLTransformer(CLIENT_CUSTOM_BOLD)
    result = transformer.transform(test_html)

    print("Original HTML:")
    print(test_html)
    print("\nTransformed HTML:")
    print(result)
