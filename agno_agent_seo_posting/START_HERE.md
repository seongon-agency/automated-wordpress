# Quick Start Guide

**WordPress SEO Publishing System - v2.0.0**

Fast reference for common tasks. For detailed documentation, see README.md, SETUP.md, and HANDOFF.md.

---

## Running the Application

### Streamlit UI (Recommended)

```bash
streamlit run app_streamlit.py
```

Opens at: http://localhost:8501

### CLI Application

```bash
python app/main.py
```

---

## First-Time Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Create .env File

```bash
cp .env.example .env
```

Edit `.env` and add your Anthropic API key:

```env
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### 3. Get WordPress Application Password

1. WordPress Admin → Users → Profile
2. Scroll to "Application Passwords"
3. Create new → Copy password
4. Use when creating project

---

## Common Tasks

### Create a New Project (WordPress Site)

**Streamlit:**
1. Click "Create Project"
2. Fill in WordPress URL, username, app password
3. Configure image settings
4. Submit

**CLI:**
1. Run `python app/main.py`
2. Choose option 2
3. Follow prompts

### Publish Google Docs to WordPress

**Prepare Google Docs:**
1. File → Share → Publish to web
2. Copy URL (should end with `/pub`)

**Streamlit:**
1. Click "Publish Content"
2. Select project
3. Paste Google Docs URL
4. Click "Publish to WordPress"
5. Wait ~1-2 minutes
6. Get post URL

**CLI:**
1. Run `python app/main.py`
2. Choose option 1
3. Select project
4. Enter Google Docs URL
5. Wait for completion

### Configure HTML Patterns with AI

**Option 1: Scan HTML Template**

Streamlit → "Scan HTML Template"
1. Select project
2. Paste sample HTML from your WordPress theme
3. AI generates patterns automatically
4. Save to project

**Option 2: Natural Language Editing**

Streamlit → "AI Pattern Editor"
1. Select project
2. Enter instruction: "Make all h2 headings blue"
3. Review AI changes
4. Save to project

### Edit Project Settings

**Streamlit:**
1. Click "Edit Project Settings"
2. Select project
3. Modify settings
4. Save changes

---

## Publishing Workflow

```
1. Google Docs URL → HTML conversion
2. Extract title (from H1)
3. Download & resize images
4. Upload images to WordPress
5. Apply HTML transformations
6. Create draft post in WordPress
```

Time: ~1-2 minutes per document

---

## Troubleshooting

### Application Won't Start

```bash
# Check Python version (need 3.11+)
python --version

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check for port conflicts
pkill -f streamlit
streamlit run app_streamlit.py
```

### "ANTHROPIC_API_KEY not found"

1. Check `.env` file exists
2. Verify API key is set
3. Restart application

### WordPress Authentication Failed

- Use Application Password (not regular password)
- No spaces in password: `xxxx xxxx xxxx xxxx`
- WordPress URL has no trailing slash
- Test: `https://your-site.com/wp-json/wp/v2/posts`

### Google Docs Conversion Failed

**Option 1 (Easier):**
- Use published Google Docs URL
- File → Share → Publish to web
- URL must end with `/pub`

**Option 2:**
- Set up Google OAuth credentials
- See SETUP.md for details

### Images Not Uploading

- Check image URLs are accessible
- Verify WordPress media uploads enabled
- Check file size limits

---

## Project Structure

```
agno_agent_seo_posting/
├── app_streamlit.py          # Streamlit UI (Primary)
├── app/main.py                # CLI interface
├── src/
│   ├── workflows/             # Complete publishing pipeline
│   ├── tools/                 # External integrations
│   ├── utils/                 # Helpers & AI features
│   └── database/              # SQLite operations
├── data/clients.db            # Your projects & history
├── .env                       # Your configuration
└── requirements.txt           # Dependencies
```

---

## Database Queries

```bash
# Open database
sqlite3 data/clients.db

# List all projects
SELECT project_id, project_name, wordpress_url FROM projects;

# Check recent publishes
SELECT published_at, post_title, success FROM publishing_history
ORDER BY published_at DESC LIMIT 10;

# Exit
.quit
```

---

## Maintenance

### Clear Temporary Images

```bash
rm -rf raw_images/* resized_images/*
```

### Backup Database

```bash
cp data/clients.db data/clients_backup_$(date +%Y%m%d).db
```

### Update Dependencies

```bash
pip install -U -r requirements.txt
```

---

## Key Features

**Multi-Project Management**
- Manage multiple WordPress sites
- Different transformation rules per site
- Reusable configurations

**AI-Powered Configuration**
- Scan HTML → Auto-generate patterns
- Natural language pattern editing
- Claude Sonnet 4.5 powered

**Automated Workflow**
- One-click publishing
- Image processing included
- Draft posts by default (safety)

**Two Interfaces**
- Streamlit UI (visual, beginner-friendly)
- CLI (fast, power users)

---

## Quick Reference

### Start Application
```bash
streamlit run app_streamlit.py
```

### Create Project
Streamlit → Create Project → Fill form → Submit

### Publish Content
Streamlit → Publish Content → Select project → Paste URL → Publish

### View Projects
Streamlit → Projects

### Edit Patterns
Streamlit → AI Pattern Editor → Natural language instructions

---

## Documentation Files

- **README.md** - Complete overview and guide
- **SETUP.md** - Detailed installation instructions
- **HANDOFF.md** - Developer documentation & architecture
- **START_HERE.md** - This file (quick reference)

---

## Support

Having issues? Check in order:

1. This file (common tasks)
2. README.md (troubleshooting section)
3. SETUP.md (setup issues)
4. HANDOFF.md (development questions)

---

## Environment Variables Reference

Required in `.env`:

```env
# Required
ANTHROPIC_API_KEY=sk-ant-...

# Optional (can configure per-project instead)
WP_BASE_URL=https://your-site.com
WP_USERNAME=your_username
WP_APP_PASS=xxxx xxxx xxxx xxxx

# Optional (defaults work fine)
DEFAULT_IMAGE_WIDTH=800
IMAGE_QUALITY=92
IMAGE_FORMAT=JPEG
```

---

## Version Information

- **Version:** v2.0.0
- **Updated:** 2025-11-13
- **Status:** Production Ready (Local)
- **Primary Interface:** Streamlit UI

---

**Ready to publish!**

Run: `streamlit run app_streamlit.py`
