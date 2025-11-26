#!/usr/bin/env python3
"""
Diagnostic script to check what's happening with Sunhouse HTML transformation
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.database import get_project
from src.utils.pattern_engine import apply_all_patterns

# Real HTML from user's post
user_html_sample = '''<p style="text-align: center;"><strong>Quạt trần kêu ù ù </strong>có thể xuất phát từ nhiều nguyên nhân như bụi bám dày, các bộ phận lắp đặt bị lỏng, động cơ khô dầu hoặc vòng bi mòn.</p>

<img class="wp-image-19536 size-full" src="https://dangbai.seongon.com/wp-content/uploads/2025/11/resized_sun-house_1-7.jpg" alt="" width="800" height="535" />
<p style="text-align: center;">Quạt trần kêu ù ù có thể do ốc vít hoặc khớp nối bị lỏng</p>'''

# Simulate what Google Docs SHOULD produce
google_docs_html_sample = '''<p style="text-align: justify;"><strong>Quạt trần kêu ù ù </strong>có thể xuất phát từ nhiều nguyên nhân như bụi bám dày, các bộ phận lắp đặt bị lỏng, động cơ khô dầu hoặc vòng bi mòn.</p>

<p style="text-align: justify;"><img class="wp-image-19536 size-full" src="https://dangbai.seongon.com/wp-content/uploads/2025/11/resized_sun-house_1-7.jpg" alt="" width="800" height="535" /></p>
<p style="text-align: center;">Quạt trần kêu ù ù có thể do ốc vít hoặc khớp nối bị lỏng</p>'''

print("=" * 80)
print("SUNHOUSE HTML TRANSFORMATION DIAGNOSIS")
print("=" * 80)
print()

# Get project patterns
project = get_project('sun-house')
patterns = project.get('html_configs', {}).get('patterns', [])

print("TEST 1: User's Current WordPress HTML")
print("=" * 80)
print()
print("INPUT (from WordPress):")
print(user_html_sample)
print()
print("APPLYING PATTERNS...")
result1 = apply_all_patterns(user_html_sample, patterns)
print()
print("OUTPUT:")
print(result1)
print()
print("ANALYSIS:")
if '<p style="text-align:center"><img' in result1 or '<p style="text-align: center"><img' in result1:
    print("✅ Images in paragraphs ARE centered")
else:
    print("❌ Images in paragraphs are NOT centered")

# Check for standalone images
if result1.count('<img') > result1.count('<p><img') + result1.count('<p style="text-align:center"><img') + result1.count('<p style="text-align: center"><img'):
    print("⚠️  WARNING: Found STANDALONE images (not wrapped in <p> tags)")
    print("    The p_with_img pattern CANNOT match standalone images!")
else:
    print("✓ All images are wrapped in <p> tags")
print()
print()

print("TEST 2: Expected Google Docs HTML")
print("=" * 80)
print()
print("INPUT (simulated Google Docs):")
print(google_docs_html_sample)
print()
print("APPLYING PATTERNS...")
result2 = apply_all_patterns(google_docs_html_sample, patterns)
print()
print("OUTPUT:")
print(result2)
print()
print("ANALYSIS:")
if '<p style="text-align:center"><img' in result2 or '<p style="text-align: center"><img' in result2:
    print("✅ Images in paragraphs ARE centered")
else:
    print("❌ Images in paragraphs are NOT centered")
print()
print()

print("=" * 80)
print("DIAGNOSIS SUMMARY")
print("=" * 80)
print()
print("The problem is likely:")
print()
print("1. GOOGLE DOCS IS NOT WRAPPING IMAGES IN <p> TAGS")
print("   - Your Google Docs might have images as standalone blocks")
print("   - The pattern <p[^>]*>(.*?<img[^>]*>.*?)</p> can ONLY match images INSIDE <p> tags")
print()
print("2. WORDPRESS IS STRIPPING <p> TAGS FROM IMAGES")
print("   - Some WordPress themes/plugins automatically unwrap images from <p> tags")
print("   - This happens AFTER our transformation, so our patterns can't fix it")
print()
print("SOLUTION:")
print()
print("You need to add a NEW pattern that matches STANDALONE images:")
print()
print("Pattern:")
print('  Element Type: standalone_img')
print('  Source: <img[^>]*>')
print('  Target: <p style="text-align:center"><img alt="" src="..." /></p>')
print()
print("But this is tricky because we need to wrap the image AND preserve the src...")
print("Let me create a better solution for you.")
