"""
Test WordPress image upload with the fixed implementation
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
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

from tools.wordpress_uploader import upload_image_to_wordpress

print("\n" + "="*80)
print("TESTING WORDPRESS IMAGE UPLOAD")
print("="*80)

# Get credentials from environment
wp_url = os.getenv('WP_BASE_URL')
wp_username = os.getenv('WP_USERNAME')
wp_app_pass = os.getenv('WP_APP_PASS')

print(f"\n📋 WordPress Credentials:")
print(f"   URL: {wp_url}")
print(f"   Username: {wp_username}")
print(f"   App Password: {'*' * 20} (loaded)")

# Check for test image
import glob
test_images = glob.glob("agno_agent_seo_posting/resized_images/*.jpg") + \
              glob.glob("agno_agent_seo_posting/resized_images/*.png")

if not test_images:
    print("\n❌ No test images found in agno_agent_seo_posting/resized_images/")
    print("Please run the Google Docs converter first to generate test images.")
    exit(1)

test_image = test_images[0]
print(f"\nTest image: {test_image}")

print("\n" + "="*80)
print("UPLOADING IMAGE...")
print("="*80)

try:
    result = upload_image_to_wordpress(
        image_path=test_image,
        wordpress_url=wp_url,
        username=wp_username,
        app_password=wp_app_pass,
        title="Test Upload",
        alt_text="Test image uploaded via API",
        description="Testing the fixed WordPress upload implementation",
        caption="Test caption"
    )

    print("\n" + "="*80)
    print("RESULT")
    print("="*80)

    if result['success']:
        print("✅ UPLOAD SUCCESSFUL!")
        print(f"\nMedia ID: {result['media_id']}")
        print(f"URL: {result['url']}")
        print("\nYou can now verify the image in WordPress Media Library.")
    else:
        print("❌ UPLOAD FAILED")
        print(f"\nError: {result['error']}")
        print("\nPlease check:")
        print("- WordPress REST API is enabled")
        print("- Application password is correct (not regular password)")
        print("- Username is correct")
        print("- WordPress URL is correct")

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
