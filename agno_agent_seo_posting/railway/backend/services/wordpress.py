"""
WordPress Service

Uploads images to WordPress media library and creates posts via REST API.
"""

import base64
import requests
from pathlib import Path
from typing import Dict, List, Optional, Any


async def upload_image_to_wordpress(
    image_path: str,
    wordpress_url: str,
    username: str,
    app_password: str,
    title: Optional[str] = None,
    alt_text: Optional[str] = None
) -> Dict[str, Any]:
    """
    Upload a single image to WordPress media library.
    """
    try:
        credentials = f"{username}:{app_password}"
        token = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')

        filename = Path(image_path).name

        with open(image_path, 'rb') as f:
            image_data = f.read()

        ext = Path(image_path).suffix.lower()
        content_type = 'image/jpeg'
        if ext == '.png':
            content_type = 'image/png'
        elif ext == '.gif':
            content_type = 'image/gif'
        elif ext == '.webp':
            content_type = 'image/webp'

        headers = {
            'Content-Type': content_type,
            'Content-Disposition': f'attachment; filename={filename}',
            'Authorization': f'Basic {token}'
        }

        params = {}
        if title:
            params['title'] = title
        if alt_text:
            params['alt_text'] = alt_text

        api_url = f"{wordpress_url.rstrip('/')}/wp-json/wp/v2/media"
        response = requests.post(
            api_url,
            headers=headers,
            data=image_data,
            params=params,
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


async def upload_images_batch(
    image_paths: List[str],
    wordpress_url: str,
    username: str,
    app_password: str
) -> Dict[str, Any]:
    """
    Upload multiple images to WordPress.
    """
    uploaded = []
    failed = []
    url_mapping = {}

    for idx, image_path in enumerate(image_paths, 1):
        result = await upload_image_to_wordpress(
            image_path, wordpress_url, username, app_password
        )

        if result['success']:
            uploaded.append({
                "image_path": image_path,
                "media_id": result['media_id'],
                "url": result['url']
            })
            filename = Path(image_path).name
            url_mapping[filename] = result['url']
        else:
            failed.append({
                "image_path": image_path,
                "error": result.get('error', 'Unknown error')
            })

            # Retry once
            retry_result = await upload_image_to_wordpress(
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
                failed = [f for f in failed if f['image_path'] != image_path]

    return {
        "success": len(failed) == 0,
        "uploaded": uploaded,
        "failed": failed,
        "url_mapping": url_mapping
    }


async def create_wordpress_post(
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
    """
    try:
        credentials = f"{username}:{app_password}"
        token = base64.b64encode(credentials.encode()).decode()
        headers = {
            'Authorization': f'Basic {token}',
            'Content-Type': 'application/json'
        }

        post_data = {
            'title': title,
            'content': content,
            'status': status
        }

        if categories:
            post_data['categories'] = categories
        if tags:
            post_data['tags'] = tags

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
    """
    import re

    modified_html = html

    for old_ref, new_url in url_mapping.items():
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
