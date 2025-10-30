"""
Test Client HTML Transformations

Run this script to test your client configurations before using them in production.
"""

from html_transformer import HTMLTransformer
from client_configs import (
    CLIENT_CUSTOM_BOLD,
    CLIENT_CUSTOM_HEADINGS,
    CLIENT_CUSTOM_LISTS,
    CLIENT_ADVANCED,
    get_client_config
)


# Sample HTML from a typical Google Doc
SAMPLE_HTML = """
<h2>Main Product Title</h2>
<p>This is an introduction paragraph with <strong>bold text</strong> and <em>italic text</em>.</p>

<h3>Key Features</h3>
<ul>
    <li>Feature one with details</li>
    <li>Feature two with specifications</li>
    <li>Feature three with benefits</li>
</ul>

<p class="aligncenter">This is a centered paragraph.</p>

<blockquote>
This is an important quote that should stand out.
</blockquote>

<p>Regular paragraph with <strong>emphasis</strong> and a <a href="https://example.com">link</a>.</p>
"""


def test_client(client_id: str, config: dict = None):
    """Test a client configuration."""
    print("=" * 80)

    if config is None:
        config = get_client_config(client_id)

    print(f"Testing: {config['name']}")
    print(f"Description: {config['description']}")
    print("=" * 80)

    transformer = HTMLTransformer(config)
    result = transformer.transform(SAMPLE_HTML)

    print("\nORIGINAL HTML:")
    print("-" * 80)
    print(SAMPLE_HTML)

    print("\nTRANSFORMED HTML:")
    print("-" * 80)
    print(result)
    print("\n" + "=" * 80 + "\n")


def test_all_clients():
    """Test all predefined clients."""
    print("\n🧪 TESTING ALL CLIENT CONFIGURATIONS\n")

    test_client("default")
    test_client("client-a", CLIENT_CUSTOM_BOLD)
    test_client("client-b", CLIENT_CUSTOM_HEADINGS)
    test_client("client-c", CLIENT_CUSTOM_LISTS)
    test_client("client-d", CLIENT_ADVANCED)

    print("✅ All tests complete!")
    print("\nTo use in production:")
    print("  python agents.py")
    print('  Then: "Publish this doc for client-a: [URL]"')


def test_specific_transformation():
    """Test a specific transformation interactively."""
    print("\n🔬 INTERACTIVE TRANSFORMATION TEST\n")

    # Your custom HTML to test
    custom_html = """
    <p>Test your HTML here with <strong>formatting</strong>.</p>
    """

    # Your custom config to test
    test_config = {
        "name": "Test Config",
        "description": "Testing specific transformations",
        "transformations": {
            "tag_replacements": {
                "strong": {
                    "new_tag": "b",
                    "preserve_content": True
                }
            },
            "attribute_rules": {
                "p": {
                    "add_class": "test-paragraph",
                    "add_style": "color: blue;"
                }
            },
            "style_injections": {},
            "class_mappings": {},
            "custom_wrappers": []
        }
    }

    transformer = HTMLTransformer(test_config)
    result = transformer.transform(custom_html)

    print("Input:")
    print(custom_html)
    print("\nOutput:")
    print(result)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # Test specific client
        client_id = sys.argv[1]
        test_client(client_id)
    else:
        # Test all clients
        test_all_clients()

    # Uncomment to test specific transformation
    # test_specific_transformation()
