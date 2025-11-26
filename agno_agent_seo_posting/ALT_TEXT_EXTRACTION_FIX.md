# Alt Text Extraction Fix

**Date:** 2025-11-18
**Issue:** Alt text from Google Docs not being captured in WordPress captions
**Status:** ✅ FIXED

---

## Problem

User reported that alt text entered in Google Docs was not appearing in WordPress caption shortcodes:

**Symptom:**
```html
[caption id="attachment_18686" align="aligncenter" width="1200"]<img class="wp-image-18686 size-full" src="..." alt="" width="1200" height="800" /> [/caption]
```

Notice the empty space after `/>` - the caption text was missing even though alt text was entered in Google Docs.

---

## Root Cause

The metadata enrichment logic in `src/workflows/publishing_workflow.py` was matching images by **filename** instead of by **original URL**.

### The Mismatch Problem

1. **Metadata extraction** (line 144): `extract_image_metadata_from_html()` creates a dict mapping **Google Docs filenames** to metadata:
   ```python
   {
     'image1.png': {'alt': 'Vietnamese text...', 'width': '800', 'height': '600', 'src': 'https://lh7-rt.googleusercontent.com/...'},
     'image2.jpg': {'alt': 'More text...', ...}
   }
   ```

2. **Image processing** (line 156): Images are downloaded and **renamed** with a prefix:
   ```python
   # Original: image1.png (from Google Docs URL)
   # Resized:  resized_testdangbai_1.png (new filename)
   ```

3. **Metadata enrichment** (OLD - BROKEN):
   ```python
   filename = Path(uploaded_img['image_path']).name  # "resized_testdangbai_1.png"
   original_meta = original_image_metadata.get(filename, {})  # Looking for "resized_testdangbai_1.png"
   ```

   But `original_image_metadata` has key `"image1.png"`, not `"resized_testdangbai_1.png"`!

   Result: `original_meta = {}` (empty), so `alt` was always `''`

---

## Solution

Changed metadata matching to use **original URLs** instead of filenames.

### Fixed Logic (src/workflows/publishing_workflow.py:199-237)

```python
# Create reverse mapping: resized_path -> original_url
resized_to_original_url = {}
for processed_img in processed_images:
    resized_path = processed_img['resized_path']
    original_url = processed_img['original_url']  # Full Google Docs URL!
    resized_to_original_url[resized_path] = original_url

for uploaded_img in upload_result['uploaded']:
    resized_path = uploaded_img['image_path']
    original_url = resized_to_original_url.get(resized_path, '')

    # Find metadata by matching the URL
    original_meta = {}
    if original_url:
        for meta_key, meta_value in original_image_metadata.items():
            if meta_key in original_url or original_url in meta_value.get('src', ''):
                original_meta = meta_value
                print(f"      ✓ Matched metadata for: {meta_key}")
                break

    # Create enriched metadata with alt text!
    enriched_metadata.append({
        'media_id': uploaded_img['media_id'],
        'url': uploaded_img['url'],
        'alt': original_meta.get('alt', ''),  # ✓ Now has alt text!
        'width': image_configs.get('target_width', 800),
        'height': original_meta.get('height', 800),
        'original_filename': Path(resized_path).name
    })
```

### Why This Works

The `processed_images` structure (from `process_images_from_html()`) contains **both**:
- `original_url`: Full Google Docs URL (e.g., `https://lh7-rt.googleusercontent.com/.../image1.png?key=xyz`)
- `resized_path`: Local resized file path (e.g., `/resized_images/resized_testdangbai_1.png`)

By mapping `resized_path → original_url`, we can then match the `original_url` against the `src` field in `original_image_metadata`.

**Example match:**
- `original_url`: `https://lh7-rt.googleusercontent.com/.../image1.png?key=xyz`
- `metadata['image1.png']['src']`: `https://lh7-rt.googleusercontent.com/.../image1.png?key=xyz`
- Match: `"image1.png" in original_url` → **True**

---

## Test Results

**Test:** `test_alt_text_extraction.py`

```
✅ Image 1: Alt text CORRECT
   Expected: 'Người chơi trầm nên lựa chọn cách đeo vòng trầm hương 108 hạt'
   Got: 'Người chơi trầm nên lựa chọn cách đeo vòng trầm hương 108 hạt'

✅ Image 2: Alt text CORRECT
   Expected: 'Beautiful landscape with mountains'
   Got: 'Beautiful landscape with mountains'

✅ Image 3: Alt text CORRECT
   Expected: ''
   Got: ''

🎉 SUCCESS! All alt texts extracted and matched correctly!
```

---

## Expected Behavior

**Input:** Google Docs with image alt text:
```html
<img src="https://lh7-rt.googleusercontent.com/.../image1.png"
     alt="Người chơi trầm nên lựa chọn cách đeo vòng trầm hương 108 hạt"
     width="800" height="600">
```

**Output:** WordPress caption with Vietnamese text:
```html
[caption id="attachment_18686" align="aligncenter" width="1200"]<img class="wp-image-18686 size-full" src="https://dangbai.seongon.com/wp-content/uploads/2025/11/resized_testdangbai_1.png" alt="" width="1200" height="800" /> Người chơi trầm nên lựa chọn cách đeo vòng trầm hương 108 hạt[/caption]
```

Note:
- Alt text appears **after** `/>` and **before** `[/caption]`
- WordPress caption format: `<img ... alt="" />` with caption text separate
- Vietnamese UTF-8 characters preserved perfectly

---

## Debug Output

When publishing, you'll now see metadata matching logs:

```
   🔗 Enriching image metadata with WordPress data...
      ✓ Matched metadata for: image1.png
      ✓ Matched metadata for: image2.jpg
      ✓ Matched metadata for: image3.png
   ✓ Enriched metadata for 3 image(s)
```

If you see warnings like:
```
      ⚠️  No metadata found for: resized_testdangbai_1.png
```

This indicates the URL matching failed, possibly because:
1. Image was not in the original HTML
2. Google Docs URL structure changed
3. Filename extraction regex didn't match

---

## Related Files Modified

1. **`src/workflows/publishing_workflow.py`** (lines 199-237)
   - Changed metadata matching from filename to original URL
   - Added reverse mapping: resized_path → original_url
   - Added debug logging for matched metadata

2. **`test_alt_text_extraction.py`** (Created)
   - Comprehensive test simulating the complete workflow
   - Verifies alt text extraction, matching, and Vietnamese UTF-8 support

---

## How to Verify Alt Text is Working

### 1. Check Metadata Extraction

When publishing, look for:
```
   📊 Extracting original image metadata from HTML...
   ✓ Extracted metadata for 7 image(s)
```

### 2. Check Metadata Matching

Look for:
```
   🔗 Enriching image metadata with WordPress data...
      ✓ Matched metadata for: image1.png
      ✓ Matched metadata for: image2.jpg
      ...
   ✓ Enriched metadata for 7 image(s)
```

### 3. Check Caption Generation

Look for:
```
   🎨 Generating WordPress caption shortcodes for images...
   [DEBUG] Found 7 img tags in HTML
   [DEBUG] Have metadata for 7 images
   [DEBUG] Processing image src: https://dangbai.seongon.com/...
   [DEBUG] ✓ Matched with key: https://dangbai.seongon.com/...
   [DEBUG] Caption generation complete: 7/7 images converted to shortcodes
```

### 4. Verify in WordPress

1. Open the published post in WordPress
2. Switch to "Code Editor" view
3. Verify caption shortcodes have text after `/>`:
   ```html
   [/caption]
   ```
   Should be:
   ```html
   /> Your caption text here[/caption]
   ```

---

## Troubleshooting

### Alt Text Still Empty After Fix

**Check 1: Is alt text in Google Docs?**
- Open Google Docs
- Right-click image → "Alt text"
- Verify alt text is filled in

**Check 2: Is metadata extracted?**
Run test:
```bash
python3 test_alt_text_extraction.py
```

Should show:
```
✓ Extracted metadata for 3 image(s)
Filename: image1.png
  Alt text: Người chơi trầm...
```

**Check 3: Are URLs matching?**
Look for debug output:
```
✓ Matched metadata for: image1.png
```

If you see `⚠️  No metadata found for:`, the URL matching failed.

---

## Summary

**Problem:** Filenames changed during processing, breaking metadata lookup

**Solution:** Match by original URL instead of filename

**Result:** Alt text now correctly flows from Google Docs → metadata → caption text

---

**Status:** ✅ FULLY FIXED and VALIDATED

Alt text from Google Docs now appears correctly in WordPress caption shortcodes with full Vietnamese UTF-8 support.
