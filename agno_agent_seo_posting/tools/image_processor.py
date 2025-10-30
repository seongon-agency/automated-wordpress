"""
Tool 2: Image Processing & Tag Generator
Handles image resizing, WordPress upload, and generates proper <img> tags

Flow:
1. Extract image tags from HTML
2. Download images from Google Docs
3. Resize images to target dimensions
4. Upload images to WordPress (if credentials provided)
5. Replace image URLs in HTML with WordPress URLs
"""

import os
import io
import re
import base64
import requests
from typing import Dict, List, Any, Optional
from pathlib import Path
from PIL import Image
from bs4 import BeautifulSoup
from urllib.parse import urlparse


class ImageProcessor:
    """Process images from HTML content."""

    def __init__(self, output_dir: str = "processed_images"):
        """
        Initialize the image processor.

        Args:
            output_dir: Directory to save processed images
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def extract_images_from_html(self, html_content: str) -> List[Dict[str, Any]]:
        """
        Extract all image references from HTML content.

        Args:
            html_content: HTML string containing images

        Returns:
            List of dictionaries containing image info (src, alt, title, etc.)
        """
        soup = BeautifulSoup(html_content, "html.parser")
        images = []

        for idx, img in enumerate(soup.find_all("img")):
            img_info = {
                "index": idx,
                "src": img.get("src", ""),
                "alt": img.get("alt", ""),
                "title": img.get("title", ""),
                "width": img.get("width"),
                "height": img.get("height"),
                "original_tag": str(img)
            }
            images.append(img_info)

        return images

    def download_image(self, url: str, timeout: int = 60) -> io.BytesIO:
        """
        Download image from URL to memory.

        Args:
            url: Image URL
            timeout: Request timeout in seconds

        Returns:
            BytesIO object containing image data
        """
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return io.BytesIO(response.content)

    def resize_image(
        self,
        img_bytes: io.BytesIO,
        target_width: Optional[int] = 800,
        target_height: Optional[int] = None,
        maintain_aspect: bool = True
    ) -> tuple[Image.Image, int, int]:
        """
        Resize image to target dimensions.

        Args:
            img_bytes: BytesIO object containing image data
            target_width: Desired width (default: 800px)
            target_height: Desired height (None = maintain aspect ratio)
            maintain_aspect: Whether to maintain aspect ratio

        Returns:
            Tuple of (resized_image, new_width, new_height)
        """
        with Image.open(img_bytes) as im:
            original_width, original_height = im.size

            if maintain_aspect and target_height is None:
                # Calculate height to maintain aspect ratio
                if target_width:
                    ratio = target_width / original_width
                    new_width = target_width
                    new_height = int(original_height * ratio)
                else:
                    new_width, new_height = original_width, original_height
            elif target_width and target_height:
                # Use exact dimensions (may distort)
                new_width, new_height = target_width, target_height
            else:
                # No resize needed
                new_width, new_height = original_width, original_height

            # Don't upscale
            if new_width > original_width:
                new_width, new_height = original_width, original_height

            # Resize image
            resized = im.convert("RGBA").resize((new_width, new_height), Image.LANCZOS)

            return resized, new_width, new_height

    def save_image(
        self,
        image: Image.Image,
        filename: str,
        format: str = "JPEG",
        quality: int = 92
    ) -> str:
        """
        Save image to disk.

        Args:
            image: PIL Image object
            filename: Output filename
            format: Image format (JPEG, PNG, WEBP)
            quality: Compression quality (1-100)

        Returns:
            Path to saved file
        """
        output_path = self.output_dir / filename

        if format.upper() in ["JPEG", "JPG"]:
            # Convert RGBA to RGB for JPEG
            bg = Image.new("RGB", image.size, (255, 255, 255))
            if image.mode == "RGBA":
                bg.paste(image, mask=image.split()[-1])
            else:
                bg = image.convert("RGB")
            bg.save(output_path, format="JPEG", quality=quality, optimize=True)
        elif format.upper() == "PNG":
            image.save(output_path, format="PNG", optimize=True)
        elif format.upper() == "WEBP":
            image.save(output_path, format="WEBP", quality=quality, method=6)
        else:
            image.save(output_path)

        return str(output_path)

    def upload_to_wordpress(
        self,
        image_path: str,
        alt_text: str = "",
        title: str = "",
        wordpress_site_url: str = "",
        wordpress_username: str = "",
        wordpress_app_password: str = ""
    ) -> Dict[str, Any]:
        """
        Upload image to WordPress media library.

        Args:
            image_path: Local path to the image file
            alt_text: Alt text for accessibility
            title: Image title
            wordpress_site_url: WordPress site URL
            wordpress_username: WordPress username
            wordpress_app_password: WordPress application password

        Returns:
            Dictionary containing upload result with media_id and url
        """
        try:
            # Prepare API endpoint
            api_url = f"{wordpress_site_url.rstrip('/')}/wp-json/wp/v2/media"

            # Create authorization header
            token = base64.b64encode(
                f"{wordpress_username}:{wordpress_app_password}".encode("utf-8")
            ).decode("utf-8")

            # Read image file
            with open(image_path, 'rb') as f:
                image_data = f.read()

            # Get filename and detect mime type
            filename = Path(image_path).name
            ext = Path(image_path).suffix.lower()
            mime_types = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp',
            }
            mime_type = mime_types.get(ext, 'image/jpeg')

            # Prepare headers
            headers = {
                'Authorization': f'Basic {token}',
                'Content-Type': mime_type,
                'Content-Disposition': f'attachment; filename={filename}'
            }

            # Prepare parameters
            params = {
                'title': title or filename,
                'alt_text': alt_text,
            }

            # Upload to WordPress
            response = requests.post(
                api_url,
                headers=headers,
                data=image_data,
                params=params,
                timeout=60
            )
            response.raise_for_status()

            result = response.json()

            return {
                "success": True,
                "media_id": result['id'],
                "url": result.get('source_url') or result['guid']['rendered'],
                "error": None
            }

        except Exception as e:
            return {
                "success": False,
                "media_id": None,
                "url": None,
                "error": str(e)
            }

    def generate_img_tag(
        self,
        src: str,
        alt: str = "",
        width: Optional[int] = None,
        height: Optional[int] = None,
        css_class: str = "",
        title: str = ""
    ) -> str:
        """
        Generate SEO-friendly <img> tag.

        Args:
            src: Image source URL
            alt: Alt text for accessibility
            width: Image width
            height: Image height
            css_class: CSS class(es)
            title: Title attribute

        Returns:
            HTML img tag string
        """
        parts = [f'<img src="{src}"']

        if alt:
            parts.append(f'alt="{alt}"')
        if width:
            parts.append(f'width="{width}"')
        if height:
            parts.append(f'height="{height}"')
        if css_class:
            parts.append(f'class="{css_class}"')
        if title:
            parts.append(f'title="{title}"')

        parts.append("/>")
        return " ".join(parts)


def process_images(
    html_content: str,
    target_width: Optional[int] = 800,
    target_height: Optional[int] = None,
    upload_to_wordpress: bool = False,
    wordpress_site_url: Optional[str] = None,
    wordpress_username: Optional[str] = None,
    wordpress_app_password: Optional[str] = None
) -> Dict[str, Any]:
    """
    Process images from HTML content: extract, download, resize, and optionally upload to WordPress.

    Flow:
    1. Extract image tags from HTML
    2. Download images from their source URLs
    3. Resize images to target dimensions
    4. Upload to WordPress (if credentials provided)
    5. Replace image URLs in HTML with WordPress URLs

    Args:
        html_content: HTML content containing image references
        target_width: Desired image width (default: 800px)
        target_height: Desired image height (None = maintain aspect ratio)
        upload_to_wordpress: Whether to upload images to WordPress
        wordpress_site_url: WordPress site URL (from WP_BASE_URL env if not provided)
        wordpress_username: WordPress username (from WP_USERNAME env if not provided)
        wordpress_app_password: WordPress app password (from WP_APP_PASS env if not provided)

    Returns:
        Dictionary containing:
        - processed_html: HTML with properly formatted <img> tags and WordPress URLs
        - image_metadata: List of processed images with URLs and dimensions
        - success: Boolean indicating success
        - error: Error message if failed
    """
    try:
        processor = ImageProcessor()

        # Get WordPress credentials from environment if not provided
        if upload_to_wordpress:
            if not wordpress_site_url:
                wordpress_site_url = os.getenv("WP_BASE_URL")
            if not wordpress_username:
                wordpress_username = os.getenv("WP_USERNAME")
            if not wordpress_app_password:
                wordpress_app_password = os.getenv("WP_APP_PASS")

            # Validate credentials
            if not all([wordpress_site_url, wordpress_username, wordpress_app_password]):
                return {
                    "success": False,
                    "processed_html": html_content,
                    "image_metadata": [],
                    "error": "WordPress credentials not provided. Set WP_BASE_URL, WP_USERNAME, and WP_APP_PASS."
                }

        # Extract images from HTML
        images = processor.extract_images_from_html(html_content)

        if not images:
            return {
                "success": True,
                "processed_html": html_content,
                "image_metadata": [],
                "error": None
            }

        print(f"   Found {len(images)} images to process")

        # Process each image
        processed_images = []
        soup = BeautifulSoup(html_content, "html.parser")

        for idx, img_info in enumerate(images):
            try:
                print(f"   Processing image {idx + 1}/{len(images)}...")

                # Step 1: Download image
                img_bytes = processor.download_image(img_info["src"])

                # Step 2: Resize image
                resized_img, new_width, new_height = processor.resize_image(
                    img_bytes,
                    target_width=target_width,
                    target_height=target_height
                )

                # Step 3: Save image locally
                filename = f"image_{idx + 1}.jpg"
                local_path = processor.save_image(resized_img, filename)

                # Step 4: Upload to WordPress (if enabled)
                wordpress_url = None
                wordpress_media_id = None
                if upload_to_wordpress:
                    print(f"      Uploading to WordPress...")
                    upload_result = processor.upload_to_wordpress(
                        image_path=local_path,
                        alt_text=img_info["alt"] or f"Image {idx + 1}",
                        title=img_info["title"] or f"Image {idx + 1}",
                        wordpress_site_url=wordpress_site_url,
                        wordpress_username=wordpress_username,
                        wordpress_app_password=wordpress_app_password
                    )

                    if upload_result["success"]:
                        wordpress_url = upload_result["url"]
                        wordpress_media_id = upload_result["media_id"]
                        print(f"      ✓ Uploaded to WordPress: {wordpress_url}")
                    else:
                        print(f"      ✗ WordPress upload failed: {upload_result['error']}")

                # Determine final URL (WordPress URL if available, otherwise local path)
                final_url = wordpress_url if wordpress_url else local_path

                # Step 5: Generate new img tag with final URL
                new_img_tag = processor.generate_img_tag(
                    src=final_url,
                    alt=img_info["alt"] or f"Image {idx + 1}",
                    width=new_width,
                    height=new_height,
                    title=img_info["title"]
                )

                # Store metadata
                image_metadata = {
                    "index": idx,
                    "original_src": img_info["src"],
                    "local_path": local_path,
                    "resized_path": local_path,  # For backward compatibility
                    "width": new_width,
                    "height": new_height,
                    "alt": img_info["alt"] or f"Image {idx + 1}",
                    "title": img_info["title"] or "",
                    "new_tag": new_img_tag
                }

                # Add WordPress metadata if uploaded
                if wordpress_url:
                    image_metadata["wordpress_url"] = wordpress_url
                    image_metadata["wordpress_media_id"] = wordpress_media_id
                    image_metadata["new_src"] = wordpress_url
                else:
                    image_metadata["new_src"] = local_path

                processed_images.append(image_metadata)

                # Replace in HTML
                img_tags = soup.find_all("img")
                if idx < len(img_tags):
                    img_tags[idx].replace_with(BeautifulSoup(new_img_tag, "html.parser"))

            except Exception as e:
                print(f"   ✗ Failed to process image {idx + 1}: {e}")
                processed_images.append({
                    "index": idx,
                    "error": str(e),
                    "original_src": img_info["src"]
                })

        processed_html = str(soup)

        print(f"   ✓ Successfully processed {len(processed_images)} images")

        return {
            "success": True,
            "processed_html": processed_html,
            "image_metadata": processed_images,
            "error": None
        }

    except Exception as e:
        return {
            "success": False,
            "processed_html": html_content,
            "image_metadata": [],
            "error": str(e)
        }


if __name__ == "__main__":
    # Test the tool
    test_html = '''
    <html>
        <body>
            <p>Test paragraph</p>
            <img src="https://via.placeholder.com/1200x800" alt="Test image" />
        </body>
    </html>
    '''

    result = process_images(test_html, target_width=800)
    print(f"Success: {result['success']}")
    print(f"Processed {len(result['image_metadata'])} images")
