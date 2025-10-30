"""
WordPress Publishing Tools for Agno Agent
Simple wrapper functions that the AI agent can call.
"""

import sys
import os

# Add parent directory to path to import functions.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from functions import (
    extract_file_id,
    export_doc_html_bytes,
    transform_html_dom,
    extract_images_from_html_text,
    download_to_memory,
    resize_fit_memory,
    upload_resized,
    build_caption_shortcode,
    ensure_unique_path,
    guess_ext_from_url,
    safe_name,
    first_n_words,
    slugify  # For Vietnamese -> ASCII conversion
)
import requests
import base64
import os
import re
from bs4 import BeautifulSoup, NavigableString
from client_configs import get_client_config, list_available_clients
from html_transformer import transform_html_for_client
from config_generator import create_client_from_examples

# WordPress API configuration (from functions.py)
WP_BASE_URL = "https://ngoncareer.com"
WP_USERNAME = "admin_career"
WP_APP_PASS = "efkV mie6 u3P8 C3mC NyM8 Ickp"
wp_pass_clean = WP_APP_PASS.replace(" ", "")
WP_API_BASE = f"{WP_BASE_URL}/wp-json/wp/v2"
token = base64.b64encode(f"{WP_USERNAME}:{wp_pass_clean}".encode("utf-8")).decode("utf-8")
auth_header = {"Authorization": f"Basic {token}"}


def publish_google_doc_to_wordpress(google_doc_url: str, post_status: str = "draft", client_id: str = "default") -> dict:
    """
    Main function: Take a Google Doc URL and publish it to WordPress.

    Args:
        google_doc_url: URL of the Google Doc
        post_status: "draft" or "publish" (default: draft for safety)
        client_id: Client configuration ID for custom HTML transformations (default: "default")
                   Use list_client_configurations() to see available clients

    Returns:
        dict with post_id, post_url, title, status, and client_used
    """
    try:
        print(f"\n📄 Processing Google Doc: {google_doc_url}")

        # Step 1: Extract file ID
        file_id = extract_file_id(google_doc_url)
        print(f"✓ Extracted file ID: {file_id}")

        # Step 2: Export HTML from Google Doc
        html_bytes, meta = export_doc_html_bytes(file_id)
        doc_title = meta.get("name", "Untitled")
        print(f"✓ Exported doc: {doc_title}")

        # Step 3: Decode HTML
        html = html_bytes.decode('utf-8')

        # Step 4: Extract title from HTML
        soup = BeautifulSoup(html, 'html.parser')
        h1 = soup.find('h1')
        title = h1.get_text(strip=True) if h1 else doc_title
        print(f"✓ Post title: {title}")

        # Step 5: Transform HTML FIRST (before processing images)
        print("🔄 Transforming HTML (standard WordPress format)...")
        html = transform_html_dom(html)

        # Step 5a: Apply client-specific HTML transformations
        client_config = get_client_config(client_id)
        client_name = client_config.get("name", client_id)
        print(f"🎨 Applying client customizations: {client_name}")

        html = transform_html_for_client(html, client_config)

        # Step 6: Extract images from transformed HTML
        print("📸 Processing images...")
        soup = BeautifulSoup(html, 'html.parser')
        image_mapping = {}  # old_src -> new WordPress info

        img_tags = soup.find_all('img')
        print(f"  Found {len(img_tags)} images in document")

        for idx, img_tag in enumerate(img_tags):
            old_src = img_tag.get('src', '')

            if not old_src or not old_src.startswith('http'):
                print(f"  ⊘ Skipping non-http image: {old_src[:50] if old_src else 'empty'}")
                continue

            try:
                print(f"  → Downloading: {old_src[:70]}...")

                # Download image to memory
                img_data = download_to_memory(old_src)

                # Generate filename from alt text (slugified to handle Vietnamese chars)
                alt_text = img_tag.get('alt', '')
                # Use slugify to convert Vietnamese characters to ASCII-safe format
                filename = slugify(alt_text) if alt_text else f"image-{idx}"
                # Fallback if slugify returns empty
                if not filename or filename == '-':
                    filename = f"image-{idx}"
                ext = guess_ext_from_url(old_src)

                # Save to temp file for upload
                temp_dir = "temp_images"
                os.makedirs(temp_dir, exist_ok=True)
                temp_path = ensure_unique_path(temp_dir, f"{filename}{ext}")

                # Resize and save
                resize_fit_memory(img_data, temp_path, 1200, 800)

                # Upload to WordPress
                print(f"  → Uploading to WordPress...")
                wp_media = upload_resized(temp_path)
                new_url = wp_media.get('source_url', '')

                # Store in mapping
                image_mapping[old_src] = {
                    'new_url': new_url,
                    'media_id': wp_media.get('id'),
                    'width': wp_media.get('media_details', {}).get('width'),
                    'height': wp_media.get('media_details', {}).get('height'),
                    'alt': alt_text,
                    'img_tag': img_tag  # Keep reference to the tag
                }

                print(f"  ✓ Uploaded: {filename}{ext} -> WP Media ID {wp_media.get('id')}")
                print(f"    Old URL: {old_src[:60]}...")
                print(f"    New URL: {new_url[:60]}...")

                # Clean up temp file
                os.remove(temp_path)

            except Exception as e:
                print(f"  ✗ Failed to process image #{idx}")
                print(f"    URL: {old_src[:100]}")
                print(f"    Alt text: {alt_text[:100] if alt_text else '(none)'}")
                print(f"    Error: {e}")
                # Continue processing other images even if one fails

        # Step 7: Replace img tags with WordPress shortcodes
        print(f"\n🖼️  Replacing {len(image_mapping)} images with WordPress media...")

        replacements = {}

        for idx, (old_src, img_info) in enumerate(image_mapping.items()):
            img_tag = img_info['img_tag']

            # Build WordPress caption shortcode with all metadata
            shortcode_info = {
                'new_src': img_info['new_url'],
                'alt': img_info['alt'] or '',
                'width': img_info['width'],
                'height': img_info['height'],
                'uploaded_media_id': img_info['media_id']
            }

            # Generate WordPress caption shortcode
            shortcode = build_caption_shortcode(shortcode_info)

            # Create unique placeholder
            placeholder = f"___IMG_PLACEHOLDER_{idx}___"
            replacements[placeholder] = shortcode

            # Replace img tag with placeholder
            img_tag.replace_with(NavigableString(placeholder))

            print(f"  ✓ Queued replacement for Media ID {img_info['media_id']}")

        # Convert to string and replace placeholders with shortcodes
        html = str(soup)
        for placeholder, shortcode in replacements.items():
            html = html.replace(placeholder, shortcode)

        print(f"✅ Replaced {len(replacements)} images with WordPress media URLs")

        # Step 8: Create WordPress post
        print("📝 Creating WordPress post...")
        post_data = {
            "title": title,
            "content": html,
            "status": post_status,
            "format": "standard"
        }

        response = requests.post(
            f"{WP_API_BASE}/posts",
            headers={**auth_header, "Content-Type": "application/json"},
            json=post_data,
            timeout=30
        )

        if response.status_code >= 400:
            raise RuntimeError(f"WordPress API error {response.status_code}: {response.text}")

        post = response.json()
        post_id = post.get('id')
        post_url = post.get('link')

        print(f"✅ Published to WordPress!")
        print(f"   Post ID: {post_id}")
        print(f"   URL: {post_url}")

        return {
            "success": True,
            "post_id": post_id,
            "post_url": post_url,
            "title": title,
            "status": post_status,
            "images_uploaded": len(image_mapping),
            "client_used": client_name
        }

    except Exception as e:
        print(f"❌ Error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def get_wordpress_post(post_id: int) -> dict:
    """
    Get details of a WordPress post.

    Args:
        post_id: WordPress post ID

    Returns:
        dict with post details
    """
    try:
        response = requests.get(
            f"{WP_API_BASE}/posts/{post_id}",
            headers=auth_header,
            timeout=10
        )

        if response.status_code >= 400:
            return {"error": f"Post not found: {response.status_code}"}

        post = response.json()
        return {
            "id": post.get('id'),
            "title": post.get('title', {}).get('rendered'),
            "url": post.get('link'),
            "status": post.get('status'),
            "date": post.get('date')
        }

    except Exception as e:
        return {"error": str(e)}


def update_wordpress_post(post_id: int, title: str = None, content: str = None, status: str = None) -> dict:
    """
    Update an existing WordPress post.

    Args:
        post_id: WordPress post ID
        title: New title (optional)
        content: New content (optional)
        status: New status like "publish", "draft" (optional)

    Returns:
        dict with update status
    """
    try:
        update_data = {}
        if title:
            update_data['title'] = title
        if content:
            update_data['content'] = content
        if status:
            update_data['status'] = status

        response = requests.post(
            f"{WP_API_BASE}/posts/{post_id}",
            headers={**auth_header, "Content-Type": "application/json"},
            json=update_data,
            timeout=30
        )

        if response.status_code >= 400:
            return {"error": f"Update failed: {response.status_code}"}

        post = response.json()
        return {
            "success": True,
            "post_id": post.get('id'),
            "post_url": post.get('link'),
            "status": post.get('status')
        }

    except Exception as e:
        return {"error": str(e)}


def list_client_configurations() -> dict:
    """
    List all available client HTML customization configurations.

    Returns:
        dict with list of available clients and their descriptions
    """
    clients = list_available_clients()
    return {
        "clients": clients,
        "count": len(clients)
    }


def create_new_client_config(
    client_name: str,
    client_id: str,
    description: str,
    original_html: str,
    desired_html: str
) -> dict:
    """
    Create a new client configuration by analyzing HTML examples.

    This function analyzes the differences between original HTML (from Google Docs)
    and the desired HTML (what the client needs), then automatically generates
    transformation rules.

    Args:
        client_name: Display name for the client (e.g., "ABC Company")
        client_id: Unique identifier (e.g., "abc-company", must be lowercase with dashes)
        description: Brief description of what customizations are needed
        original_html: Example HTML from Google Docs (the "before" state)
        desired_html: Example HTML the client needs (the "after" state)

    Returns:
        dict with success status, client_id, and generated configuration details

    Example:
        original_html = '<p>Text with <strong>bold</strong></p>'
        desired_html = '<p class="content">Text with <b class="fw-bold">bold</b></p>'

        result = create_new_client_config(
            client_name="XYZ Corp",
            client_id="xyz-corp",
            description="Uses <b> instead of <strong>, adds custom classes",
            original_html=original_html,
            desired_html=desired_html
        )
    """
    return create_client_from_examples(
        client_name=client_name,
        client_id=client_id,
        description=description,
        original_html=original_html,
        desired_html=desired_html
    )


def batch_publish_google_docs(
    google_doc_urls: list,
    post_status: str = "draft",
    client_id: str = "default"
) -> dict:
    """
    Publish multiple Google Docs to WordPress in batch.

    Args:
        google_doc_urls: List of Google Docs URLs to publish
        post_status: Status for all posts ("draft" or "publish")
        client_id: Client configuration ID to use for all posts

    Returns:
        dict with summary of published posts, successes, and failures

    Example:
        urls = [
            "https://docs.google.com/document/d/ABC123/edit",
            "https://docs.google.com/document/d/DEF456/edit",
            "https://docs.google.com/document/d/GHI789/edit"
        ]
        result = batch_publish_google_docs(urls, post_status="draft", client_id="my-client")
    """
    if not isinstance(google_doc_urls, list):
        return {
            "success": False,
            "error": "google_doc_urls must be a list of URLs"
        }

    print(f"\n📦 BATCH PUBLISHING {len(google_doc_urls)} DOCUMENTS")
    print(f"   Status: {post_status}")
    print(f"   Client: {client_id}")
    print("=" * 80)

    results = {
        "total": len(google_doc_urls),
        "successful": 0,
        "failed": 0,
        "posts": [],
        "errors": []
    }

    for idx, url in enumerate(google_doc_urls, 1):
        print(f"\n[{idx}/{len(google_doc_urls)}] Processing: {url[:60]}...")
        print("-" * 80)

        try:
            # Publish the document
            result = publish_google_doc_to_wordpress(
                google_doc_url=url,
                post_status=post_status,
                client_id=client_id
            )

            if result.get("success"):
                results["successful"] += 1
                results["posts"].append({
                    "url": url,
                    "post_id": result.get("post_id"),
                    "post_url": result.get("post_url"),
                    "title": result.get("title"),
                    "status": result.get("status"),
                    "client_used": result.get("client_used"),
                    "images_uploaded": result.get("images_uploaded")
                })
                print(f"✅ [{idx}/{len(google_doc_urls)}] Success: {result.get('title')}")
            else:
                results["failed"] += 1
                results["errors"].append({
                    "url": url,
                    "error": result.get("error", "Unknown error")
                })
                print(f"❌ [{idx}/{len(google_doc_urls)}] Failed: {result.get('error')}")

        except Exception as e:
            results["failed"] += 1
            results["errors"].append({
                "url": url,
                "error": str(e)
            })
            print(f"❌ [{idx}/{len(google_doc_urls)}] Error: {e}")

    # Print summary
    print("\n" + "=" * 80)
    print("📊 BATCH PUBLISHING SUMMARY")
    print("=" * 80)
    print(f"Total documents: {results['total']}")
    print(f"✅ Successful: {results['successful']}")
    print(f"❌ Failed: {results['failed']}")
    print(f"Success rate: {(results['successful']/results['total']*100):.1f}%")

    if results["posts"]:
        print(f"\n✅ Successfully Published ({results['successful']}):")
        for post in results["posts"]:
            print(f"   • {post['title']}")
            print(f"     URL: {post['post_url']}")
            print(f"     ID: {post['post_id']}, Status: {post['status']}")

    if results["errors"]:
        print(f"\n❌ Failed ({results['failed']}):")
        for error in results["errors"]:
            print(f"   • {error['url'][:60]}...")
            print(f"     Error: {error['error']}")

    print("=" * 80)

    return results


def list_recent_posts(count: int = 5) -> dict:
    """
    List recent WordPress posts.

    Args:
        count: Number of posts to retrieve (default: 5)

    Returns:
        dict with list of posts
    """
    try:
        response = requests.get(
            f"{WP_API_BASE}/posts",
            params={"per_page": count, "orderby": "date", "order": "desc"},
            headers=auth_header,
            timeout=10
        )

        if response.status_code >= 400:
            return {"error": f"Failed to fetch posts: {response.status_code}"}

        posts = response.json()
        result = []

        for post in posts:
            result.append({
                "id": post.get('id'),
                "title": post.get('title', {}).get('rendered'),
                "url": post.get('link'),
                "status": post.get('status'),
                "date": post.get('date')
            })

        return {"posts": result}

    except Exception as e:
        return {"error": str(e)}
