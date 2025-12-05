# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **WordPress SEO Publishing System** that automates publishing from Google Docs to WordPress with AI-powered HTML transformation. The main application is in `agno_agent_seo_posting/`.

**Current Version:** v2.0.0 (Streamlit-based multi-project system)

## Running the Application

### Primary Interface: Streamlit UI

```bash
cd agno_agent_seo_posting
streamlit run app_streamlit.py
```

Opens at: http://localhost:8501

### CLI Interface (Alternative)

```bash
cd agno_agent_seo_posting
python app/main.py
```

## Testing

### Run All Tests

```bash
cd agno_agent_seo_posting/tests
python -m pytest -v
```

### Run Individual Test Files

```bash
# Database operations
python tests/test_database.py

# Pattern engine (regex transformations)
python tests/test_pattern_engine.py

# Complete workflow integration
python tests/test_workflow_integration.py

# AI pattern modification
python tests/test_pattern_modification.py

# Google Docs conversion
python tests/test_google_docs.py

# Image processing
python tests/test_image_download.py

# WordPress upload
python tests/test_wordpress_upload.py
```

## Environment Setup

### Required Environment Variables

Create `.env` file in `agno_agent_seo_posting/`:

```env
# Required
ANTHROPIC_API_KEY=sk-ant-your-api-key-here

# Optional: Default WordPress credentials (can configure per-project)
WP_BASE_URL=https://your-wordpress-site.com
WP_USERNAME=your_wordpress_username
WP_APP_PASS=xxxx xxxx xxxx xxxx

# Optional: Database path
CLIENT_DB_PATH=./data/clients.db

# Optional: Image processing
DEFAULT_IMAGE_WIDTH=800
IMAGE_QUALITY=92
IMAGE_FORMAT=JPEG
```

### Install Dependencies

```bash
cd agno_agent_seo_posting
pip install -r requirements.txt
```

## Core Architecture

### System Design

The system uses a **workflow-based architecture** (not Agno framework agents):

```
User Interfaces (Streamlit UI / CLI)
         ↓
Publishing Workflow (6-step pipeline)
         ↓
Tools Layer (Google Docs, Image Processing, HTML Transform, WordPress)
         ↓
Utilities Layer (Pattern Engine, HTML Extractor, AI Pattern Modifier)
         ↓
Database Layer (SQLite)
```

### Publishing Workflow (6 Steps)

Located in `src/workflows/publishing_workflow.py`:

1. **Convert Google Docs to HTML** - Uses published URL or Google Drive API
2. **Extract title and clean HTML** - Extracts H1 as title, removes metadata
3. **Process images** - Download and resize images from Google Docs
4. **Upload images to WordPress** - Upload to WordPress media library via REST API
5. **Apply HTML transformations** - Apply project-specific regex patterns
6. **Create WordPress post** - Publish as draft via REST API

### Project Structure

```
agno_agent_seo_posting/
├── app_streamlit.py              # Main Streamlit UI (primary interface)
├── app/
│   ├── main.py                   # CLI entry point
│   ├── configure.py              # Project configuration wizard
│   └── edit.py                   # Project editor
├── src/
│   ├── workflows/
│   │   └── publishing_workflow.py    # Complete 6-step publishing pipeline
│   ├── tools/
│   │   ├── google_docs_converter.py  # Google Docs → HTML conversion
│   │   ├── image_processor.py        # Download & resize images
│   │   ├── html_transformer.py       # Apply regex patterns to HTML
│   │   └── wordpress_uploader.py     # WordPress REST API client
│   ├── utils/
│   │   ├── html_extractor.py         # Title extraction, HTML cleaning
│   │   ├── pattern_engine.py         # Regex pattern application
│   │   └── pattern_modifier.py       # AI-powered pattern modification
│   ├── database/
│   │   ├── schema.sql                # Database schema
│   │   └── project_manager.py        # CRUD operations
│   └── config/
│       └── settings.py               # Environment settings loader
├── tests/                        # Test suite (pytest)
├── data/
│   └── clients.db                # SQLite database (projects & history)
├── credentials/                  # Google OAuth (git-ignored)
├── raw_images/                   # Temp downloaded images (git-ignored)
└── resized_images/               # Temp processed images (git-ignored)
```

## Key Implementation Details

### Multi-Project System

The system manages multiple WordPress sites (projects) with different formatting rules:

**Database Schema:**
- `projects` table: WordPress credentials, HTML transformation patterns, image settings
- `publishing_history` table: Audit log of all publishes (success/failure)

**Project Configuration:**
```python
{
    "project_id": "client_slug",
    "project_name": "Client Name",
    "wordpress_url": "https://site.com",
    "wordpress_username": "admin",
    "wordpress_app_password": "xxxx xxxx xxxx xxxx",
    "html_configs": {
        "patterns": [
            {
                "element_type": "p",
                "source_pattern": "<p[^>]*>(.*?)</p>",
                "target_pattern": "<p class=\"custom\">\\1</p>"
            }
        ]
    },
    "image_configs": {
        "target_width": 800,
        "image_quality": 92,
        "image_format": "JPEG"
    }
}
```

### AI-Powered HTML Pattern System

**Two Configuration Methods:**

1. **Scan HTML Template** - AI analyzes sample HTML and generates regex patterns automatically
2. **Natural Language Editing** - Modify patterns with plain English (e.g., "Make all h2 headings blue")

Implementation: `src/utils/pattern_modifier.py` uses Claude Sonnet 4.5 API

### Google Docs Conversion

**Two Methods:**

1. **Published URL** (default, no auth required):
   - User publishes Google Doc to web (File → Share → Publish to web)
   - URL must end with `/pub`
   - System fetches HTML directly

2. **Google Drive API** (fallback, requires OAuth):
   - Uses `credentials/client_secret.json` for OAuth
   - First run opens browser for authentication
   - Token saved to `credentials/token.json`

### WordPress Integration

- Uses **WordPress REST API v2**
- Requires **Application Password** (not regular password)
- Images uploaded to media library BEFORE post creation
- Posts created as **drafts** by default (safety)
- Endpoints:
  - `/wp-json/wp/v2/media` - Image upload
  - `/wp-json/wp/v2/posts` - Post creation

## Database Operations

All database operations are in `src/database/project_manager.py`:

**Key Functions:**
- `init_database()` - Creates tables if not exist
- `create_project()` - Add new WordPress site
- `get_project(project_id)` - Fetch project configuration
- `update_project(project_id, **kwargs)` - Modify project settings
- `list_projects(status='active')` - Get all projects
- `delete_project(project_id)` - Remove project
- `log_publishing()` - Record publish attempt to history

**Database file:** `data/clients.db` (SQLite)

## Development Patterns

### Adding a New Page to Streamlit UI

1. Add navigation button in sidebar (around line 50-80 in `app_streamlit.py`)
2. Add page routing in main section (around line 100+)
3. Implement page function following existing pattern

### Modifying the Publishing Workflow

Edit `src/workflows/publishing_workflow.py`:
- Workflow is sequential (steps 1-6)
- Each step has try/except error handling
- Returns consistent dict: `{"success": bool, "error": str, ...}`
- Logs to `publishing_history` table

### Adding New HTML Transformation Pattern

Patterns use regex with capture groups:
```python
{
    "element_type": "h2",
    "source_pattern": "<h2[^>]*>(.*?)</h2>",
    "target_pattern": "<h2 class=\"section-title\">\\1</h2>"
}
```

Applied by `src/utils/pattern_engine.py` using `re.sub()` with `re.DOTALL` flag.

### Error Handling Convention

All tools and workflows return consistent format:
```python
{
    "success": bool,
    "data": any,           # On success
    "error": str,          # On failure
    "step_failed": str     # For workflows, which step failed
}
```

## Important Notes

### Security

These files contain sensitive data and are **git-ignored**:
- `.env` - API keys and default credentials
- `credentials/client_secret.json` - Google OAuth credentials
- `credentials/token.json` - Google OAuth token
- `data/clients.db` - Database with WordPress passwords

### Image Processing

- Images downloaded to `raw_images/`
- Resized maintaining aspect ratio to `resized_images/`
- Original URLs in HTML replaced with WordPress media URLs
- Both directories are git-ignored and should be cleared periodically

### WordPress Application Passwords

**Critical:** Must use WordPress **Application Passwords**, not regular passwords:
1. WordPress Admin → Users → Profile
2. Scroll to "Application Passwords"
3. Create new → Copy entire password (format: `xxxx xxxx xxxx xxxx`)

### Testing Google Docs URLs

Valid Google Docs URL formats:
- Published: `https://docs.google.com/document/d/e/2PACX-xxx/pub` ✓
- Edit mode: `https://docs.google.com/document/d/xxx/edit` ✗ (won't work without OAuth)

## Common Development Tasks

### Add New Project (Programmatic)

```python
from src.database import create_project

create_project(
    project_id="client_slug",
    project_name="Client Name",
    wordpress_url="https://site.com",
    wordpress_username="admin",
    wordpress_app_password="xxxx xxxx xxxx xxxx",
    html_configs={"patterns": []},
    image_configs={"target_width": 800, "image_quality": 92, "image_format": "JPEG"}
)
```

### Query Publishing History

```bash
sqlite3 data/clients.db

SELECT published_at, post_title, success, error_message
FROM publishing_history
ORDER BY published_at DESC
LIMIT 10;
```

### Clear Temporary Images

```bash
rm -rf raw_images/* resized_images/*
```

### Backup Database

```bash
cp data/clients.db data/clients_backup_$(date +%Y%m%d).db
```

## Troubleshooting

### "ANTHROPIC_API_KEY not found"
- Verify `.env` file exists in `agno_agent_seo_posting/`
- Check API key is set correctly
- Restart application

### WordPress Authentication Failed
- Use Application Password, not regular password
- Remove any spaces from password in `.env` (should be: `xxxx xxxx xxxx xxxx`)
- Test REST API: `https://your-site.com/wp-json/wp/v2/posts`

### Images Not Processing
- Check image URLs are publicly accessible
- Verify sufficient disk space for temp files
- Ensure `raw_images/` and `resized_images/` directories exist

### Port Already in Use (Streamlit)
```bash
# Kill existing Streamlit processes
pkill -f streamlit

# Or use different port
streamlit run app_streamlit.py --server.port 8502
```

## Version Information

**Current Version:** v2.0.0 (2025-11-13)

**Major Changes from Previous Versions:**
- **v2.0.0**: Complete rewrite with Streamlit UI, removed Agno framework agent system
- **v1.2.0**: Added natural language pattern editing, restructured codebase
- **v1.0.0**: Initial MVP with multi-project management

**Technology Stack:**
- Python 3.11+
- Streamlit (web UI)
- SQLite (database)
- Claude Sonnet 4.5 (AI features)
- WordPress REST API
- Google Drive API (optional)
- BeautifulSoup (HTML parsing)
- Pillow (image processing)

## Documentation Files

- **SESSION_STATE.md** - **READ THIS FIRST** - Current project state, recent changes, and context for continuing work
- **README.md** - Complete overview and features
- **SETUP.md** - Detailed installation guide
- **HANDOFF.md** - Developer documentation and architecture
- **START_HERE.md** - Quick reference for common tasks

## Important Notes for New Sessions

1. **Always read `agno_agent_seo_posting/SESSION_STATE.md` first** - Contains recent work, current state, and pending items
2. **Database is Supabase** (cloud PostgreSQL), not SQLite
3. **UI is in Vietnamese** - All text translated as of 2025-12-02
4. **Credentials in `.streamlit/secrets.toml`** - Never commit this file
