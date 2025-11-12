# WordPress SEO Publishing System

**Automated Google Docs → WordPress Publishing Platform**

Multi-client SEO content publishing system with AI-powered HTML transformation, natural language pattern editing, and multi-project management.

---

## 🎯 Overview

This system automates the complete workflow for publishing SEO content from Google Docs to WordPress with client-specific HTML transformations:

1. **Convert** Google Docs to clean HTML (via Google Drive API)
2. **Process** images (download, resize, upload to WordPress)
3. **Transform** HTML to match client-specific formats (AI-powered)
4. **Publish** to WordPress as draft posts

### Key Features

- ✨ **AI-Powered Configuration** - AI analyzes sample HTML and generates transformation patterns automatically
- 🗣️ **Natural Language Editing** - Modify HTML patterns using plain English ("Make all h2 headings blue")
- 🎯 **Multi-Project Management** - Configure once per client, publish many times
- 🖼️ **Automated Image Processing** - Download, resize, and upload images automatically
- 📊 **Publishing History** - Track all publishes with success/failure logs
- 🔒 **Secure Credentials** - Isolated credentials directory (git-ignored)

---

## 📁 Project Structure

```
wordpress-seo-publisher/
├── app/                          # Application entry points
│   ├── main.py                   # Main CLI application
│   ├── configure.py              # Project configuration wizard
│   └── edit.py                   # Project editor (with natural language support)
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
│   ├── test_database.py          # Database tests
│   ├── test_workflow_integration.py   # Integration tests
│   ├── test_pattern_engine.py    # Pattern transformation tests
│   ├── test_pattern_modification.py   # Natural language editing tests
│   └── ...                       # Additional test files
│
├── data/                         # Runtime data
│   ├── clients.db                # SQLite database
│   └── images/                   # Temporary image storage
│       ├── raw/                  # Downloaded images
│       └── resized/              # Processed images
│
├── credentials/                  # Sensitive files (git-ignored)
│   ├── client_secret.json        # Google OAuth credentials
│   └── token.json                # Google OAuth token
│
├── docs/                         # Documentation
│   └── LARK_IMPLEMENTATION_PLAN.md    # Future Larksuite integration plan
│
├── README.md                     # This file
├── requirements.txt              # Python dependencies
├── .env                          # Environment variables (git-ignored)
├── .env.example                  # Example environment file
└── .gitignore                    # Git ignore rules
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **WordPress site** with REST API enabled
- **WordPress Application Password** (not regular password)
- **Google Cloud Project** with Drive API enabled
- **Google OAuth Credentials** (client_secret.json)
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

# Optional: Default WordPress credentials
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

2. **Setup Google OAuth**:
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

```bash
# Run from project root
python app/main.py
```

You'll see:
```
================================================================================
SEO PUBLISHING SYSTEM - MVP v1.0
================================================================================

Automated Google Docs to WordPress Publishing
with AI-Powered Project Configuration

================================================================================

[MAIN MENU]
----------------------------------------
1. Publish Google Docs to WordPress
2. Configure New Project
3. Edit Existing Project
4. List All Projects
5. Exit
----------------------------------------
```

---

## 📖 Usage Guide

### 1. Configure a New Project

```bash
# Select option 2 from main menu
python app/main.py
> 2
```

The AI-powered wizard will guide you through:

1. **Basic Info**: Project ID, name, WordPress URL, credentials
2. **Image Settings**: Target width, quality, format, CSS classes
3. **HTML Analysis**: Paste sample HTML → AI extracts patterns automatically

**Example**: You paste this sample HTML:
```html
<p class="article-body" style="text-align: justify;">This is a paragraph.</p>
<h2 class="section-header">Heading</h2>
<strong>Bold text</strong>
```

AI generates transformation patterns:
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

### 2. Publish Content

```bash
# Select option 1 from main menu
python app/main.py
> 1
```

**Steps**:
1. Select configured project (or skip for no transformations)
2. Enter Google Docs URL (any edit/view URL works)
3. Watch the automation work:

```
[1/6] 📄 Converting Google Docs to HTML... ✓
[2/6] 📝 Extracting post title... ✓
[3/6] 🖼️  Processing images... ✓
[4/6] ⬆️  Uploading images to WordPress... ✓
[5/6] 🔄 Applying HTML transformations... ✓
[6/6] 📤 Creating WordPress post... ✓

✅ PUBLISHING COMPLETED SUCCESSFULLY!
🔗 Post URL: https://your-site.com/your-post/
```

**First Time Publishing**: Browser opens for Google authentication → Grant access to Drive API → Token saved for future use

### 3. Edit Project (Natural Language)

```bash
# Select option 3 from main menu
python app/main.py
> 3
```

**Natural Language Editing** (NEW! ✨):

```
Select project: dangbaiseongon
Choose: 1. HTML transformation patterns
Choose: 1. Modify with natural language

Enter instruction: Make all h2 headings blue

AI Preview:
  <h2 class="section-header">\\1</h2>
  →
  <h2 class="section-header" style="color: blue;">\\1</h2>

Save changes? (Y/n): y
✓ Patterns updated!
```

**Examples of natural language instructions**:
- "Make all h2 headings blue"
- "Add margin-bottom: 20px to paragraphs"
- "Make links open in new tab"
- "Add class 'highlight' to all h3 headings"

### 4. List All Projects

```bash
# Select option 4 from main menu
python app/main.py
> 4
```

Shows all configured projects with details:
- Project ID and name
- WordPress URL
- Number of HTML patterns
- Image width settings
- Status (active/inactive)

---

## 🏗️ Architecture

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

### Publishing Workflow (6 Steps)

```
Google Docs URL
    ↓
[1] Convert to HTML (Google Drive API)
    ↓
[2] Extract title & clean HTML (Remove H1 and content before)
    ↓
[3] Process images (Download & resize)
    ↓
[4] Upload images to WordPress (Binary upload)
    ↓
[5] Apply HTML transformations (Project-specific patterns)
    ↓
[6] Create WordPress post (Draft with transformed HTML)
    ↓
Log to history & return post URL
```

### Key Components

**Tools** (`src/tools/`):
- `google_docs_converter.py` - Google Drive API integration
- `image_processor.py` - Image download and resizing
- `html_transformer.py` - Pattern-based HTML transformation
- `wordpress_uploader.py` - WordPress REST API client

**Utilities** (`src/utils/`):
- `html_extractor.py` - Title extraction and HTML cleaning
- `pattern_engine.py` - Regex pattern application
- `pattern_modifier.py` - AI-powered pattern modification (NEW!)

**Workflows** (`src/workflows/`):
- `publishing_workflow.py` - Complete 6-step publishing pipeline

---

## 🧪 Testing

### Run All Tests

```bash
# Run from project root
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

### Test Results

Current status: **All tests passing ✅**

```
test_database.py:             PASSED ✅
test_pattern_engine.py:       PASSED ✅
test_workflow_integration.py: PASSED ✅
test_pattern_modification.py: PASSED ✅ (5/5 tests)
test_edit_project.py:         PASSED ✅
```

---

## 🐛 Troubleshooting

### "ANTHROPIC_API_KEY not found"
- Ensure `.env` file exists with your API key
- Check file is in project root directory

### "WordPress credentials not configured"
- Configure project with credentials, OR
- Set `WP_BASE_URL`, `WP_USERNAME`, `WP_APP_PASS` in `.env`

### "Failed to convert Google Docs"
- Verify you have access to the Google Doc
- Check `client_secret.json` is in `credentials/` directory
- On first run, browser will open for authentication

### Images Not Processing
- Check image URLs are accessible
- Verify sufficient disk space for temp files
- Check `data/images/` directories exist

### WordPress Authentication Failed
- Verify WordPress REST API is enabled
- Use **Application Password**, not regular password
- Go to: WordPress → Users → Profile → Application Passwords

### Import Errors
- Ensure you're running from project root: `python app/main.py`
- Check all dependencies installed: `pip install -r requirements.txt`

---

## 🔐 Security Notes

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

---

## 📊 Version History

**v1.2.0** (2025-11-13) - Current
- ✨ Added natural language pattern editing
- 🏗️ Restructured codebase for clarity
- 📚 Comprehensive documentation
- ✅ Full test suite

**v1.1.0** (2025-11-12)
- Added project editing feature
- Fixed Google API connection issues
- Comprehensive testing suite

**v1.0.0** (2025-11-11)
- Initial MVP release
- Multi-project management
- AI-powered configuration
- Complete publishing workflow

---

## 🚀 Roadmap

### Completed
- [x] Multi-project configuration system
- [x] AI-powered HTML pattern analysis
- [x] Natural language pattern editing
- [x] Complete publishing workflow
- [x] Image processing pipeline
- [x] Publishing history tracking
- [x] Comprehensive testing

### Planned (Next Phase)
- [ ] FastAPI REST API backend
- [ ] Larksuite Bot integration
- [ ] Lark Base table integration
- [ ] Bulk processing capability
- [ ] Web-based UI (Streamlit or React)
- [ ] Analytics dashboard

See [LARK_IMPLEMENTATION_PLAN.md](docs/LARK_IMPLEMENTATION_PLAN.md) for detailed future plans.

---

## 📄 License

Internal use only. Not for public distribution.

---

## 👥 Support

For issues or questions:
1. Check this README
2. Review troubleshooting section
3. Check test results for component-specific issues
4. Review code comments for implementation details

---

**Built with**:
- Python 3.11+
- Claude Sonnet 4.5 (AI model)
- SQLite (database)
- Google Drive API (Google Docs)
- WordPress REST API (publishing)
- BeautifulSoup (HTML parsing)
- Pillow (image processing)

---

**Version**: v1.2.0
**Last Updated**: 2025-11-13
**Status**: Production Ready ✅
