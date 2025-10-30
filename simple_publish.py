"""
Simple WordPress Publishing Script (No AI Agent)
Use this to test basic publishing functionality without running the full agent.

Usage:
    python simple_publish.py https://docs.google.com/document/d/YOUR_DOC_ID/edit
"""

import sys
sys.path.insert(0, 'agno')

from wordpress_tools import publish_google_doc_to_wordpress


def main():
    if len(sys.argv) < 2:
        print("Usage: python simple_publish.py <google_doc_url>")
        print("\nExample:")
        print("  python simple_publish.py https://docs.google.com/document/d/1ABC123/edit")
        sys.exit(1)

    google_doc_url = sys.argv[1]

    print("=" * 60)
    print("WordPress Publisher (Simple Mode)")
    print("=" * 60)

    result = publish_google_doc_to_wordpress(google_doc_url, post_status="draft")

    print("\n" + "=" * 60)
    if result.get("success"):
        print("✅ SUCCESS!")
        print(f"\nPost ID: {result['post_id']}")
        print(f"Post URL: {result['post_url']}")
        print(f"Title: {result['title']}")
        print(f"Status: {result['status']}")
        print(f"Images: {result['images_uploaded']}")
    else:
        print("❌ FAILED!")
        print(f"\nError: {result.get('error')}")
    print("=" * 60)


if __name__ == "__main__":
    main()
