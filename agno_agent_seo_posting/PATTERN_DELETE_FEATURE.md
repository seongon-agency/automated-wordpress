# Pattern Delete Feature

## Overview

Added the ability to delete individual HTML transformation patterns directly from the pattern viewer interface.

## Location

**Page:** AI Pattern Editor (Edit HTML Patterns - Natural Language)

**File:** `app_streamlit.py` (Lines 701-730)

## Features

### 1. Enhanced Pattern Display

Replaced simple JSON display with an interactive UI that shows:

- **Pattern Number** and **Element Type**
- **Source Pattern** (regex)
- **Target Pattern** (replacement)
- **Delete Button** (🗑️) for each pattern

### 2. One-Click Delete

Each pattern has a delete button that:
- Removes the pattern from the list
- Updates the database immediately
- Refreshes the UI to show updated patterns
- Shows success confirmation message

### 3. Visual Layout

```
┌─────────────────────────────────────────────────────┬────┐
│ Pattern 1: `p_justify`                              │ 🗑️ │
│ Source: <p[^>]*style="[^"]*text-align:\s*justify... │    │
│ Target: <p class="custom">\\1</p>                   │    │
├─────────────────────────────────────────────────────┴────┤
│ Pattern 2: `table`                                   │ 🗑️ │
│ Source: <table[^>]*>(.*?)</table>                   │    │
│ Target: <table style="width: 100%">\\1</table>     │    │
└──────────────────────────────────────────────────────────┘
```

## How to Use

1. Go to **Edit HTML Patterns (Natural Language)** in the sidebar
2. Select a project from the dropdown
3. Expand **"View & Manage Current Patterns"**
4. Click the 🗑️ button next to any pattern you want to remove
5. Confirm the deletion in the success message
6. The pattern list will refresh automatically

## Technical Implementation

### Pattern Display Logic

```python
for idx, pattern in enumerate(current_patterns):
    col1, col2 = st.columns([10, 1])

    with col1:
        st.markdown(f"**Pattern {idx + 1}: `{pattern.get('element_type', 'unknown')}`**")
        st.code(f"Source: {pattern.get('source_pattern', 'N/A')}\nTarget: {pattern.get('target_pattern', 'N/A')}", language="html")

    with col2:
        if st.button("🗑️", key=f"delete_pattern_{idx}"):
            # Delete logic
```

### Delete Logic

1. **Filter out the pattern:**
   ```python
   updated_patterns = [p for i, p in enumerate(current_patterns) if i != idx]
   ```

2. **Update database:**
   ```python
   updated_html_configs = {**html_configs, 'patterns': updated_patterns}
   update_project(selected_project_id, html_configs=updated_html_configs)
   ```

3. **Refresh UI:**
   ```python
   st.success(f"Pattern {idx + 1} ({pattern.get('element_type')}) deleted successfully!")
   st.rerun()
   ```

## Benefits

1. **Quick Pattern Management** - Remove incorrect patterns without re-scanning
2. **No Code Required** - Simple point-and-click interface
3. **Immediate Feedback** - See changes instantly
4. **Safe Operation** - Database updated atomically

## Use Cases

### Scenario 1: Wrong Pattern Generated
- AI generated a pattern that doesn't match your needs
- Click delete button to remove it
- Add a corrected pattern using natural language instructions

### Scenario 2: Conflicting Patterns
- Two patterns are interfering with each other
- Delete one to resolve the conflict
- Test the transformation with remaining pattern

### Scenario 3: Simplifying Configuration
- Too many specific patterns created
- Delete redundant ones
- Keep only the essential general patterns

## Example Workflow

```
1. User scans HTML template → 10 patterns generated
2. User tests transformation → Pattern #5 causes issues
3. User goes to AI Pattern Editor
4. User clicks 🗑️ next to Pattern #5
5. Pattern deleted → 9 patterns remain
6. User tests again → Works correctly
```

## Future Enhancements

Potential improvements:
- Bulk delete (select multiple patterns)
- Undo delete functionality
- Pattern reordering (drag & drop)
- Pattern editing inline
- Export/import patterns

## Testing

To test the delete functionality:

1. Create or select a project with patterns
2. Navigate to **Edit HTML Patterns (Natural Language)**
3. Click the 🗑️ button next to any pattern
4. Verify:
   - ✓ Success message appears
   - ✓ Pattern is removed from the list
   - ✓ Pattern count updates
   - ✓ Database persists the change (refresh page to confirm)

## Date Added

2025-11-21

## Related Files

- `app_streamlit.py` - Main UI implementation
- `src/database/project_manager.py` - Database update function
- `AI_PATTERN_GENERATION_RULES.md` - Pattern generation rules
