"""
Tool 4: WordPress Publisher
Publishes formatted HTML and images to WordPress
"""

import os
import base64
import requests
from typing import Dict, List, Any, Optional
from pathlib import Path


class WordPressPublisher:
    """Publish content to WordPress via REST API."""

    def __init__(self, site_url: str, username: str, app_password: str):
        """
        Initialize WordPress publisher.

        Args:
            site_url: WordPress site URL (without trailing slash)
            username: WordPress username
            app_password: WordPress application password
        """
        self.site_url = site_url.rstrip('/')
        self.api_base = f"{self.site_url}/wp-json/wp/v2"
        self.media_endpoint = f"{self.api_base}/media"
        self.posts_endpoint = f"{self.api_base}/posts"

        # Create authorization header
        token = base64.b64encode(f"{username}:{app_password}".encode("utf-8")).decode("utf-8")
        self.headers = {"Authorization": f"Basic {token}"}

    def upload_image(
        self,
        image_path: str,
        title: str = "",
        alt_text: str = "",
        description: str = "",
        caption: str = "",
        post_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Upload an image to WordPress media library.

        Args:
            image_path: Path to the image file
            title: Image title
            alt_text: Alt text for accessibility
            description: Image description
            caption: Image caption
            post_id: Associated post ID (optional)

        Returns:
            Dictionary containing upload result with media ID and URL
        """
        try:
            # Read image file
            with open(image_path, 'rb') as f:
                image_data = f.read()

            # Get filename and detect mime type
            filename = Path(image_path).name
            mime_type = self._guess_mime_type(image_path)

            # Prepare headers
            upload_headers = {
                **self.headers,
                'Content-Type': mime_type,
                'Content-Disposition': f'attachment; filename={filename}'
            }

            # Prepare parameters
            params = {
                'title': title or filename,
                'alt_text': alt_text,
                'description': description,
                'caption': caption
            }

            if post_id:
                params['post'] = post_id

            # Upload image
            response = requests.post(
                self.media_endpoint,
                headers=upload_headers,
                data=image_data,
                params=params,
                timeout=60
            )
            response.raise_for_status()

            result = response.json()

            return {
                "success": True,
                "media_id": result['id'],
                "url": result['guid']['rendered'],
                "source_url": result.get('source_url'),
                "error": None
            }

        except Exception as e:
            return {
                "success": False,
                "media_id": None,
                "url": None,
                "error": str(e)
            }

    def upload_images_batch(
        self,
        image_paths: List[str],
        metadata: Optional[List[Dict[str, str]]] = None,
        post_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Upload multiple images to WordPress.

        Args:
            image_paths: List of image file paths
            metadata: List of metadata dicts (title, alt, description, caption)
            post_id: Associated post ID (optional)

        Returns:
            List of upload results
        """
        results = []

        for idx, path in enumerate(image_paths):
            # Get metadata for this image if provided
            meta = metadata[idx] if metadata and idx < len(metadata) else {}

            result = self.upload_image(
                image_path=path,
                title=meta.get('title', ''),
                alt_text=meta.get('alt', ''),
                description=meta.get('description', ''),
                caption=meta.get('caption', ''),
                post_id=post_id
            )

            results.append(result)

        return results

    def create_post(
        self,
        title: str,
        content: str,
        status: str = "draft",
        slug: Optional[str] = None,
        categories: Optional[List[int]] = None,
        tags: Optional[List[int]] = None,
        featured_media: Optional[int] = None,
        excerpt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a WordPress post.

        Args:
            title: Post title
            content: Post content (HTML)
            status: Post status ("draft" or "publish")
            slug: Post slug (URL-friendly name)
            categories: List of category IDs
            tags: List of tag IDs
            featured_media: Featured image media ID
            excerpt: Post excerpt

        Returns:
            Dictionary containing post creation result
        """
        try:
            # Prepare post data
            post_data = {
                "title": title,
                "content": content,
                "status": status
            }

            if slug:
                post_data["slug"] = slug
            if categories:
                post_data["categories"] = categories
            if tags:
                post_data["tags"] = tags
            if featured_media:
                post_data["featured_media"] = featured_media
            if excerpt:
                post_data["excerpt"] = excerpt

            # Create post
            response = requests.post(
                self.posts_endpoint,
                json=post_data,
                headers=self.headers,
                timeout=60
            )
            response.raise_for_status()

            result = response.json()

            return {
                "success": True,
                "post_id": result['id'],
                "post_url": result['link'],
                "status": result['status'],
                "error": None
            }

        except Exception as e:
            return {
                "success": False,
                "post_id": None,
                "post_url": None,
                "status": None,
                "error": str(e)
            }

    def update_post(
        self,
        post_id: int,
        title: Optional[str] = None,
        content: Optional[str] = None,
        status: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Update an existing WordPress post.

        Args:
            post_id: Post ID to update
            title: New title (optional)
            content: New content (optional)
            status: New status (optional)
            **kwargs: Additional post fields to update

        Returns:
            Dictionary containing update result
        """
        try:
            # Prepare update data
            update_data = {}
            if title:
                update_data["title"] = title
            if content:
                update_data["content"] = content
            if status:
                update_data["status"] = status

            update_data.update(kwargs)

            # Update post
            response = requests.post(
                f"{self.posts_endpoint}/{post_id}",
                json=update_data,
                headers=self.headers,
                timeout=60
            )
            response.raise_for_status()

            result = response.json()

            return {
                "success": True,
                "post_id": result['id'],
                "post_url": result['link'],
                "status": result['status'],
                "error": None
            }

        except Exception as e:
            return {
                "success": False,
                "post_id": post_id,
                "error": str(e)
            }

    def _guess_mime_type(self, file_path: str) -> str:
        """Guess MIME type from file extension."""
        ext = Path(file_path).suffix.lower()
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.svg': 'image/svg+xml'
        }
        return mime_types.get(ext, 'application/octet-stream')


def publish_to_wordpress(
    formatted_html: str,
    post_title: str,
    wordpress_site_url: Optional[str] = None,
    post_status: str = "draft",
    username: Optional[str] = None,
    app_password: Optional[str] = None,
    categories: Optional[List[int]] = None,
    tags: Optional[List[int]] = None,
    featured_image_url: Optional[str] = None,
    image_paths: Optional[List[str]] = None,
    image_metadata: Optional[List[Dict[str, str]]] = None
) -> Dict[str, Any]:
    """
    Publish formatted HTML and images to WordPress.

    Args:
        formatted_html: Final formatted HTML content
        post_title: Blog post title
        wordpress_site_url: Target WordPress site URL (from WP_BASE_URL env if not provided)
        post_status: "draft" or "publish" (default: "draft")
        username: WordPress username (from WP_USERNAME env if not provided)
        app_password: WordPress app password (from WP_APP_PASS env if not provided)
        categories: Category IDs or names
        tags: Tag names
        featured_image_url: URL of featured image
        image_paths: Local paths to images to upload
        image_metadata: Metadata for images (alt, title, etc.)

    Returns:
        Dictionary containing:
        - post_url: URL of the created WordPress post
        - post_id: WordPress post ID
        - status: Publication status
        - uploaded_images: List of uploaded image results
        - success: Boolean indicating success
        - error: Error message if failed
    """
    try:
        # Get WordPress site URL from environment if not provided
        if not wordpress_site_url:
            wordpress_site_url = os.getenv("WP_BASE_URL")

        if not wordpress_site_url:
            return {
                "success": False,
                "error": "WordPress site URL not provided. Set WP_BASE_URL environment variable or pass wordpress_site_url parameter."
            }

        # Get credentials from environment if not provided
        if not username:
            username = os.getenv("WP_USERNAME")
        if not app_password:
            app_password = os.getenv("WP_APP_PASS")

        if not username or not app_password:
            return {
                "success": False,
                "error": "WordPress credentials not provided. Set WP_USERNAME and WP_APP_PASS environment variables."
            }

        # Create publisher
        publisher = WordPressPublisher(wordpress_site_url, username, app_password)

        # Upload images first if provided
        uploaded_images = []
        if image_paths:
            uploaded_images = publisher.upload_images_batch(
                image_paths=image_paths,
                metadata=image_metadata
            )

            # Replace local image paths with WordPress URLs in HTML
            for idx, upload_result in enumerate(uploaded_images):
                if upload_result['success'] and idx < len(image_paths):
                    local_path = image_paths[idx]
                    wp_url = upload_result['source_url'] or upload_result['url']
                    formatted_html = formatted_html.replace(local_path, wp_url)

        # Determine featured image
        featured_media_id = None
        if uploaded_images and uploaded_images[0]['success']:
            featured_media_id = uploaded_images[0]['media_id']

        # Create post
        post_result = publisher.create_post(
            title=post_title,
            content=formatted_html,
            status=post_status,
            categories=categories,
            tags=tags,
            featured_media=featured_media_id
        )

        if not post_result['success']:
            return {
                "success": False,
                "error": f"Failed to create post: {post_result['error']}",
                "uploaded_images": uploaded_images
            }

        return {
            "success": True,
            "post_url": post_result['post_url'],
            "post_id": post_result['post_id'],
            "status": post_result['status'],
            "uploaded_images": uploaded_images,
            "error": None
        }

    except Exception as e:
        return {
            "success": False,
            "post_url": None,
            "post_id": None,
            "status": None,
            "uploaded_images": [],
            "error": str(e)
        }


if __name__ == "__main__":
    # Test configuration
    import dotenv
    dotenv.load_dotenv()

    print("WordPress Publisher Tool - Test")
    print("Note: Set WP_BASE_URL, WP_USERNAME, and WP_APP_PASS in .env file")
