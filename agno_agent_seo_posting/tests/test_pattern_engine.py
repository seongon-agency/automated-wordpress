"""
Test script for pattern engine - HTML transformation testing.
"""

import sys
from utils.pattern_engine import apply_pattern, apply_all_patterns, transform_html_with_config
from tools.html_transformer import transform_html


def test_pattern_engine():
    """Test pattern engine transformations."""
    print("="*80)
    print("TESTING PATTERN ENGINE")
    print("="*80)

    # Sample HTML input
    sample_html = """
    <p>This is a simple paragraph.</p>
    <p>This is another paragraph with <b>bold text</b>.</p>
    <h2>A Heading</h2>
    <p>Paragraph after heading.</p>
    <ul>
        <li>Item 1</li>
        <li>Item 2</li>
    </ul>
    """

    print("\n1. Testing single pattern transformation...")
    print("   Input HTML:")
    print(f"   {sample_html.strip()[:100]}...")

    # Test single pattern - add class to <p> tags
    pattern = {
        "element_type": "p",
        "source_pattern": r"<p[^>]*>(.*?)</p>",
        "target_pattern": r'<p class="article-text">\1</p>'
    }

    result = apply_pattern(sample_html, pattern)

    if 'class="article-text"' in result:
        print("   [OK] Pattern applied - class added to <p> tags")
    else:
        print("   [ERROR] Pattern not applied correctly")
        print(f"   Result: {result}")

    # Test multiple patterns
    print("\n2. Testing multiple patterns...")
    patterns = [
        {
            "element_type": "p",
            "source_pattern": r"<p[^>]*>(.*?)</p>",
            "target_pattern": r'<p class="article-text">\1</p>'
        },
        {
            "element_type": "strong",
            "source_pattern": r"<b>(.*?)</b>",
            "target_pattern": r"<strong>\1</strong>"
        },
        {
            "element_type": "h2",
            "source_pattern": r"<h2[^>]*>(.*?)</h2>",
            "target_pattern": r'<h2 class="section-header">\1</h2>'
        }
    ]

    result = apply_all_patterns(sample_html, patterns)

    checks = [
        ('class="article-text"', "Paragraph classes"),
        ("<strong>bold text</strong>", "Bold to strong conversion"),
        ('class="section-header"', "H2 classes")
    ]

    all_passed = True
    for check_string, check_name in checks:
        if check_string in result:
            print(f"   [OK] {check_name}")
        else:
            print(f"   [ERROR] {check_name} - not found")
            all_passed = False

    if not all_passed:
        print("\n   Transformed HTML:")
        print(result)

    # Test with html_configs format (as stored in database)
    print("\n3. Testing with html_configs format (database format)...")
    html_configs = {
        "patterns": [
            {
                "element_type": "p",
                "source_pattern": r"<p[^>]*>(.*?)</p>",
                "target_pattern": r'<p class="test-paragraph">\1</p>'
            },
            {
                "element_type": "ul",
                "source_pattern": r"<ul[^>]*>(.*?)</ul>",
                "target_pattern": r'<ul class="bullet-list">\1</ul>'
            }
        ]
    }

    result = transform_html_with_config(sample_html, html_configs)

    if 'class="test-paragraph"' in result and 'class="bullet-list"' in result:
        print("   [OK] html_configs format works correctly")
    else:
        print("   [ERROR] html_configs format not working")
        print(f"   Result: {result}")

    # Test the html_transformer tool
    print("\n4. Testing html_transformer tool...")
    tool_result = transform_html(sample_html, html_configs)

    if tool_result['success']:
        print(f"   [OK] Tool succeeded - {tool_result['patterns_applied']} patterns applied")
        if 'class="test-paragraph"' in tool_result['transformed_html']:
            print("   [OK] Transformation verified in output")
        else:
            print("   [ERROR] Transformation not found in output")
    else:
        print(f"   [ERROR] Tool failed: {tool_result.get('error', 'Unknown error')}")

    # Test edge case - no patterns
    print("\n5. Testing edge case - no patterns...")
    result = transform_html(sample_html, None)
    if result['success'] and result['patterns_applied'] == 0:
        print("   [OK] Handles None html_configs correctly")
    else:
        print("   [ERROR] Failed to handle None html_configs")

    # Test edge case - empty patterns
    print("\n6. Testing edge case - empty patterns...")
    result = transform_html(sample_html, {"patterns": []})
    if result['success'] and result['patterns_applied'] == 0:
        print("   [OK] Handles empty patterns correctly")
    else:
        print("   [ERROR] Failed to handle empty patterns")

    print("\n" + "="*80)
    print("[OK] PATTERN ENGINE TESTS COMPLETE!")
    print("="*80)


if __name__ == "__main__":
    try:
        test_pattern_engine()
    except Exception as e:
        print(f"\n[ERROR] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
