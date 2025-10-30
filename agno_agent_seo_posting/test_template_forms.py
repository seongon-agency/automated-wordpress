"""
Test script for template form extraction and intelligent application.

This tests the new Version 2.0 functionality:
1. Extract ALL unique forms from template
2. Intelligently apply the most appropriate form based on content context
"""

from utils.template_parser import extract_template_rules
from tools.html_formatter import format_html_with_template


def test_template_extraction():
    """Test that template parser extracts all unique forms."""
    print("="*80)
    print("TEST 1: Template Form Extraction")
    print("="*80)

    # Template with multiple paragraph forms
    template_html = """
    <html>
        <body>
            <p dir="ltr" style="text-align: justify; font-size: 16px;">Regular text paragraph 1</p>
            <p dir="ltr" style="text-align: justify; font-size: 16px;">Regular text paragraph 2</p>
            <p dir="ltr" style="text-align: justify; font-size: 16px;">Regular text paragraph 3</p>
            <p dir="ltr" style="text-align: center; font-size: 16px;">Image paragraph 1</p>
            <p dir="ltr" style="text-align: center; font-size: 16px;">Image paragraph 2</p>
            <img class="aligncenter size-full" alt="Template" />
            <h2 style="color: #333; font-weight: bold; font-size: 24px;">Heading Style</h2>
        </body>
    </html>
    """

    rules = extract_template_rules(template_html)

    # Check paragraph rules
    print("\n📝 Paragraph Rules:")
    if 'p' in rules:
        p_rule = rules['p']
        print(f"  Default: {p_rule.get('default', {})}")
        print(f"  Justify: {p_rule.get('justify', {})}")
        print(f"  Center: {p_rule.get('center', {})}")
        print(f"  Total variants found: {len(p_rule.get('variants', []))}")

        for i, variant in enumerate(p_rule.get('variants', []), 1):
            print(f"\n  Variant {i} (used {variant['count']} times):")
            for attr, value in variant['attrs'].items():
                print(f"    {attr}: {value}")

    # Check image rules
    print("\n🖼️  Image Rules:")
    if 'img' in rules:
        img_rule = rules['img']
        print(f"  Default: {img_rule.get('default', {})}")
        print(f"  Total variants found: {len(img_rule.get('variants', []))}")

    # Check heading rules
    print("\n📑 H2 Heading Rules:")
    if 'h2' in rules:
        h2_rule = rules['h2']
        print(f"  Default: {h2_rule.get('default', {})}")
        print(f"  Total variants found: {len(h2_rule.get('variants', []))}")

    print("\n✅ Template extraction test complete!\n")
    return rules


def test_intelligent_formatting():
    """Test that formatter applies the correct form based on content context."""
    print("="*80)
    print("TEST 2: Intelligent Form Application")
    print("="*80)

    # Template with two paragraph forms
    template_html = """
    <html>
        <body>
            <p dir="ltr" style="text-align: justify; font-size: 16px; line-height: 1.6;">Text paragraph 1</p>
            <p dir="ltr" style="text-align: justify; font-size: 16px; line-height: 1.6;">Text paragraph 2</p>
            <p dir="ltr" style="text-align: center; font-size: 16px;">Image paragraph 1</p>
            <img class="aligncenter size-full wp-image-123" />
            <h2 style="color: #2c3e50; font-weight: bold;">Heading</h2>
        </body>
    </html>
    """

    # Content with different paragraph types
    content_html = """
    <html>
        <body>
            <h2>My Article Title</h2>
            <p>This is a regular text paragraph that should get justify alignment.</p>
            <p>Another text paragraph with more content.</p>
            <p><img src="image1.jpg" alt="Image 1" /></p>
            <p>Back to regular text.</p>
            <p><img src="image2.jpg" alt="Image 2" /></p>
        </body>
    </html>
    """

    result = format_html_with_template(content_html, template_html)

    if result['success']:
        print("\n✅ Formatting successful!")
        print("\n📄 Formatted HTML (first 1500 chars):")
        print("-" * 80)
        formatted = result['formatted_html']
        print(formatted[:1500])
        print("-" * 80)

        # Check if paragraphs are correctly formatted
        print("\n🔍 Verifying formatting:")

        # Check for justify alignment in text paragraphs
        if 'text-align: justify' in formatted or 'text-align:justify' in formatted:
            print("  ✓ Justify alignment found (for text paragraphs)")
        else:
            print("  ✗ Justify alignment NOT found")

        # Check for center alignment in image paragraphs
        if 'text-align: center' in formatted or 'text-align:center' in formatted:
            print("  ✓ Center alignment found (for image paragraphs)")
        else:
            print("  ✗ Center alignment NOT found")

        # Check for heading formatting
        if 'color' in formatted and 'h2' in formatted.lower():
            print("  ✓ H2 heading formatting applied")
        else:
            print("  ✗ H2 heading formatting NOT applied")

        # Check for image class
        if 'aligncenter' in formatted:
            print("  ✓ Image class applied")
        else:
            print("  ✗ Image class NOT applied")

    else:
        print(f"\n❌ Formatting failed: {result['error']}")

    print("\n✅ Intelligent formatting test complete!\n")
    return result


def test_edge_cases():
    """Test edge cases and special scenarios."""
    print("="*80)
    print("TEST 3: Edge Cases")
    print("="*80)

    # Template with only one paragraph form
    template_html = """
    <html>
        <body>
            <p dir="ltr" style="text-align: justify;">Single form paragraph</p>
        </body>
    </html>
    """

    content_html = """
    <html>
        <body>
            <p>Text paragraph</p>
            <p><img src="test.jpg" /></p>
        </body>
    </html>
    """

    result = format_html_with_template(content_html, template_html)

    print(f"\n✅ Edge case test: {('PASSED' if result['success'] else 'FAILED')}")
    print("   (Template with single form should still work)")

    return result


if __name__ == "__main__":
    print("\n" + "="*80)
    print("🧪 TESTING TEMPLATE FORM EXTRACTION & INTELLIGENT APPLICATION")
    print("="*80 + "\n")

    try:
        # Run tests
        test_template_extraction()
        test_intelligent_formatting()
        test_edge_cases()

        print("="*80)
        print("✅ ALL TESTS COMPLETED!")
        print("="*80 + "\n")

    except Exception as e:
        print(f"\n❌ TEST FAILED WITH ERROR:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
