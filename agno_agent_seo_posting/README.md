# WordPress SEO Publishing System

**Automated Google Docs to WordPress Publishing Platform**

Multi-client SEO content publishing system with AI-powered HTML transformation, natural language pattern editing, and multi-project management.

---

## Overview

This system automates the complete workflow for publishing SEO content from Google Docs to WordPress with client-specific HTML transformations:

1. **Convert** Google Docs to clean HTML (via Google Drive API)
2. **Process** images (download, resize, upload to WordPress)
3. **Transform** HTML to match client-specific formats (AI-powered)
4. **Publish** to WordPress as draft posts

### Key Features

- **AI-Powered Configuration** - AI analyzes sample HTML and generates transformation patterns automatically
- **Natural Language Editing** - Modify HTML patterns using plain English ("Make all h2 headings blue")
- **Multi-Project Management** - Configure once per client, publish many times
- **Automated Image Processing** - Download, resize, and upload images automatically
- **Web Interface & CLI** - Choose between Streamlit UI (recommended) or command-line interface
- **Publishing History** - Track all publishes with success/failure logs
- **Secure Credentials** - Isolated credentials directory (git-ignored)

---

## Quick Start

### Prerequisites

- **Python 3.11+**
- **WordPress site** with REST API enabled
- **WordPress Application Password** (not regular password)
- **Google Cloud Project** with Drive API enabled (optional, for Google Docs API access)
- **Anthropic API Key** (for AI features)

### Installation

```bash
# Navigate to project directory
cd agno_agent_seo_posting

# Install dependencies
pip install -r requirements.txt
```

### Configuration

1. **Create `.env` file** (copy from `.env.example`):

```env
# Required: Anthropic API for AI features
ANTHROPIC_API_KEY=sk-ant-...

# Optional: Default WordPress credentials (for "No Project" mode)
WP_BASE_URL=https://your-wordpress-site.com
WP_USERNAME=your_username
WP_APP_PASS=xxxx xxxx xxxx xxxx

# Optional: Database path
CLIENT_DB_PATH=./data/clients.db

# Optional: Image processing settings
DEFAULT_IMAGE_WIDTH=800
IMAGE_QUALITY=92
IMAGE_FORMAT=JPEG
```

2. **Setup Google OAuth** (Optional, for Google Docs API):
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create/select project → Enable **Google Drive API**
   - Create OAuth credentials (Desktop app)
   - Download JSON → Rename to `client_secret.json`
   - Place in `credentials/` directory

3. **Get WordPress Application Password**:
   - WordPress Admin → Users → Profile
   - Scroll to "Application Passwords"
   - Create new password → Copy it

### Run the Application

**Option 1: Streamlit UI (Recommended)**

```bash
streamlit run app_streamlit.py
```

Opens at: http://localhost:8501

**Option 2: CLI**

```bash
python app/main.py
```

---

## Project Structure

```
agno_agent_seo_posting/
├── app/                          # CLI application
│   ├── main.py                   # Main entry point
│   ├── configure.py              # Project configuration wizard
│   └── edit.py                   # Project editor
│
├── src/                          # Core source code
│   ├── database/                 # Database operations
│   │   ├── __init__.py
│   │   ├── schema.sql           # Database schema
│   │   └── project_manager.py   # CRUD operations
│   │
│   ├── tools/                    # Core tools
│   │   ├── __init__.py
│   │   ├── google_docs_converter.py   # Google Docs → HTML
│   │   ├── image_processor.py         # Image download & resize
│   │   ├── html_transformer.py        # Apply HTML transformations
│   │   └── wordpress_uploader.py      # WordPress API client
│   │
│   ├── utils/                    # Utility functions
│   │   ├── __init__.py
│   │   ├── html_extractor.py          # Extract title, clean HTML
│   │   ├── pattern_engine.py          # Apply regex patterns
│   │   └── pattern_modifier.py        # AI pattern modification
│   │
│   ├── workflows/                # End-to-end workflows
│   │   ├── __init__.py
│   │   └── publishing_workflow.py     # Complete publishing pipeline
│   │
│   └── config/                   # Configuration
│       ├── __init__.py
│       └── settings.py           # Environment settings
│
├── tests/                        # Test suite
│   ├── test_database.py
│   ├── test_workflow_integration.py
│   ├── test_pattern_engine.py
│   └── test_pattern_modification.py
│
├── data/                         # Runtime data
│   └── clients.db                # SQLite database
│
├── credentials/                  # Sensitive files (git-ignored)
│   ├── client_secret.json        # Google OAuth credentials
│   └── token.json                # Google OAuth token
│
├── raw_images/                   # Temporary raw images (git-ignored)
├── resized_images/               # Temporary processed images (git-ignored)
│
├── app_streamlit.py              # Streamlit UI (NEW - Primary Interface)
├── requirements.txt              # Python dependencies
├── .env                          # Environment variables (git-ignored)
├── .env.example                  # Example environment file
├── .gitignore                    # Git ignore rules
├── README.md                     # This file
├── SETUP.md                      # Detailed setup guide
└── HANDOFF.md                    # Developer handoff documentation
```

---

## Usage Guide

### Streamlit UI (Recommended)

Run: `streamlit run app_streamlit.py`

**Features:**
- **Dashboard** - View system status and quick stats
- **Projects** - View all configured WordPress sites
- **Create Project** - Add new WordPress site with wizard
- **Edit Project** - Modify existing project settings
- **AI Pattern Editor** - Use natural language to modify HTML patterns
- **Scan HTML Template** - Upload sample HTML and auto-generate patterns
- **Publish Content** - Publish Google Docs to WordPress
- **Publishing History** - View past publications

**Publishing Workflow (Streamlit):**
1. Navigate to "Publish Content"
2. Select your project
3. Paste Google Docs URL (must be published to web)
4. Click "Publish to WordPress"
5. Wait for completion (1-2 minutes)
6. Get WordPress post URL

### CLI Application

Run: `python app/main.py`

**Main Menu:**
```
[MAIN MENU]
----------------------------------------
1. Publish Google Docs to WordPress
2. Configure New Project
3. Edit Existing Project
4. List All Projects
5. Exit
----------------------------------------
```

**Publishing Workflow (CLI):**
1. Select option 1
2. Choose project (or "No project" for defaults)
3. Enter Google Docs URL
4. Watch automated steps execute
5. Get WordPress post URL

---

## Architecture

### Database Schema

**`projects` table**:
```sql
- project_id (PRIMARY KEY)
- project_name
- wordpress_url
- wordpress_username
- wordpress_app_password
- html_configs (JSON)      -- Transformation patterns
- image_configs (JSON)     -- Image settings
- status
- created_at, updated_at, last_published_at
- notes
```

**`publishing_history` table**:
```sql
- id (PRIMARY KEY)
- google_docs_url
- success (boolean)
- project_id
- wordpress_post_id
- wordpress_post_url
- post_title
- post_status
- images_processed
- error_message
- execution_time_seconds
- published_at
```

### Publishing Workflow

```
Google Docs URL (published to web)
    ↓
[1] Convert to HTML
    ↓
[2] Extract title & clean HTML
    ↓
[3] Process images (Download & resize)
    ↓
[4] Upload images to WordPress
    ↓
[5] Apply HTML transformations (Project-specific patterns)
    ↓
[6] Create WordPress post (Draft)
    ↓
Log to history & return post URL
```

### Key Components

**Tools** (`src/tools/`):
- `google_docs_converter.py` - Google Drive API integration
- `image_processor.py` - Image download and resizing (Pillow)
- `html_transformer.py` - Pattern-based HTML transformation
- `wordpress_uploader.py` - WordPress REST API client

**Utilities** (`src/utils/`):
- `html_extractor.py` - Title extraction and HTML cleaning
- `pattern_engine.py` - Regex pattern application
- `pattern_modifier.py` - AI-powered pattern modification

**Workflows** (`src/workflows/`):
- `publishing_workflow.py` - Complete 6-step publishing pipeline

**Database** (`src/database/`):
- `project_manager.py` - CRUD operations for projects
- `schema.sql` - Database schema definition

---

## AI Features

### 1. HTML Pattern Generation

Paste sample HTML → AI extracts patterns automatically

**Example Input:**
```html
<p class="article-body" style="text-align: justify;">This is a paragraph.</p>
<h2 class="section-header">Heading</h2>
<strong>Bold text</strong>
```

**AI Generated Patterns:**
```json
{
  "patterns": [
    {
      "element_type": "p",
      "source_pattern": "<p[^>]*>(.*?)</p>",
      "target_pattern": "<p class=\"article-body\" style=\"text-align: justify;\">\\1</p>"
    },
    {
      "element_type": "h2",
      "source_pattern": "<h2[^>]*>(.*?)</h2>",
      "target_pattern": "<h2 class=\"section-header\">\\1</h2>"
    }
  ]
}
```

### 2. Natural Language Pattern Editing

Use plain English to modify patterns:

**Examples:**
- "Make all h2 headings blue"
- "Add margin-bottom: 20px to paragraphs"
- "Make links open in new tab"
- "Add class 'highlight' to all h3 headings"
- "Remove all styling from images"

**How it works:**
1. Select project in AI Pattern Editor
2. Enter natural language instruction
3. AI modifies patterns and shows preview
4. Review changes
5. Save to project

---

## Testing

### Run All Tests

```bash
cd tests
python -m pytest
```

### Test Individual Components

```bash
# Database operations
python tests/test_database.py

# Pattern engine
python tests/test_pattern_engine.py

# Workflow integration
python tests/test_workflow_integration.py

# Natural language editing
python tests/test_pattern_modification.py
```

---

## Troubleshooting

### "ANTHROPIC_API_KEY not found"
- Ensure `.env` file exists with your API key
- Check file is in project root directory

### "WordPress credentials not configured"
- Configure project with credentials, OR
- Set `WP_BASE_URL`, `WP_USERNAME`, `WP_APP_PASS` in `.env`

### "Failed to convert Google Docs"
- **Option 1**: Use published Google Docs URL (ends with `/pub`)
  - File → Share → Publish to web
  - No authentication needed
- **Option 2**: Use Google Drive API
  - Set up OAuth credentials (`client_secret.json`)
  - First run will open browser for authentication

### Images Not Processing
- Check image URLs are accessible
- Verify sufficient disk space for temp files
- Check `raw_images/` and `resized_images/` directories exist

### WordPress Authentication Failed
- Verify WordPress REST API is enabled
- Use **Application Password**, not regular password
- Go to: WordPress → Users → Profile → Application Passwords

### Streamlit App Not Loading
- Make sure port 8501 is available
- Check if another Streamlit instance is running
- Try: `streamlit run app_streamlit.py --server.port 8502`

---

## Security Notes

### Sensitive Files (git-ignored)

These files contain sensitive data and should NEVER be committed:
- `.env` - Environment variables with API keys
- `credentials/client_secret.json` - Google OAuth credentials
- `credentials/token.json` - Google OAuth token
- `data/clients.db` - Database with WordPress credentials

### Safe Sharing

To share this project:
1. Copy `.env` → `.env.example` and remove sensitive values
2. Exclude `credentials/` and `data/` directories
3. Share `.env.example` as template
4. Document required credentials in handoff notes

---

## Version History

**v2.0.0** (2025-11-13) - Current
- Added Streamlit web UI as primary interface
- Improved navigation and UX (clean, professional design)
- Enhanced AI pattern editor with visual feedback
- Complete codebase cleanup (removed Railway/FastAPI)
- Simplified architecture (local-first development)
- Comprehensive documentation for team handoff

**v1.2.0** (2025-11-13)
- Added natural language pattern editing
- Restructured codebase for clarity
- Comprehensive documentation
- Full test suite

**v1.0.0** (2025-11-11)
- Initial MVP release
- Multi-project management
- AI-powered configuration
- Complete publishing workflow

---

## Technology Stack

- **Python 3.11+** - Core language
- **Streamlit** - Web UI framework
- **SQLite** - Local database
- **Claude Sonnet 4.5** - AI model (Anthropic)
- **Google Drive API** - Google Docs conversion (optional)
- **WordPress REST API** - Publishing target
- **BeautifulSoup** - HTML parsing
- **Pillow** - Image processing
- **Requests** - HTTP client

---

## Support & Documentation

- **README.md** (this file) - Quick start and overview
- **SETUP.md** - Detailed installation and configuration
- **HANDOFF.md** - Developer guide and architecture details
- **START_HERE.md** - Quick reference for common tasks

For issues or questions:
1. Check documentation files
2. Review troubleshooting section
3. Check test results for component-specific issues
4. Review code comments for implementation details

---

**Version**: v2.0.0
**Last Updated**: 2025-11-13
**Status**: Production Ready - Local Development
**Primary Interface**: Streamlit UI at http://localhost:8501
