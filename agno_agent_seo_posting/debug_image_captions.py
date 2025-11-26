"""
Debug script for testing WordPress caption generation for images.
"""

import sys
sys.path.insert(0, 'src')

from tools.wordpress_uploader import (
    extract_image_metadata_from_html,
    replace_images_with_wordpress_captions
)

print("="*80)
print("DEBUG: WordPress Image Caption Generation")
print("="*80)

# Sample HTML with images (typical Google Docs output)
test_html = """
<p style="text-align: center;"><img src="https://lh3.googleusercontent.com/image1.jpg" alt="Beautiful Sunset" width="1600" height="900"></p>
<p>Some text here.</p>
<p style="text-align: center;"><img src="https://lh3.googleusercontent.com/image2.png" alt="Mountain View" width="1920" height="1080"></p>
"""

print("\n📄 ORIGINAL HTML:")
print(test_html)

# Step 1: Extract metadata from original HTML
print("\n" + "="*80)
print("STEP 1: Extract Image Metadata from Original HTML")
print("="*80)

original_metadata = extract_image_metadata_from_html(test_html)

print(f"\nExtracted metadata for {len(original_metadata)} images:")
for filename, meta in original_metadata.items():
    print(f"\n  {filename}:")
    print(f"    alt: {meta.get('alt')}")
    print(f"    width: {meta.get('width')}")
    print(f"    height: {meta.get('height')}")
    print(f"    src: {meta.get('src')}")

# Step 2: Simulate WordPress upload (enriched metadata)
print("\n" + "="*80)
print("STEP 2: Simulate WordPress Upload & Metadata Enrichment")
print("="*80)

enriched_metadata = [
    {
        'media_id': 12345,
        'url': 'https://mywordpress.com/wp-content/uploads/2024/11/image1.jpg',
        'alt': 'Beautiful Sunset',
        'width': 1200,
        'height': 675,
        'original_filename': 'image1.jpg'
    },
    {
        'media_id': 12346,
        'url': 'https://mywordpress.com/wp-content/uploads/2024/11/image2.png',
        'alt': 'Mountain View',
        'width': 1200,
        'height': 675,
        'original_filename': 'image2.png'
    }
]

print(f"\nEnriched metadata for {len(enriched_metadata)} images:")
for meta in enriched_metadata:
    print(f"\n  {meta['original_filename']}:")
    print(f"    media_id: {meta['media_id']}")
    print(f"    url: {meta['url']}")
    print(f"    alt: {meta['alt']}")
    print(f"    width: {meta['width']}")
    print(f"    height: {meta['height']}")

# Step 3: Generate WordPress captions
print("\n" + "="*80)
print("STEP 3: Generate WordPress Caption Shortcodes")
print("="*80)

result_html = replace_images_with_wordpress_captions(
    test_html,
    enriched_metadata,
    target_width=1200
)

print("\n✅ RESULT HTML:")
print(result_html)

# Verify caption format
print("\n" + "="*80)
print("VERIFICATION:")
print("="*80)

expected_patterns = [
    '[caption id="attachment_12345"',
    '[caption id="attachment_12346"',
    'class="wp-image-12345 size-full"',
    'class="wp-image-12346 size-full"',
    'Beautiful Sunset',
    'Mountain View',
    'width="1200"',
]

for pattern in expected_patterns:
    if pattern in result_html:
        print(f"  ✅ Found: {pattern}")
    else:
        print(f"  ❌ MISSING: {pattern}")

# Check if images were replaced or not
if test_html == result_html:
    print("\n⚠️  WARNING: HTML unchanged! Images NOT replaced with captions!")
    print("\nPossible issues:")
    print("  1. Image src URLs don't match between original and enriched metadata")
    print("  2. BeautifulSoup parsing issue")
    print("  3. Filename extraction not working")
else:
    print("\n✅ SUCCESS: Images replaced with WordPress caption shortcodes!")

print("\n" + "="*80 + "\n")
