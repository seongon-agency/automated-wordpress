# Image Metadata Preservation & WordPress Caption Implementation

## Overview

This document describes the implementation of image metadata preservation and WordPress caption shortcode generation in the SEO Publishing System.

## What Was Implemented

### 1. Image Metadata Extraction (`wordpress_uploader.py`)

**Function:** `extract_image_metadata_from_html(html: str) -> Dict[str, Dict[str, str]]`

**Purpose:** Extract original image metadata (alt text, width, height) from Google Docs HTML BEFORE image processing.

**Inputs:**
- HTML content from Google Docs conversion

**Outputs:**
- Dictionary mapping filenames to metadata:
  ```python
  {
      "image1.jpg": {
          "alt": "Beautiful Sunset",
          "width": "1600",
          "height": "900",
          "src": "https://lh3.googleusercontent.com/..."
      }
  }
  ```

**Implementation Details:**
- Uses BeautifulSoup to parse HTML
- Finds all `<img>` tags
- Extracts filename from src URL using regex
- Preserves alt, width, height attributes
- Returns filename-keyed dictionary for easy lookup

### 2. WordPress Caption Generation (`wordpress_uploader.py`)

**Function:** `replace_images_with_wordpress_captions(html: str, image_metadata: List[Dict[str, Any]], target_width: int = 1200) -> str`

**Purpose:** Replace simple `<img>` tags with WordPress caption shortcode format.

**Inputs:**
- HTML content (after transformation)
- Enriched image metadata with WordPress upload data
- Target width from project configuration

**Outputs:**
- HTML with WordPress caption shortcodes:
  ```html
  [caption id="attachment_12345" align="aligncenter" width="1200"]
  <img class="wp-image-12345 size-full" src="https://..." alt="..." width="1200" height="800" />
  Alt Text
  [/caption]
  ```

**Caption Format Specification:**
- `id="attachment_{media_id}"` - WordPress attachment ID
- `align="aligncenter"` - Center alignment
- `width="{target_width}"` - From project config
- `class="wp-image-{media_id} size-full"` - WordPress image class
- `src="{wordpress_url}"` - WordPress media URL
- `alt="{original_alt}"` - Preserved from Google Docs
- `width` and `height` attributes on `<img>` tag
- Caption text = alt text (appears below image in WordPress)

### 3. Publishing Workflow Integration (`publishing_workflow.py`)

**Modified Steps:**

#### Step 3: Extract Metadata (Line 141-145)
```python
# Extract original image metadata (alt, width, height) from cleaned HTML
# This MUST happen BEFORE image processing, so we preserve Google Docs metadata
print("   📊 Extracting original image metadata from HTML...")
original_image_metadata = extract_image_metadata_from_html(cleaned_html)
print(f"   ✓ Extracted metadata for {len(original_image_metadata)} image(s)")
```

**Why This Step:** Google Docs HTML contains metadata that gets lost during image processing. We extract it early to preserve it.

#### Step 4: Enrich Upload Metadata (Line 190-206)
```python
# Merge WordPress upload data with original image metadata
print("   🔗 Enriching image metadata with WordPress data...")
for uploaded_img in upload_result['uploaded']:
    filename = Path(uploaded_img['image_path']).name
    original_meta = original_image_metadata.get(filename, {})

    # Create enriched metadata with both WordPress and original data
    enriched_metadata.append({
        'media_id': uploaded_img['media_id'],      # From WordPress
        'url': uploaded_img['url'],                # From WordPress
        'alt': original_meta.get('alt', ''),       # From Google Docs
        'width': image_configs.get('target_width', 800),  # From project config
        'height': original_meta.get('height', 800),       # From Google Docs
        'original_filename': filename
    })

print(f"   ✓ Enriched metadata for {len(enriched_metadata)} image(s)")
```

**Why This Step:** Combines WordPress upload results (media_id, url) with original metadata (alt, height) for complete information.

#### Step 5: Generate Captions (Line 235-243)
```python
# Replace images with WordPress caption shortcode format
if enriched_metadata:
    print("   🎨 Generating WordPress caption shortcodes for images...")
    final_html = replace_images_with_wordpress_captions(
        transformed_html,
        enriched_metadata,
        target_width=image_configs.get('target_width', 1200)
    )
    print(f"   ✓ Generated {len(enriched_metadata)} caption shortcode(s)")
```

**Why This Step:** Transforms simple `<img>` tags into WordPress-native caption shortcodes with all metadata intact.

## Data Flow

```
Google Docs HTML
    ↓
[STEP 1] Extract original metadata (alt, width, height)
    ↓
[STEP 2] Process images (download, resize)
    ↓
[STEP 3] Upload to WordPress (get media_id, url)
    ↓
[STEP 4] Enrich metadata (combine WordPress data + original metadata)
    ↓
[STEP 5] Apply HTML transformations (patterns)
    ↓
[STEP 6] Generate WordPress captions (replace <img> with [caption] shortcode)
    ↓
Final WordPress Post
```

## Example Transformation

### Input (Google Docs HTML)
```html
<h1>My Blog Post</h1>
<p>Check out this beautiful sunset!</p>
<img src="https://lh3.googleusercontent.com/photo1.jpg"
     alt="Beautiful Sunset"
     width="1600"
     height="900">
```

### Intermediate (After Metadata Extraction)
```python
original_metadata = {
    "photo1.jpg": {
        "alt": "Beautiful Sunset",
        "width": "1600",
        "height": "900",
        "src": "https://lh3.googleusercontent.com/photo1.jpg"
    }
}
```

### Intermediate (After WordPress Upload)
```python
enriched_metadata = [
    {
        "media_id": 12345,
        "url": "https://mysite.com/wp-content/uploads/2024/11/photo1.jpg",
        "alt": "Beautiful Sunset",      # Preserved from original
        "width": 1200,                  # From project config
        "height": 900,                  # Preserved from original
        "original_filename": "photo1.jpg"
    }
]
```

### Output (Final WordPress HTML)
```html
<p>Check out this beautiful sunset!</p>
[caption id="attachment_12345" align="aligncenter" width="1200"]
<img class="wp-image-12345 size-full"
     src="https://mysite.com/wp-content/uploads/2024/11/photo1.jpg"
     alt="Beautiful Sunset"
     width="1200"
     height="900" />
Beautiful Sunset
[/caption]
```

## Testing

### Test Script: `test_image_metadata.py`

Run the comprehensive test suite:
```bash
python3 test_image_metadata.py
```

**Tests Included:**
1. **Metadata Extraction Test** - Verifies extraction from HTML
2. **Caption Generation Test** - Verifies WordPress shortcode format
3. **Complete Workflow Test** - End-to-end metadata preservation

### Test Results
All tests pass successfully:
- ✅ Metadata extraction works correctly
- ✅ Caption shortcodes generated with proper format
- ✅ Attachment IDs correctly applied
- ✅ WP-image classes correctly applied
- ✅ Alt text preserved from original
- ✅ Dimensions correctly managed

## Configuration

### Project Settings (Image Config)

The target width is configured per-project in `image_configs`:

```python
{
    "target_width": 1200,    # Used in caption shortcode width
    "image_quality": 92,
    "image_format": "JPEG"
}
```

Default if not configured: `800px`

### Environment Variables

No additional environment variables required for this feature.

## WordPress Compatibility

### Caption Shortcode Format

WordPress natively supports the `[caption]` shortcode format:

```
[caption id="attachment_ID" align="aligncenter" width="WIDTH"]
<img class="wp-image-ID size-full" src="URL" alt="ALT" width="WIDTH" height="HEIGHT" />
CAPTION_TEXT
[/caption]
```

**References:**
- [WordPress Caption Shortcode Documentation](https://codex.wordpress.org/Gallery_Shortcode#Images_with_Captions)
- [WordPress Image Alignment](https://wordpress.org/support/article/image-alignment/)

### WordPress Output

When rendered by WordPress, the caption shortcode becomes:

```html
<div id="attachment_12345" class="wp-caption aligncenter" style="width: 1210px">
    <img class="wp-image-12345 size-full"
         src="https://..."
         alt="..."
         width="1200"
         height="800">
    <p class="wp-caption-text">Beautiful Sunset</p>
</div>
```

## Advantages of This Approach

1. **Metadata Preservation** - Alt text, dimensions preserved from Google Docs
2. **WordPress Native** - Uses WordPress shortcode format (no custom plugins needed)
3. **SEO Benefits** - Alt text improves image SEO
4. **Accessibility** - Alt text improves screen reader accessibility
5. **Responsive** - WordPress handles responsive image sizing
6. **Consistent Styling** - Uses WordPress theme's caption styles
7. **Caption Support** - Images automatically get captions (alt text)

## Backward Compatibility

### Fallback Behavior

If enriched metadata is not available (edge case), the workflow falls back to simple URL replacement:

```python
if enriched_metadata:
    # Use caption shortcodes
    final_html = replace_images_with_wordpress_captions(...)
else:
    # Fallback: simple URL replacement
    if url_mapping:
        final_html = replace_image_urls_in_html(...)
```

This ensures the workflow never breaks even if metadata extraction fails.

## Files Modified

1. **`src/tools/wordpress_uploader.py`** (Lines 288-389)
   - Added `extract_image_metadata_from_html()` function
   - Added `replace_images_with_wordpress_captions()` function

2. **`src/workflows/publishing_workflow.py`** (Lines 25-31, 141-145, 190-206, 235-243)
   - Imported new functions
   - Added metadata extraction step
   - Added metadata enrichment step
   - Added caption generation step

3. **`test_image_metadata.py`** (New file)
   - Comprehensive test suite for metadata preservation

## Future Enhancements

Potential improvements for future versions:

1. **Custom Caption Text** - Allow different caption text than alt text
2. **Image Alignment Options** - Support left, right, none alignment
3. **Image Size Classes** - Support thumbnail, medium, large, full
4. **Figure Tag Support** - Option to use `<figure>` tags instead of shortcodes
5. **Lazy Loading** - Add `loading="lazy"` attribute for performance
6. **Srcset Support** - Generate responsive image srcset attributes
7. **WebP Conversion** - Convert images to WebP format for better performance

## Support

For issues or questions about this implementation:
- Review test results: `python3 test_image_metadata.py`
- Check workflow logs during publishing
- Verify WordPress REST API is accessible
- Ensure images are publicly accessible from Google Docs

## Version History

- **v2.1.0** (2024-11-14) - Image metadata preservation and WordPress caption generation implemented
- Implements user requirement: Store metadata and generate WordPress caption shortcodes with attachment IDs, wp-image classes, and preserved alt text
