"""
Test image downloading from Google Docs to identify the issue
"""

from tools.google_docs_converter import google_docs_to_html
from tools.image_processor import extract_image_urls, download_images

print("\n" + "="*80)
print("TESTING IMAGE DOWNLOAD FROM GOOGLE DOCS")
print("="*80)

# Test with your Google Docs URL
test_url = input("\nPaste your Google Docs URL: ").strip()

print("\n" + "="*80)
print("STEP 1: Converting Google Docs to HTML")
print("="*80)

try:
    result = google_docs_to_html(test_url)

    if not result['success']:
        print(f"❌ Failed: {result.get('error')}")
        exit(1)

    print(f"✅ Success!")
    print(f"   HTML length: {len(result['raw_html'])} characters")

    html = result['raw_html']

    print("\n" + "="*80)
    print("STEP 2: Extracting image URLs from HTML")
    print("="*80)

    image_urls = extract_image_urls(html)
    print(f"Found {len(image_urls)} image(s)")

    if not image_urls:
        print("No images found in document. Test complete.")
        exit(0)

    for idx, url in enumerate(image_urls, 1):
        print(f"{idx}. {url[:100]}...")

    print("\n" + "="*80)
    print("STEP 3: Downloading images")
    print("="*80)

    download_result = download_images(image_urls, base_name="test")

    print("\n" + "="*80)
    print("DOWNLOAD RESULTS")
    print("="*80)

    if download_result['success']:
        print(f"✅ All images downloaded successfully!")
        print(f"   Downloaded: {len(download_result['downloaded'])}")
        for img in download_result['downloaded']:
            print(f"   - {img['filename']} → {img['local_path']}")
    else:
        print(f"⚠️  Some downloads failed")
        print(f"   Downloaded: {len(download_result['downloaded'])}")
        print(f"   Failed: {len(download_result['failed'])}")

        for img in download_result['downloaded']:
            print(f"   ✓ {img['filename']}")

        for failure in download_result['failed']:
            print(f"   ✗ {failure['url'][:80]}...")
            print(f"      Error: {failure['error']}")

except Exception as e:
    print(f"\n❌ EXCEPTION OCCURRED:")
    print(f"Type: {type(e).__name__}")
    print(f"Message: {str(e)}")

    import traceback
    print("\nFull traceback:")
    traceback.print_exc()

print("\n" + "="*80)
