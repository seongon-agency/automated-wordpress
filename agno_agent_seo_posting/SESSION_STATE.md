# Session State - WordPress SEO Publishing System

**Last Updated:** 2025-12-03
**Branch:** claude_lam_het

---

## Project Overview

This is a **WordPress SEO Publishing System** that automates publishing from Google Docs to WordPress with AI-powered HTML transformation. The main application is a Streamlit web app.

**Current Version:** v2.0.0 (Streamlit-based multi-project system)

---

## Recent Work Completed

### 1. Migration from SQLite to Supabase (Completed)

- **Why:** To enable cloud deployment on Streamlit Cloud (SQLite doesn't persist on Streamlit Cloud)
- **What was done:**
  - Updated `src/database/project_manager.py` to use Supabase instead of SQLite
  - Updated `src/database/schema.sql` with PostgreSQL/Supabase syntax
  - Created `migrate_to_supabase.py` migration script
  - Successfully migrated **5 projects** and **94 publishing history records**

**Supabase Configuration:**
- URL: `https://znrdcqyximcpprljcbzi.supabase.co`
- Tables: `projects`, `publishing_history`
- Credentials stored in `.streamlit/secrets.toml`

### 2. Full Vietnamese Translation (Completed - 2025-12-02)

Translated the entire `app_streamlit.py` UI from English to Vietnamese:

- Page config and sidebar navigation
- Home page content
- Projects page content
- Create Project page content
- Edit Project page content
- AI Pattern Editor page content
- Scan HTML Template page content
- Publish Content page content
- Batch Publish page content
- Publishing History and Footer

**Important:** Conditional checks were updated to use Vietnamese option labels:
```python
# Resize method options
"Chiều Rộng Cố Định" -> resize_method_key = "fixed_width"
"Kích Thước Gốc Google Docs" -> resize_method_key = "google_docs_original"
"Không Thay Đổi (Chất Lượng Gốc)" -> resize_method_key = "no_resize"

# Naming method options
"Mặc Định (tên_dự_án)" -> naming_method_key = "default"
"Theo Alt Text" -> naming_method_key = "alt_text"
"Theo Từ Khóa Chính" -> naming_method_key = "main_keyword"
```

### 3. Bug Fixes Applied

- **Image naming method save issue:** Fixed the create project form to properly save image naming method
- **Main keyword input not appearing:** Fixed conditional logic for showing main keyword input field

### 4. Save HTML to Google Docs Feature (Completed - 2025-12-03)

Added a new optional feature to save the processed HTML content to a Google Docs file after publishing.

**What was done:**
- Added UI fields in Create/Edit Project forms:
  - Checkbox: "Luu HTML Da Xu Ly Vao Google Docs"
  - Text input: "URL Thu Muc Google Docs"
- Created new tool: `src/tools/google_docs_creator.py`
- Added Step 7 to publishing workflow (optional, non-blocking)
- Updated `schema.sql` with new column for tracking

**How it works:**
1. Enable the feature in project settings
2. Paste a Google Drive folder URL where docs should be saved
3. After each successful publish, a Google Doc is created containing:
   - Post title and timestamp
   - Link to WordPress post
   - The full processed HTML content

**New settings in `image_configs` JSONB:**
```python
"save_html_to_google_docs": True/False
"google_docs_folder_url": "https://drive.google.com/drive/folders/..."
```

**Files modified:**
- `app_streamlit.py` - UI fields for the feature
- `src/workflows/publishing_workflow.py` - Added Step 7
- `src/tools/google_docs_creator.py` - New file
- `src/database/schema.sql` - Added `saved_html_docs_url` column

---

## Current Application State

### Running the App

```bash
cd agno_agent_seo_posting
streamlit run app_streamlit.py
```

Opens at: http://localhost:8501

### Key Files

| File | Purpose |
|------|---------|
| `app_streamlit.py` | Main Streamlit UI (fully translated to Vietnamese) |
| `src/database/project_manager.py` | Supabase database operations |
| `src/workflows/publishing_workflow.py` | 7-step publishing pipeline |
| `src/tools/google_docs_creator.py` | Creates Google Docs with HTML content |
| `.streamlit/secrets.toml` | API keys and credentials (DO NOT COMMIT) |

### Database (Supabase)

- **Projects table:** Stores WordPress site configs, HTML patterns, image settings
- **Publishing history:** Audit log of all publish attempts

### Existing Projects in Database

5 projects migrated from SQLite:
1. Check Supabase dashboard for current projects
2. Or use the "Danh Sách Dự Án" page in the app

---

## Configuration Files

### .streamlit/secrets.toml (DO NOT COMMIT)

Contains:
- `SUPABASE_URL` and `SUPABASE_KEY` - Database credentials
- `ANTHROPIC_API_KEY` - For AI features
- `WP_BASE_URL`, `WP_USERNAME`, `WP_APP_PASS` - Default WordPress
- `DRIVE_FOLDER_ID` - Google Drive folder
- Image processing defaults

### credentials/ folder

- `client_secret.json` - Google OAuth credentials
- `token.json` - Google OAuth token (for reading Google Docs)
- `token_drive_upload.json` - Google Drive upload token (for image backup)
- `token_docs_creator.json` - Google Docs creator token (for saving HTML)

---

## Architecture Summary

```
User Interface (Streamlit - app_streamlit.py)
         ↓
Publishing Workflow (6-step pipeline)
         ↓
Tools Layer (Google Docs, Image Processing, HTML Transform, WordPress)
         ↓
Utilities Layer (Pattern Engine, HTML Extractor, AI Pattern Modifier)
         ↓
Database Layer (Supabase - PostgreSQL)
```

### Publishing Workflow Steps

1. Convert Google Docs to HTML
2. Extract title and clean HTML
3. Process images (download & resize)
3.5. Upload images to Google Drive (optional)
4. Upload images to WordPress
5. Apply HTML transformations (project-specific patterns)
6. Create WordPress post (as draft)
7. Save HTML to Google Docs (optional)

---

## Known Issues / Pending Items

- None currently pending
- All translation tasks completed
- Database migration completed

---

## Quick Commands

```bash
# Run the app
cd agno_agent_seo_posting
streamlit run app_streamlit.py

# Run tests
cd agno_agent_seo_posting/tests
python -m pytest -v

# Clear temp images
rm -rf raw_images/* resized_images/*

# Kill stuck Streamlit processes
pkill -f streamlit
```

---

## For Claude Code (Next Session)

When starting a new session:

1. Read this file first: `SESSION_STATE.md`
2. Read `CLAUDE.md` for full project documentation
3. The app is in Vietnamese - all UI text has been translated
4. Database is Supabase (cloud), not SQLite
5. Main entry point is `app_streamlit.py`

**Git status at session end:**
- Branch: `claude_lam_het`
- Uncommitted changes: Vietnamese translation in `app_streamlit.py`
- Several test files and documentation files staged

---

## Contact / Notes

- WordPress sites use **Application Passwords** (not regular passwords)
- Google Docs URLs work with any format (edit, view, or published)
- Posts are created as **drafts** for safety
- First run requires Google OAuth (browser opens once)
