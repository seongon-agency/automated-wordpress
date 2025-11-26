"""
WordPress Uploader

Uploads images to WordPress media library and creates posts via REST API.
"""

import os
import base64
import requests
from pathlib import Path
from typing import Dict, List, Optional, Any


def upload_image_to_wordpress(
    image_path: str,
    wordpress_url: str,
    username: str,
    app_password: str,
    title: Optional[str] = None,
    alt_text: Optional[str] = None,
    description: Optional[str] = None,
    caption: Optional[str] = None
) -> Dict[str, Any]:
    """
    Upload a single image to WordPress media library.

    Args:
        image_path: Path to image file
        wordpress_url: WordPress site URL
        username: WordPress username
        app_password: WordPress application password
        title: Image title (optional)
        alt_text: Image alt text (optional)
        description: Image description (optional)
        caption: Image caption (optional)

    Returns:
        Dict containing:
        - success: bool
        - media_id: int (WordPress media ID)
        - url: str (URL of uploaded image)
        - error: str (if failed)
    """
    try:
        # Prepare authentication token
        credentials = f"{username}:{app_password}"
        token = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')

        # Get filename
        filename = Path(image_path).name

        # Read image file as binary
        with open(image_path, 'rb') as f:
            image_data = f.read()

        # Detect image type from extension
        ext = Path(image_path).suffix.lower()
        content_type = 'image/jpeg'
        if ext in ['.png']:
            content_type = 'image/png'
        elif ext in ['.gif']:
            content_type = 'image/gif'
        elif ext in ['.webp']:
            content_type = 'image/webp'

        # Prepare headers - send as binary with Content-Type
        headers = {
            'Content-Type': content_type,
            'Content-Disposition': f'attachment; filename={filename}',
            'Authorization': f'Basic {token}'  # Must be string, not dict
        }

        # Prepare metadata as URL parameters
        params = {}
        if title:
            params['title'] = title
        if alt_text:
            params['alt_text'] = alt_text
        if description:
            params['description'] = description
        if caption:
            params['caption'] = caption

        # Upload to WordPress - send binary data directly
        api_url = f"{wordpress_url.rstrip('/')}/wp-json/wp/v2/media"
        response = requests.post(
            api_url,
            headers=headers,
            data=image_data,  # Binary data in body, NOT multipart
            params=params,    # Metadata as URL params, NOT JSON
            timeout=60
        )

        response.raise_for_status()
        data = response.json()

        return {
            "success": True,
            "media_id": data['id'],
            "url": data['source_url'],
            "media_details": data.get('media_details', {})
        }

    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP {e.response.status_code}"
        try:
            error_data = e.response.json()
            error_msg += f": {error_data.get('message', 'Unknown error')}"
        except:
            error_msg += f": {e.response.text if hasattr(e.response, 'text') else 'Unknown error'}"

        return {
            "success": False,
            "error": error_msg
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def upload_images_batch(
    image_paths: List[str],
    wordpress_url: str,
    username: str,
    app_password: str
) -> Dict[str, Any]:
    """
    Upload multiple images to WordPress.

    Args:
        image_paths: List of paths to image files
        wordpress_url: WordPress site URL
        username: WordPress username
        app_password: WordPress application password

    Returns:
        Dict containing:
        - success: bool (true if all succeeded)
        - uploaded: List[Dict] with image_path, media_id, url
        - failed: List[Dict] with image_path, error
        - url_mapping: Dict mapping old filenames to new WordPress URLs
    """
    uploaded = []
    failed = []
    url_mapping = {}

    for idx, image_path in enumerate(image_paths, 1):
        print(f"   [{idx}/{len(image_paths)}] Uploading: {Path(image_path).name}")

        result = upload_image_to_wordpress(
            image_path, wordpress_url, username, app_password
        )

        if result['success']:
            uploaded.append({
                "image_path": image_path,
                "media_id": result['media_id'],
                "url": result['url']
            })

            # Create filename -> URL mapping
            filename = Path(image_path).name
            url_mapping[filename] = result['url']
        else:
            failed.append({
                "image_path": image_path,
                "error": result.get('error', 'Unknown error')
            })

            # Retry once on failure
            retry_result = upload_image_to_wordpress(
                image_path, wordpress_url, username, app_password
            )
            if retry_result['success']:
                uploaded.append({
                    "image_path": image_path,
                    "media_id": retry_result['media_id'],
                    "url": retry_result['url']
                })
                filename = Path(image_path).name
                url_mapping[filename] = retry_result['url']
                # Remove from failed list
                failed = [f for f in failed if f['image_path'] != image_path]

    return {
        "success": len(failed) == 0,
        "uploaded": uploaded,
        "failed": failed,
        "url_mapping": url_mapping
    }


def create_wordpress_post(
    title: str,
    content: str,
    wordpress_url: str,
    username: str,
    app_password: str,
    status: str = "draft",
    categories: Optional[List[int]] = None,
    tags: Optional[List[int]] = None
) -> Dict[str, Any]:
    """
    Create a WordPress post.

    Args:
        title: Post title
        content: Post content (HTML)
        wordpress_url: WordPress site URL
        username: WordPress username
        app_password: WordPress application password
        status: Post status (draft, publish, private)
        categories: List of category IDs
        tags: List of tag IDs

    Returns:
        Dict containing:
        - success: bool
        - post_id: int
        - post_url: str (URL to view the post)
        - edit_url: str (URL to edit the post)
        - error: str (if failed)
    """
    try:
        # Prepare authentication
        credentials = f"{username}:{app_password}"
        token = base64.b64encode(credentials.encode()).decode()
        headers = {
            'Authorization': f'Basic {token}',
            'Content-Type': 'application/json'
        }

        # Prepare post data
        post_data = {
            'title': title,
            'content': content,
            'status': status
        }

        if categories:
            post_data['categories'] = categories
        if tags:
            post_data['tags'] = tags

        # Create post via WordPress REST API
        api_url = f"{wordpress_url.rstrip('/')}/wp-json/wp/v2/posts"
        response = requests.post(
            api_url,
            headers=headers,
            json=post_data,
            timeout=60
        )

        response.raise_for_status()
        data = response.json()

        return {
            "success": True,
            "post_id": data['id'],
            "post_url": data['link'],
            "edit_url": f"{wordpress_url.rstrip('/')}/wp-admin/post.php?post={data['id']}&action=edit",
            "status": data['status']
        }

    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP {e.response.status_code}"
        try:
            error_data = e.response.json()
            error_msg += f": {error_data.get('message', 'Unknown error')}"
        except:
            pass

        # Add detailed debugging info
        error_msg += f" | URL: {api_url}"
        error_msg += f" | Title length: {len(title)}"
        error_msg += f" | Content length: {len(content)}"

        return {
            "success": False,
            "error": error_msg
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def extract_image_metadata_from_html(html: str) -> Dict[str, Dict[str, str]]:
    """
    Extract image metadata (src, alt, dimensions) from HTML.

    Args:
        html: HTML content with images

    Returns:
        Dict mapping image URLs (full src) to their metadata (alt, width, height)
    """
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, 'html.parser')
    metadata = {}

    print(f"   [DEBUG] Extracting metadata from HTML ({len(html)} chars)...")

    for idx, img in enumerate(soup.find_all('img'), 1):
        src = img.get('src', '')
        if src:
            # Try to get alt text from multiple possible attributes
            alt_text = img.get('alt', '') or img.get('title', '') or ''

            # Debug: show all attributes of the img tag
            all_attrs = dict(img.attrs)
            print(f"   [DEBUG] Image {idx} attributes: {list(all_attrs.keys())}")

            # Use the full URL as the key (works with both regular URLs and Google Docs URLs)
            # This matches better with the original_url in processed_images
            metadata[src] = {
                'alt': alt_text,
                'width': img.get('width', ''),
                'height': img.get('height', ''),
                'src': src
            }
            # Debug: print what we're extracting
            print(f"   [DEBUG] Image {idx}: alt='{alt_text[:50] if alt_text else '(empty)'}' src={src[:60]}...")

    print(f"   [DEBUG] Extracted metadata for {len(metadata)} image(s)")
    return metadata


def replace_images_with_wordpress_captions(
    html: str,
    image_metadata: List[Dict[str, Any]],
    target_width: int = 1200,
    max_caption_width: int = None
) -> str:
    """
    Replace img tags with WordPress caption shortcode format.

    Args:
        html: HTML content
        image_metadata: List of dicts with media_id, url, alt, width, height
        target_width: Target width from workflow settings
        max_caption_width: Maximum width for caption wrapper (prevents stretching)

    Returns:
        HTML with WordPress caption format

    Format:
        [caption id="attachment_{media_id}" align="aligncenter" width="{width}"]
        <img title="" class="aligncenter size-full wp-image-{media_id}" src="{url}" alt="{alt}" width="{width}" height="{height}">
        [/caption]
    """
    import re
    from bs4 import BeautifulSoup
    import uuid

    soup = BeautifulSoup(html, 'html.parser')

    # Create a mapping of original src/filename to metadata
    metadata_map = {}
    for item in image_metadata:
        # Map by WordPress URL
        metadata_map[item['url']] = item
        # Also map by filename for fallback
        if 'original_filename' in item:
            metadata_map[item['original_filename']] = item

    # Store placeholders and their replacement shortcodes
    replacements = {}

    # Find all img tags and replace them with unique placeholders
    images_found = soup.find_all('img')
    print(f"   [DEBUG] Found {len(images_found)} img tags in HTML")
    print(f"   [DEBUG] Have metadata for {len(image_metadata)} images")

    images_replaced = 0
    for img in images_found:
        src = img.get('src', '')
        if not src:
            print(f"   [DEBUG] Skipping img tag with no src")
            continue

        print(f"   [DEBUG] Processing image src: {src[:80]}...")

        # Find matching metadata
        meta = None
        for key, value in metadata_map.items():
            if key in src or src in key:
                meta = value
                print(f"   [DEBUG] ✓ Matched with key: {key[:80]}...")
                break

        if not meta:
            print(f"   [DEBUG] ✗ No metadata match found for: {src[:80]}...")
            print(f"   [DEBUG]   Available keys: {list(metadata_map.keys())[:3]}")
            continue

        # Get dimensions
        width = meta.get('width', target_width)
        height = meta.get('height', 800)
        alt_text = meta.get('alt', '')  # This becomes the caption text
        media_id = meta.get('media_id', 0)
        wp_url = meta['url']

        images_replaced += 1

        # For caption wrapper width, constrain to max_caption_width to prevent stretching
        # when theme's content area is narrower than the image
        if max_caption_width:
            caption_width = min(width, max_caption_width)
        else:
            caption_width = width

        # Create unique placeholder
        placeholder = f"CAPTION_PLACEHOLDER_{uuid.uuid4().hex}"

        # Check if image has alt text for caption
        if alt_text and alt_text.strip():
            # Create WordPress caption shortcode for images WITH alt text
            # WordPress format: [caption id="attachment_ID" align="aligncenter" width="W"]<img class="wp-image-ID size-full" src="URL" alt="ALT_TEXT" width="W" height="H" /> CAPTION_TEXT[/caption]
            caption_shortcode = (
                f'[caption id="attachment_{media_id}" align="aligncenter" width="{caption_width}"]'
                f'<img class="wp-image-{media_id} size-full" '
                f'src="{wp_url}" alt="{alt_text}" width="{width}" height="{height}" /> '
                f'{alt_text}[/caption]'
            )
            print(f"   [DEBUG] ✓ Creating caption shortcode for image with alt text")
        else:
            # For images WITHOUT alt text, create centered <p> wrapper instead of shortcode
            caption_shortcode = (
                f'<p style="text-align: center;">'
                f'<img class="wp-image-{media_id} size-full" '
                f'src="{wp_url}" alt="" width="{width}" height="{height}" />'
                f'</p>'
            )
            print(f"   [DEBUG] ⏭️ Creating centered <p> for image without alt text")

        # Store the replacement
        replacements[placeholder] = caption_shortcode

        # Find the parent <p> tag to replace (WordPress captions should replace the paragraph)
        parent_p = img.find_parent('p')
        if parent_p:
            # IMPORTANT: Find next sibling BEFORE replacing parent
            # This checks if the next element is a <p> tag with duplicate caption text
            # This happens when users add both alt text AND a caption paragraph in Google Docs
            next_sibling = parent_p.find_next_sibling()

            # Replace the entire paragraph with the placeholder
            parent_p.replace_with(placeholder)

            # Now check if we should remove the duplicate caption paragraph
            if next_sibling and next_sibling.name == 'p':
                sibling_text = next_sibling.get_text(strip=True)
                # If the next paragraph matches the alt text (caption), remove it
                if sibling_text and alt_text and sibling_text == alt_text:
                    print(f"   [DEBUG] ✓ Removing duplicate caption paragraph: '{sibling_text[:60]}...'")
                    next_sibling.decompose()
        else:
            # If no <p> parent, find next sibling and then replace the img tag
            next_sibling = img.find_next_sibling()

            # Replace just the img tag
            img.replace_with(placeholder)

            # Check for duplicate caption in next sibling
            if next_sibling and next_sibling.name == 'p':
                sibling_text = next_sibling.get_text(strip=True)
                if sibling_text and alt_text and sibling_text == alt_text:
                    print(f"   [DEBUG] ✓ Removing duplicate caption paragraph: '{sibling_text[:60]}...'")
                    next_sibling.decompose()

    # Convert soup to string
    result_html = str(soup)

    # Now replace all placeholders with actual WordPress shortcodes
    print(f"   [DEBUG] Replacing {len(replacements)} placeholder(s) with shortcodes...")
    for placeholder, shortcode in replacements.items():
        result_html = result_html.replace(placeholder, shortcode)

    print(f"   [DEBUG] Caption generation complete: {images_replaced}/{len(images_found)} images converted to shortcodes")

    return result_html


def replace_image_urls_in_html(html: str, url_mapping: Dict[str, str]) -> str:
    """
    Replace local image URLs with WordPress media URLs.

    Args:
        html: HTML content with local image references
        url_mapping: Dict mapping old URLs/filenames to new WordPress URLs

    Returns:
        HTML with updated image URLs
    """
    import re

    modified_html = html

    # Replace each old URL with new WordPress URL
    for old_ref, new_url in url_mapping.items():
        # Try to match the old reference in src attributes
        # Handle both full URLs and just filenames
        patterns = [
            f'src=["\']([^"\']*{re.escape(old_ref)})["\']',
            f'src=["\']([^"\']*/{re.escape(old_ref)})["\']',
        ]

        for pattern in patterns:
            modified_html = re.sub(
                pattern,
                f'src="{new_url}"',
                modified_html,
                flags=re.IGNORECASE
            )

    return modified_html


# Make functions available as Agno tools
upload_image_to_wordpress.__annotations__ = {
    'image_path': str,
    'wordpress_url': str,
    'username': str,
    'app_password': str,
    'title': Optional[str],
    'alt_text': Optional[str],
    'description': Optional[str],
    'caption': Optional[str],
    'return': Dict[str, Any]
}

upload_images_batch.__annotations__ = {
    'image_paths': List[str],
    'wordpress_url': str,
    'username': str,
    'app_password': str,
    'return': Dict[str, Any]
}

create_wordpress_post.__annotations__ = {
    'title': str,
    'content': str,
    'wordpress_url': str,
    'username': str,
    'app_password': str,
    'status': str,
    'categories': Optional[List[int]],
    'tags': Optional[List[int]],
    'return': Dict[str, Any]
}

replace_image_urls_in_html.__annotations__ = {
    'html': str,
    'url_mapping': Dict[str, str],
    'return': str
}
