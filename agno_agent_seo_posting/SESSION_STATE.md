# Session State - WordPress SEO Publishing System

**Last Updated:** 2025-12-05
**Branch:** claude_lam_het
**Current Version:** v2.1.0

---

## Project Overview

This is a **WordPress SEO Publishing System** that automates publishing from Google Docs to WordPress with AI-powered HTML transformation. The main application is a Streamlit web app deployed on Streamlit Cloud.

**Deployment:** https://github.com/seongon-agency/automated-wordpress (Streamlit Cloud)

---

## Recent Changes Log

### 2025-12-05

#### Change #1: Enhanced Image Resize Options
**Commits:** `57dbc62`, `af4be82`

**What changed:**
- Modified "Fixed Width" resize option to support both width AND height
- Added height input field in Create/Edit Project forms
- Behavior:
  - Only width provided → proportional resize (original behavior)
  - Both width and height provided → exact dimensions resize

**Files modified:**
- `app_streamlit.py` - Create Project form (lines 342-383)
- `app_streamlit.py` - Edit Project form (lines 690-731)
- `app_streamlit.py` - Form submission logic

**UI Labels:**
- Section renamed: "Cài Đặt Chiều Rộng Cố Định" → "Cài Đặt Kích Thước Tùy Chỉnh"
- New field: "Chiều Cao Ảnh (px)" (value 0 = proportional)

---

#### Change #2: Removed Google Drive Backup Feature
**Commit:** `57dbc62`

**What changed:**
- Removed Google Drive folder URL input from Create Project form
- Removed Google Drive folder URL input from Edit Project form
- Removed `google_drive_folder_url` from image_configs

**Reason:** Feature was not being used

---

#### Change #3: Fixed Radio Button State Persistence Bug
**Commit:** `fc0b0b8`

**Problem:**
After saving project settings, radio buttons (resize method, naming method) showed old values instead of saved values.

**Root Cause:**
Streamlit widgets with `key` parameter persist values independently. The `index` parameter is ignored when a `key` exists in session state.

**Solution:**
- Removed `key="resize_method_selector"` from resize method radio
- Removed `key="naming_method_selector"` from naming method radio
- Radio widgets now use `index` parameter correctly

**Files modified:**
- `app_streamlit.py` (lines 609-614, 639-644, 565-575, 841-853)

---

#### Change #4: Added Success Message After Saving Project
**Commit:** `1d653ab`

**What changed:**
- Added visible success message "Thay đổi thành công!" at top of Edit Project page after saving
- Uses session state flag (`edit_save_success`) to persist message across page rerun
- Message auto-clears after being displayed once

**Files modified:**
- `app_streamlit.py` (lines 536-539, 851-852)

---

### 2025-12-02 (Previous Session)

#### Vietnamese Translation (Completed)
- Translated entire `app_streamlit.py` UI from English to Vietnamese
- Updated conditional checks to use Vietnamese option labels

#### Database Migration (Completed)
- Migrated from SQLite to Supabase for Streamlit Cloud deployment
- 5 projects and 94 publishing history records migrated

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
| `app_streamlit.py` | Main Streamlit UI (Vietnamese) |
| `src/database/project_manager.py` | Supabase database operations |
| `src/workflows/publishing_workflow.py` | 6-step publishing pipeline |
| `src/tools/image_processor.py` | Image download, resize, upload |
| `.streamlit/secrets.toml` | API keys and credentials (DO NOT COMMIT) |
| `SESSION_STATE.md` | This file - project state tracking |

---

## image_configs Structure

```json
{
  "resize_method": "fixed_width" | "google_docs_original" | "no_resize",
  "target_width": 800,
  "target_height": null,
  "image_quality": 92,
  "image_format": "JPEG" | "PNG" | "WEBP",
  "enable_auto_captions": true,
  "naming_method": "default" | "alt_text" | "main_keyword",
  "alt_text_words": 5
}
```

### Resize Methods

| UI Label (Vietnamese) | Backend Key | Behavior |
|----------------------|-------------|----------|
| Chiều Rộng Cố Định | `fixed_width` | Resize to target_width (and optional target_height) |
| Kích Thước Gốc Google Docs | `google_docs_original` | Use dimensions from Google Docs HTML |
| Không Thay Đổi (Chất Lượng Gốc) | `no_resize` | Copy original images without processing |

### Naming Methods

| UI Label (Vietnamese) | Backend Key |
|----------------------|-------------|
| Mặc Định (tên_dự_án) | `default` |
| Theo Alt Text | `alt_text` |
| Theo Từ Khóa Chính | `main_keyword` |

---

## Database (Supabase)

**Tables:**
- `projects` - WordPress site configs, HTML patterns, image settings
- `publishing_history` - Audit log of all publish attempts

**Credentials:** Stored in `.streamlit/secrets.toml`

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
3. Process images (download & resize based on project settings)
4. Upload images to WordPress media library
5. Apply HTML transformations (project-specific patterns)
6. Create WordPress post (as draft)

---

## Known Issues / Pending Items

### Resolved
- [x] Radio button state not persisting after save (fixed 2025-12-05)
- [x] Vietnamese translation completed (2025-12-02)
- [x] SQLite to Supabase migration (2025-12-02)

### Open
- [ ] None currently tracked

---

## Important Implementation Notes

### Streamlit Session State
- **DO NOT use `key` parameter** on radio buttons that need to reflect database values
- Use `index` parameter with session state tracking instead
- Always clear relevant session state keys before `st.rerun()`

### Session State Keys Used (Edit Project)
- `edit_project_id` - Currently selected project
- `edit_resize_method` - Current resize method selection
- `edit_naming_method_state` - Current naming method selection
- `edit_save_success` - Flag to show success message after save

---

## Configuration Files

### .streamlit/secrets.toml (DO NOT COMMIT)

Contains:
- `SUPABASE_URL` and `SUPABASE_KEY` - Database credentials
- `ANTHROPIC_API_KEY` - For AI features
- `WP_BASE_URL`, `WP_USERNAME`, `WP_APP_PASS` - Default WordPress
- Image processing defaults

### credentials/ folder

- `client_secret.json` - Google OAuth credentials
- `token.json` - Google OAuth token (auto-generated on first run)

---

## Quick Commands

```bash
# Run the app locally
cd agno_agent_seo_posting
streamlit run app_streamlit.py

# Run tests
cd agno_agent_seo_posting/tests
python -m pytest -v

# Clear temp images
rm -rf raw_images/* resized_images/*

# Kill stuck Streamlit processes
pkill -f streamlit

# Check git status
git status

# Push changes to trigger Streamlit Cloud redeploy
git add -A && git commit -m "message" && git push
```

---

## For Claude Code (Next Session)

When starting a new session:

1. **Read this file first:** `SESSION_STATE.md`
2. **Read `CLAUDE.md`** for full project documentation
3. The app UI is in **Vietnamese**
4. Database is **Supabase** (cloud PostgreSQL), not SQLite
5. Main entry point is `app_streamlit.py`
6. After code changes, **commit and push** to deploy to Streamlit Cloud

---

## Change Log Template

Use this template when recording new changes:

```markdown
#### Change #N: [Brief Title]
**Commit:** `[hash]`

**What changed:**
- [Description]

**Why:**
- [Reason]

**Files modified:**
- `filename.py` (description)
```

---

## Contact / Notes

- WordPress sites use **Application Passwords** (not regular passwords)
- Google Docs URLs work with any format (edit, view, or published)
- Posts are created as **drafts** for safety
- First run requires Google OAuth (browser opens once)
