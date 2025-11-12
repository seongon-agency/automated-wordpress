"""
Test Google Docs converter to see exact error
"""

from tools.google_docs_converter import google_docs_to_html

# Test with your actual URL
test_url = input("Paste your Google Docs URL: ").strip()

print("\n" + "="*80)
print("TESTING GOOGLE DOCS CONVERTER")
print("="*80)
print(f"\nURL: {test_url}\n")

try:
    result = google_docs_to_html(test_url)

    print("Result:")
    print(f"Success: {result.get('success')}")

    if result.get('success'):
        print(f"Document name: {result.get('document_name')}")
        print(f"File ID: {result.get('file_id')}")
        print(f"HTML length: {len(result.get('raw_html', ''))} characters")
        print("\nFirst 500 chars of HTML:")
        print(result.get('raw_html', '')[:500])
    else:
        print(f"Error: {result.get('error')}")

except Exception as e:
    print(f"\n❌ EXCEPTION OCCURRED:")
    print(f"Type: {type(e).__name__}")
    print(f"Message: {str(e)}")

    import traceback
    print("\nFull traceback:")
    traceback.print_exc()

print("\n" + "="*80)
