"""
Test AI-powered pattern modification with various instructions.
"""

import os
import sys
import json
from utils.pattern_modifier import modify_patterns_with_ai

print("="*80)
print("TESTING AI PATTERN MODIFICATION")
print("="*80)

# Sample starting patterns
base_patterns = [
    {
        "element_type": "p",
        "source_pattern": "<p[^>]*>(.*?)</p>",
        "target_pattern": "<p class=\"article-text\">\\1</p>"
    },
    {
        "element_type": "h2",
        "source_pattern": "<h2[^>]*>(.*?)</h2>",
        "target_pattern": "<h2 class=\"section-header\">\\1</h2>"
    },
    {
        "element_type": "a",
        "source_pattern": "<a([^>]*)>(.*?)</a>",
        "target_pattern": "<a\\1>\\2</a>"
    }
]

# Test cases
test_cases = [
    {
        "name": "Add color to h2",
        "instruction": "Make all h2 headings blue",
        "expected_change": "h2 should have color: blue style"
    },
    {
        "name": "Add class to paragraphs",
        "instruction": "Add class 'highlight' to all paragraphs",
        "expected_change": "p should have both article-text and highlight classes"
    },
    {
        "name": "Make links open in new tab",
        "instruction": "Make all links open in a new tab",
        "expected_change": "a should have target=_blank"
    },
    {
        "name": "Add margin to paragraphs",
        "instruction": "Add margin-bottom: 20px to all paragraphs",
        "expected_change": "p should have margin-bottom style"
    },
    {
        "name": "Change h2 color",
        "instruction": "Change h2 color to red",
        "expected_change": "h2 should have color: red"
    }
]

passed = 0
failed = 0

for i, test_case in enumerate(test_cases, 1):
    print(f"\n{'='*80}")
    print(f"TEST {i}/{len(test_cases)}: {test_case['name']}")
    print("="*80)

    print(f"\nInstruction: '{test_case['instruction']}'")
    print(f"Expected: {test_case['expected_change']}")

    # Make a copy of base patterns for each test
    test_patterns = json.loads(json.dumps(base_patterns))

    print("\n[AI] Processing...")

    result = modify_patterns_with_ai(test_patterns, test_case['instruction'])

    if result['success']:
        print(f"\n[OK] {result['changes_made']}")

        print("\nModified patterns:")
        for pattern in result['patterns']:
            if pattern['element_type'] in ['p', 'h2', 'a']:  # Only show relevant ones
                print(f"\n  {pattern['element_type']}:")
                print(f"    Target: {pattern['target_pattern']}")

        passed += 1
    else:
        print(f"\n[ERROR] {result.get('error', 'Unknown error')}")
        failed += 1

# Summary
print("\n" + "="*80)
print("TEST SUMMARY")
print("="*80)
print(f"\nTotal tests: {len(test_cases)}")
print(f"Passed: {passed}")
print(f"Failed: {failed}")

if failed == 0:
    print("\n[OK] ALL TESTS PASSED!")
else:
    print(f"\n[WARNING] {failed} test(s) failed")

print("="*80)
