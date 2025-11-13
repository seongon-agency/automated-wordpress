# Developer Handoff Documentation

## Project Overview

**WordPress SEO Publishing System** - Automated content publishing pipeline from Google Docs to WordPress with AI-powered HTML transformation.

**Version:** v2.0.0
**Last Updated:** 2025-11-13
**Status:** Production Ready (Local Development)

---

## Quick Context

### What This System Does

1. Takes Google Docs URL as input
2. Converts to clean HTML
3. Downloads and processes images
4. Applies client-specific HTML transformations
5. Uploads images to WordPress
6. Creates draft post in WordPress

### Key Differentiators

- **AI-Powered Configuration**: Claude Sonnet 4.5 analyzes sample HTML and generates transformation patterns
- **Natural Language Editing**: Modify patterns with plain English ("Make all h2 blue")
- **Multi-Project**: Manage multiple WordPress sites with different formatting rules
- **Two Interfaces**: Streamlit UI (primary) + CLI (legacy)

---

## Architecture Overview

### System Design

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACES                          │
├─────────────────────────────────────────────────────────────┤
│  Streamlit UI (app_streamlit.py)     CLI (app/main.py)    │
└─────────────┬───────────────────────────────┬───────────────┘
              │                               │
              ▼                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   WORKFLOWS LAYER                           │
│           (src/workflows/publishing_workflow.py)            │
└─────────────┬───────────────────────────────────────────────┘
              │
              ├── 1. Google Docs → HTML
              ├── 2. Extract title
              ├── 3. Process images
              ├── 4. Upload to WordPress
              ├── 5. Apply transformations
              └── 6. Create post
              │
┌─────────────┴───────────────────────────────────────────────┐
│                      TOOLS LAYER                            │
├─────────────────────────────────────────────────────────────┤
│  google_docs_converter.py    image_processor.py            │
│  html_transformer.py         wordpress_uploader.py         │
└─────────────┬───────────────────────────────────────────────┘
              │
┌─────────────┴───────────────────────────────────────────────┐
│                    UTILITIES LAYER                          │
├─────────────────────────────────────────────────────────────┤
│  html_extractor.py    pattern_engine.py                    │
│  pattern_modifier.py (AI-powered)                          │
└─────────────────────────────────────────────────────────────┘
              │
┌─────────────┴───────────────────────────────────────────────┐
│                   DATABASE LAYER                            │
├─────────────────────────────────────────────────────────────┤
│  SQLite (data/clients.db)                                  │
│  - projects table: WordPress sites & configs               │
│  - publishing_history: Audit log                           │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| UI Framework | Streamlit 1.28+ | Web interface |
| CLI Framework | Native Python | Command-line interface |
| AI Model | Claude Sonnet 4.5 | Pattern generation & modification |
| Database | SQLite 3 | Project storage |
| Image Processing | Pillow (PIL) | Resize, format conversion |
| HTML Parsing | BeautifulSoup4 | HTML parsing & manipulation |
| WordPress API | REST API | Post creation, media upload |
| Google API | Drive API v3 | Google Docs conversion (optional) |

---

## Code Structure Deep Dive

### Core Files Reference

#### 1. **app_streamlit.py** (Primary Interface)

**Purpose:** Main web interface using Streamlit

**Key Features:**
- Session state navigation
- 8 pages: Dashboard, Projects, Create/Edit, AI Editor, Scanner, Publish, History
- Direct workflow execution (no API calls)
- Form validation
- Progress indicators

**Code Structure:**
```python
# Page Configuration
st.set_page_config(...)

# Session State Init
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Home"

# Navigation (Sidebar)
# - Quick Publish button
# - Categorized sections (Overview, Projects, AI Config, Publishing)
# - Quick stats

# Page Routing
if page == "Home": ...
elif page == "Projects": ...
elif page == "Create Project": ...
# ... etc
```

**Important Notes:**
- No emojis (user preference)
- Direct function calls to `src.workflows.publishing_workflow`
- Uses `st.session_state` for page navigation
- Forms use `st.form()` for better UX

#### 2. **src/workflows/publishing_workflow.py** (Business Logic)

**Purpose:** Complete end-to-end publishing pipeline

**Function:** `execute_publishing_workflow(google_docs_url, project_id=None)`

**Returns:**
```python
{
    "success": bool,
    "post_url": str,
    "post_title": str,
    "images_processed": int,
    "execution_time": float,
    "error": str (if failed),
    "step_failed": str (if failed)
}
```

**Workflow Steps:**
```python
# Step 1: Convert Google Docs to HTML
html_content = convert_google_docs_to_html(url)

# Step 2: Extract title (H1) & clean HTML
title, cleaned_html = extract_title_and_clean_html(html_content)

# Step 3: Download & resize images
image_urls = extract_image_urls(cleaned_html)
local_images = download_and_process_images(image_urls)

# Step 4: Upload images to WordPress
wordpress_image_map = upload_images_to_wordpress(local_images, wp_creds)

# Step 5: Apply HTML transformations
transformed_html = apply_transformations(cleaned_html, patterns)

# Step 6: Create WordPress post
post = create_wordpress_post(title, transformed_html, wp_creds)
```

**Error Handling:**
- Try/except at each step
- Returns step name on failure
- Logs to `publishing_history` table

#### 3. **src/database/project_manager.py** (Data Layer)

**Purpose:** All database operations (CRUD)

**Key Functions:**

```python
# Initialize database (creates tables)
init_database() -> None

# Create new project
create_project(
    project_id: str,
    project_name: str,
    wordpress_url: str,
    wordpress_username: str,
    wordpress_app_password: str,
    html_configs: dict = None,
    image_configs: dict = None,
    notes: str = None
) -> dict

# Get project by ID
get_project(project_id: str) -> dict

# List all projects
list_projects(status: str = 'active') -> list[dict]

# Update project
update_project(project_id: str, **kwargs) -> dict

# Delete project
delete_project(project_id: str) -> bool

# Log publishing activity
log_publishing(
    google_docs_url: str,
    success: bool,
    project_id: str = None,
    ...
) -> None
```

**Database Schema:**

```sql
-- projects table
CREATE TABLE projects (
    project_id TEXT PRIMARY KEY,
    project_name TEXT NOT NULL,
    wordpress_url TEXT NOT NULL,
    wordpress_username TEXT NOT NULL,
    wordpress_app_password TEXT NOT NULL,
    html_configs TEXT,  -- JSON: {patterns: [...]}
    image_configs TEXT, -- JSON: {target_width, quality, format}
    status TEXT DEFAULT 'active',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_published_at TIMESTAMP
);

-- publishing_history table
CREATE TABLE publishing_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    google_docs_url TEXT NOT NULL,
    success INTEGER NOT NULL,
    project_id TEXT,
    wordpress_post_id INTEGER,
    wordpress_post_url TEXT,
    post_title TEXT,
    post_status TEXT,
    images_processed INTEGER DEFAULT 0,
    error_message TEXT,
    execution_time_seconds REAL,
    published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id)
);
```

#### 4. **src/tools/** (External Integrations)

**google_docs_converter.py:**
```python
def convert_google_docs_to_html(url: str) -> str:
    """
    Converts Google Docs to HTML

    Method 1 (default): Published URL (/pub endpoint)
    - No authentication needed
    - URL must be published to web
    - Fast and simple

    Method 2 (fallback): Google Drive API
    - Requires OAuth credentials
    - Works with any accessible doc
    - First run opens browser for auth
    """
```

**image_processor.py:**
```python
def download_and_resize_images(
    image_urls: list,
    target_width: int = 800,
    image_quality: int = 92,
    image_format: str = 'JPEG'
) -> dict:
    """
    Downloads images and resizes them

    Returns: {original_url: local_file_path}

    Process:
    1. Download to raw_images/
    2. Resize maintaining aspect ratio
    3. Save to resized_images/
    4. Return mapping
    """
```

**html_transformer.py:**
```python
def apply_html_transformations(
    html_content: str,
    patterns: list[dict]
) -> str:
    """
    Applies regex patterns to HTML

    Pattern format:
    {
        "element_type": "p",
        "source_pattern": "<p[^>]*>(.*?)</p>",
        "target_pattern": "<p class=\"custom\">\\1</p>"
    }

    Uses pattern_engine.py for regex application
    """
```

**wordpress_uploader.py:**
```python
def upload_image_to_wordpress(
    image_path: str,
    wordpress_url: str,
    username: str,
    app_password: str
) -> int:
    """
    Uploads image to WordPress media library

    Returns: media_id (int)

    Uses: WordPress REST API v2
    Endpoint: /wp-json/wp/v2/media
    Auth: Basic Auth with Application Password
    """

def create_wordpress_post(
    title: str,
    content: str,
    wordpress_url: str,
    username: str,
    app_password: str,
    status: str = 'draft'
) -> dict:
    """
    Creates WordPress post

    Returns: {id, link, ...}

    Endpoint: /wp-json/wp/v2/posts
    Default status: 'draft' (for safety)
    """
```

#### 5. **src/utils/** (Helpers)

**pattern_modifier.py** (AI-Powered):
```python
def modify_patterns_with_ai(
    current_patterns: list[dict],
    instruction: str,
    api_key: str
) -> dict:
    """
    Uses Claude AI to modify patterns based on natural language

    Args:
        current_patterns: Existing transformation patterns
        instruction: Plain English instruction
        api_key: Anthropic API key

    Returns:
        {
            "success": bool,
            "patterns": list[dict],  # Modified patterns
            "changes_made": str      # Description of changes
        }

    Example instruction:
        "Make all h2 headings blue"

    AI modifies:
        <h2>\\1</h2>
        →
        <h2 style="color: blue;">\\1</h2>
    """
```

**pattern_engine.py:**
```python
def apply_patterns(html: str, patterns: list[dict]) -> str:
    """
    Applies regex patterns sequentially

    For each pattern:
        1. Compile source_pattern regex
        2. Replace with target_pattern
        3. Use re.sub() with DOTALL flag

    Returns: Transformed HTML
    """
```

---

## Development Guidelines

### Adding New Features

#### Example: Add New Page to Streamlit

1. **Update Navigation** (app_streamlit.py):
```python
# Add button in sidebar
if st.sidebar.button("My New Page", use_container_width=True):
    st.session_state.current_page = "My New Page"

# Add page handler
elif page == "My New Page":
    st.title("My New Page")
    st.markdown("Content here")
    # ... your page logic
```

2. **Test:**
```bash
streamlit run app_streamlit.py
```

#### Example: Add New Workflow Step

1. **Create Tool** (src/tools/my_new_tool.py):
```python
def my_new_function(input_data):
    """
    Description of what this does

    Args:
        input_data: Description

    Returns:
        result: Description

    Raises:
        ValueError: When...
    """
    # Implementation
    return result
```

2. **Integrate into Workflow** (src/workflows/publishing_workflow.py):
```python
# Add after Step 5
result['step'] = "6/7"
result['message'] = "Running my new step..."
new_data = my_new_function(input_data)
```

3. **Test:**
```python
# Create test in tests/test_my_new_tool.py
def test_my_new_function():
    result = my_new_function(test_input)
    assert result == expected_output
```

### Code Style Guidelines

**Python Style:**
- Follow PEP 8
- Use type hints where possible
- Document all functions with docstrings
- Keep functions under 50 lines

**Naming Conventions:**
```python
# Functions: snake_case
def convert_html_to_text():
    pass

# Classes: PascalCase
class WordPressUploader:
    pass

# Constants: UPPER_SNAKE_CASE
DEFAULT_IMAGE_WIDTH = 800

# Private: _leading_underscore
def _internal_helper():
    pass
```

**Error Handling:**
```python
# Always catch specific exceptions
try:
    result = risky_operation()
except SpecificError as e:
    logger.error(f"Failed: {e}")
    return {"success": False, "error": str(e)}

# Return consistent formats
return {
    "success": bool,
    "data": any,
    "error": str or None
}
```

### Testing Strategy

**Run Tests:**
```bash
cd tests
python -m pytest -v
```

**Test Structure:**
```python
# tests/test_my_feature.py

def test_happy_path():
    """Test normal operation"""
    result = my_function(valid_input)
    assert result['success'] == True

def test_error_handling():
    """Test error cases"""
    result = my_function(invalid_input)
    assert result['success'] == False
    assert 'error' in result

def test_edge_cases():
    """Test boundary conditions"""
    result = my_function(edge_case_input)
    # Assertions
```

---

## Common Development Tasks

### Task 1: Add New HTML Pattern

**Scenario:** Client wants to add custom image class

**Steps:**
1. Open Streamlit → Edit Project
2. Select project
3. Go to AI Pattern Editor
4. Enter: "Add class 'featured-image' to all images"
5. Review AI-generated change
6. Save to project

**Programmatic:**
```python
from src.database import get_project, update_project

# Get current patterns
project = get_project('client_id')
patterns = project['html_configs']['patterns']

# Add new pattern
patterns.append({
    "element_type": "img",
    "source_pattern": r"<img([^>]*)>",
    "target_pattern": r'<img class="featured-image"\1>'
})

# Update project
update_project('client_id', html_configs={'patterns': patterns})
```

### Task 2: Debug Publishing Failure

**Check Logs:**
```python
import sqlite3

conn = sqlite3.connect('data/clients.db')
cursor = conn.cursor()

# Get recent failures
cursor.execute("""
    SELECT published_at, post_title, error_message, execution_time_seconds
    FROM publishing_history
    WHERE success = 0
    ORDER BY published_at DESC
    LIMIT 10
""")

for row in cursor.fetchall():
    print(f"{row[0]}: {row[1]} - {row[2]} ({row[3]}s)")
```

**Common Issues:**
- WordPress auth: Check Application Password
- Google Docs: Ensure URL is published
- Images: Check image URLs accessible
- Patterns: Test regex in isolation

### Task 3: Backup Database

```bash
# Create backup
cp data/clients.db data/clients_backup_$(date +%Y%m%d).db

# Restore backup
cp data/clients_backup_20251113.db data/clients.db
```

### Task 4: Add New Environment Variable

1. **Add to `.env`:**
```env
NEW_FEATURE_ENABLED=true
```

2. **Add to `.env.example`:**
```env
# Optional: New Feature Flag
NEW_FEATURE_ENABLED=false
```

3. **Use in code:**
```python
import os
from dotenv import load_dotenv

load_dotenv()

if os.getenv('NEW_FEATURE_ENABLED') == 'true':
    # New feature code
    pass
```

---

## Deployment Considerations

### Current Status

**Current:** Local development only
**Primary Interface:** Streamlit at localhost:8501

### If You Need to Deploy

**Option 1: Streamlit Cloud** (Recommended)
```bash
# Deploy directly to Streamlit Cloud
# 1. Push to GitHub
# 2. Go to share.streamlit.io
# 3. Connect repository
# 4. Set secrets (ANTHROPIC_API_KEY, etc.)
```

**Option 2: Docker**
```dockerfile
# Dockerfile (example)
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "app_streamlit.py"]
```

**Option 3: Traditional Server**
```bash
# Use systemd service
# Or screen/tmux for persistent session
screen -S wordpress-publisher
streamlit run app_streamlit.py --server.port 8501
# Ctrl+A, D to detach
```

---

## Known Issues & Limitations

### Current Limitations

1. **No Bulk Processing**
   - One document at a time
   - Workaround: CLI loop script

2. **No Scheduling**
   - Manual trigger only
   - Future: Add cron/scheduled jobs

3. **Limited History View**
   - History page is placeholder
   - Workaround: Query SQLite directly

4. **No User Authentication**
   - Anyone with access can use
   - Future: Add login system

### Known Issues

1. **Large Images**
   - Very large images (>10MB) may timeout
   - Workaround: Reduce quality in project settings

2. **Complex HTML**
   - Some Google Docs formatting lost
   - Workaround: Use simpler formatting

3. **Google API Rate Limits**
   - If using Drive API heavily
   - Workaround: Use published URLs instead

---

## Maintenance Tasks

### Weekly

- [ ] Check `data/clients.db` size
- [ ] Clear `raw_images/` and `resized_images/`
- [ ] Review failed publishes in history

### Monthly

- [ ] Backup database
- [ ] Update dependencies: `pip install -U -r requirements.txt`
- [ ] Review and archive old projects

### As Needed

- [ ] Rotate API keys
- [ ] Update WordPress passwords
- [ ] Test publishing workflow end-to-end

---

## Quick Reference

### Restart Application

```bash
# Kill all Streamlit processes
pkill -f streamlit

# Start fresh
streamlit run app_streamlit.py
```

### Database Queries

```sql
-- List all projects
SELECT project_id, project_name, wordpress_url FROM projects;

-- Count successful publishes
SELECT COUNT(*) FROM publishing_history WHERE success = 1;

-- Recent activity
SELECT * FROM publishing_history ORDER BY published_at DESC LIMIT 10;
```

### Environment

```bash
# Check Python version
python --version  # Need 3.11+

# Check dependencies
pip list

# Check environment variables
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('ANTHROPIC_API_KEY')[:10] + '...')"
```

---

## Support & Resources

### Documentation Files

- **README.md** - Overview and quick start
- **SETUP.md** - Installation guide
- **HANDOFF.md** - This file (architecture & development)
- **START_HERE.md** - Quick reference

### External Resources

- **Streamlit Docs:** https://docs.streamlit.io/
- **WordPress REST API:** https://developer.wordpress.org/rest-api/
- **Anthropic Claude:** https://docs.anthropic.com/
- **Google Drive API:** https://developers.google.com/drive

### Code Comments

All complex functions have inline comments. Look for:
- `# Step X:` comments in workflows
- Docstrings on all public functions
- `# IMPORTANT:` for critical notes

---

## Handoff Checklist

Before you start development:

- [ ] Read this entire document
- [ ] Run through SETUP.md
- [ ] Start application successfully
- [ ] Create test project
- [ ] Publish test Google Doc
- [ ] Review code structure (src/ directory)
- [ ] Run test suite
- [ ] Check environment variables configured

---

## Contact & Questions

**Previous Developer:** [Your Name]
**Handoff Date:** 2025-11-13

For questions about:
- **Architecture:** Review this document + code comments
- **Bugs:** Check publishing_history table
- **Features:** Check TODO comments in code
- **Deployment:** See "Deployment Considerations" section

---

**Good luck! The codebase is clean and ready for your contributions.**

All temporary files removed, documentation complete, and tests passing.
