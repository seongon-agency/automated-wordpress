"""
Image Processor Service

Downloads images from URLs, resizes them, and prepares for WordPress upload.
"""

import os
import re
import urllib.request
import unicodedata
from pathlib import Path
from typing import Dict, List, Optional, Any
from PIL import Image
from bs4 import BeautifulSoup


# Directories for image processing
RAW_IMAGES_DIR = Path("/tmp/raw_images")
RESIZED_IMAGES_DIR = Path("/tmp/resized_images")

# Ensure directories exist
RAW_IMAGES_DIR.mkdir(exist_ok=True)
RESIZED_IMAGES_DIR.mkdir(exist_ok=True)


def text_to_slug(text: str, max_words: Optional[int] = None) -> str:
    """Convert text to URL-friendly slug format."""
    if not text:
        return ""

    text = unicodedata.normalize('NFD', text)
    text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    words = text.split()

    if max_words and max_words > 0:
        words = words[:max_words]

    slug = '-'.join(words)
    slug = re.sub(r'-+', '-', slug)
    slug = slug.strip('-')

    return slug


def extract_images_with_alt(html: str) -> List[Dict[str, Any]]:
    """Extract image URLs with their alt text and dimensions from HTML."""
    soup = BeautifulSoup(html, 'lxml')
    images = []

    for img in soup.find_all('img'):
        src = img.get('src', '')

        if not (src.startswith('http://') or src.startswith('https://')):
            continue

        alt = img.get('alt', '') or img.get('title', '') or ''

        width = None
        height = None

        width_attr = img.get('width', '')
        height_attr = img.get('height', '')

        if width_attr:
            try:
                width = int(str(width_attr).replace('px', '').strip())
            except (ValueError, AttributeError):
                pass

        if height_attr:
            try:
                height = int(str(height_attr).replace('px', '').strip())
            except (ValueError, AttributeError):
                pass

        # Try style attribute if dimensions not found
        if width is None or height is None:
            style = img.get('style', '')
            if style:
                if width is None:
                    width_match = re.search(r'width\s*:\s*(\d+(?:\.\d+)?)\s*px', style, re.IGNORECASE)
                    if width_match:
                        width = int(float(width_match.group(1)))
                if height is None:
                    height_match = re.search(r'height\s*:\s*(\d+(?:\.\d+)?)\s*px', style, re.IGNORECASE)
                    if height_match:
                        height = int(float(height_match.group(1)))

        images.append({
            'url': src,
            'alt': alt.strip(),
            'width': width,
            'height': height
        })

    return images


def download_images(
    image_urls: List[str],
    naming_method: str = "default",
    main_keyword: str = "",
    alt_text_words: int = 5,
    image_alt_texts: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Download images from URLs to temp directory."""
    downloaded = []
    failed = []
    unnamed_counter = [0]

    for idx, url in enumerate(image_urls, 1):
        try:
            ext = '.png'
            alt_text = ""
            if image_alt_texts and idx - 1 < len(image_alt_texts):
                alt_text = image_alt_texts[idx - 1]

            # Generate filename
            if naming_method == "alt_text" and alt_text:
                slug = text_to_slug(alt_text, max_words=alt_text_words)
                if slug:
                    filename_base = slug
                else:
                    unnamed_counter[0] += 1
                    filename_base = f"unnamed-image-{unnamed_counter[0]}"
            elif naming_method == "main_keyword" and main_keyword:
                slug = text_to_slug(main_keyword)
                filename_base = f"{slug}-{idx:02d}" if slug else f"image-{idx:02d}"
            else:
                filename_base = f"image_{idx}"

            filename = f"{filename_base}{ext}"
            local_path = RAW_IMAGES_DIR / filename

            # Modify Google Docs URLs to get full resolution
            download_url = url
            if 'googleusercontent.com' in url:
                download_url = re.sub(r'=w\d+(-h\d+)?$', '=s0', url)
                download_url = re.sub(r'=s\d+$', '=s0', download_url)
                download_url = re.sub(r'=h\d+$', '=s0', download_url)
                if '=s0' not in download_url and '=' not in download_url.split('/')[-1]:
                    download_url = url + '=s0'

            urllib.request.urlretrieve(download_url, str(local_path))

            downloaded.append({
                "url": url,
                "local_path": str(local_path),
                "filename": filename
            })

        except Exception as e:
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
    quality: int = 92,
    image_format: str = "JPEG",
    per_image_dimensions: Optional[List[tuple]] = None
) -> Dict[str, Any]:
    """Resize images according to configuration."""
    resized = []
    failed = []

    for idx, img_path in enumerate(image_paths):
        try:
            img = Image.open(img_path)

            # Convert RGBA to RGB for JPEG
            if image_format.upper() == 'JPEG' and img.mode in ('RGBA', 'LA', 'P'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                rgb_img.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                img = rgb_img

            # Determine dimensions
            if per_image_dimensions and idx < len(per_image_dimensions):
                target_w, target_h = per_image_dimensions[idx]
                if target_w and target_h:
                    new_size = (target_w, target_h)
                elif target_w:
                    width_percent = (target_w / float(img.size[0]))
                    new_height = int((float(img.size[1]) * float(width_percent)))
                    new_size = (target_w, new_height)
                else:
                    width_percent = (target_width / float(img.size[0]))
                    new_height = int((float(img.size[1]) * float(width_percent)))
                    new_size = (target_width, new_height)
            else:
                width_percent = (target_width / float(img.size[0]))
                new_height = int((float(img.size[1]) * float(width_percent)))
                new_size = (target_width, new_height)

            resized_img = img.resize(new_size, Image.Resampling.LANCZOS)

            original_name = Path(img_path).stem
            ext = '.' + image_format.lower().replace('jpeg', 'jpg')
            output_filename = f"{original_name}{ext}"
            output_path = RESIZED_IMAGES_DIR / output_filename

            save_kwargs = {'format': image_format.upper()}
            if image_format.upper() == 'JPEG':
                save_kwargs['quality'] = quality
                save_kwargs['subsampling'] = 0
                save_kwargs['optimize'] = False
            elif image_format.upper() == 'PNG':
                save_kwargs['compress_level'] = 6
            elif image_format.upper() == 'WEBP':
                save_kwargs['quality'] = quality
                save_kwargs['method'] = 6

            resized_img.save(output_path, **save_kwargs)

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


async def process_images_from_html(
    html: str,
    image_config: Optional[Dict] = None,
    main_keyword: str = ""
) -> Dict[str, Any]:
    """
    Complete image processing pipeline: extract, download, resize.
    """
    if not image_config:
        image_config = {
            "target_width": 800,
            "image_quality": 92,
            "image_format": "JPEG",
            "resize_method": "fixed_width",
            "naming_method": "default",
            "alt_text_words": 5
        }

    resize_method = image_config.get('resize_method', 'fixed_width')
    naming_method = image_config.get('naming_method', 'default')

    # Extract images with alt text
    images_with_alt = extract_images_with_alt(html)
    image_urls = [img['url'] for img in images_with_alt]
    image_alt_texts = [img['alt'] for img in images_with_alt]

    if not image_urls:
        return {
            "success": True,
            "processed_images": [],
            "message": "No images found in HTML"
        }

    # Download images
    download_result = download_images(
        image_urls,
        naming_method=naming_method,
        main_keyword=main_keyword,
        alt_text_words=image_config.get('alt_text_words', 5),
        image_alt_texts=image_alt_texts
    )

    if not download_result['downloaded']:
        return {
            "success": False,
            "error": "Failed to download any images",
            "failed": download_result['failed']
        }

    image_paths = [img['local_path'] for img in download_result['downloaded']]

    # Handle different resize methods
    if resize_method == 'google_docs_original':
        per_image_dimensions = []
        for download_info in download_result['downloaded']:
            matching_meta = next(
                (img for img in images_with_alt if img['url'] == download_info['url']),
                None
            )
            if matching_meta and matching_meta.get('width'):
                per_image_dimensions.append((matching_meta['width'], matching_meta['height']))
            else:
                per_image_dimensions.append((image_config.get('target_width', 800), None))

        resize_result = resize_images(
            image_paths,
            target_width=image_config.get('target_width', 800),
            quality=image_config.get('image_quality', 92),
            image_format=image_config.get('image_format', 'JPEG'),
            per_image_dimensions=per_image_dimensions
        )
    else:
        resize_result = resize_images(
            image_paths,
            target_width=image_config.get('target_width', 800),
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
