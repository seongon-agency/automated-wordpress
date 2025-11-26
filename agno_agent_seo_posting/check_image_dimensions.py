#!/usr/bin/env python3
"""
Helper script to check dimensions of resized images.
Useful for verifying Google Docs original size resizing is working correctly.
"""

import os
import glob
from PIL import Image
from pathlib import Path

def check_image_dimensions():
    """Check dimensions of all resized images, sorted by modification time."""

    resized_dir = Path("resized_images")

    if not resized_dir.exists():
        print("❌ resized_images directory not found")
        return

    # Get all image files
    image_files = []
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.webp']:
        image_files.extend(glob.glob(str(resized_dir / ext)))

    if not image_files:
        print("❌ No images found in resized_images/")
        return

    # Sort by modification time (newest first)
    image_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)

    print("=" * 80)
    print("RESIZED IMAGE DIMENSIONS (newest first)")
    print("=" * 80)
    print()

    for img_path in image_files[:10]:  # Show last 10 images
        try:
            img = Image.open(img_path)
            width, height = img.size
            filename = Path(img_path).name
            mtime = os.path.getmtime(img_path)

            # Check if it's the default 800px width
            is_default = (width == 800)
            marker = "⚠️  DEFAULT WIDTH" if is_default else "✓"

            print(f"{marker} {filename}")
            print(f"   Dimensions: {width}x{height}")
            print()

        except Exception as e:
            print(f"❌ Error reading {img_path}: {e}")
            print()

    print("=" * 80)
    print()
    print("Expected behavior with 'Google Docs Original Size':")
    print("  - Images should have DIFFERENT widths (not all 800px)")
    print("  - Each image should match its Google Docs dimensions")
    print()
    print("If all images show 800px width, the dimensions are not being extracted.")
    print("=" * 80)

if __name__ == "__main__":
    check_image_dimensions()
