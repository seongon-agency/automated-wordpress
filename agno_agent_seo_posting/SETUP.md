# Setup Guide - WordPress SEO Publishing System

Complete step-by-step installation and configuration guide.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [WordPress Setup](#wordpress-setup)
5. [Google Drive API Setup (Optional)](#google-drive-api-setup-optional)
6. [First Run](#first-run)
7. [Verification](#verification)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

- **Python 3.11 or higher**
  - Check: `python --version`
  - Download: https://www.python.org/downloads/

- **pip** (Python package manager)
  - Included with Python 3.11+
  - Check: `pip --version`

- **Git** (for cloning repository)
  - Check: `git --version`
  - Download: https://git-scm.com/downloads

### Required Accounts & Credentials

1. **Anthropic API Account**
   - Sign up: https://console.anthropic.com/
   - Get API key from dashboard
   - Required for AI features (pattern generation, natural language editing)

2. **WordPress Site**
   - WordPress 5.0+ with REST API enabled (default)
   - Admin access to generate Application Password
   - HTTPS recommended

3. **Google Cloud Account** (Optional, for Google Docs API)
   - Only needed if using Google Drive API for Docs conversion
   - Alternative: Use published Google Docs URLs (no API needed)

---

## Installation

### Step 1: Clone Repository

```bash
# Clone the repository
git clone <repository-url>

# Navigate to project directory
cd automated-wordpress/agno_agent_seo_posting
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed agno-X.X.X anthropic-X.X.X streamlit-X.X.X ...
```

### Step 4: Verify Installation

```bash
# Check installed packages
pip list | grep -E "streamlit|anthropic|agno"
```

Should show:
- streamlit >= 1.28.0
- anthropic (latest)
- agno (latest)

---

## Configuration

### Step 1: Create Environment File

```bash
# Copy example environment file
cp .env.example .env

# Edit with your preferred editor
# Windows: notepad .env
# macOS/Linux: nano .env
```

### Step 2: Configure Environment Variables

Open `.env` and configure:

```env
# ============================================
# REQUIRED: Anthropic API
# ============================================
ANTHROPIC_API_KEY=sk-ant-your-api-key-here

# ============================================
# OPTIONAL: Default WordPress Credentials
# (Used when publishing without a project)
# ============================================
WP_BASE_URL=https://your-wordpress-site.com
WP_USERNAME=your_wordpress_username
WP_APP_PASS=xxxx xxxx xxxx xxxx

# ============================================
# OPTIONAL: Database Configuration
# ============================================
CLIENT_DB_PATH=./data/clients.db

# ============================================
# OPTIONAL: Image Processing Settings
# ============================================
DEFAULT_IMAGE_WIDTH=800
IMAGE_QUALITY=92
IMAGE_FORMAT=JPEG
```

**Notes:**
- Replace `your-api-key-here` with actual Anthropic API key
- WordPress credentials are optional (can configure per-project instead)
- Image settings have sensible defaults

### Step 3: Create Required Directories

```bash
# Create data directory
mkdir -p data

# Create credentials directory
mkdir -p credentials

# Create image directories
mkdir -p raw_images resized_images
```

---

## WordPress Setup

### Step 1: Generate Application Password

1. **Log into WordPress Admin**
   - Go to: `https://your-site.com/wp-admin`

2. **Navigate to Profile**
   - Click: **Users** → **Profile**
   - Or direct: `https://your-site.com/wp-admin/profile.php`

3. **Scroll to Application Passwords Section**
   - Located near bottom of profile page

4. **Create New Application Password**
   - Enter application name: `SEO Publisher` (or any name)
   - Click: **Add New Application Password**

5. **Copy Generated Password**
   - Password format: `xxxx xxxx xxxx xxxx xxxx xxxx`
   - Copy immediately (won't be shown again)
   - Paste into `.env` file as `WP_APP_PASS`

### Step 2: Verify REST API Access

**Test in browser:**
```
https://your-site.com/wp-json/wp/v2/posts
```

**Expected:** JSON response with posts data

**If error:**
- Check WordPress version (need 4.7+)
- Ensure REST API not disabled by plugin
- Check .htaccess allows API access

### Step 3: Test Credentials (Optional)

```bash
# Test WordPress connection
curl -u "username:xxxx xxxx xxxx xxxx" \
     https://your-site.com/wp-json/wp/v2/users/me
```

**Expected:** JSON with your user data

---

## Google Drive API Setup (Optional)

**Only needed if:** You want to use Google Drive API for Docs conversion

**Alternative:** Use published Google Docs URLs (no API setup needed)

### Step 1: Create Google Cloud Project

1. Go to: https://console.cloud.google.com/
2. Click: **Create Project**
3. Enter project name: `WordPress Publisher`
4. Click: **Create**

### Step 2: Enable Google Drive API

1. In Google Cloud Console
2. Navigate to: **APIs & Services** → **Library**
3. Search: `Google Drive API`
4. Click on it → Click **Enable**

### Step 3: Create OAuth Credentials

1. Navigate to: **APIs & Services** → **Credentials**
2. Click: **Create Credentials** → **OAuth client ID**
3. If prompted, configure OAuth consent screen:
   - User type: **External**
   - App name: `WordPress Publisher`
   - Support email: Your email
   - Scopes: Not needed
   - Test users: Add your email

4. Create OAuth client ID:
   - Application type: **Desktop app**
   - Name: `WordPress Publisher Desktop`
   - Click: **Create**

### Step 4: Download Credentials

1. Click **Download JSON** button
2. Rename file to: `client_secret.json`
3. Move to: `credentials/client_secret.json`

```bash
# Move downloaded file
mv ~/Downloads/client_secret*.json credentials/client_secret.json
```

### Step 5: First Authentication

On first run using Google Drive API:
1. Browser will open automatically
2. Sign in to Google account
3. Grant access to Drive API
4. Token saved to `credentials/token.json`

---

## First Run

### Option 1: Streamlit UI (Recommended)

```bash
# Start Streamlit application
streamlit run app_streamlit.py
```

**Expected output:**
```
You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

**Browser opens automatically to:** http://localhost:8501

### Option 2: CLI Application

```bash
# Start CLI application
python app/main.py
```

**Expected output:**
```
================================================================================
SEO PUBLISHING SYSTEM - v2.0.0
================================================================================

[MAIN MENU]
----------------------------------------
1. Publish Google Docs to WordPress
2. Configure New Project
3. Edit Existing Project
4. List All Projects
5. Exit
----------------------------------------
Choose an option:
```

---

## Verification

### Test 1: Database Initialization

```bash
# Check database file created
ls -lh data/clients.db
```

**Expected:** File exists with size > 0 bytes

### Test 2: Create Test Project

**Via Streamlit:**
1. Click: **Create Project**
2. Fill in test data
3. Submit
4. Check: Project appears in **Projects** page

**Via CLI:**
1. Choose option: `2`
2. Follow prompts
3. Check: Project listed in option `4`

### Test 3: Environment Variables

**Python test:**
```python
import os
from dotenv import load_dotenv

load_dotenv()

# Check Anthropic API key
assert os.getenv('ANTHROPIC_API_KEY'), "ANTHROPIC_API_KEY not set"
print("Environment variables loaded correctly")
```

### Test 4: Import Verification

**Python test:**
```python
# Test core imports
from src.database import list_projects, create_project
from src.workflows.publishing_workflow import execute_publishing_workflow
from src.tools import google_docs_converter, wordpress_uploader

print("All imports successful")
```

---

## Troubleshooting

### Issue: "Module not found" errors

**Solution:**
```bash
# Ensure in correct directory
pwd  # Should show: .../agno_agent_seo_posting

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Issue: "ANTHROPIC_API_KEY not found"

**Solution:**
```bash
# Check .env file exists
ls -la .env

# Check .env content (don't share output!)
cat .env | grep ANTHROPIC

# Verify loading in Python:
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('Key found!' if os.getenv('ANTHROPIC_API_KEY') else 'Key not found')"
```

### Issue: Database permission errors

**Solution:**
```bash
# Create data directory if missing
mkdir -p data

# Check permissions
ls -la data/

# If needed, fix permissions:
chmod 755 data/
```

### Issue: Port 8501 already in use

**Solution:**
```bash
# Option 1: Kill existing Streamlit
pkill -f streamlit

# Option 2: Use different port
streamlit run app_streamlit.py --server.port 8502
```

### Issue: WordPress authentication fails

**Checklist:**
- [ ] Using Application Password (not regular password)
- [ ] No spaces in password (should be: xxxx xxxx xxxx xxxx)
- [ ] WordPress URL has no trailing slash
- [ ] WordPress REST API enabled
- [ ] Test with curl command (see WordPress Setup)

### Issue: Google Drive API not working

**Solutions:**

**Option 1:** Use published Google Docs instead
- File → Share → Publish to web
- Use URL ending in `/pub`
- No API setup needed

**Option 2:** Fix OAuth credentials
- Check `credentials/client_secret.json` exists
- Delete `credentials/token.json` and re-authenticate
- Verify Drive API is enabled in Google Cloud Console

---

## Next Steps

After successful setup:

1. **Read START_HERE.md** - Quick reference guide
2. **Create first project** - Configure a WordPress site
3. **Test publishing** - Publish a simple Google Doc
4. **Review HANDOFF.md** - Understand architecture

---

## Directory Structure After Setup

```
agno_agent_seo_posting/
├── .env                      # Your configuration ✓
├── data/
│   └── clients.db            # Created on first run ✓
├── credentials/
│   ├── client_secret.json    # Your OAuth creds (optional) ✓
│   └── token.json            # Generated on first auth ✓
├── raw_images/               # Created ✓
├── resized_images/           # Created ✓
└── ...                       # Other project files
```

---

## Security Checklist

Before committing to Git:

- [ ] `.env` is in `.gitignore` (already configured)
- [ ] `credentials/` is in `.gitignore` (already configured)
- [ ] `data/clients.db` is in `.gitignore` (already configured)
- [ ] No API keys in code files
- [ ] `.env.example` has placeholder values only

---

## Support

If you encounter issues not covered here:

1. Check **Troubleshooting** section in README.md
2. Review error messages carefully
3. Check Python version compatibility
4. Verify all dependencies installed
5. Check file permissions

---

**Setup complete!** Ready to start publishing.

Run: `streamlit run app_streamlit.py`
