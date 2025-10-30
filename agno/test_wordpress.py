"""
Simple test script to verify WordPress publishing works
Run this before starting the full agent to make sure everything is configured correctly.
"""

import sys
import os

# Test imports
print("Testing imports...")
try:
    from wordpress_tools import (
        publish_google_doc_to_wordpress,
        get_wordpress_post,
        list_recent_posts
    )
    print("✓ WordPress tools imported successfully")
except Exception as e:
    print(f"✗ Failed to import wordpress_tools: {e}")
    sys.exit(1)

try:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from functions import extract_file_id, strip_diacritics
    print("✓ Functions imported successfully")
except Exception as e:
    print(f"✗ Failed to import functions: {e}")
    sys.exit(1)

# Test basic functions
print("\nTesting basic functions...")

# Test URL parsing
test_url = "https://docs.google.com/document/d/1ABC123DEF456/edit"
try:
    file_id = extract_file_id(test_url)
    assert file_id == "1ABC123DEF456"
    print(f"✓ URL parsing works: {test_url} -> {file_id}")
except Exception as e:
    print(f"✗ URL parsing failed: {e}")

# Test Vietnamese text processing
test_text = "Tôi yêu Việt Nam"
try:
    result = strip_diacritics(test_text)
    assert result == "Toi yeu Viet Nam"
    print(f"✓ Vietnamese processing works: '{test_text}' -> '{result}'")
except Exception as e:
    print(f"✗ Vietnamese processing failed: {e}")

# Test WordPress API connection
print("\nTesting WordPress API connection...")
try:
    result = list_recent_posts(count=1)
    if "error" in result:
        print(f"✗ WordPress API error: {result['error']}")
    else:
        posts = result.get("posts", [])
        if posts:
            print(f"✓ WordPress API connected successfully")
            print(f"  Most recent post: {posts[0].get('title')}")
        else:
            print("✓ WordPress API connected (no posts found)")
except Exception as e:
    print(f"✗ WordPress API connection failed: {e}")

# Test file system
print("\nTesting file system...")
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

required_files = [
    "client_secret.json",
    "token.json",
    "functions.py"
]

for filename in required_files:
    filepath = os.path.join(parent_dir, filename)
    if os.path.exists(filepath):
        print(f"✓ Found {filename}")
    else:
        print(f"✗ Missing {filename}")

# Summary
print("\n" + "="*50)
print("SETUP CHECK COMPLETE")
print("="*50)
print("\nIf all tests passed, you can run:")
print("  python agents.py")
print("\nTo publish a document, provide a Google Docs URL to the agent.")
print("\nExample URLs:")
print("  https://docs.google.com/document/d/YOUR_DOC_ID/edit")
print("  https://docs.google.com/document/d/YOUR_DOC_ID")
