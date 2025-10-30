# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an SEO pipeline for automated WordPress publishing of blogs. The system consists of two main components:

1. **Legacy WordPress Publishing Pipeline** - Python scripts that handle Google Docs export, image processing, HTML transformation, and WordPress API integration
2. **Agno AI Agent System** - Modern AI agent framework for content creation and CMS management with tracing/evaluation capabilities

## Development Setup

### Root Level (WordPress Pipeline)
```bash
# Install dependencies
pip install -r requirements.txt

# Required packages: google-api-python-client, google-auth, google-auth-oauthlib, pandas, beautifulsoup4, gspread, pillow
```

### Agno Directory (AI Agents)
```bash
cd agno
pip install -r requirements.txt

# Required packages: agno, pandas, beautifulsoup4
```

### Environment Configuration
- Root level requires `client_secret.json` and `token.json` for Google API authentication
- `agno/.env` file needed for AI agent configuration with required keys:
  - `ANTHROPIC_API_KEY` - Claude API access
  - `DIRECTUS_URL`, `DIRECTUS_USER_EMAIL`, `DIRECTUS_USER_PASSWORD` - CMS integration
  - Optional: `COHERE_API_KEY` for embeddings (RAG feature currently disabled)

## Architecture

### WordPress Publishing Pipeline (`functions.py`)

The main pipeline processes Google Docs content for WordPress publication:

1. **Authentication & Google Drive Integration** (`get_creds()`)
   - OAuth2 flow with Google Drive and Sheets APIs
   - Token persistence in `token.json`

2. **Content Extraction**
   - `extract_file_id()` - Parse Google Docs/Drive URLs
   - `export_doc_html_bytes()` - Export docs as HTML
   - `extract_images_from_html_text()` - Extract embedded images

3. **Vietnamese Text Processing**
   - `strip_diacritics()` - Remove Vietnamese diacritical marks (mỹ nhân → my nhan)
   - `slugify()` - Convert Vietnamese text to URL-safe slugs

4. **Image Processing Pipeline**
   - `download_to_memory()` / `download_to_file()` - Fetch images
   - `resize_fit()` / `resize_fit_memory()` - Resize with aspect ratio preservation
   - `upload_resized()` - Upload to WordPress media library
   - `build_caption_shortcode()` - Generate WordPress caption shortcodes

5. **HTML Transformation** (`transform_html_dom()`)
   - Removes Google Docs artifacts (comments, styles, redirects)
   - Normalizes paragraph alignment (dir="ltr", text-align)
   - Converts `<span style="font-weight: bold">` to `<strong>`
   - Wraps italic text with `<em>` tags
   - Centers image-containing paragraphs
   - Removes font-family/font-size styling
   - Strips `&nbsp;` entities

6. **WordPress API Integration**
   - Hardcoded credentials in `functions.py:258-262` (WP_BASE_URL, WP_USERNAME, WP_APP_PASS)
   - Basic auth with application password
   - Media upload endpoint: `/wp-json/wp/v2/media`

### Agno AI Agent System (`agno/`)

Modern agentic framework built on the Agno library:

- **`agents.py`** - Main agent server with AgentOS architecture
  - Web CMS Agent - Posts content to CMS via MCP tools
  - Multi-agent team capability (outline, writer, evaluator - currently commented out)
  - SQLite database for session/memory/metrics storage
  - Phoenix tracing integration on `localhost:6006`
  - Serves on web interface via `AgentOS.serve()`

- **`workflow.py`** - Simple test agent demonstrating Agno workflow capabilities
  - Math operations (power, factorial)
  - Example of agent + tools integration

### Data Flow

```
Google Sheets (URLs) →
  extract_file_id() →
    export_doc_html_bytes() →
      transform_html_dom() →
        Image extraction & processing →
          upload_resized() →
            WordPress API
```

## Common Commands

### Running the Agno Agent Server
```bash
cd agno
python agents.py
# Serves web interface with Phoenix tracing on http://localhost:6006
```

### Testing Basic Agent
```bash
cd agno
python workflow.py
# Interactive math agent for testing
```

### Working with Jupyter Notebook
```bash
jupyter notebook notebook.ipynb
# Contains step-by-step WordPress pipeline execution
```

## Key Implementation Details

### WordPress Credentials
WordPress API credentials are **hardcoded** in `functions.py:258-262`. To update:
- `WP_BASE_URL` - WordPress site URL (no trailing slash)
- `WP_USERNAME` - WordPress admin username
- `WP_APP_PASS` - Application password from WP dashboard

### Image Processing Constraints
- Two resize modes available:
  - `resize_fit()` - Maintains aspect ratio, fits within max dimensions
  - `resize_fit_memory()` - Forces exact dimensions (may distort)
- Supported formats: JPG, PNG, WebP, GIF, SVG
- JPEG quality: 92, WebP quality: 90

### HTML Transformation Rules
The `transform_html_dom()` function enforces specific WordPress formatting:
- All `<p>` tags get `dir="ltr"` and `text-align: justify` (unless center/right)
- Image paragraphs wrapped with `<span style="font-weight: 400">`
- Tables get `width: 100%` if not specified
- Google redirect links unwrapped to direct URLs

### Database Schema (Agno)
SQLite database (`database.db`) with tables:
- `sessions` - Agent/Team/Workflow runs
- `memory` - User memory storage
- `metrics` - Performance aggregations
- `evals` - Evaluation data
- `knowledge` - RAG content (feature disabled)

## Git Workflow

The repository includes basic git commands in `git_notices.md`:
```bash
git add .
git commit -m "message"
git push origin main
```

Current branch: `agno-workflow` (main branch: `main`)

## Testing & Observability

### Phoenix Tracing
The Agno agent system integrates with Arize Phoenix for tracing:
- Endpoint: `http://localhost:6006`
- Project name: "writer"
- Auto-instrumentation enabled
- Note: Total token usage/costs not tracked due to Agno limitations

### Agent Features
- Session history and memory persistence
- Chat history retrieval (2 runs back)
- Session search capability
- Response streaming
- Markdown output
- Debug mode available
