"""
Diagnostic script: Check if Google Docs HTML contains alt text.

This script fetches your Google Docs and shows whether images have alt text.
"""

import sys
sys.path.insert(0, 'src')

from tools.google_docs_converter import google_docs_to_html
from tools.wordpress_uploader import extract_image_metadata_from_html

print("="*100)
print("DIAGNOSTIC: Check Google Docs Alt Text")
print("="*100)

# Get Google Docs URL from command line or user input
if len(sys.argv) > 1:
    google_docs_url = sys.argv[1].strip()
    print(f"\nUsing URL from command line: {google_docs_url[:80]}...")
else:
    print("\nEnter your Google Docs URL:")
    print("(It should be a published URL ending with /pub)")
    try:
        google_docs_url = input("URL: ").strip()
    except EOFError:
        print("\n❌ No URL provided. Usage: python3 check_google_docs_alt_text.py <google_docs_url>")
        sys.exit(1)

if not google_docs_url:
    print("\n❌ No URL provided. Usage: python3 check_google_docs_alt_text.py <google_docs_url>")
    sys.exit(1)

print(f"\n📄 Fetching Google Docs from: {google_docs_url[:80]}...")

# Convert Google Docs to HTML
result = google_docs_to_html(google_docs_url)

if not result['success']:
    print(f"\n❌ Failed to fetch Google Docs: {result.get('error', 'Unknown error')}")
    sys.exit(1)

print(f"✓ Successfully fetched: {result['document_name']}")

# Extract image metadata
print("\n" + "="*100)
print("EXTRACTING IMAGE METADATA")
print("="*100)

raw_html = result['raw_html']
metadata = extract_image_metadata_from_html(raw_html)

print(f"\n✓ Found {len(metadata)} image(s) in Google Docs")

if len(metadata) == 0:
    print("\n⚠️  No images found in this Google Docs document!")
    print("Please make sure your document contains images.")
    sys.exit(0)

# Display each image's metadata
print("\n" + "="*100)
print("IMAGE METADATA")
print("="*100)

for idx, (filename, meta) in enumerate(metadata.items(), 1):
    print(f"\n{idx}. Filename: {filename}")
    print(f"   Source URL: {meta.get('src', 'NONE')[:100]}...")
    print(f"   Alt text: '{meta.get('alt', '')}'")
    print(f"   Width: {meta.get('width', 'NONE')}")
    print(f"   Height: {meta.get('height', 'NONE')}")

    if not meta.get('alt', ''):
        print(f"   ⚠️  WARNING: This image has NO alt text!")
        print(f"   → In Google Docs, right-click the image → 'Alt text' → Enter description")

# Summary
print("\n" + "="*100)
print("SUMMARY")
print("="*100)

images_with_alt = sum(1 for meta in metadata.values() if meta.get('alt', ''))
images_without_alt = len(metadata) - images_with_alt

print(f"\nTotal images: {len(metadata)}")
print(f"Images WITH alt text: {images_with_alt}")
print(f"Images WITHOUT alt text: {images_without_alt}")

if images_without_alt > 0:
    print(f"\n⚠️  {images_without_alt} image(s) are missing alt text!")
    print("\nTo add alt text in Google Docs:")
    print("1. Right-click on the image")
    print("2. Select 'Alt text'")
    print("3. Enter a description in the 'Alt text' field")
    print("4. Click 'OK'")
    print("5. Re-publish your document (File → Share → Publish to web)")
else:
    print("\n✅ All images have alt text!")

print("\n" + "="*100)
print("\nThis diagnostic shows what alt text exists in your Google Docs.")
print("If images show 'WARNING: This image has NO alt text', you need to add it in Google Docs.")
print("="*100 + "\n")
