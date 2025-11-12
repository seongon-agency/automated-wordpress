# Multi-Client SEO Publishing System - Solution Plan

**Version**: 1.0
**Date**: 2025-11-12
**Status**: Planning Phase

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Problem Statement](#problem-statement)
3. [Solution Architecture](#solution-architecture)
4. [Database Schema](#database-schema)
5. [Agent System Design](#agent-system-design)
6. [Workflow Design](#workflow-design)
7. [Client Configuration Process](#client-configuration-process)
8. [Error Handling Strategy](#error-handling-strategy)
9. [Implementation Phases](#implementation-phases)
10. [Technical Specifications](#technical-specifications)

---

## Executive Summary

This plan outlines a **multi-client SEO publishing system** that automates the conversion of Google Docs content to WordPress posts, handling client-specific HTML styling variations through AI-powered configuration management.

**Key Innovation**: Instead of hardcoded transformation rules, an AI agent learns and applies each client's unique HTML structure, stored in a SQLite database for reuse.

**Core Capabilities**:
- Automated Google Docs → HTML → WordPress pipeline
- Image processing and WordPress media library integration
- AI-powered client HTML configuration learning
- Multi-client management with configuration persistence
- Intelligent error recovery and retry mechanisms

---

## Problem Statement

### Current Challenges

1. **Client Styling Variations**: Different WordPress configurations use different HTML structures
   - Client A: `<strong>` for bold
   - Client B: `<b>` for bold
   - Client C: Custom CSS classes on paragraphs

2. **Manual Configuration Overhead**: Each new client requires manual workflow setup

3. **Image Handling Complexity**: Images must be:
   - Extracted from Google Docs
   - Resized per client specifications
   - Uploaded to WordPress media library
   - URLs replaced in final HTML

4. **Scalability**: Hard to maintain unique workflows for dozens of clients

### Solution Goals

1. **Zero-touch publishing**: Once configured, clients publish without manual intervention
2. **AI-driven adaptation**: Agent learns HTML patterns from examples
3. **Centralized client management**: Single database for all client configurations
4. **Graceful error handling**: Intelligent recovery from API failures
5. **Easy onboarding**: Simple process to add new clients

---

## Solution Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER INTERACTION LAYER                        │
│  ┌──────────────┐              ┌──────────────┐                 │
│  │ CLI Interface│              │  Web UI      │                 │
│  │ (Quick Runs) │              │ (Agno Serve) │                 │
│  └──────────────┘              └──────────────┘                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                    AGENT ORCHESTRATION LAYER                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │            Main Orchestrator Agent                       │   │
│  │  - Client selection/validation                           │   │
│  │  - Workflow coordination                                 │   │
│  │  - Error handling & recovery                             │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Content    │  │    HTML      │  │  WordPress   │          │
│  │  Converter   │  │ Transformer  │  │  Publisher   │          │
│  │    Agent     │  │    Agent     │  │    Agent     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │        Client Configuration Agent (Specialized)          │   │
│  │  - HTML pattern analysis                                 │   │
│  │  - Configuration generation                              │   │
│  │  - Template drift detection                              │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                      DATA LAYER                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Client Database (SQLite)                                │   │
│  │  - clients table                                         │   │
│  │  - html_patterns table                                   │   │
│  │  - image_configs table                                   │   │
│  │  - publishing_history table                              │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Agent System Database (SQLite)                          │   │
│  │  - sessions, memory, metrics, evals, knowledge           │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                   EXTERNAL SERVICES                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Google Docs  │  │  WordPress   │  │   Anthropic  │          │
│  │     API      │  │   REST API   │  │   Claude API │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└──────────────────────────────────────────────────────────────────┘
```

### Component Overview

#### 1. User Interaction Layer
- **CLI Interface**: Fast execution for configured workflows
- **Web UI**: Configuration management, client setup, monitoring

#### 2. Agent Orchestration Layer
- **Main Orchestrator**: Coordinates workflow, manages client selection
- **Content Converter**: Google Docs → HTML conversion
- **HTML Transformer**: Applies client-specific HTML rules
- **WordPress Publisher**: Handles image uploads and post creation
- **Client Configuration Agent**: Learns new client configurations

#### 3. Data Layer
- **Client Database**: Stores all client-specific configurations
- **Agent System Database**: Agno framework's session/memory storage

#### 4. External Services
- Google Docs API (via published URLs)
- WordPress REST API
- Anthropic Claude API

---

## Database Schema

### Client Database: `clients.db`

#### Table: `projects`

Stores all project (client) information in a single table with JSON columns for flexible configuration.

```sql
CREATE TABLE projects (
    project_id TEXT PRIMARY KEY,          -- Unique identifier (e.g., "acme_corp")
    project_name TEXT NOT NULL,           -- Display name (e.g., "Acme Corporation")
    wordpress_url TEXT NOT NULL,          -- WordPress site URL
    wordpress_username TEXT NOT NULL,     -- WP username
    wordpress_app_password TEXT NOT NULL, -- WP application password (encrypted)
    html_configs JSON,                    -- HTML transformation rules (see example below)
    image_configs JSON,                   -- Image processing settings (see example below)
    status TEXT DEFAULT 'active',         -- active | inactive | testing
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_published_at TIMESTAMP,          -- Last successful publish
    notes TEXT                            -- Additional notes for agent
);
```

**Example `html_configs` JSON**:
```json
{
  "patterns": [
    {
      "element_type": "p",
      "source_pattern": "<p[^>]*>(.*?)</p>",
      "target_pattern": "<p class=\"article-body\" style=\"text-align: justify;\">\\1</p>"
    },
    {
      "element_type": "strong",
      "source_pattern": "<b>(.*?)</b>",
      "target_pattern": "<strong>\\1</strong>"
    },
    {
      "element_type": "h2",
      "source_pattern": "<h2[^>]*>(.*?)</h2>",
      "target_pattern": "<h2 class=\"section-header\">\\1</h2>"
    },
    {
      "element_type": "img",
      "source_pattern": "<img([^>]*src=\"[^\"]*\")([^>]*)>",
      "target_pattern": "<img\\1 class=\"wp-image aligncenter\" loading=\"lazy\"\\2>"
    }
  ]
}
```

**Example `image_configs` JSON**:
```json
{
  "target_width": 800,
  "target_height": null,
  "image_quality": 92,
  "image_format": "JPEG",
  "alignment": "center",
  "css_classes": "wp-image aligncenter",
  "additional_attributes": {
    "loading": "lazy"
  }
}
```

#### Table: `publishing_history`

Tracks all publishing activities for auditing and recovery.

```sql
CREATE TABLE publishing_history (
    publish_id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id TEXT NOT NULL,
    google_docs_url TEXT NOT NULL,
    wordpress_post_id INTEGER,            -- WP post ID if successful
    wordpress_post_url TEXT,              -- Full URL to published post
    post_title TEXT,
    post_status TEXT,                     -- draft | publish
    images_processed INTEGER DEFAULT 0,
    success BOOLEAN,
    error_message TEXT,
    execution_time_seconds REAL,
    published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients(client_id)
);
```


---

## MVP Scope (Phase 1 Focus)

### ✅ What We're Building Now

**Core Functionality**:
1. **Simple database** with `projects` table (JSON configs) and `publishing_history` table
2. **Basic workflow**: Google Docs → HTML transformation → WordPress publish
3. **Project selection**: Interactive list of projects or "no-project" option
4. **Configuration agent**: AI agent that learns HTML patterns from example HTML input
5. **Image processing**: Download, resize, upload to WordPress, replace URLs

**Key Features**:
- Store project configs in single `projects` table with JSON columns
- AI agent generates HTML transformation patterns from sample HTML
- Apply patterns to convert Google Docs HTML to client's format
- Process images and upload to WordPress media library
- Create WordPress post with transformed HTML

### ❌ What We're NOT Building Yet (Future Enhancements)

**Deferred to Later**:
- ❌ Template drift detection (manual config updates for now)
- ❌ Advanced error recovery strategies (basic retry only)
- ❌ Configuration change tracking/auditing
- ❌ Automatic pattern conflict resolution
- ❌ Web UI dashboard (CLI only for MVP)
- ❌ Batch processing multiple docs
- ❌ Scheduled publishing
- ❌ Advanced monitoring/analytics

**Rationale**: Focus on proving the core concept - AI-assisted HTML transformation for multi-project publishing. Once this works reliably, we can layer on sophistication.

---

## Agent System Design

### Agent Architecture

The system uses **AgentOS** with specialized agents coordinated by a main orchestrator.

### 1. Main Orchestrator Agent

**Name**: `SEO Publishing Orchestrator`
**Role**: Coordinate the end-to-end publishing workflow

**Responsibilities**:
- Present list of configured projects (or accept "no-project" option)
- Validate project configuration exists
- Coordinate workflow execution across specialized agents
- Report final status to user

**Tools**:
- `list_projects()` - Get all active projects from database
- `get_project_config()` - Retrieve project configuration
- `execute_publishing_workflow()` - Main workflow orchestrator

**Key Behaviors**:
- Always provides interactive project selection
- Allows "no-project" for testing scenarios
- Validates all prerequisites before starting workflow
- Logs all operations to publishing_history (basic success/failure)

### 2. Content Converter Agent

**Name**: `Content Converter`
**Role**: Convert Google Docs to clean HTML

**Responsibilities**:
- Accept published Google Docs URL
- Extract raw HTML content
- Parse and clean HTML structure
- Extract post title (H1 tag)
- Identify all images and their URLs

**Tools**:
- `google_docs_to_html()` - Convert doc to HTML
- `extract_title()` - Get H1 title
- `extract_images()` - Find all image URLs

**Key Behaviors**:
- Works only with published Google Docs URLs (`/pub` endpoint)
- Extracts only document content (not Google wrapper)
- Preserves all semantic HTML structure

### 3. HTML Transformer Agent

**Name**: `HTML Transformer`
**Role**: Apply project-specific HTML transformations

**Responsibilities**:
- Retrieve project's HTML patterns from database
- Apply transformation rules to content HTML
- Handle complex nested structures

**Tools**:
- `get_html_patterns()` - Load project patterns from DB
- `apply_html_transformations()` - Transform HTML using patterns

**Key Behaviors**:
- Applies transformations sequentially based on patterns list
- If no patterns exist, passes HTML through unchanged
- Uses regex-based pattern matching for flexibility

### 4. Image Processor Agent

**Name**: `Image Processor`
**Role**: Handle image download, resize, and WordPress upload

**Responsibilities**:
- Download images from Google Docs URLs
- Resize according to project configuration
- Upload to WordPress media library
- Return mapping of old URLs → new WordPress URLs

**Tools**:
- `download_images()` - Download from Google
- `resize_images()` - Apply project dimensions
- `upload_to_wordpress()` - Upload to WP media library
- `create_url_mapping()` - Generate old→new URL map

**Key Behaviors**:
- Processes images sequentially
- Basic retry on upload failure (1-2 attempts)
- Maintains image quality during resize
- Generates WordPress-friendly filenames

### 5. WordPress Publisher Agent

**Name**: `WordPress Publisher`
**Role**: Create/update WordPress posts

**Responsibilities**:
- Replace image URLs in HTML with WordPress URLs
- Create draft or published post via REST API
- Set post metadata (title, status)
- Return published post URL

**Tools**:
- `replace_image_urls()` - Update image URLs in HTML
- `create_wordpress_post()` - Create post via API
- `update_post_metadata()` - Set categories, tags, etc.

**Key Behaviors**:
- Always creates draft by default (safer)
- Validates credentials before publishing
- Returns full clickable post URL
- Logs all publishes to publishing_history

### 6. Project Configuration Agent (Specialized)

**Name**: `Project Configuration Specialist`
**Role**: Learn and configure new project HTML patterns

**Responsibilities**:
- Guide user through project setup process
- Analyze provided HTML template
- Extract transformation patterns automatically
- Store configuration in database

**Tools**:
- `create_new_project()` - Initialize project in DB
- `analyze_html_template()` - Extract patterns from example HTML
- `generate_transformation_rules()` - Create regex patterns
- `test_transformation()` - Validate rules work correctly

**Key Behaviors**:
- Interactive configuration flow
- Asks clarifying questions about HTML patterns
- Provides before/after preview of transformations
- Requests user confirmation before saving
- Saves html_configs and image_configs as JSON in projects table

---

## Workflow Design

### Main Publishing Workflow (MVP)

**Entry Point**: User provides Google Docs URL

```
START
  │
  ├─► [1] Project Selection
  │     │
  │     ├─► List all active projects from DB
  │     ├─► User selects project OR "no-project"
  │     ├─► Load project configuration (if selected)
  │     └─► Validate WordPress credentials
  │
  ├─► [2] Content Conversion
  │     │
  │     ├─► Convert Google Docs URL to HTML
  │     ├─► Extract post title (H1)
  │     ├─► Extract all image URLs
  │     └─► Clean and parse HTML structure
  │
  ├─► [3] Image Processing
  │     │
  │     ├─► Download all images from Google
  │     ├─► Resize per project image_config (or defaults)
  │     ├─► Upload to WordPress media library
  │     └─► Generate URL mapping (old → new)
  │
  ├─► [4] HTML Transformation
  │     │
  │     ├─► Load project HTML patterns (if project selected)
  │     ├─► Apply transformations sequentially
  │     └─► Replace image URLs with WordPress URLs
  │
  ├─► [5] WordPress Publishing
  │     │
  │     ├─► Create WordPress post (draft by default)
  │     ├─► Set post title and content
  │     ├─► Log to publishing_history
  │     └─► Return post URL
  │
  └─► [6] Completion Report
        │
        ├─► Display post URL (clickable)
        ├─► Show statistics (images processed)
        └─► Report success/failure
END
```

### Project Configuration Workflow (MVP)

**Entry Point**: User wants to add/configure a project

```
START
  │
  ├─► [1] Project Information Gathering
  │     │
  │     ├─► Ask: Project ID (e.g., "acme_corp")
  │     ├─► Ask: Project display name
  │     ├─► Ask: WordPress site URL
  │     ├─► Ask: WordPress credentials (username + app password)
  │     └─► Create entry in projects table
  │
  ├─► [2] Image Configuration
  │     │
  │     ├─► Ask: Target image width (default: 800px)
  │     ├─► Ask: Image quality (default: 92)
  │     ├─► Ask: Image alignment preference
  │     ├─► Ask: Any custom CSS classes for images
  │     └─► Prepare image_configs JSON
  │
  ├─► [3] HTML Pattern Analysis
  │     │
  │     ├─► Ask: "Paste your project's HTML template"
  │     ├─► Agent analyzes HTML structure
  │     ├─► Identify elements: p, h2, h3, strong, em, ul, ol, table, img, etc.
  │     ├─► Extract attributes and classes
  │     └─► Generate transformation patterns
  │
  ├─► [4] Pattern Review & Confirmation
  │     │
  │     ├─► Show detected patterns to user
  │     ├─► Display before/after examples
  │     ├─► Ask: "Does this look correct?"
  │     ├─► Allow manual adjustments if needed
  │     └─► Prepare html_configs JSON
  │
  ├─► [5] Save Configuration
  │     │
  │     ├─► Save html_configs JSON to projects table
  │     ├─► Save image_configs JSON to projects table
  │     ├─► Mark project as "active"
  │     └─►
  │
  └─► [6] Configuration Complete
        │
        ├─► Display success message
        ├─► Option: Test with a Google Docs URL
        └─► Return to main menu
END
```

---

## Client Configuration Process

### Adding a New Client: Step-by-Step

#### Phase 1: Basic Information
1. **Client ID**: Unique identifier (slug format: `client_name_2025`)
2. **Client Name**: Display name
3. **WordPress URL**: Full site URL
4. **Credentials**: Username + Application Password

#### Phase 2: Image Configuration
1. **Target Dimensions**: Width (and optional height)
2. **Quality**: JPEG quality 1-100
3. **Format**: JPEG/PNG/WEBP
4. **CSS Classes**: Custom classes for `<img>` tags
5. **Alignment**: left/center/right default

#### Phase 3: HTML Pattern Learning

**Agent-Driven Analysis**:

User provides sample HTML template. Agent analyzes and extracts:

1. **Paragraph patterns**:
   ```
   Detected: <p class="article-body" style="text-align: justify;">
   Rule: All <p> tags → add class="article-body", style="text-align: justify;"
   ```

2. **Heading patterns**:
   ```
   Detected: <h2 class="section-header">
   Rule: All <h2> tags → add class="section-header"
   ```

3. **Bold/Emphasis patterns**:
   ```
   Detected: <strong> (not <b>)
   Rule: Convert all <b> tags → <strong>
   ```

4. **List patterns**:
   ```
   Detected: <ul class="bullet-list">
   Rule: All <ul> tags → add class="bullet-list"
   ```

5. **Image patterns**:
   ```
   Detected: <img class="wp-image aligncenter" loading="lazy">
   Rule: All <img> tags → add class="wp-image aligncenter", loading="lazy"
   ```

#### Phase 4: Pattern Review
- Agent shows all detected patterns
- User reviews and confirms/edits
- Agent generates regex transformation rules
- Rules saved to `html_patterns` table

#### Phase 5: Test Publish
- User provides test Google Docs URL
- Full workflow executes with new config
- Preview generated HTML
- User approves → client marked "active"

### Configuration Storage Example

After configuration, database contains:

**clients table**:
```
client_id: acme_corp
client_name: Acme Corporation
wordpress_url: https://acme.com
wordpress_username: admin
wordpress_app_password: xxxx xxxx xxxx xxxx
status: active
```

**html_patterns table**:
```
1. element_type: p
   source_pattern: <p[^>]*>(.*?)</p>
   target_pattern: <p class="article-body" style="text-align: justify;">\\1</p>

2. element_type: strong
   source_pattern: <b>(.*?)</b>
   target_pattern: <strong>\\1</strong>

3. element_type: h2
   source_pattern: <h2[^>]*>(.*?)</h2>
   target_pattern: <h2 class="section-header">\\1</h2>

4. element_type: img
   source_pattern: <img([^>]*src="[^"]*")([^>]*)>
   target_pattern: <img\\1 class="wp-image aligncenter" loading="lazy"\\2>
```

**image_configs table**:
```
client_id: acme_corp
target_width: 1200
image_quality: 95
image_format: WEBP
css_classes: wp-image aligncenter
```

---

## Implementation Phases (MVP Focus)

### Phase 1: Database & Core Infrastructure (Days 1-2)

**Goals**:
- Set up simple projects database with JSON columns
- Create basic database access layer

**Deliverables**:
- `clients.db` SQLite database with 2 tables: `projects` and `publishing_history`
- `database/` module:
  - `project_manager.py` - Project CRUD operations
  - `schema.sql` - Simple database schema

**Success Criteria**:
- Can create/read/update/delete projects
- Can store html_configs and image_configs as JSON
- Can log basic publishing history

### Phase 2: Content Conversion & Image Processing (Days 3-4)

**Goals**:
- Refactor existing Google Docs converter
- Refactor existing image processor
- Create WordPress image uploader

**Deliverables**:
- `tools/google_docs_converter.py` (cleaned up)
- `tools/image_processor.py` (cleaned up)
- `tools/wordpress_uploader.py` (new)

**Success Criteria**:
- Can convert published Google Docs to HTML
- Can download and resize images
- Can upload images to WordPress media library
- Returns URL mappings for replacements

### Phase 3: HTML Transformation Engine (Days 5-6)

**Goals**:
- Build simple pattern-based HTML transformer
- Apply regex patterns from JSON config

**Deliverables**:
- `tools/html_transformer.py` - Pattern application
- `utils/pattern_engine.py` - Regex transformation logic

**Success Criteria**:
- Can load patterns from projects.html_configs JSON
- Can apply transformations sequentially
- Handles basic HTML elements (p, h2, h3, strong, img, ul, ol, table)

### Phase 4: Project Configuration Agent (Days 7-9)

**Goals**:
- Build agent to analyze HTML templates
- Generate transformation patterns from sample HTML
- Interactive configuration flow

**Deliverables**:
- `agents/configuration_agent.py` - Main configuration agent
- `tools/pattern_analyzer.py` - Extract patterns from HTML

**Success Criteria**:
- Agent can analyze pasted HTML template
- Extracts element patterns and attributes
- Saves html_configs and image_configs as JSON
- Provides preview of transformations

### Phase 5: Main Orchestrator & Workflow (Days 10-12)

**Goals**:
- Build main orchestrator agent
- Implement end-to-end publishing workflow
- Project selection interface

**Deliverables**:
- `agents/orchestrator.py` - Main orchestrator
- `workflows/publishing_workflow.py` - Complete workflow
- `main.py` - CLI entry point

**Success Criteria**:
- Can list projects and allow selection (or "no-project")
- Executes full workflow: Docs → Transform → Images → WordPress
- Logs success/failure to publishing_history
- Returns clickable WordPress post URL

### Phase 6: Testing & Polish (Days 13-14)

**Goals**:
- Test end-to-end with real Google Docs
- Test with 2-3 different project configurations
- Basic documentation

**Deliverables**:
- `README.md` - Updated with MVP instructions
- `USAGE.md` - How to configure projects and publish

**Success Criteria**:
- Successfully publishes to WordPress with correct HTML formatting
- Project configuration saves and loads correctly
- Images process and upload correctly
- Basic error messages are clear

---

## Technical Specifications

### Technology Stack

**Core Framework**:
- **Agno**: AI agent orchestration (by Anthropic)
- **Claude Sonnet 4.5**: Primary AI model

**Backend**:
- **Python 3.11+**: Programming language
- **SQLite**: Client and agent databases
- **FastAPI**: Web framework (via Agno)

**Libraries**:
- **BeautifulSoup4**: HTML parsing and manipulation
- **Pillow**: Image processing and resizing
- **requests**: HTTP client for APIs
- **google-api-python-client**: Google Docs API
- **python-dotenv**: Environment management
- **pydantic**: Data validation

**External APIs**:
- **WordPress REST API**: Post creation, media upload
- **Google Docs Published API**: Document access
- **Anthropic API**: Claude model access

### Environment Variables

```env
# Anthropic API
ANTHROPIC_API_KEY=sk-ant-...

# Database
CLIENT_DB_PATH=./clients.db
AGENT_DB_PATH=./seo_agent.db

# Default WordPress (override per client)
DEFAULT_WP_USERNAME=admin
DEFAULT_WP_APP_PASSWORD=xxxx xxxx xxxx xxxx

# Image Processing Defaults
DEFAULT_IMAGE_WIDTH=800
DEFAULT_IMAGE_QUALITY=92
DEFAULT_IMAGE_FORMAT=JPEG

# Application Settings
DEBUG_MODE=false
LOG_LEVEL=INFO
MAX_RETRIES=3
RETRY_BACKOFF_SECONDS=2
```

### File Structure (MVP)

```
/Users/haxuanbach/VSCode/
│
├── agno_agent_seo_posting/
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── orchestrator.py         # Main orchestrator agent
│   │   └── configuration_agent.py  # Project configuration agent
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── google_docs_converter.py  # Google Docs → HTML
│   │   ├── image_processor.py        # Image download/resize
│   │   ├── html_transformer.py       # Pattern-based transformation
│   │   ├── wordpress_uploader.py     # WP media & post upload
│   │   └── pattern_analyzer.py       # HTML pattern extraction
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── project_manager.py      # Project CRUD operations
│   │   └── schema.sql              # Database schema (2 tables)
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── pattern_engine.py       # Core transformation logic
│   │   └── html_extractor.py       # Extract title, images, etc.
│   │
│   ├── workflows/
│   │   ├── __init__.py
│   │   └── publishing_workflow.py  # Main publishing workflow
│   │
│   ├── main.py                     # CLI entry point
│   ├── config.py                   # Configuration management
│   ├── requirements.txt
│   └── .env
│
├── clients.db                      # Project database (2 tables)
├── seo_agent.db                    # Agent system database (Agno)
├── SOLUTION_PLAN.md                # This document
├── CLAUDE.md                       # Claude Code guidance
└── README.md                       # Project documentation
```

### API Design (MVP)

#### Database API

```python
# Project Management
def create_project(project_id, project_name, wordpress_url, username, password, html_configs, image_configs) -> Project
def get_project(project_id) -> Project
def update_project(project_id, **kwargs) -> Project
def delete_project(project_id) -> bool
def list_projects(status='active') -> List[Project]

# History Tracking
def log_publish(project_id, google_docs_url, success, **kwargs) -> PublishRecord
def get_publish_history(project_id, limit=10) -> List[PublishRecord]
```

#### Agent Tools API

```python
# Main Orchestrator Tools
def list_projects() -> List[Dict]
def get_project_config(project_id: str) -> Dict
def execute_publishing_workflow(google_docs_url: str, project_id: Optional[str]) -> Dict

# Content Converter Tools
def google_docs_to_html(url: str) -> Dict[str, Any]
def extract_title(html: str) -> str
def extract_images(html: str) -> List[str]

# HTML Transformer Tools
def apply_html_transformations(html: str, patterns: List[Dict]) -> str

# Image Processor Tools
def download_images(image_urls: List[str]) -> List[Path]
def resize_images(image_paths: List[Path], config: Dict) -> List[Path]
def upload_to_wordpress(images: List[Path], wp_url: str, credentials: Dict) -> Dict[str, str]

# WordPress Publisher Tools
def replace_image_urls(html: str, url_mapping: Dict) -> str
def create_wordpress_post(title: str, content: str, wp_url: str, credentials: Dict) -> Dict

# Configuration Agent Tools
def analyze_html_template(html: str) -> Dict  # Returns html_configs JSON
def create_image_config(width: int, quality: int, ...) -> Dict  # Returns image_configs JSON
```

### CLI Interface Design (MVP)

```bash
# Main entry point - interactive
python main.py

# The agent will:
# 1. Ask: "Configure new project or publish?"
# 2. If publish:
#    - Show list of projects (or "no-project")
#    - Ask for Google Docs URL
#    - Execute workflow
# 3. If configure:
#    - Run configuration workflow
#    - Save to database
```

---

## Success Metrics (MVP)

### MVP Completion Checklist
- [ ] Database: Projects table with JSON columns created
- [ ] Configuration: Can configure a new project via agent
- [ ] Agent extracts HTML patterns from sample HTML correctly
- [ ] Patterns saved as JSON to projects.html_configs
- [ ] Image configs saved as JSON to projects.image_configs
- [ ] Publishing: Full workflow executes end-to-end
- [ ] Google Docs → HTML conversion works
- [ ] Images download, resize, and upload to WordPress
- [ ] HTML transformations apply correctly based on patterns
- [ ] WordPress post created with clickable URL returned
- [ ] History logged to publishing_history table
- [ ] Can run with "no-project" option (skip transformations)
- [ ] Successfully published 2-3 test posts with different project configs
- [ ] Basic error messages are clear and actionable

---

## Open Questions & Future Enhancements

### Open Questions (To Resolve During Implementation)

1. **Credential Security**:
   - How to encrypt WordPress passwords in database?
   - Use `cryptography` library with master key?

2. **Pattern Conflicts**:
   - What if multiple patterns match the same element?
   - Priority system sufficient or need more sophisticated logic?

3. **Large Documents**:
   - How to handle very long Google Docs (100+ pages)?
   - Should we paginate or process in chunks?

4. **Rate Limiting**:
   - Do we need to throttle WordPress API calls?
   - Should implement exponential backoff globally?

5. **Multi-user Support**:
   - In future, should multiple users be able to manage clients?
   - Need user authentication system?

### Future Enhancements (Post-MVP)

1. **Scheduled Publishing**:
   - Queue posts for future publication
   - Cron job integration

2. **Batch Processing**:
   - Process multiple Google Docs in one run
   - Bulk import from Google Drive folder

3. **Template Library**:
   - Pre-built configurations for common WordPress themes
   - Community-contributed patterns

4. **Advanced Image Features**:
   - Automatic image optimization (compression)
   - CDN integration
   - Alt text generation via AI

5. **Analytics Dashboard**:
   - Publishing statistics per client
   - Success rate trends
   - Performance metrics

6. **WordPress Plugin**:
   - Companion plugin for easier integration
   - Custom API endpoints for better performance

7. **Multi-Platform Support**:
   - Publish to Medium, Substack, Ghost, etc.
   - Unified content distribution

8. **SEO Enhancements**:
   - Automatic meta description generation
   - Keyword optimization suggestions
   - Internal linking recommendations

---

## Conclusion

This solution plan provides a focused **MVP blueprint** for building a **multi-project SEO publishing system** that solves the core problem: **automated Google Docs → WordPress publishing with project-specific HTML transformations**.

**Key Features (MVP)**:
1. **Simple database**: Single `projects` table with JSON columns for configs
2. **AI-powered configuration**: Agent learns HTML patterns from sample HTML
3. **Flexible workflow**: Works with or without project configuration
4. **Image processing**: Automatic download, resize, and WordPress upload
5. **Pattern-based transformation**: Regex-based HTML transformation engine

**What Makes This Work**:
- **JSON storage** for configs = simple, flexible, easy to inspect
- **Agent-driven** pattern extraction = no manual regex writing
- **Modular architecture** = easy to extend later
- **Focus on core value** = prove concept before adding bells and whistles

**Implementation Timeline**:
- **~2 weeks** for MVP (6 phases)
- Can start testing with real projects after Phase 5 (Day 12)

**Next Steps**:
1. ✅ Review and approve this simplified plan
2. Begin Phase 1: Database setup (Days 1-2)
3. Build iteratively, testing at each phase

**Deferred to Later** (not blocking MVP):
- Template drift detection
- Advanced error recovery
- Configuration change tracking
- Web UI dashboard
- Batch processing
- Analytics

---

**Document Status**: ✅ MVP-Focused - Ready for Implementation
**Last Updated**: 2025-11-12
**Version**: 2.0 (Simplified)
