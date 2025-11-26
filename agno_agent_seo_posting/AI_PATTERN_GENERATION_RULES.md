# AI Pattern Generation Rules

## Overview

The AI pattern generation system has been updated to follow strict rules for HTML transformation patterns. These rules ensure consistent, optimized output across all projects.

## Updated Files

1. **app/configure.py** (Lines 55-95)
   - CLI configuration wizard AI prompt

2. **app_streamlit.py** (Lines 1005-1056)
   - Streamlit "Scan HTML Template" - Source + Target mode

3. **app_streamlit.py** (Lines 1042-1083)
   - Streamlit "Scan HTML Template" - Target-only mode

## New Rules

### 1. Paragraph Tags - Minimal Patterns

**Rule:** Create ONE pattern for all `<p>` tags with the same text-align value.

**Before (Bad):**
```json
{
  "element_type": "p",
  "source_pattern": "<p dir=\"ltr\" style=\"text-align: justify\">(.*?)</p>",
  "target_pattern": "<p class=\"custom\">\\1</p>"
},
{
  "element_type": "p",
  "source_pattern": "<p class=\"foo\" style=\"text-align:justify\">(.*?)</p>",
  "target_pattern": "<p class=\"custom\">\\1</p>"
}
```

**After (Good):**
```json
{
  "element_type": "p_justify",
  "source_pattern": "<p[^>]*style=\"[^\"]*text-align:\\s*justify[^\"]*\"[^>]*>(.*?)</p>",
  "target_pattern": "<p class=\"custom\">\\1</p>"
}
```

**Benefits:**
- Covers ALL variations of justify paragraphs with ONE regex
- No need for multiple similar patterns
- More maintainable and efficient

### 2. Paragraph Tags with Images - Center Alignment

**Rule:** ALL `<p>` tags containing `<img>` must have `text-align: center` in the target pattern, **regardless of the source paragraph's text-align value**.

**Important:** Even if the source paragraph has `text-align: justify`, it MUST be changed to `text-align: center` in the target pattern when it contains an image.

**Before (Source HTML):**
```html
<p style="text-align:justify"><img alt="..." src="/pic/news/images/image.jpg" style="height:529px; width:790px" /></p>
```

**After (Target Pattern):**
```json
{
  "element_type": "p_with_image",
  "source_pattern": "<p[^>]*>.*?<img[^>]*>.*?</p>",
  "target_pattern": "<p style=\"text-align: center\">\\1</p>"
}
```

**Result (Transformed HTML):**
```html
<p style="text-align: center"><img alt="..." src="/pic/news/images/image.jpg" style="height:529px; width:790px" /></p>
```

### 3. Table Tags - Full Width

**Rule:** ALL `<table>` tags must include `style="width: 100%"` in the target pattern.

**Example:**
```json
{
  "element_type": "table",
  "source_pattern": "<table[^>]*>(.*?)</table>",
  "target_pattern": "<table style=\"width: 100%\" class=\"custom-table\">\\1</table>"
}
```

### 4. Image Tags - Generic src Patterns

**Rule:** DO NOT include specific src URL values in patterns. Use generic regex with capture groups to preserve the src value.

**Before (Bad):**
```json
{
  "element_type": "img",
  "source_pattern": "<img src=\"https://example.com/image.jpg\"[^>]*>",
  "target_pattern": "<img src=\"https://example.com/image.jpg\" class=\"custom\">"
}
```

**After (Good):**
```json
{
  "element_type": "img",
  "source_pattern": "<img[^>]*(src=\"[^\"]*\")[^>]*>",
  "target_pattern": "<img \\1 class=\"custom\">"
}
```

**Benefits:**
- Works with ANY image URL (not tied to specific URLs)
- Preserves the original src value using capture groups
- More flexible and maintainable

### 5. General Regex Patterns - Minimize Count

**Rule:** Use regex to create patterns that match multiple variations.

**Key Regex Components:**
- `[^>]*` - Match any attributes
- `\\s*` - Match optional whitespace
- `[^\"]*` - Match content within quotes
- `(?:...)` - Non-capturing group

**Example:**
```regex
# Matches all these variations:
# <p style="text-align:justify">
# <p style="text-align: justify">
# <p style="color: red; text-align: justify; font-size: 14px">
# <p dir="ltr" style="text-align: justify">

<p[^>]*style="[^"]*text-align:\\s*justify[^"]*"[^>]*>(.*?)</p>
```

## Prompt Structure

The updated prompts include a "CRITICAL RULES (MUST FOLLOW)" section:

```
CRITICAL RULES (MUST FOLLOW):
1. **<p> tags - Use MINIMAL patterns** with REGEX:
   - Create ONE pattern for ALL <p> tags with "text-align:justify" or "text-align: justify" (case insensitive)
   - Create ONE pattern for ALL <p> tags with "text-align:center" or "text-align: center" (case insensitive)
   - For <p> tags containing <img>, ALWAYS set text-align to center in target_pattern
   - Use regex like: <p[^>]*style="[^"]*text-align:\\s*justify[^"]*"[^>]*>(.*?)</p>

2. **<table> tags - ALWAYS set to full width**:
   - Add style="width: 100%" to ALL table tags in target_pattern

3. **<img> tags - Use generic src patterns**:
   - DO NOT include specific src URL values in patterns
   - Use generic regex: <img[^>]*(src="[^"]*")[^>]*> to match ANY image
   - Use capture groups to preserve the src: (src="[^"]*")
   - In target_pattern, use \\1 to preserve the captured src
   - Example: source_pattern: <img[^>]*(src="[^"]*")[^>]*>, target_pattern: <img \\1 class="custom">

4. **Use GENERAL regex patterns - minimize pattern count**:
   - Don't create separate patterns for each variation
   - Use [^>]* to match any attributes
   - Use \\s* to match optional whitespace
   - Example: ONE pattern <p[^>]*style="[^"]*text-align:\\s*justify[^"]*"[^>]*> covers ALL justify paragraphs
```

## Expected Behavior

When users use "Scan & Generate Patterns" in Streamlit or configure projects via CLI:

1. **Fewer patterns generated** - AI will create ONE pattern per text-align type instead of multiple
2. **Consistent table styling** - All tables will be full-width
3. **Centered images** - Paragraphs containing images will be center-aligned
4. **Better regex coverage** - Patterns will match more variations automatically

## Testing

To test the new pattern generation:

1. Go to Streamlit UI → "Scan & Generate Patterns"
2. Paste sample HTML with:
   - Multiple `<p>` tags with `text-align: justify`
   - Multiple `<p>` tags with `text-align: center`
   - `<p>` tags containing images
   - `<table>` tags
3. Click "Analyze HTML & Generate Patterns"
4. Verify:
   - ✓ Only ONE pattern for justify paragraphs
   - ✓ Only ONE pattern for center paragraphs
   - ✓ Paragraph-with-image pattern has center alignment
   - ✓ Table pattern includes width: 100%
   - ✓ Image patterns use generic src (not specific URLs)

## Model Version

All prompts use: **claude-sonnet-4-5-20250929**

## Date Updated

2025-11-21
