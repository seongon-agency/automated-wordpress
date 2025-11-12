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

        return {
            "success": False,
            "error": error_msg
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


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
