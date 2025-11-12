# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains an **SEO Blog Publishing System** built with the [Agno framework](https://docs.agno.com/) (Anthropic's AI agent framework). The system automates the conversion of Google Docs content into SEO-optimized HTML and publishes to WordPress.

The main application is in `agno_agent_seo_posting/` directory.

## Core Architecture

### Agent System (AgentOS)

The system uses **Agno's AgentOS** architecture with specialized agents:

1. **SEO Blog Publisher** (Primary Agent) - Orchestrates the complete workflow using a single tool
2. **Content Converter** - Converts Google Docs to HTML
3. **HTML Formatter** - Applies template formatting
4. **WordPress Publisher** - Publishes content to WordPress

### Workflow Pattern

The system implements a **single-tool orchestration pattern** to solve Claude's natural tendency to stop after 3-5 tool calls. Instead of chaining multiple tools, the agent calls one orchestrator tool (`execute_complete_seo_workflow`) that internally executes all 6 steps:

1. Convert content Google Docs → HTML
2. Convert template Google Docs → HTML
3. Extract title from content (h1 tag)
4. Process, resize, and upload images to WordPress
5. Apply template formatting to content
6. Publish post to WordPress

This workflow is implemented in `tools/workflow_orchestrator.py`.

### Dynamic HTML Formatting System (v4.0)

The system uses a **truly dynamic pattern extraction** approach:
- **Zero hardcoding** - works with ANY HTML template (Google Docs, Bootstrap, custom CSS)
- **Automatic detection** - discovers all element types and patterns in template
- **Intelligent matching** - context-aware heuristics for pattern selection
- Template parsing in `utils/template_parser.py`
- HTML transformation in `tools/html_formatter.py`

### Tool Organization

Tools are categorized in `tools/__init__.py`:
- **CONVERSION_TOOLS**: `google_docs_to_html`
- **PROCESSING_TOOLS**: `process_images`
- **FORMATTING_TOOLS**: `format_html_with_template`
- **PUBLISHING_TOOLS**: `publish_to_wordpress`
- **ORCHESTRATION_TOOLS**: `execute_complete_seo_workflow`

## Running the Application

### Start the SEO Publishing System

```bash
cd agno_agent_seo_posting
python seo_agents.py
```

Or using Agno CLI:
```bash
agno serve seo_agents:app --reload
```

### Run Workflow-Based System

For the workflow-based approach (alternative implementation):
```bash
cd agno_agent_seo_posting
python agno_workflow.py
```

### Run Content Team System

For the content creation team (outline + writer agents):
```bash
cd agno_agent_seo_posting
python agents.py
```

### Testing Components

Test individual tools:
```bash
cd agno_agent_seo_posting
python test.py  # Tests Google Docs converter
```

## Environment Setup

### Required Environment Variables

Create `.env` file in `agno_agent_seo_posting/`:

```env
# Required
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# WordPress Publishing (required for publishing)
WP_BASE_URL=https://your-wordpress-site.com
WP_USERNAME=your_wordpress_username
WP_APP_PASS=your_wordpress_app_password

# Optional
DEFAULT_IMAGE_WIDTH=800
IMAGE_QUALITY=92
IMAGE_FORMAT=JPEG
```

### Dependencies

Install from root or from `agno_agent_seo_posting/`:
```bash
pip install -r requirements.txt
```

Main dependencies:
- `agno` - Anthropic's AI agent framework
- `anthropic` - Anthropic API client
- `beautifulsoup4` - HTML parsing
- `Pillow` - Image processing
- `requests` - HTTP requests
- `google-api-python-client`, `google-auth` - Google Docs API
- `fastapi` - Web framework (for Agno)
- `python-dotenv` - Environment variable management

## Database

The system uses **SQLite** for persistence:
- Database file: `seo_agent.db`
- Tables: sessions, memory, metrics, evals, knowledge
- Configured in `seo_agents.py` using `agno.db.sqlite.SqliteDb`

## Key Implementation Details

### Google Docs Input

- Documents must be **published to web** (not just shared)
- URLs should end with `/pub`
- Example: `https://docs.google.com/document/d/e/2PACX-xxx/pub`
- No OAuth required - published docs are publicly accessible

### Image Processing

- Images downloaded from Google Docs
- Resized to target width (default: 800px)
- Uploaded to WordPress media library BEFORE post creation
- Image URLs in HTML updated with WordPress media URLs

### Template System

Templates define formatting rules by example:
- Create a Google Doc with formatted examples of each element
- System extracts patterns (paragraph styles, heading formats, image classes)
- Applies patterns to content automatically
- Supports: paragraphs, headings, lists, tables, links, images

### WordPress Publishing

- Uses WordPress REST API
- Requires application password (not regular password)
- Images uploaded first, then referenced in post
- Posts created as drafts by default
- Returns clickable post URL

## Version History

**v4.0.0** - Revolutionary dynamic HTML formatting (current)
- Complete rewrite to truly dynamic pattern extraction
- Works with any HTML template without code changes

**v3.1.0** - Template attribute consistency
- Fixed template attributes applied to all tag types
- Simplified attribute preservation logic

**v3.0.0** - Workflow orchestrator architecture
- Created single orchestrator tool to solve "stops after 3 tools" problem
- Agent calls one tool that runs all 6 steps internally

## Important Notes

- The system is designed for **automated pipeline execution** - agents don't wait for user confirmation between steps
- The workflow orchestrator ensures reliable end-to-end execution
- Session history and memory are enabled for context tracking
- Model used: **Claude Sonnet 4.5** (`claude-sonnet-4-5-20250929`)
