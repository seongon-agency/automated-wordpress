#!/usr/bin/env python3
"""
Debug script to test ACTUAL patterns from database against real HTML
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.database import list_projects
from src.utils.pattern_engine import apply_all_patterns, sort_patterns_by_specificity

# Test HTML - your exact example
test_html = '''<p style="text-align: justify;"><img class="wp-image-19382 size-full" src="https://dangbai.seongon.com/wp-content/uploads/2025/11/resized_sun-house_2-4.jpg" alt="" width="800" height="535" /></p>'''

print("=" * 80)
print("TESTING REAL PATTERNS FROM DATABASE")
print("=" * 80)
print()

print("INPUT HTML:")
print(test_html)
print()

# Get all projects
projects = list_projects(status='active')

if not projects:
    print("❌ No projects found in database")
    sys.exit(1)

print(f"Found {len(projects)} project(s)")
print()

for project in projects:
    project_id = project.get('project_id')
    project_name = project.get('project_name')
    html_configs = project.get('html_configs', {})
    patterns = html_configs.get('patterns', [])

    print("=" * 80)
    print(f"PROJECT: {project_name} ({project_id})")
    print("=" * 80)
    print()

    if not patterns:
        print("⚠️  No patterns configured for this project")
        print()
        continue

    print(f"Total patterns: {len(patterns)}")
    print()

    # Show pattern order BEFORE sorting
    print("PATTERNS (ORIGINAL ORDER):")
    for idx, pattern in enumerate(patterns, 1):
        element_type = pattern.get('element_type', 'unknown')
        source = pattern.get('source_pattern', '')
        target = pattern.get('target_pattern', '')
        print(f"  {idx}. {element_type}")
        print(f"     Source: {source[:80]}...")
        print(f"     Target: {target[:80]}...")
        print()

    # Sort patterns
    sorted_patterns = sort_patterns_by_specificity(patterns)

    print("PATTERNS (AFTER SORTING BY SPECIFICITY):")
    for idx, pattern in enumerate(sorted_patterns, 1):
        element_type = pattern.get('element_type', 'unknown')
        source = pattern.get('source_pattern', '')
        target = pattern.get('target_pattern', '')
        print(f"  {idx}. {element_type}")
        print(f"     Source: {source[:80]}...")
        print(f"     Target: {target[:80]}...")
        print()

    # Apply patterns step by step
    print("=" * 80)
    print("APPLYING PATTERNS STEP BY STEP")
    print("=" * 80)
    print()

    current_html = test_html

    for idx, pattern in enumerate(sorted_patterns, 1):
        element_type = pattern.get('element_type', 'unknown')
        source = pattern.get('source_pattern', '')
        target = pattern.get('target_pattern', '')

        print(f"STEP {idx}: Applying pattern '{element_type}'")
        print(f"  Source pattern: {source}")
        print(f"  Target pattern: {target}")
        print()

        # Check if pattern matches current HTML
        import re
        match = re.search(source, current_html, flags=re.IGNORECASE | re.DOTALL)

        if match:
            print(f"  ✅ MATCHES current HTML")

            # Apply pattern
            new_html = re.sub(source, target, current_html, flags=re.IGNORECASE | re.DOTALL)

            if new_html != current_html:
                print(f"  🔄 HTML CHANGED")
                print(f"  Before: {current_html}")
                print(f"  After:  {new_html}")
                current_html = new_html
            else:
                print(f"  ⚠️  Pattern matched but HTML didn't change")
        else:
            print(f"  ❌ Does NOT match current HTML")

        print()

    print("=" * 80)
    print("FINAL RESULT")
    print("=" * 80)
    print()
    print("Final HTML:")
    print(current_html)
    print()

    # Check if centered
    if 'text-align: center' in current_html or 'text-align:center' in current_html:
        print("✅ SUCCESS - Image paragraph is centered!")
    else:
        print("❌ FAILED - Image paragraph is NOT centered")
        print()
        print("DIAGNOSIS:")
        print("  The p_with_image pattern either:")
        print("  1. Doesn't match the HTML (check the regex)")
        print("  2. Is being overridden by another pattern that runs after it")
        print("  3. Has an incorrect target_pattern")

    print()
