# Caption Generation Fix Summary

**Date:** 2025-11-14
**Issue:** Image caption shortcodes not being generated & image widths not being modified

---

## Problem

When publishing content, two issues occurred:
1. WordPress `[caption]` shortcodes were NOT being generated for images
2. Image widths were NOT being modified to the project's target width (1200px)

---

## Root Cause

The caption generation workflow had a **critical ordering bug**:

### OLD (Broken) Workflow:
```
1. Apply HTML patterns (HTML has Google Docs URLs)
2. Try to generate captions
   ❌ FAILS - Can't match images!
   - HTML has: https://lh3.googleusercontent.com/d/abc123
   - Metadata has: https://dangbai.seongon.com/.../resized_testdangbai_1.jpg
   - NO MATCH = NO CAPTIONS
3. Replace URLs (too late!)
```

### The Matching Problem:

The `replace_images_with_wordpress_captions()` function tries to match images by:
1. WordPress URL in metadata
2. Filename in metadata

But at the time it runs, the HTML still has Google Docs URLs, so:
- `https://lh3.googleusercontent.com/...` (in HTML)
- Does NOT match `https://dangbai.seongon.com/...` (in metadata)
- Result: **No metadata found = No captions generated**

---

## Solution

Reorder the workflow to **replace URLs BEFORE generating captions**:

### NEW (Fixed) Workflow:
```
1. Apply HTML patterns
2. Replace URLs with WordPress URLs FIRST ✓
   - HTML now has: https://dangbai.seongon.com/.../resized_testdangbai_1.jpg
3. Generate captions
   ✓ SUCCESS - URLs match!
   - Caption generator can now match images by WordPress URL
   - Generates proper [caption] shortcodes
   - Sets correct width (1200px)
```

---

## Changes Made

### File Modified:
`src/workflows/publishing_workflow.py` (lines 235-257)

### Before:
```python
# Replace images with WordPress caption shortcode format (if enabled)
enable_auto_captions = image_configs.get('enable_auto_captions', True)

if enriched_metadata and enable_auto_captions:
    # Generate captions (FAILS - URLs don't match yet)
    final_html = replace_images_with_wordpress_captions(...)
else:
    if url_mapping:
        # Replace URLs (too late!)
        final_html = replace_image_urls_in_html(...)
```

### After:
```python
# CRITICAL: Replace image URLs FIRST (before caption generation)
if url_mapping:
    print("   🔗 Replacing image URLs with WordPress media URLs...")
    transformed_html = replace_image_urls_in_html(transformed_html, url_mapping)
    print(f"   ✓ Replaced {len(url_mapping)} image URL(s)")

# Now generate captions (if enabled) on the HTML with updated URLs
enable_auto_captions = image_configs.get('enable_auto_captions', True)

if enriched_metadata and enable_auto_captions:
    print("   🎨 Generating WordPress caption shortcodes for images...")
    final_html = replace_images_with_wordpress_captions(
        transformed_html,
        enriched_metadata,
        target_width=image_configs.get('target_width', 1200)
    )
    print(f"   ✓ Generated {len(enriched_metadata)} caption shortcode(s)")
```

---

## Test Results

Ran `test_caption_fix.py` with simulated workflow:

```
✅ SUCCESS: All images have caption shortcodes!
   - Image 1: [caption id="attachment_12345"]
   - Image 2: [caption id="attachment_12346"]

✅ SUCCESS: Image widths set to 1200px (from project settings)
```

---

## Expected Output

After this fix, published posts will have:

### Before (Broken):
```html
<p><img src="https://lh3.googleusercontent.com/d/abc123"
     alt="Beautiful Sunset" width="1600" height="900"></p>
```
- Wrong URL (Google Docs URL)
- Wrong width (original 1600px, not project's 1200px)
- No caption shortcode

### After (Fixed):
```html
<p>[caption id="attachment_12345" align="aligncenter" width="1200"]
<img class="wp-image-12345 size-full"
     src="https://dangbai.seongon.com/wp-content/uploads/2024/11/resized_testdangbai_1.jpg"
     alt="Beautiful Sunset" width="1200" height="675" />
Beautiful Sunset[/caption]</p>
```
- ✅ WordPress URL
- ✅ Correct width (1200px from project settings)
- ✅ WordPress caption shortcode with attachment ID
- ✅ Image caption text (from alt attribute)

---

## Debug Scripts Created

1. **debug_caption_matching.py** - Demonstrates the URL matching issue
2. **test_caption_fix.py** - Verifies the fix works correctly

Both scripts can be run to understand the issue and verify the solution.

---

## Impact

This fix resolves both reported issues:

1. ✅ **Caption shortcodes now generated** - Images wrapped with `[caption]` shortcodes
2. ✅ **Image widths now modified** - Set to project's `target_width` (1200px)

The fix also ensures:
- WordPress media IDs are properly assigned to images
- Image alt text is used as caption text
- WordPress alignment (aligncenter) is applied
- Image classes (wp-image-{id} size-full) are added

---

## Next Steps

1. Test with actual Google Docs content
2. Verify captions render correctly in WordPress
3. Check that image widths are consistently applied
4. Ensure the caption toggle setting still works (enable/disable)

---

**Status:** ✅ Fixed and tested

The workflow now correctly:
1. Replaces URLs first
2. Generates captions on HTML with WordPress URLs
3. Sets image widths from project configuration
