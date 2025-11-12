"""
Test the universal HTML cleaning logic
"""

from utils.html_extractor import extract_title_from_html, clean_html_for_wordpress

print("\n" + "="*80)
print("TESTING HTML CLEANING LOGIC")
print("="*80)

# Test HTML with content before H1
test_html = """
<html>
<head><title>Test</title></head>
<body>
    <p>This is some content before the H1</p>
    <div>More content before H1</div>
    <h1>This is the main title</h1>
    <p>This is content after the H1 that should remain</p>
    <h2>Subheading</h2>
    <p>More content that should remain</p>
    <img src="https://example.com/image.jpg" />
</body>
</html>
"""

print("\n" + "="*80)
print("ORIGINAL HTML")
print("="*80)
print(test_html)

print("\n" + "="*80)
print("STEP 1: Extract Title")
print("="*80)
title = extract_title_from_html(test_html)
print(f"Title extracted: {title}")

print("\n" + "="*80)
print("STEP 2: Clean HTML (Remove H1 and everything before it)")
print("="*80)
cleaned = clean_html_for_wordpress(test_html)
print(cleaned)

print("\n" + "="*80)
print("VERIFICATION")
print("="*80)

# Check that H1 is removed
if "<h1>" in cleaned or "<H1>" in cleaned.upper():
    print("❌ FAILED: H1 still present in cleaned HTML")
else:
    print("✅ PASSED: H1 removed")

# Check that content before H1 is removed
if "This is some content before the H1" in cleaned:
    print("❌ FAILED: Content before H1 still present")
else:
    print("✅ PASSED: Content before H1 removed")

if "More content before H1" in cleaned:
    print("❌ FAILED: Content before H1 still present")
else:
    print("✅ PASSED: Content before H1 removed")

# Check that content after H1 remains
if "This is content after the H1 that should remain" in cleaned:
    print("✅ PASSED: Content after H1 preserved")
else:
    print("❌ FAILED: Content after H1 was removed")

if "<h2>Subheading</h2>" in cleaned:
    print("✅ PASSED: H2 preserved")
else:
    print("❌ FAILED: H2 was removed")

if "image.jpg" in cleaned:
    print("✅ PASSED: Images preserved")
else:
    print("❌ FAILED: Images were removed")

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80)
