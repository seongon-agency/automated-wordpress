"""
Debug script: Show raw HTML from Google Docs to see what's being exported.
"""

import sys
sys.path.insert(0, 'src')

from tools.google_docs_converter import google_docs_to_html

if len(sys.argv) < 2:
    print("Usage: python3 debug_google_docs_html.py <google_docs_url>")
    sys.exit(1)

google_docs_url = sys.argv[1]

print("Fetching Google Docs...")
result = google_docs_to_html(google_docs_url)

if not result['success']:
    print(f"Failed: {result.get('error')}")
    sys.exit(1)

print(f"\nDocument: {result['document_name']}")
print(f"File ID: {result['file_id']}")

raw_html = result['raw_html']

print(f"\nHTML Length: {len(raw_html)} characters")
print("\n" + "="*100)
print("RAW HTML (first 5000 characters):")
print("="*100)
print(raw_html[:5000])
print("\n" + "="*100)

# Search for image tags
import re
img_tags = re.findall(r'<img[^>]+>', raw_html, re.IGNORECASE)
print(f"\nFound {len(img_tags)} <img> tags in HTML")

if img_tags:
    print("\nImage tags:")
    for idx, tag in enumerate(img_tags[:5], 1):  # Show first 5
        print(f"{idx}. {tag}")
else:
    print("\nNo <img> tags found in HTML!")

# Check for image references
google_user_content = raw_html.count('googleusercontent.com')
lh_rt = raw_html.count('lh7-rt.googleusercontent.com')

print(f"\nImage URL patterns:")
print(f"  - 'googleusercontent.com': {google_user_content} occurrences")
print(f"  - 'lh7-rt.googleusercontent.com': {lh_rt} occurrences")

# Save to file for inspection
with open('debug_google_docs_output.html', 'w', encoding='utf-8') as f:
    f.write(raw_html)

print(f"\n✓ Full HTML saved to: debug_google_docs_output.html")
print("\nYou can open this file to see exactly what Google Docs is exporting.")
