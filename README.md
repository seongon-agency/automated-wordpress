# automated-wordpress
AI Agent for automated WordPress publishing from Google Docs.

## 🚀 Quick Start

### Option 1: AI Agent (Recommended)
```bash
cd agno
pip install -r requirements.txt
python agents.py
```
Then open http://localhost:7777 and chat with the agent to publish docs.

### Option 2: Simple Script
```bash
pip install -r requirements.txt
python simple_publish.py https://docs.google.com/document/d/YOUR_DOC_ID/edit
```

## What This Does

Takes a Google Docs URL → Publishes to WordPress automatically:
- Extracts content and images from Google Docs
- Processes and uploads images to WordPress
- Transforms HTML for WordPress compatibility
- Creates WordPress post (as draft by default)

## Files

- `agno/agents.py` - AI agent that publishes to WordPress
- `agno/wordpress_tools.py` - WordPress publishing functions
- `functions.py` - Core utility functions (Google Docs, image processing, HTML transformation)
- `simple_publish.py` - Standalone script (no AI needed)
- `notebook.ipynb` - Original manual workflow (20 steps)
