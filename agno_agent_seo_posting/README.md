# SEO Publishing System - MVP v1.0

**Automated Google Docs → WordPress Publishing with AI-Powered Project Configuration**

Transform your SEO content workflow with intelligent HTML transformation and multi-project management.

---

## 🎯 What It Does

This system automates the entire pipeline from Google Docs to WordPress:

1. **Converts** Google Docs to clean HTML
2. **Processes** images (download, resize, upload to WordPress)
3. **Transforms** HTML to match client-specific formats (AI-powered)
4. **Publishes** to WordPress as a draft post

### Key Innovation: AI-Powered Configuration

Instead of manually coding HTML transformations for each client, an AI agent analyzes sample HTML and automatically generates transformation patterns. Configure once, publish many times!

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- WordPress site with REST API enabled
- WordPress application password
- **Google Cloud Project with Drive API enabled**
- **Google OAuth credentials (client_secret.json)**

### Installation

```bash
cd agno_agent_seo_posting
pip install -r requirements.txt
```

### Google API Setup

1. **Create Google Cloud Project**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create new project or select existing one
   - Enable **Google Drive API**

2. **Create OAuth Credentials**:
   - Go to **APIs & Services → Credentials**
   - Click **Create Credentials → OAuth client ID**
   - Application type: **Desktop app**
   - Download JSON file
   - Rename to `client_secret.json`
   - Place in `agno_agent_seo_posting/` directory

### Environment Configuration

Create `.env` file:

```env
# Required: Anthropic API (for AI agents)
ANTHROPIC_API_KEY=sk-ant-...

# Optional: Google OAuth (defaults to client_secret.json in current dir)
GOOGLE_CLIENT_SECRETS=./client_secret.json

# Optional: Default WordPress credentials
WP_BASE_URL=https://your-wordpress-site.com
WP_USERNAME=your_username
WP_APP_PASS=xxxx xxxx xxxx xxxx

# Optional: Database path
CLIENT_DB_PATH=./clients.db
```

### Run the System

```bash
python3 main.py
```

---

## 📖 Usage Guide

### First Time Setup

1. **Run the application**:
   ```bash
   python3 main.py
   ```

2. **Configure a project** (Option 2):
   - Provide project details (ID, name, WordPress credentials)
   - Configure image settings (width, quality, format)
   - Paste sample HTML from your desired output format
   - AI agent analyzes and generates transformation patterns
   - Review and confirm configuration

3. **Publish content** (Option 1):
   - Select configured project (or "no-project")
   - Provide Google Docs URL (must be published)
   - System automatically processes and publishes

### Publishing Google Docs

**First Time Setup**: On first run, the system will:
1. Open your browser for Google authentication
2. Ask you to grant access to Google Drive
3. Save credentials to `token.json` for future use

**Publishing Process**:
1. Use any Google Docs URL (edit or view URL works)
2. The system uses Google Drive API to export as HTML
3. No need to publish the document publicly!

### Project Configuration

The AI agent will guide you through:

1. **Basic Info**: Project ID, name, WordPress URL, credentials
2. **Image Settings**: Target width, quality, format, CSS classes
3. **HTML Analysis**: Paste sample HTML → AI extracts patterns
4. **Review**: Confirm before saving

#### Example HTML Analysis

You paste this sample:
```html
<p class="article-body" style="text-align: justify;">This is a paragraph.</p>
<h2 class="section-header">Heading</h2>
<strong>Bold text</strong>
```

AI generates:
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
    },
    {
      "element_type": "strong",
      "source_pattern": "<b>(.*?)</b>",
      "target_pattern": "<strong>\\1</strong>"
    }
  ]
}
```

---

## 🏗️ Architecture

### Components

```
agno_agent_seo_posting/
├── database/           # SQLite with JSON configs
│   ├── schema.sql
│   └── project_manager.py
├── tools/              # Core functionality
│   ├── google_docs_converter.py
│   ├── image_processor.py
│   ├── html_transformer.py
│   ├── wordpress_uploader.py
│   └── pattern_analyzer.py
├── agents/             # AI agents
│   ├── orchestrator.py         # Main coordinator
│   └── configuration_agent.py  # Project setup
├── workflows/          # End-to-end workflows
│   └── publishing_workflow.py
├── utils/              # Helper functions
│   ├── pattern_engine.py
│   └── html_extractor.py
└── main.py             # Entry point
```

### Database Schema

**`projects` table**: Stores all project configurations
- `project_id`: Unique identifier
- `html_configs`: JSON with transformation patterns
- `image_configs`: JSON with image settings
- WordPress credentials and metadata

**`publishing_history` table**: Tracks all publishes
- Records success/failure
- Stores execution time
- Links to WordPress post

### Workflow

```
Google Docs URL
    ↓
Convert to HTML
    ↓
Extract title & images
    ↓
Download & resize images
    ↓
Upload images to WordPress
    ↓
Apply HTML transformations (project-specific)
    ↓
Replace image URLs with WordPress URLs
    ↓
Create WordPress post (draft)
    ↓
Log to history
    ↓
Return post URL
```

---

## 🔧 Advanced Usage

### No-Project Mode

Publish without transformations:
- Select "No project" when prompted
- Uses default image settings
- Skips HTML transformations
- Still uploads images and creates post

### Managing Projects

```python
from database import list_projects, get_project, update_project

# List all projects
projects = list_projects(status='active')

# Get specific project
project = get_project('acme_corp')

# Update configuration
update_project('acme_corp', wordpress_url='https://new-url.com')
```

### Direct Workflow Execution

```python
from workflows import execute_publishing_workflow

result = execute_publishing_workflow(
    google_docs_url="https://docs.google.com/document/d/e/2PACX-xxx/pub",
    project_id="acme_corp"
)

if result['success']:
    print(f"Published: {result['post_url']}")
```

---

## 🧪 Testing

### Test Database

```bash
python3 test_database.py
```

Tests:
- ✅ Database initialization
- ✅ Project CRUD operations
- ✅ JSON config storage
- ✅ Publishing history logging

### Manual Testing Checklist

- [ ] Configure a project
- [ ] Publish Google Doc with images
- [ ] Verify HTML transformations applied
- [ ] Check WordPress post created
- [ ] Confirm images uploaded correctly
- [ ] Review publishing history

---

## 🐛 Troubleshooting

### "ANTHROPIC_API_KEY not found"
- Ensure `.env` file exists with your API key

### "WordPress credentials not configured"
- Either configure project with credentials
- Or set WP_BASE_URL, WP_USERNAME, WP_APP_PASS in `.env`

### "Failed to convert Google Docs"
- Verify document is published to web (File → Share → Publish to web)
- URL must end with `/pub`

### Images Not Processing
- Check image URLs are accessible
- Verify sufficient disk space
- Check `raw_images/` and `resized_images/` directories exist

### WordPress Authentication Failed
- Verify WordPress REST API is enabled
- Use **Application Password**, not regular password
- Go to WordPress → Users → Profile → Application Passwords

---

## 📝 Development

### Adding New HTML Patterns

Projects can be reconfigured anytime:

1. Run configuration wizard again
2. Provide new sample HTML
3. AI agent updates patterns
4. Old configuration is replaced

### Extending the System

Easy extension points:
- Add new tools in `tools/`
- Create specialized agents in `agents/`
- Add workflow steps in `workflows/`

---

## 🎓 Examples

### Example 1: Simple Blog Post

**Google Docs Content**:
- Title: "10 Tips for SEO"
- 3 images
- Paragraphs and headings

**Result**:
- HTML transformed to match project style
- Images resized to 800px, uploaded
- Draft post created with clickable URL

### Example 2: Multi-Client Publishing

**Scenario**: You manage 5 different client WordPress sites

**Solution**:
1. Configure 5 projects (one per client)
2. Each project has unique HTML patterns
3. Publish to any client by selecting their project
4. HTML automatically adapts to client's format

---

## 📊 Success Metrics

MVP completion criteria:
- ✅ Database with JSON configs
- ✅ AI agent extracts HTML patterns
- ✅ End-to-end publishing workflow
- ✅ Image processing and upload
- ✅ HTML transformations apply correctly
- ✅ WordPress post creation
- ✅ Publishing history logging

---

## 🔮 Future Enhancements

Deferred to post-MVP:
- Template drift detection
- Advanced error recovery
- Web UI dashboard
- Batch processing
- Scheduled publishing
- Analytics and reporting

---

## 📄 License

This is a custom implementation for internal use.

---

## 👥 Support

For issues or questions:
1. Check troubleshooting section
2. Review SOLUTION_PLAN.md for architecture details
3. Check CLAUDE.md for development guidance

---

**Built with**:
- [Agno Framework](https://docs.agno.com/) - AI agent orchestration
- Claude Sonnet 4.5 - AI model
- SQLite - Data persistence
- Beautiful Soup - HTML parsing
- Pillow - Image processing

---

**Version**: MVP 1.0
**Last Updated**: 2025-11-12
