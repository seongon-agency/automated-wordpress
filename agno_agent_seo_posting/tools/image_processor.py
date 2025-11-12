"""
Image Processor

Downloads images from URLs, resizes them according to configuration,
and prepares them for WordPress upload.
"""

import os
import re
import requests
import urllib.request
from PIL import Image
from pathlib import Path
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse, unquote


# Directories for image processing
RAW_IMAGES_DIR = Path("raw_images")
RESIZED_IMAGES_DIR = Path("resized_images")

# Ensure directories exist
RAW_IMAGES_DIR.mkdir(exist_ok=True)
RESIZED_IMAGES_DIR.mkdir(exist_ok=True)


def extract_image_urls(html: str) -> List[str]:
    """
    Extract all image URLs from HTML.

    Args:
        html: HTML content

    Returns:
        List of image URLs
    """
    # Find all <img src="..."> tags
    img_pattern = r'<img[^>]+src=["\']([^"\']+)["\']'
    urls = re.findall(img_pattern, html, re.IGNORECASE)

    # Filter out data URLs and invalid URLs
    valid_urls = []
    for url in urls:
        if url.startswith('http://') or url.startswith('https://'):
            valid_urls.append(url)

    return valid_urls


def download_images(image_urls: List[str], base_name: str = "image") -> Dict[str, Any]:
    """
    Download images from URLs to raw_images directory.

    Args:
        image_urls: List of image URLs to download
        base_name: Base name for saved files (default: "image")

    Returns:
        Dict containing:
        - success: bool
        - downloaded: List[Dict] with url, local_path, filename
        - failed: List[Dict] with url, error
    """
    downloaded = []
    failed = []

    for idx, url in enumerate(image_urls, 1):
        try:
            # Default to .png for Google Docs images (like old code)
            ext = '.png'

            # Generate filename
            filename = f"{base_name}_{idx}{ext}"
            local_path = RAW_IMAGES_DIR / filename

            # Download image using urllib (like old code)
            # This handles Google Docs images better than requests
            print(f"   Downloading image {idx}/{len(image_urls)}: {url[:80]}...")
            urllib.request.urlretrieve(url, str(local_path))

            print(f"   ✓ Downloaded: {filename}")

            downloaded.append({
                "url": url,
                "local_path": str(local_path),
                "filename": filename
            })

        except Exception as e:
            print(f"   ✗ Failed to download image {idx}: {str(e)}")
            failed.append({
                "url": url,
                "error": str(e)
            })

    return {
        "success": len(failed) == 0,
        "downloaded": downloaded,
        "failed": failed
    }


def resize_images(
    image_paths: List[str],
    target_width: int = 800,
    target_height: Optional[int] = None,
    quality: int = 92,
    image_format: str = "JPEG"
) -> Dict[str, Any]:
    """
    Resize images according to configuration.

    Args:
        image_paths: List of paths to images in raw_images directory
        target_width: Target width in pixels
        target_height: Target height (None = maintain aspect ratio)
        quality: JPEG quality 1-100
        image_format: Output format (JPEG, PNG, WEBP)

    Returns:
        Dict containing:
        - success: bool
        - resized: List[Dict] with original_path, resized_path, filename
        - failed: List[Dict] with original_path, error
    """
    resized = []
    failed = []

    for img_path in image_paths:
        try:
            # Open image
            img = Image.open(img_path)

            # Convert RGBA to RGB for JPEG
            if image_format.upper() == 'JPEG' and img.mode in ('RGBA', 'LA', 'P'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                rgb_img.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                img = rgb_img

            # Calculate new dimensions
            if target_height:
                new_size = (target_width, target_height)
            else:
                # Maintain aspect ratio
                width_percent = (target_width / float(img.size[0]))
                new_height = int((float(img.size[1]) * float(width_percent)))
                new_size = (target_width, new_height)

            # Resize image
            resized_img = img.resize(new_size, Image.Resampling.LANCZOS)

            # Generate output filename
            original_name = Path(img_path).stem
            ext = '.' + image_format.lower().replace('jpeg', 'jpg')
            output_filename = f"resized_{original_name}{ext}"
            output_path = RESIZED_IMAGES_DIR / output_filename

            # Save resized image
            resized_img.save(
                output_path,
                format=image_format.upper(),
                quality=quality,
                optimize=True
            )

            resized.append({
                "original_path": img_path,
                "resized_path": str(output_path),
                "filename": output_filename,
                "dimensions": new_size
            })

        except Exception as e:
            failed.append({
                "original_path": img_path,
                "error": str(e)
            })

    return {
        "success": len(failed) == 0,
        "resized": resized,
        "failed": failed
    }


def process_images_from_html(
    html: str,
    image_config: Optional[Dict] = None,
    base_name: str = "image"
) -> Dict[str, Any]:
    """
    Complete image processing pipeline: extract, download, resize.

    This is a convenience function that combines all steps.

    Args:
        html: HTML content containing images
        image_config: Dict with image settings (target_width, image_quality, etc.)
        base_name: Base name for saved files

    Returns:
        Dict containing:
        - success: bool
        - processed_images: List[Dict] with original_url, local_path info
        - failed: List of failures
    """
    # Default config
    if not image_config:
        image_config = {
            "target_width": 800,
            "image_quality": 92,
            "image_format": "JPEG"
        }

    # Extract image URLs
    image_urls = extract_image_urls(html)

    if not image_urls:
        return {
            "success": True,
            "processed_images": [],
            "message": "No images found in HTML"
        }

    # Download images
    download_result = download_images(image_urls, base_name)

    if not download_result['downloaded']:
        return {
            "success": False,
            "error": "Failed to download any images",
            "failed": download_result['failed']
        }

    # Resize images
    image_paths = [img['local_path'] for img in download_result['downloaded']]
    resize_result = resize_images(
        image_paths,
        target_width=image_config.get('target_width', 800),
        target_height=image_config.get('target_height'),
        quality=image_config.get('image_quality', 92),
        image_format=image_config.get('image_format', 'JPEG')
    )

    # Combine results
    processed = []
    for download_info, resize_info in zip(download_result['downloaded'], resize_result['resized']):
        processed.append({
            "original_url": download_info['url'],
            "raw_path": download_info['local_path'],
            "resized_path": resize_info['resized_path'],
            "filename": resize_info['filename'],
            "dimensions": resize_info['dimensions']
        })

    return {
        "success": True,
        "processed_images": processed,
        "download_failed": download_result['failed'],
        "resize_failed": resize_result['failed']
    }


# Make functions available as Agno tools
extract_image_urls.__annotations__ = {'html': str, 'return': List[str]}
download_images.__annotations__ = {'image_urls': List[str], 'base_name': str, 'return': Dict[str, Any]}
resize_images.__annotations__ = {
    'image_paths': List[str],
    'target_width': int,
    'target_height': Optional[int],
    'quality': int,
    'image_format': str,
    'return': Dict[str, Any]
}
process_images_from_html.__annotations__ = {
    'html': str,
    'image_config': Optional[Dict],
    'base_name': str,
    'return': Dict[str, Any]
}
