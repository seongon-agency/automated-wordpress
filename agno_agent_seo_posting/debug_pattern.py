#!/usr/bin/env python3
"""
Debug script to test pattern matching for paragraphs with images
"""

import re

# Test HTML - your exact example
test_html = '''<p style="text-align: justify;"><img class="wp-image-19382 size-full" src="https://dangbai.seongon.com/wp-content/uploads/2025/11/resized_sun-house_2-4.jpg" alt="" width="800" height="535" /></p>'''

print("=" * 80)
print("TESTING PARAGRAPH WITH IMAGE PATTERN")
print("=" * 80)
print()

print("INPUT HTML:")
print(test_html)
print()

# Test different pattern variations
patterns_to_test = [
    {
        "name": "Pattern 1: Basic p with img",
        "source": r"<p[^>]*>.*?<img[^>]*>.*?</p>",
        "target": r'<p style="text-align: center">\1</p>'
    },
    {
        "name": "Pattern 2: Capture everything inside p",
        "source": r"<p[^>]*>(.*?<img[^>]*>.*?)</p>",
        "target": r'<p style="text-align: center">\1</p>'
    },
    {
        "name": "Pattern 3: Match any style and img",
        "source": r'<p[^>]*style="[^"]*"[^>]*>(.*?<img[^>]*>.*?)</p>',
        "target": r'<p style="text-align: center">\1</p>'
    },
    {
        "name": "Pattern 4: Explicit justify + img",
        "source": r'<p[^>]*style="[^"]*text-align:\s*justify[^"]*"[^>]*>(.*?<img[^>]*>.*?)</p>',
        "target": r'<p style="text-align: center">\1</p>'
    },
]

for i, pattern in enumerate(patterns_to_test, 1):
    print(f"{'='*80}")
    print(f"TEST {i}: {pattern['name']}")
    print(f"{'='*80}")
    print(f"Source pattern: {pattern['source']}")
    print(f"Target pattern: {pattern['target']}")
    print()

    try:
        # Check if pattern matches
        match = re.search(pattern['source'], test_html, flags=re.IGNORECASE | re.DOTALL)

        if match:
            print("✅ PATTERN MATCHES")
            print(f"   Matched text: {match.group(0)[:100]}...")
            if match.groups():
                print(f"   Captured groups: {len(match.groups())}")
                for idx, group in enumerate(match.groups(), 1):
                    print(f"   Group {idx}: {group[:100]}...")

            # Apply transformation
            result = re.sub(
                pattern['source'],
                pattern['target'],
                test_html,
                flags=re.IGNORECASE | re.DOTALL
            )

            print()
            print("OUTPUT HTML:")
            print(result)
            print()

            # Check if it worked
            if 'text-align: center' in result or 'text-align:center' in result:
                print("✅ SUCCESS - Image paragraph is now centered!")
            else:
                print("❌ FAILED - Still not centered")
        else:
            print("❌ PATTERN DOES NOT MATCH")
            print("   The regex doesn't match the input HTML")

    except re.error as e:
        print(f"❌ REGEX ERROR: {e}")

    print()

print("=" * 80)
print("RECOMMENDATION")
print("=" * 80)
print()
print("Use the pattern that shows '✅ SUCCESS' above.")
print("If none worked, there might be an issue with how patterns are stored/applied.")
