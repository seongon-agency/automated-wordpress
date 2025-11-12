"""
Test HTML cleaning with complex Google Docs-like structure
"""

from utils.html_extractor import extract_title_from_html, clean_html_for_wordpress

print("\n" + "="*80)
print("TESTING HTML CLEANING - ADVANCED (Google Docs-like structure)")
print("="*80)

# Test HTML with complex nested structure like Google Docs exports
test_html = """
<html>
<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type">
    <style type="text/css">@import url(https://themes.googleusercontent.com/fonts/css?kit=dpiI8CyVsrzWsJLBFKehGpLhv3qFjX7dUn1mYxfCXhI);</style>
</head>
<body class="c19 doc-content">
    <p class="c2"><span class="c0">This is gibberish before H1</span></p>
    <p class="c2"><span class="c0">More gibberish metadata</span></p>
    <div class="c10">
        <p class="c2"><span class="c0">Nested gibberish in a div</span></p>
    </div>
    <h1 class="c8" id="h.1234567890"><span class="c4">Main Article Title Here</span></h1>
    <p class="c2"><span class="c0">This is the first real paragraph that should appear.</span></p>
    <p class="c2"><span class="c0">This is the second paragraph.</span></p>
    <h2 class="c3" id="h.0987654321"><span class="c1">First Subheading</span></h2>
    <p class="c2"><span class="c0">Content under the subheading.</span></p>
    <img src="https://lh7-rt.googleusercontent.com/docsz/AD_4nXf..." />
    <h2 class="c3"><span class="c1">Second Subheading</span></h2>
    <p class="c2"><span class="c0">More content here.</span></p>
</body>
</html>
"""

print("\n" + "="*80)
print("STEP 1: Extract Title")
print("="*80)
title = extract_title_from_html(test_html)
print(f"Title extracted: '{title}'")

print("\n" + "="*80)
print("STEP 2: Clean HTML")
print("="*80)
cleaned = clean_html_for_wordpress(test_html)

print("\n" + "="*80)
print("CLEANED HTML OUTPUT:")
print("="*80)
print(cleaned[:500] + "..." if len(cleaned) > 500 else cleaned)

print("\n" + "="*80)
print("VERIFICATION")
print("="*80)

# Check that H1 is removed
if "Main Article Title Here" in cleaned and ("<h1" in cleaned.lower()):
    print("❌ FAILED: H1 tag still present in cleaned HTML")
elif "Main Article Title Here" in cleaned:
    print("❌ FAILED: H1 content still present in cleaned HTML")
else:
    print("✅ PASSED: H1 completely removed")

# Check that ALL content before H1 is removed
checks = [
    ("This is gibberish before H1", "Gibberish before H1"),
    ("More gibberish metadata", "Metadata gibberish"),
    ("Nested gibberish in a div", "Nested gibberish"),
]

all_gibberish_removed = True
for text, description in checks:
    if text in cleaned:
        print(f"❌ FAILED: {description} still present")
        all_gibberish_removed = False
    else:
        print(f"✅ PASSED: {description} removed")

# Check that content after H1 is preserved
if "This is the first real paragraph that should appear" in cleaned:
    print("✅ PASSED: First paragraph after H1 preserved")
else:
    print("❌ FAILED: First paragraph after H1 was removed")

if "This is the second paragraph" in cleaned:
    print("✅ PASSED: Second paragraph preserved")
else:
    print("❌ FAILED: Second paragraph was removed")

if "First Subheading" in cleaned:
    print("✅ PASSED: Subheadings preserved")
else:
    print("❌ FAILED: Subheadings were removed")

if "googleusercontent.com" in cleaned:
    print("✅ PASSED: Images preserved")
else:
    print("❌ FAILED: Images were removed")

print("\n" + "="*80)
if all_gibberish_removed:
    print("✅ ALL TESTS PASSED - HTML cleaning works correctly!")
else:
    print("⚠️  SOME TESTS FAILED - Review the output above")
print("="*80)
