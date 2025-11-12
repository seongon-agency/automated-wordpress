# Project Structure - SEO Publishing System

**Clean, organized codebase structure after refactoring**

---

## 📂 Directory Tree

```
agno_agent_seo_posting/
│
├── main.py                              # ⭐ Main entry point
├── simple_configuration.py              # ⭐ Configuration wizard
│
├── database/                            # 🗄️ Database layer
│   ├── __init__.py
│   ├── schema.sql
│   └── project_manager.py
│
├── workflows/                           # 🔄 Business logic
│   ├── __init__.py
│   └── publishing_workflow.py
│
├── tools/                               # 🛠️ Core functionality
│   ├── __init__.py
│   ├── google_docs_converter.py
│   ├── image_processor.py
│   ├── html_transformer.py
│   └── wordpress_uploader.py
│
├── utils/                               # 🧰 Helper functions
│   ├── __init__.py
│   ├── html_extractor.py
│   └── pattern_engine.py
│
├── tests/                               # 🧪 Test files
│   ├── test_database.py
│   ├── test_full_workflow.py
│   ├── test_google_docs.py
│   ├── test_html_cleaning.py
│   ├── test_html_cleaning_advanced.py
│   ├── test_image_download.py
│   └── test_wordpress_upload.py
│
├── archived/                            # 📦 Old/unused files
│   ├── agents.py
│   ├── agno_workflow.py
│   ├── configuration_agent.py
│   ├── functions_agent.py
│   ├── functions_workflow.py
│   ├── orchestrator.py
│   └── pattern_analyzer.py
│
├── docs/                                # 📖 Documentation
│   ├── README.md
│   ├── QUICKSTART.md
│   ├── USAGE.md
│   ├── CURRENT_STATE.md
│   ├── PROJECT_STRUCTURE.md
│   ├── FIXES_APPLIED.md
│   ├── CONFIGURATION_FIX.md
│   ├── CONFIGURATION_GUIDE.md
│   ├── AGENT_REMOVAL.md
│   └── IMPLEMENTATION_SUMMARY.md
│
├── config/                              # ⚙️ Configuration (unused currently)
│   ├── __init__.py
│   └── settings.py
│
├── .env                                 # Environment variables
├── requirements.txt                     # Python dependencies
├── client_secret.json                   # Google OAuth
├── token.json                           # Google OAuth token
│
├── seo_agent.db                         # SQLite database
├── raw_images/                          # Downloaded images (temp)
└── resized_images/                      # Processed images (temp)
```

---

## 📄 File Descriptions

### ⭐ Entry Points

#### `main.py` (Main Application)
**Purpose**: Interactive CLI with 4 menu options
- Option 1: Publish Google Docs to WordPress
- Option 2: Configure New Project
- Option 3: List All Projects
- Option 4: Exit

**Key Functions**:
- `main()` - Main loop
- `display_menu()` - Show options
- `list_all_projects()` - Show configured projects

**Dependencies**: workflows, database, simple_configuration

---

#### `simple_configuration.py` (Configuration Wizard)
**Purpose**: CLI wizard to create/configure projects

**Key Functions**:
- `run_simple_configuration()` - Main wizard flow
- `analyze_html_sample_with_ai()` - AI-powered HTML analysis
- `analyze_html_sample_simple()` - Fallback BeautifulSoup analysis

**Workflow**:
1. Gather basic info (project ID, WordPress creds)
2. Configure images (width, quality, format)
3. Analyze HTML sample (AI or simple)
4. Review configuration
5. Save to database

**Can be run standalone**: `python3 simple_configuration.py`

---

### 🗄️ Database Layer

#### `database/schema.sql`
**Purpose**: Database schema definition

**Tables**:
- `projects` - Project configurations (with JSON columns)
- `publishing_history` - Logging all publish attempts

---

#### `database/project_manager.py`
**Purpose**: Database operations (CRUD)

**Key Functions**:
- `init_database()` - Initialize tables
- `create_project()` - Create new project
- `get_project()` - Retrieve project by ID
- `update_project()` - Update project
- `list_projects()` - List all projects
- `log_publish()` - Log publishing attempt

**Note**: Handles JSON serialization/deserialization for configs

---

### 🔄 Workflows

#### `workflows/publishing_workflow.py`
**Purpose**: Complete end-to-end publishing workflow

**Main Function**: `execute_publishing_workflow(google_docs_url, project_id)`

**6 Steps**:
1. Convert Google Docs to HTML
2. Extract title and clean HTML (universal)
3. Process images (download & resize)
4. Upload images to WordPress
5. Apply HTML transformations (project-specific)
6. Create WordPress post

**Returns**: Dict with success status, post URL, execution time, etc.

---

### 🛠️ Tools

#### `tools/google_docs_converter.py`
**Purpose**: Google Docs → HTML conversion

**Key Functions**:
- `google_docs_to_html()` - Main conversion function
- `get_credentials()` - OAuth authentication
- `extract_file_id()` - Extract file ID from various URL formats

**Uses**: Google Drive API (not web scraping)

---

#### `tools/image_processor.py`
**Purpose**: Image download, resize, preparation

**Key Functions**:
- `extract_image_urls()` - Find all images in HTML
- `download_images()` - Download from URLs (uses urllib)
- `resize_images()` - Resize to target dimensions
- `process_images_from_html()` - Complete pipeline

**Directories**: `raw_images/`, `resized_images/`

---

#### `tools/html_transformer.py`
**Purpose**: Apply HTML transformation patterns

**Key Functions**:
- `transform_html()` - Apply patterns to HTML
- `transform_html_with_config()` - Transform with specific config

**Uses**: `utils/pattern_engine.py` for regex operations

---

#### `tools/wordpress_uploader.py`
**Purpose**: WordPress media upload and post creation

**Key Functions**:
- `upload_image_to_wordpress()` - Upload single image (binary)
- `upload_images_batch()` - Upload multiple images
- `create_wordpress_post()` - Create draft post
- `replace_image_urls_in_html()` - Update URLs after upload

**Authentication**: WordPress application passwords

---

### 🧰 Utilities

#### `utils/html_extractor.py`
**Purpose**: Extract elements and clean HTML

**Key Functions**:
- `extract_title_from_html()` - Get H1 as title
- `extract_images_from_html()` - Get image URLs
- `remove_content_before_h1()` - Universal cleaning
- `clean_html_for_wordpress()` - All universal cleaning

**Note**: Universal cleaning applies to ALL projects

---

#### `utils/pattern_engine.py`
**Purpose**: Regex pattern matching and transformation

**Key Functions**:
- `apply_pattern()` - Apply single regex pattern
- `transform_html_with_config()` - Apply all patterns from config

**Used by**: `tools/html_transformer.py`

---

### 🧪 Tests

#### `test_database.py`
Tests database operations (CRUD, JSON handling)

#### `test_full_workflow.py`
End-to-end test of complete publishing flow

#### `test_google_docs.py`
Test Google Docs HTML extraction

#### `test_html_cleaning.py`
Test universal HTML cleaning (basic)

#### `test_html_cleaning_advanced.py`
Test HTML cleaning with nested structures

#### `test_image_download.py`
Test image download from Google Docs

#### `test_wordpress_upload.py`
Test WordPress media upload

---

### 📦 Archived Files

**Why archived**: These files were causing httpx errors or are no longer used

#### `archived/configuration_agent.py`
Old streaming agent for configuration (broke with httpx errors)

#### `archived/orchestrator.py`
Old agent for orchestrating workflow (broke with httpx errors)

#### `archived/functions_workflow.py`
Original working code (kept as reference)

#### `archived/agents.py`
Old agent definitions

#### `archived/agno_workflow.py`
Old Agno workflow implementation

#### `archived/functions_agent.py`
Old function-based agent

#### `archived/pattern_analyzer.py`
Old pattern analysis tool (now uses direct AI calls)

**Note**: These can be safely deleted or kept for reference

---

### 📖 Documentation

#### `README.md`
Main project documentation, setup instructions

#### `QUICKSTART.md`
5-minute quick start guide

#### `USAGE.md`
Detailed usage instructions

#### `CURRENT_STATE.md`
Current development status (this session's work)

#### `PROJECT_STRUCTURE.md`
This file - codebase organization

#### `FIXES_APPLIED.md`
All bugs fixed and how

#### `CONFIGURATION_FIX.md`
Configuration wizard fix documentation

#### `CONFIGURATION_GUIDE.md`
How to use configuration wizard

#### `AGENT_REMOVAL.md`
Why agents were removed and replacements

#### `IMPLEMENTATION_SUMMARY.md`
Original MVP implementation plan

---

## 🔄 Data Flow

### Publishing Flow:
```
main.py (Option 1)
    ↓
workflows/publishing_workflow.py
    ↓
    ├─→ tools/google_docs_converter.py (Google Docs → HTML)
    ├─→ utils/html_extractor.py (Extract title, clean HTML)
    ├─→ tools/image_processor.py (Download, resize images)
    ├─→ tools/wordpress_uploader.py (Upload images)
    ├─→ tools/html_transformer.py (Apply patterns)
    │       └─→ utils/pattern_engine.py (Regex operations)
    └─→ tools/wordpress_uploader.py (Create post)
    ↓
database/project_manager.py (Log to history)
```

### Configuration Flow:
```
main.py (Option 2)
    ↓
simple_configuration.py
    ↓
    ├─→ AI Analysis (one-shot Anthropic API)
    │   └─→ Generate transformation patterns
    ↓
database/project_manager.py (Save project)
```

---

## 🎯 Module Dependencies

### No External Dependencies (Self-contained):
- `utils/html_extractor.py`
- `utils/pattern_engine.py`

### Tool Dependencies:
- `google_docs_converter.py` → Google Drive API, OAuth
- `image_processor.py` → PIL, urllib, requests
- `html_transformer.py` → utils/pattern_engine
- `wordpress_uploader.py` → requests, base64

### Workflow Dependencies:
- `publishing_workflow.py` → all tools + utils + database

### Main Dependencies:
- `main.py` → workflows + database + simple_configuration
- `simple_configuration.py` → database + anthropic (optional)

---

## 📦 Python Package Dependencies

```
# Core
agno                    # Agent framework (not currently used)
anthropic               # Claude API (for HTML analysis)
python-dotenv           # Environment variables

# Google APIs
google-auth
google-auth-oauthlib
google-api-python-client

# Data Processing
beautifulsoup4          # HTML parsing
Pillow                  # Image processing
pandas                  # Data manipulation (optional)

# HTTP & Web
requests                # HTTP requests
fastapi[standard]       # Web framework (optional, not used)

# Other
gspread                 # Google Sheets (optional, not used)
pydantic                # Data validation (optional)
```

---

## 🗄️ Database Tables

### `projects`
```
project_id              TEXT PRIMARY KEY
project_name            TEXT NOT NULL
wordpress_url           TEXT NOT NULL
wordpress_username      TEXT NOT NULL
wordpress_app_password  TEXT NOT NULL
html_configs            TEXT (JSON)
image_configs           TEXT (JSON)
status                  TEXT DEFAULT 'active'
created_at              TIMESTAMP
updated_at              TIMESTAMP
last_published_at       TIMESTAMP
notes                   TEXT
```

### `publishing_history`
```
id                      INTEGER PRIMARY KEY
google_docs_url         TEXT NOT NULL
success                 BOOLEAN
project_id              TEXT
wordpress_post_id       INTEGER
wordpress_post_url      TEXT
post_title              TEXT
post_status             TEXT
images_processed        INTEGER
error_message           TEXT
execution_time_seconds  REAL
published_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

---

## 🎯 Key Design Patterns

### 1. Separation of Concerns
- **Tools** = Individual operations
- **Workflows** = Orchestrate tools
- **Utils** = Pure functions, no side effects

### 2. Database Abstraction
All database operations go through `database/project_manager.py`

### 3. Error Handling
Functions return dicts with `success` boolean and error messages

### 4. Configuration as Data
HTML patterns stored as JSON, not code

### 5. Two-Phase Transformation
- Universal cleaning (all projects)
- Project-specific patterns (per client)

---

## 🚀 Running the Application

### Interactive Mode:
```bash
python3 main.py
```

### Standalone Configuration:
```bash
python3 simple_configuration.py
```

### Tests:
```bash
python3 test_full_workflow.py
python3 test_database.py
```

---

**This structure provides**:
- Clear separation of concerns
- Easy testing (isolated modules)
- Simple debugging (clear data flow)
- Easy maintenance (organized files)
