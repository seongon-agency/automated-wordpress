"""
Test the complete publishing workflow to identify where it fails
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file FIRST
load_dotenv()

# Verify credentials are loaded
if not os.getenv('WP_BASE_URL'):
    print("ERROR: WP_BASE_URL not found in .env file")
    sys.exit(1)
if not os.getenv('WP_USERNAME'):
    print("ERROR: WP_USERNAME not found in .env file")
    sys.exit(1)
if not os.getenv('WP_APP_PASS'):
    print("ERROR: WP_APP_PASS not found in .env file")
    sys.exit(1)

from workflows.publishing_workflow import execute_publishing_workflow

print("\n" + "="*80)
print("TESTING COMPLETE PUBLISHING WORKFLOW")
print("="*80)

# Display loaded credentials
print("\n📋 WordPress Credentials:")
print(f"   URL: {os.getenv('WP_BASE_URL')}")
print(f"   Username: {os.getenv('WP_USERNAME')}")
print(f"   App Password: {'*' * 20} (loaded)")

# Get URL from user
google_docs_url = input("\nPaste your Google Docs URL: ").strip()
project_id = input("Project ID (or press Enter for no-project): ").strip() or None

print("\n" + "="*80)
print("STARTING TEST")
print("="*80)
print(f"Google Docs URL: {google_docs_url}")
print(f"Project ID: {project_id or 'None (no-project mode)'}")
print(f"WordPress Target: {os.getenv('WP_BASE_URL')}")
print("="*80 + "\n")

try:
    result = execute_publishing_workflow(
        google_docs_url=google_docs_url,
        project_id=project_id
    )

    print("\n" + "="*80)
    print("WORKFLOW RESULT")
    print("="*80)

    for key, value in result.items():
        print(f"{key}: {value}")

except Exception as e:
    print("\n" + "="*80)
    print("❌ EXCEPTION OCCURRED")
    print("="*80)
    print(f"Type: {type(e).__name__}")
    print(f"Message: {str(e)}")

    import traceback
    print("\nFull traceback:")
    traceback.print_exc()

print("\n" + "="*80)
