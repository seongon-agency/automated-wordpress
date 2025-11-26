"""
Debug script: Understanding the caption generation order issue.

The workflow applies transformations in this order:
1. Apply user's HTML patterns (Step 5)
2. Generate WordPress captions (after Step 5)

This means if you have a pattern to format images, it gets applied BEFORE
the caption generator runs, which might overwrite your pattern changes.
"""

import sys
sys.path.insert(0, 'src')

from utils.pattern_engine import apply_all_patterns
from tools.wordpress_uploader import replace_images_with_wordpress_captions
from database import get_project

print("="*80)
print("DEBUG: Caption Generation Order Issue")
print("="*80)

# Sample HTML (as it comes from Google Docs)
original_html = """
<p style="text-align: center;"><img src="https://lh3.googleusercontent.com/image1.jpg" alt="Beautiful Sunset" width="1600" height="900"></p>
<p>Some text here.</p>
"""

print("\n📄 ORIGINAL HTML (from Google Docs):")
print(original_html)

# Load project patterns
project = get_project("testdangbai")
patterns = project['html_configs']['patterns']

print(f"\n📋 Found {len(patterns)} pattern(s) in project")

# Find image-related patterns
image_patterns = [p for p in patterns if 'image' in p.get('element_type', '').lower()]
if image_patterns:
    print(f"\n🖼️  Found {len(image_patterns)} image-related pattern(s):")
    for i, p in enumerate(image_patterns, 1):
        print(f"\n  Pattern {i} ({p.get('element_type')}):")
        print(f"    Source: {p.get('source_pattern')[:80]}...")
        print(f"    Target: {p.get('target_pattern')[:80]}...")

# STEP 5: Apply user's patterns
print("\n" + "="*80)
print("STEP 5: Apply User's HTML Patterns")
print("="*80)

transformed_html = apply_all_patterns(original_html, patterns)
print("\n✓ RESULT after applying patterns:")
print(transformed_html)

if transformed_html == original_html:
    print("\n⚠️  No changes! Patterns didn't match the HTML structure.")
else:
    print("\n✓ HTML was transformed by patterns")

# STEP 5.5: Generate WordPress captions (happens AFTER patterns)
print("\n" + "="*80)
print("STEP 5.5: Generate WordPress Captions (HARDCODED)")
print("="*80)

# Simulate WordPress upload metadata
enriched_metadata = [
    {
        'media_id': 12345,
        'url': 'https://dangbai.seongon.com/wp-content/uploads/2024/11/image1.jpg',
        'alt': 'Beautiful Sunset',
        'width': 1200,
        'height': 675,
        'original_filename': 'image1.jpg'
    }
]

print("\n🎨 Applying hardcoded caption generation...")
final_html = replace_images_with_wordpress_captions(
    transformed_html,  # Uses result from STEP 5
    enriched_metadata,
    target_width=1200
)

print("\n✓ FINAL HTML (after caption generation):")
print(final_html)

# Analysis
print("\n" + "="*80)
print("ANALYSIS:")
print("="*80)

print("""
The workflow order is:
  1. Apply user's HTML patterns (your custom transformations)
  2. Generate WordPress captions (hardcoded function)

This creates TWO problems:

Problem 1: USER PATTERNS CAN'T CONTROL CAPTIONS
  - If you have a pattern to format image captions, it's applied BEFORE
    the caption generator runs
  - The caption generator then overwrites your pattern changes
  - Your pattern basically has no effect

Problem 2: CAPTION GENERATOR CAN'T BE DISABLED/CUSTOMIZED
  - The caption generator is HARDCODED in the workflow
  - It ALWAYS wraps images with [caption] shortcodes
  - You can't use patterns to remove or customize caption format
  - Even with empty target_pattern (""), the caption generator still runs

SOLUTIONS:

Option A: Move caption generation BEFORE pattern application
  - Generate captions first
  - Then apply user patterns to customize caption format
  - This lets patterns control the final caption structure

Option B: Make caption generation optional/configurable
  - Add a project setting: "enable_auto_captions" (true/false)
  - Only call replace_images_with_wordpress_captions() if enabled
  - Let patterns handle caption formatting when disabled

Option C: Use patterns INSTEAD of hardcoded function
  - Remove the hardcoded caption generator
  - Provide caption patterns as examples in pattern library
  - Gives users full control over caption format via patterns
""")

print("\n💡 RECOMMENDATION:")
print("   Implement Option B: Make caption generation configurable")
print("   This preserves current behavior but gives users control.")

print("\n" + "="*80 + "\n")
