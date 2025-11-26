"""
Image Processor

Downloads images from URLs, resizes them according to configuration,
and prepares them for WordPress upload.

Supports two image naming options:
1. Alt Text Based: Use first N words of alt text in slug format
2. Main Keyword Based: Use provided keyword with numbered suffix
"""

import os
import re
import requests
import urllib.request
import unicodedata
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


def text_to_slug(text: str, max_words: Optional[int] = None) -> str:
    """
    Convert text to URL-friendly slug format.

    Args:
        text: Input text to convert
        max_words: Maximum number of words to include (None = all words)

    Returns:
        Slug string (lowercase, hyphens, no special chars)

    Examples:
        "Hello World!" -> "hello-world"
        "Quạt trần kêu ù ù" -> "quat-tran-keu-u-u"
        "Image with 10 words here" (max_words=3) -> "image-with-10"
    """
    if not text:
        return ""

    # Normalize unicode characters (convert Vietnamese, etc. to ASCII-like)
    # NFD decomposition separates base characters from diacritics
    text = unicodedata.normalize('NFD', text)

    # Remove diacritical marks (accents)
    text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')

    # Convert to lowercase
    text = text.lower()

    # Replace any non-alphanumeric characters with spaces
    text = re.sub(r'[^a-z0-9\s]', ' ', text)

    # Split into words
    words = text.split()

    # Limit words if specified
    if max_words and max_words > 0:
        words = words[:max_words]

    # Join with hyphens
    slug = '-'.join(words)

    # Remove consecutive hyphens
    slug = re.sub(r'-+', '-', slug)

    # Remove leading/trailing hyphens
    slug = slug.strip('-')

    return slug


def extract_images_with_alt(html: str) -> List[Dict[str, Any]]:
    """
    Extract image URLs with their alt text and dimensions from HTML.

    Args:
        html: HTML content

    Returns:
        List of dicts with 'url', 'alt', 'width', 'height'
    """
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, 'html.parser')
    images = []

    for img in soup.find_all('img'):
        src = img.get('src', '')

        # Only process valid HTTP(S) URLs
        if not (src.startswith('http://') or src.startswith('https://')):
            continue

        # Get alt text
        alt = img.get('alt', '') or img.get('title', '') or ''

        # Get dimensions
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
                        try:
                            width = int(float(width_match.group(1)))
                        except ValueError:
                            pass

                if height is None:
                    height_match = re.search(r'height\s*:\s*(\d+(?:\.\d+)?)\s*px', style, re.IGNORECASE)
                    if height_match:
                        try:
                            height = int(float(height_match.group(1)))
                        except ValueError:
                            pass

        images.append({
            'url': src,
            'alt': alt.strip(),
            'width': width,
            'height': height
        })

    return images


def generate_image_filename(
    index: int,
    naming_method: str = "default",
    alt_text: str = "",
    main_keyword: str = "",
    alt_text_words: int = 5,
    base_name: str = "image",
    unnamed_counter: Optional[List[int]] = None
) -> str:
    """
    Generate filename for an image based on naming method.

    Args:
        index: Image index (1-based)
        naming_method: "default", "alt_text", or "main_keyword"
        alt_text: Alt text of the image (for alt_text method)
        main_keyword: Main keyword (for main_keyword method)
        alt_text_words: Number of words to use from alt text
        base_name: Base name for default naming
        unnamed_counter: Mutable list with single int for tracking unnamed images

    Returns:
        Filename without extension
    """
    if naming_method == "alt_text":
        if alt_text and alt_text.strip():
            # Use first N words of alt text as slug
            slug = text_to_slug(alt_text, max_words=alt_text_words)
            if slug:
                return slug

        # No alt text - use unnamed_image_N
        if unnamed_counter is not None:
            unnamed_counter[0] += 1
            return f"unnamed-image-{unnamed_counter[0]}"
        else:
            return f"unnamed-image-{index}"

    elif naming_method == "main_keyword":
        if main_keyword and main_keyword.strip():
            slug = text_to_slug(main_keyword)
            if slug:
                # Format with leading zero for numbers < 10
                return f"{slug}-{index:02d}"

        # Fallback if no keyword
        return f"image-{index:02d}"

    else:  # default
        return f"{base_name}_{index}"


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


def extract_image_metadata(html: str) -> List[Dict[str, Any]]:
    """
    Extract image URLs with their dimensions from HTML.

    Args:
        html: HTML content

    Returns:
        List of dicts with 'url', 'width', 'height' (dimensions in pixels or None if not specified)
    """
    from bs4 import BeautifulSoup
    import re

    soup = BeautifulSoup(html, 'html.parser')
    image_metadata = []

    for img in soup.find_all('img'):
        src = img.get('src', '')

        # Only process valid HTTP(S) URLs
        if not (src.startswith('http://') or src.startswith('https://')):
            continue

        # Extract width and height attributes
        width_attr = img.get('width', '')
        height_attr = img.get('height', '')

        # Parse dimensions (remove 'px' suffix if present)
        width = None
        height = None

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

        # If width/height not found in attributes, try to extract from style attribute
        if width is None or height is None:
            style = img.get('style', '')
            if style:
                # Extract width from style (e.g., "width: 500px" or "width:500px")
                if width is None:
                    width_match = re.search(r'width\s*:\s*(\d+(?:\.\d+)?)\s*px', style, re.IGNORECASE)
                    if width_match:
                        try:
                            width = int(float(width_match.group(1)))
                        except ValueError:
                            pass

                # Extract height from style (e.g., "height: 300px" or "height:300px")
                if height is None:
                    height_match = re.search(r'height\s*:\s*(\d+(?:\.\d+)?)\s*px', style, re.IGNORECASE)
                    if height_match:
                        try:
                            height = int(float(height_match.group(1)))
                        except ValueError:
                            pass

        image_metadata.append({
            'url': src,
            'width': width,
            'height': height
        })

    return image_metadata


def download_images(
    image_urls: List[str],
    base_name: str = "image",
    naming_config: Optional[Dict[str, Any]] = None,
    image_alt_texts: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Download images from URLs to raw_images directory.

    Args:
        image_urls: List of image URLs to download
        base_name: Base name for saved files (default: "image")
        naming_config: Optional dict with naming settings:
            - naming_method: "default", "alt_text", or "main_keyword"
            - alt_text_words: Number of words for alt_text method (default: 5)
            - main_keyword: Keyword for main_keyword method
        image_alt_texts: Optional list of alt texts matching image_urls order

    Returns:
        Dict containing:
        - success: bool
        - downloaded: List[Dict] with url, local_path, filename
        - failed: List[Dict] with url, error
    """
    downloaded = []
    failed = []

    # Parse naming config
    naming_method = "default"
    alt_text_words = 5
    main_keyword = ""

    if naming_config:
        naming_method = naming_config.get('naming_method', 'default')
        alt_text_words = naming_config.get('alt_text_words', 5)
        main_keyword = naming_config.get('main_keyword', '')

    # Counter for unnamed images (alt_text method)
    unnamed_counter = [0]

    for idx, url in enumerate(image_urls, 1):
        try:
            # Default to .png for Google Docs images (like old code)
            ext = '.png'

            # Get alt text for this image if available
            alt_text = ""
            if image_alt_texts and idx - 1 < len(image_alt_texts):
                alt_text = image_alt_texts[idx - 1]

            # Generate filename based on naming method
            filename_base = generate_image_filename(
                index=idx,
                naming_method=naming_method,
                alt_text=alt_text,
                main_keyword=main_keyword,
                alt_text_words=alt_text_words,
                base_name=base_name,
                unnamed_counter=unnamed_counter
            )
            filename = f"{filename_base}{ext}"
            local_path = RAW_IMAGES_DIR / filename

            # Modify Google Docs image URLs to get FULL RESOLUTION
            # Google serves images with size params like =w800-h600 or =s800
            # We can get original quality by using =s0 (original size) or =w0-h0
            download_url = url
            if 'googleusercontent.com' in url:
                # Remove existing size parameters and request original size
                # Patterns: =w800, =h600, =w800-h600, =s800
                download_url = re.sub(r'=w\d+(-h\d+)?$', '=s0', url)
                download_url = re.sub(r'=s\d+$', '=s0', download_url)
                download_url = re.sub(r'=h\d+$', '=s0', download_url)
                # If no size param found, add =s0 to get original
                if '=s0' not in download_url and '=' not in download_url.split('/')[-1]:
                    download_url = url + '=s0'
                if download_url != url:
                    print(f"   📷 Requesting full resolution image...")

            # Download image using urllib (like old code)
            # This handles Google Docs images better than requests
            print(f"   Downloading image {idx}/{len(image_urls)}: {download_url[:80]}...")
            urllib.request.urlretrieve(download_url, str(local_path))

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


def copy_images_without_resize(
    image_paths: List[str]
) -> Dict[str, Any]:
    """
    Copy images to output directory without resizing or re-encoding.
    Preserves original quality.

    Args:
        image_paths: List of paths to images in raw_images directory

    Returns:
        Dict containing:
        - success: bool
        - resized: List[Dict] with original_path, resized_path, filename, dimensions
        - failed: List[Dict] with original_path, error
    """
    import shutil

    copied = []
    failed = []

    for img_path in image_paths:
        try:
            path = Path(img_path)
            if not path.exists():
                failed.append({
                    "original_path": img_path,
                    "error": "File not found"
                })
                continue

            # Get original dimensions
            img = Image.open(img_path)
            original_size = img.size
            img.close()

            # Copy to output directory with same name
            output_path = RESIZED_IMAGES_DIR / path.name
            shutil.copy2(img_path, output_path)

            copied.append({
                "original_path": img_path,
                "resized_path": str(output_path),
                "filename": path.name,
                "dimensions": original_size
            })

        except Exception as e:
            failed.append({
                "original_path": img_path,
                "error": str(e)
            })

    return {
        "success": len(failed) == 0,
        "resized": copied,  # Keep same key for compatibility
        "failed": failed
    }


def resize_images(
    image_paths: List[str],
    target_width: int = 800,
    target_height: Optional[int] = None,
    quality: int = 92,
    image_format: str = "JPEG",
    per_image_dimensions: Optional[List[tuple]] = None
) -> Dict[str, Any]:
    """
    Resize images according to configuration.

    Args:
        image_paths: List of paths to images in raw_images directory
        target_width: Target width in pixels (used if per_image_dimensions is None)
        target_height: Target height (None = maintain aspect ratio)
        quality: JPEG quality 1-100
        image_format: Output format (JPEG, PNG, WEBP)
        per_image_dimensions: Optional list of (width, height) tuples for each image
                             If provided, overrides target_width/target_height for each image

    Returns:
        Dict containing:
        - success: bool
        - resized: List[Dict] with original_path, resized_path, filename
        - failed: List[Dict] with original_path, error
    """
    resized = []
    failed = []

    for idx, img_path in enumerate(image_paths):
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

            # Determine dimensions for this image
            if per_image_dimensions and idx < len(per_image_dimensions):
                # Use Google Docs dimensions if provided
                target_w, target_h = per_image_dimensions[idx]
                if target_w and target_h:
                    new_size = (target_w, target_h)
                elif target_w:
                    # Only width specified, maintain aspect ratio
                    width_percent = (target_w / float(img.size[0]))
                    new_height = int((float(img.size[1]) * float(width_percent)))
                    new_size = (target_w, new_height)
                else:
                    # Fallback to default if no dimensions
                    width_percent = (target_width / float(img.size[0]))
                    new_height = int((float(img.size[1]) * float(width_percent)))
                    new_size = (target_width, new_height)
            else:
                # Use default target dimensions
                if target_height:
                    new_size = (target_width, target_height)
                else:
                    # Maintain aspect ratio
                    width_percent = (target_width / float(img.size[0]))
                    new_height = int((float(img.size[1]) * float(width_percent)))
                    new_size = (target_width, new_height)

            # Resize image
            resized_img = img.resize(new_size, Image.Resampling.LANCZOS)

            # Generate output filename (keep original name, no "resized_" prefix)
            original_name = Path(img_path).stem
            ext = '.' + image_format.lower().replace('jpeg', 'jpg')
            output_filename = f"{original_name}{ext}"
            output_path = RESIZED_IMAGES_DIR / output_filename

            # Save resized image with maximum quality settings
            save_kwargs = {
                'format': image_format.upper(),
            }

            if image_format.upper() == 'JPEG':
                # JPEG-specific settings for maximum quality:
                # - subsampling=0 means 4:4:4 (no chroma subsampling, preserves color detail)
                # - quality=100 is maximum
                save_kwargs['quality'] = quality
                save_kwargs['subsampling'] = 0  # 4:4:4 - no color loss
                save_kwargs['optimize'] = False  # Don't optimize, preserve quality
            elif image_format.upper() == 'PNG':
                # PNG is lossless, compress_level controls file size vs speed
                save_kwargs['compress_level'] = 6  # Balance between size and speed
            elif image_format.upper() == 'WEBP':
                # WebP settings
                save_kwargs['quality'] = quality
                save_kwargs['method'] = 6  # Highest quality compression method

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


def process_images_from_html(
    html: str,
    image_config: Optional[Dict] = None,
    base_name: str = "image",
    main_keyword: str = ""
) -> Dict[str, Any]:
    """
    Complete image processing pipeline: extract, download, resize.

    This is a convenience function that combines all steps.

    Args:
        html: HTML content containing images
        image_config: Dict with image settings:
            - target_width: int (default 800)
            - image_quality: int (default 92)
            - image_format: str (default "JPEG")
            - resize_method: str ("fixed_width" or "google_docs_original")
            - naming_method: str ("default", "alt_text", or "main_keyword")
            - alt_text_words: int (default 5, for alt_text naming)
        base_name: Base name for saved files (for default naming)
        main_keyword: Main keyword for main_keyword naming method

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
            "image_format": "JPEG",
            "resize_method": "fixed_width",
            "naming_method": "default",
            "alt_text_words": 5
        }

    # Get resize method (default to "fixed_width" for backward compatibility)
    resize_method = image_config.get('resize_method', 'fixed_width')
    naming_method = image_config.get('naming_method', 'default')

    # Extract images with alt text for naming
    images_with_alt = extract_images_with_alt(html)
    image_urls = [img['url'] for img in images_with_alt]
    image_alt_texts = [img['alt'] for img in images_with_alt]

    # Log naming method
    if naming_method == "alt_text":
        alt_text_words = image_config.get('alt_text_words', 5)
        print(f"   Using alt text naming (first {alt_text_words} words)")
    elif naming_method == "main_keyword":
        print(f"   Using main keyword naming: '{main_keyword}'")
    else:
        print(f"   Using default naming: {base_name}_N")

    if not image_urls:
        return {
            "success": True,
            "processed_images": [],
            "message": "No images found in HTML"
        }

    # Prepare naming config
    naming_config = {
        "naming_method": naming_method,
        "alt_text_words": image_config.get('alt_text_words', 5),
        "main_keyword": main_keyword
    }

    # Download images with naming config
    download_result = download_images(
        image_urls,
        base_name,
        naming_config=naming_config,
        image_alt_texts=image_alt_texts
    )

    if not download_result['downloaded']:
        return {
            "success": False,
            "error": "Failed to download any images",
            "failed": download_result['failed']
        }

    # Get image paths
    image_paths = [img['local_path'] for img in download_result['downloaded']]

    # Handle different resize methods
    if resize_method == 'no_resize':
        # Copy images without any resizing or re-encoding (preserves original quality)
        print(f"   Using original quality (no resize)")
        resize_result = copy_images_without_resize(image_paths)

    elif resize_method == 'google_docs_original':
        # Use dimensions from Google Docs
        per_image_dimensions = []
        for download_info in download_result['downloaded']:
            matching_meta = next(
                (img for img in images_with_alt if img['url'] == download_info['url']),
                None
            )
            if matching_meta and matching_meta.get('width'):
                per_image_dimensions.append((matching_meta['width'], matching_meta['height']))
                print(f"   Image {download_info['url'][:60]}... will be resized to {matching_meta['width']}x{matching_meta['height']}")
            else:
                per_image_dimensions.append((image_config.get('target_width', 800), None))
                print(f"   Warning: No dimensions found for {download_info['url'][:60]}..., using default width")

        resize_result = resize_images(
            image_paths,
            target_width=image_config.get('target_width', 800),
            target_height=image_config.get('target_height'),
            quality=image_config.get('image_quality', 92),
            image_format=image_config.get('image_format', 'JPEG'),
            per_image_dimensions=per_image_dimensions
        )

    else:
        # Default: fixed_width resize
        resize_result = resize_images(
            image_paths,
            target_width=image_config.get('target_width', 800),
            target_height=image_config.get('target_height'),
            quality=image_config.get('image_quality', 92),
            image_format=image_config.get('image_format', 'JPEG'),
            per_image_dimensions=None
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
