"""
Integration test for workflow components.
Tests the pipeline from HTML input through transformation without external API calls.
"""

import os
import sys
from database import init_database, create_project, get_project
from utils.html_extractor import extract_title_from_html, clean_html_for_wordpress
from tools.html_transformer import transform_html


def test_workflow_integration():
    """Test workflow integration - database -> HTML transformation."""
    print("="*80)
    print("TESTING WORKFLOW INTEGRATION")
    print("="*80)

    # Setup test database
    os.environ['CLIENT_DB_PATH'] = 'test_workflow.db'

    # Clean up old test database
    if os.path.exists('test_workflow.db'):
        os.remove('test_workflow.db')
        print("[OK] Cleaned up old test database\n")

    print("1. Initializing test database...")
    init_database()

    # Create a test project with HTML patterns
    print("\n2. Creating test project with HTML patterns...")
    html_configs = {
        "patterns": [
            {
                "element_type": "p",
                "source_pattern": r"<p[^>]*>(.*?)</p>",
                "target_pattern": r'<p class="article-paragraph" style="text-align: justify;">\1</p>'
            },
            {
                "element_type": "strong",
                "source_pattern": r"<b>(.*?)</b>",
                "target_pattern": r"<strong>\1</strong>"
            },
            {
                "element_type": "h2",
                "source_pattern": r"<h2[^>]*>(.*?)</h2>",
                "target_pattern": r'<h2 class="section-heading">\1</h2>'
            },
            {
                "element_type": "ul",
                "source_pattern": r"<ul[^>]*>(.*?)</ul>",
                "target_pattern": r'<ul class="bullet-list">\1</ul>'
            }
        ]
    }

    image_configs = {
        "target_width": 800,
        "image_quality": 92,
        "image_format": "JPEG",
        "css_classes": "wp-image aligncenter"
    }

    project = create_project(
        project_id="test_client",
        project_name="Test Client",
        wordpress_url="https://testclient.wordpress.com",
        wordpress_username="admin",
        wordpress_app_password="test pass word 1234",
        html_configs=html_configs,
        image_configs=image_configs,
        notes="Integration test project"
    )

    print(f"[OK] Created project: {project['project_id']}")
    print(f"   Patterns: {len(project['html_configs']['patterns'])}")

    # Simulate raw Google Docs HTML
    print("\n3. Simulating Google Docs HTML input...")
    raw_html = """
    <html>
    <body>
    <div class="google-docs-header">Some header content</div>
    <h1>My Amazing Blog Post</h1>
    <p>This is the first paragraph with <b>bold text</b> in it.</p>
    <h2>Section 1: Introduction</h2>
    <p>This section introduces the topic with some important information.</p>
    <p>Here's another paragraph in this section.</p>
    <h2>Section 2: Main Content</h2>
    <p>This is the main content section.</p>
    <ul>
        <li>First bullet point</li>
        <li>Second bullet point</li>
        <li>Third bullet point</li>
    </ul>
    <p>Final paragraph with conclusion.</p>
    </body>
    </html>
    """

    print(f"[OK] Raw HTML: {len(raw_html)} characters")

    # Step 1: Extract title
    print("\n4. Extracting title from H1...")
    title = extract_title_from_html(raw_html)
    print(f"[OK] Title: {title}")

    # Step 2: Clean HTML (remove H1 and everything before it)
    print("\n5. Cleaning HTML (universal cleaning)...")
    cleaned_html = clean_html_for_wordpress(raw_html)
    print(f"[OK] Cleaned HTML: {len(cleaned_html)} characters (was {len(raw_html)})")
    print(f"   Removed: {len(raw_html) - len(cleaned_html)} characters")

    # Verify H1 is removed
    if "<h1>" not in cleaned_html:
        print("[OK] H1 successfully removed")
    else:
        print("[ERROR] H1 still present!")

    # Step 3: Retrieve project configuration
    print("\n6. Retrieving project configuration from database...")
    retrieved_project = get_project("test_client")
    print(f"[OK] Retrieved: {retrieved_project['project_name']}")
    print(f"   Patterns: {len(retrieved_project['html_configs']['patterns'])}")

    # Step 4: Apply HTML transformations
    print("\n7. Applying project-specific HTML transformations...")
    transform_result = transform_html(
        cleaned_html,
        retrieved_project['html_configs']
    )

    if not transform_result['success']:
        print(f"[ERROR] Transformation failed: {transform_result.get('error')}")
        return False

    transformed_html = transform_result['transformed_html']
    patterns_applied = transform_result['patterns_applied']

    print(f"[OK] Transformation successful")
    print(f"   Patterns applied: {patterns_applied}")

    # Step 5: Verify transformations
    print("\n8. Verifying transformations...")

    verifications = [
        ('class="article-paragraph"', "Paragraph classes"),
        ('style="text-align: justify;"', "Paragraph styles"),
        ("<strong>bold text</strong>", "Bold to strong conversion"),
        ('class="section-heading"', "H2 classes"),
        ('class="bullet-list"', "UL classes"),
    ]

    all_passed = True
    for check_string, check_name in verifications:
        if check_string in transformed_html:
            print(f"   [OK] {check_name}")
        else:
            print(f"   [ERROR] {check_name} - not found")
            all_passed = False

    # Display sample of transformed HTML
    print("\n9. Sample of transformed HTML:")
    print("-" * 80)
    # Show first 500 characters
    print(transformed_html[:500])
    if len(transformed_html) > 500:
        print(f"... ({len(transformed_html) - 500} more characters)")
    print("-" * 80)

    # Summary
    print("\n" + "="*80)
    if all_passed:
        print("[OK] WORKFLOW INTEGRATION TEST PASSED!")
        print("="*80)
        print("\n[SUMMARY]")
        print(f"  Post Title: {title}")
        print(f"  Original HTML: {len(raw_html)} chars")
        print(f"  After Cleaning: {len(cleaned_html)} chars")
        print(f"  After Transform: {len(transformed_html)} chars")
        print(f"  Patterns Applied: {patterns_applied}")
        print(f"  All Verifications: PASSED")
        return True
    else:
        print("[ERROR] WORKFLOW INTEGRATION TEST FAILED!")
        print("="*80)
        print("\nSome transformations did not apply correctly.")
        print("Review the transformed HTML above.")
        return False

    print("="*80)


if __name__ == "__main__":
    try:
        success = test_workflow_integration()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[ERROR] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
