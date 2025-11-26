"""
Debug script: Why captions aren't being generated - URL matching issue.

The problem is likely that:
1. HTML still has Google Docs URLs (https://lh3.googleusercontent.com/...)
2. Metadata has WordPress URLs (https://dangbai.seongon.com/...)
3. Filenames don't match because resized files have different names

This script simulates the actual workflow to identify the mismatch.
"""

import sys
sys.path.insert(0, 'src')

from bs4 import BeautifulSoup

print("="*80)
print("DEBUG: Caption Matching Issue")
print("="*80)

# Simulate actual HTML after transformations (still has Google Docs URLs)
html_after_transforms = """
<p>Some content here.</p>
<p><img src="https://lh3.googleusercontent.com/d/1abc123xyz" alt="Test Image" width="1600" height="900"></p>
<p>More content.</p>
"""

# Simulate enriched metadata (has WordPress URLs and resized filenames)
enriched_metadata = [
    {
        'media_id': 12345,
        'url': 'https://dangbai.seongon.com/wp-content/uploads/2024/11/resized_testdangbai_1.jpg',
        'alt': 'Test Image',
        'width': 1200,
        'height': 675,
        'original_filename': 'resized_testdangbai_1.jpg'  # Note: This is the RESIZED filename!
    }
]

print("\n📄 HTML (after patterns, before captions):")
print(html_after_transforms)

print("\n📊 Enriched Metadata:")
for meta in enriched_metadata:
    print(f"  media_id: {meta['media_id']}")
    print(f"  url: {meta['url']}")
    print(f"  original_filename: {meta['original_filename']}")
    print(f"  alt: {meta['alt']}")

# Simulate the matching logic from replace_images_with_wordpress_captions
print("\n" + "="*80)
print("MATCHING LOGIC SIMULATION")
print("="*80)

soup = BeautifulSoup(html_after_transforms, 'html.parser')

# Create metadata map (same as function)
metadata_map = {}
for item in enriched_metadata:
    metadata_map[item['url']] = item
    if 'original_filename' in item:
        metadata_map[item['original_filename']] = item

print("\n📋 Metadata Map Keys:")
for key in metadata_map.keys():
    print(f"  - {key}")

# Try to match images
print("\n🔍 Attempting to match images:")
for img in soup.find_all('img'):
    src = img.get('src', '')
    print(f"\n  Image src: {src}")

    # Try to find matching metadata
    meta = None
    for key, value in metadata_map.items():
        print(f"    Checking if '{key}' in '{src}' or vice versa...")
        if key in src or src in key:
            print(f"      ✅ MATCH FOUND!")
            meta = value
            break
        else:
            print(f"      ❌ No match")

    if not meta:
        print(f"  ⚠️  NO METADATA FOUND for this image!")
        print(f"  This is why captions aren't being generated!")

print("\n" + "="*80)
print("ROOT CAUSE")
print("="*80)
print("""
The problem is clear:

1. HTML has Google Docs URLs:
   https://lh3.googleusercontent.com/d/1abc123xyz

2. Metadata has WordPress URLs:
   https://dangbai.seongon.com/wp-content/uploads/2024/11/resized_testdangbai_1.jpg

3. Metadata has resized filenames:
   resized_testdangbai_1.jpg

4. There's NO connection between the old and new URLs!

The caption generator can't match images because:
- WordPress URL is NOT in Google Docs URL
- Resized filename is NOT in Google Docs URL
- There's no mapping between old and new

SOLUTIONS:

Option 1: Replace URLs BEFORE caption generation
  - First call replace_image_urls_in_html() to update URLs
  - Then call replace_images_with_wordpress_captions()
  - This way images have WordPress URLs when caption generator runs

Option 2: Improve metadata to include original URL
  - Add 'original_src' to enriched_metadata
  - Match by original_src first, then by filename

Option 3: Match by alt text
  - If alt text is unique, use it as matching key
  - Risky if alt text is empty or duplicated
""")

print("\n💡 RECOMMENDATION:")
print("   Option 1 is the safest and simplest fix.")
print("   Modify the workflow to replace URLs before generating captions.")
print("\n" + "="*80 + "\n")
