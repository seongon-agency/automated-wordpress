# Alt Text Extraction Fix - Summary

**Date:** 2025-11-18
**Status:** ✅ FULLY FIXED AND TESTED
**Issue:** Alt text from Google Docs was not appearing in WordPress captions

---

## The Problem

WordPress caption shortcodes were being generated with the correct format, but the caption text (from Google Docs alt text) was empty:

```html
<!-- BEFORE (BROKEN) -->
[caption id="attachment_18686" align="aligncenter" width="1200"]<img class="wp-image-18686 size-full" src="..." alt="" width="1200" height="800" /> [/caption]
                                                                                                                                                    ^
                                                                                                                                      Caption text missing here!
```

---

## Root Cause

The `extract_image_metadata_from_html()` function in `src/tools/wordpress_uploader.py` was using a regex pattern to extract filenames with file extensions:

```python
# BROKEN CODE:
filename_match = re.search(r'([^/]+\.(jpg|jpeg|png|gif|webp))', src, re.IGNORECASE)
```

**Problem:** Google Docs image URLs don't have file extensions!

Example Google Docs URL:
```
https://lh7-rt.googleusercontent.com/docsz/AD_4nXfo_Znc_Pb3PIAPzCmtdXoDScOZ3T8h7J_brsxl_eKiaETqOvnPVgS659u0nQZum2Q_CzWmA5sY33oj3x_wiHsLkp4tZ9tBB8FNySHkKoh9sNenjbGzFJH3HfatUx50ze992U6WqQ?key=I9hDmGzHGRO9mEYhm4t8qw
```

There's no `.jpg`, `.png`, or other extension, so the regex never matched and returned 0 images.

---

## The Fix

### 1. Updated `src/tools/wordpress_uploader.py` (lines 293-320)

Changed the function to use the **full URL** as the dictionary key instead of trying to extract a filename:

```python
def extract_image_metadata_from_html(html: str) -> Dict[str, Dict[str, str]]:
    """
    Extract image metadata (src, alt, dimensions) from HTML.

    Returns:
        Dict mapping image URLs (full src) to their metadata (alt, width, height)
    """
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, 'html.parser')
    metadata = {}

    for img in soup.find_all('img'):
        src = img.get('src', '')
        if src:
            # Use the full URL as the key (works with both regular URLs and Google Docs URLs)
            # This matches better with the original_url in processed_images
            metadata[src] = {
                'alt': img.get('alt', ''),
                'width': img.get('width', ''),
                'height': img.get('height', ''),
                'src': src
            }

    return metadata
```

**Key change:** `metadata[src] = {...}` instead of `metadata[filename] = {...}`

### 2. Updated `src/workflows/publishing_workflow.py` (lines 210-231)

Updated the metadata matching logic to use full URL for lookup and added debug logging:

```python
for uploaded_img in upload_result['uploaded']:
    resized_path = uploaded_img['image_path']
    original_url = resized_to_original_url.get(resized_path, '')

    # Match metadata by original URL (metadata dict now uses full URLs as keys)
    original_meta = original_image_metadata.get(original_url, {})

    if original_meta:
        print(f"      ✓ Matched metadata for: {original_url[:80]}...")
        print(f"         Alt text: '{original_meta.get('alt', '')[:80]}...'")
    else:
        print(f"      ⚠️  No metadata found for: {original_url[:80] if original_url else Path(resized_path).name}")

    # Create enriched metadata with both WordPress and original data
    enriched_metadata.append({
        'media_id': uploaded_img['media_id'],
        'url': uploaded_img['url'],
        'alt': original_meta.get('alt', ''),  # ✅ Now correctly captures alt text!
        'width': image_configs.get('target_width', 800),
        'height': original_meta.get('height', 800),
        'original_filename': Path(resized_path).name
    })
```

---

## Test Results

### End-to-End Test: ✅ PASSED

```
🎉 TEST PASSED! Alt text extraction working correctly!

✅ Found expected Vietnamese alt text:
   'Người chơi trầm nên lựa chọn cách đeo vòng trầm hương 108 hạt ngay ngắn trước ngực
    để giữ dáng tự nhiên, tôn nét thanh lịch và lan tỏa ý nghĩa tâm linh'

   This alt text will appear in WordPress caption shortcode as:
   [caption id="attachment_ID" ...]<img .../> Người chơi trầm nên lựa chọn cách đeo vòng
   trầm hương 108 hạt ngay ngắn trước ngực để giữ dáng tự nhiên, tôn nét thanh lịch
   và lan tỏa ý nghĩa tâm linh [/caption]
```

### Your Document Status

Your Google Doc: `https://docs.google.com/document/d/1xLXoQH9xozi0F_bb6ikSAu6W6KQqc1JJwlFV15gLSpY/edit?tab=t.0`

**Results:**
- Total images: 7
- Images **WITH** alt text: 1 ✅
- Images **WITHOUT** alt text: 6 ⚠️

**This is why you saw empty captions!** Most of your images don't have alt text defined in Google Docs.

---

## How to Add Alt Text in Google Docs

To get captions on all your images, you need to add alt text in Google Docs:

### Step-by-Step Instructions:

1. **Open your Google Doc**
   - Go to: https://docs.google.com/document/d/1xLXoQH9xozi0F_bb6ikSAu6W6KQqc1JJwlFV15gLSpY/edit

2. **For each image without alt text:**
   - Right-click on the image
   - Select **"Alt text"** from the menu
   - Enter a description in the **"Alt text"** field
   - Click **"OK"**

3. **Save (automatic)**
   - Google Docs saves automatically
   - No need to re-publish if you're using edit URLs with OAuth

4. **Verify alt text was added:**
   - Run the diagnostic script:
     ```bash
     python3 check_google_docs_alt_text.py "https://docs.google.com/document/d/1xLXoQH9xozi0F_bb6ikSAu6W6KQqc1JJwlFV15gLSpY/edit?tab=t.0"
     ```

5. **Re-run your publishing workflow**
   - The alt text will now appear in WordPress captions

---

## Expected Output

### BEFORE (with empty alt text):
```html
[caption id="attachment_18686" align="aligncenter" width="1200"]<img class="wp-image-18686 size-full" src="https://dangbai.seongon.com/wp-content/uploads/2025/11/resized_testdangbai_1.png" alt="" width="1200" height="800" /> [/caption]
```

### AFTER (with Vietnamese alt text - FINAL FIX):
```html
[caption id="attachment_18686" align="aligncenter" width="1200"]<img class="wp-image-18686 size-full" src="https://dangbai.seongon.com/wp-content/uploads/2025/11/resized_testdangbai_1.png" alt="Người chơi trầm nên lựa chọn cách đeo vòng trầm hương 108 hạt ngay ngắn trước ngực để giữ dáng tự nhiên, tôn nét thanh lịch và lan tỏa ý nghĩa tâm linh" width="1200" height="800" /> Người chơi trầm nên lựa chọn cách đeo vòng trầm hương 108 hạt ngay ngắn trước ngực để giữ dáng tự nhiên, tôn nét thanh lịch và lan tỏa ý nghĩa tâm linh[/caption]
```

Notice:
- The Vietnamese text appears in the `alt=""` attribute inside the `<img>` tag (for SEO and screen readers)
- The same text also appears **after** `/>` and **before** `[/caption]` (for visual caption display)
- This provides BOTH accessibility and visual caption functionality

---

## Verification Workflow

When you publish your document after adding alt text, you'll see this in the logs:

```
[3/6] 🖼️  Processing images...
   📊 Extracting original image metadata from HTML...
   ✓ Extracted metadata for 7 image(s)

[4/6] ⬆️  Uploading images to WordPress...
   🔗 Enriching image metadata with WordPress data...
      ✓ Matched metadata for: https://lh7-rt.googleusercontent.com/docsz/AD_4nXfo_Znc...
         Alt text: 'Người chơi trầm nên lựa chọn cách đeo vòng trầm hương 108 hạt...'
      ✓ Matched metadata for: https://lh7-rt.googleusercontent.com/docsz/AD_4nXebFif...
         Alt text: 'Your new alt text here...'
   ✓ Enriched metadata for 7 image(s)

[5/6] 🔄 Applying HTML transformations...
   🎨 Generating WordPress caption shortcodes for images...
   [DEBUG] Found 7 img tags in HTML
   [DEBUG] Have metadata for 7 images
   [DEBUG] Processing image src: https://dangbai.seongon.com/...
   [DEBUG] ✓ Matched with key: https://dangbai.seongon.com/...
   [DEBUG] Caption generation complete: 7/7 images converted to shortcodes
```

---

## Troubleshooting

### "No metadata found for: [filename]"

**Cause:** The URL matching failed (shouldn't happen with the fix)

**Solution:** Check the debug output and verify that:
1. Images exist in Google Docs HTML
2. The `original_url` is being extracted correctly
3. The metadata dict has the same URL as a key

### "Images WITHOUT alt text: X"

**Cause:** You haven't added alt text to those images in Google Docs

**Solution:** Follow the "How to Add Alt Text in Google Docs" section above

### Vietnamese characters showing as gibberish

**Cause:** UTF-8 encoding issue

**Solution:** The system fully supports UTF-8. This shouldn't happen. If it does, verify:
- Your WordPress site has UTF-8 charset in database
- The API requests are using `charset=utf-8`

---

## Files Modified

1. **`src/tools/wordpress_uploader.py`** (lines 293-320)
   - Changed from filename-based keys to URL-based keys
   - Now works with Google Docs URLs without file extensions

2. **`src/workflows/publishing_workflow.py`** (lines 210-231)
   - Updated metadata matching to use URL lookup
   - Added debug logging for matched alt text

---

## Summary

**What was broken:**
- Regex looked for filenames with extensions
- Google Docs URLs don't have extensions
- Result: 0 images extracted, all alt text lost

**What's fixed:**
- Use full URL as key instead of filename
- Works with both regular URLs and Google Docs URLs
- Vietnamese UTF-8 fully supported

**What you need to do:**
- Add alt text to images 2-7 in your Google Doc
- Re-publish your document
- Alt text will now appear in WordPress captions

---

**Status:** ✅ FULLY FIXED AND VALIDATED

The system now correctly extracts alt text from Google Docs and generates WordPress caption shortcodes with full Vietnamese UTF-8 support.
