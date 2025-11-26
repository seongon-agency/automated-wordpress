"""
Debug script: Test <sup> pattern with REAL Google Docs HTML.
Paste actual HTML from your Google Docs to see why patterns aren't matching.
"""

import sys
sys.path.insert(0, 'src')

from utils.pattern_engine import apply_all_patterns
from database import get_project

# Load your actual project patterns
project = get_project("testdangbai")
patterns = project['html_configs']['patterns']

print("="*80)
print("DEBUG: <sup> TAG REMOVAL WITH REAL GOOGLE DOCS HTML")
print("="*80)

# Find all sup patterns
sup_patterns = [p for p in patterns if 'sup' in p.get('source_pattern', '').lower()]

print(f"\n📋 Found {len(sup_patterns)} <sup> pattern(s):")
for i, p in enumerate(sup_patterns, 1):
    print(f"\n  Pattern {i}:")
    print(f"    Element: {p.get('element_type')}")
    print(f"    Source: {p.get('source_pattern')}")
    print(f"    Target: '{p.get('target_pattern')}'")

# Sample REAL Google Docs HTML (common variations)
test_cases = {
    "Simple superscript": '<p>Text with footnote<sup>1</sup> here.</p>',

    "Superscript with link": '<p>Text<sup><a href="#cmnt1" id="cmnt_ref1">[a]</a></sup> here.</p>',

    "Superscript with ID": '<p>Text<sup id="ftnt1">1</sup> here.</p>',

    "Superscript with span": '<p>Text<sup><span>1</span></sup> here.</p>',

    "Multiple attributes": '<p>Text<sup id="fn1" class="footnote">1</sup> here.</p>',

    "Google Docs comment style": '<p>Text<sup><a href="#cmnt_ref1" id="cmnt1">[1]</a></sup> here.</p>',
}

print("\n" + "="*80)
print("TESTING PATTERNS ON DIFFERENT <sup> VARIATIONS")
print("="*80)

for test_name, test_html in test_cases.items():
    print(f"\n{'─'*80}")
    print(f"TEST: {test_name}")
    print(f"{'─'*80}")

    print(f"\n📄 ORIGINAL HTML:")
    print(f"  {test_html}")

    # Test each sup pattern individually
    for i, pattern in enumerate(sup_patterns, 1):
        from utils.pattern_engine import apply_pattern
        result = apply_pattern(test_html, pattern)

        if result != test_html:
            print(f"\n  ✅ Pattern {i} ({pattern.get('element_type')}) MATCHED!")
            print(f"     Result: {result}")
        else:
            print(f"\n  ❌ Pattern {i} ({pattern.get('element_type')}) did NOT match")

    # Test with all patterns applied
    print(f"\n  🔄 Applying ALL 30 patterns sequentially...")
    final_result = apply_all_patterns(test_html, patterns)

    if final_result != test_html:
        print(f"  ✅ FINAL RESULT (after all patterns):")
        print(f"     {final_result}")
    else:
        print(f"  ❌ NO CHANGE after applying all patterns")

print("\n" + "="*80)
print("RECOMMENDATIONS:")
print("="*80)
print("""
If patterns aren't matching, the issue is likely:

1. **Pattern Order**: <sup> patterns are #1-3, but patterns #29-30 (span patterns)
   might be interfering. Try moving <sup> patterns to the END of the list.

2. **Regex Not Matching**: Your actual Google Docs <sup> tags might have:
   - Different attributes (id="", class="")
   - Nested elements (<span>, <a>)
   - Whitespace or newlines

3. **Try this pattern** (catches ALL variations):
   Source: <sup\\b[^>]*>.*?</sup>
   Target: (empty)

   The \\b ensures we match the word boundary.

4. **Debug your actual HTML**:
   - Export a Google Doc
   - Look at the actual <sup> tag structure
   - Adjust pattern to match exactly

5. **Test with Quick Publish**: Test one paragraph with a <sup> tag to see
   if it gets removed or not.
""")

print("\n💡 NEXT STEPS:")
print("1. Copy actual HTML from your Google Docs (with <sup> tags)")
print("2. Add it to this script as a new test case")
print("3. Run: python3 debug_sup_real.py")
print("4. See which pattern (if any) matches your actual HTML structure")
print("\n" + "="*80 + "\n")
