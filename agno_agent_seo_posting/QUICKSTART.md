# Quick Start Guide - SEO Publishing System

Get up and running in 5 minutes!

---

## Prerequisites

- Python 3.11+
- WordPress site with REST API enabled
- WordPress application password
- Anthropic API key
- **Google Cloud Project with Drive API enabled**
- **Google OAuth client_secret.json file**

---

## 1. Install (2 minutes)

```bash
cd agno_agent_seo_posting
pip install -r requirements.txt
```

---

## 2. Configure (5 minutes)

### Google API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create/select project → Enable Google Drive API
3. Create OAuth credentials (Desktop app)
4. Download JSON → Rename to `client_secret.json`
5. Place in `agno_agent_seo_posting/` folder

### Environment File

Create `.env` file:

```bash
# Copy this to .env file
ANTHROPIC_API_KEY=your-anthropic-api-key-here
GOOGLE_CLIENT_SECRETS=./client_secret.json
WP_BASE_URL=https://your-wordpress-site.com
WP_USERNAME=your-username
WP_APP_PASS=xxxx xxxx xxxx xxxx
```

**Get WordPress Application Password**:
1. WordPress Admin → Users → Profile
2. Scroll to "Application Passwords"
3. Create new password → Copy it

---

## 3. Run (1 minute)

```bash
python3 main.py
```

You'll see:
```
🚀 SEO PUBLISHING SYSTEM - MVP v1.0
================================================================================

📋 MAIN MENU
1. 📤 Publish Google Docs to WordPress
2. 🔧 Configure New Project
3. 📁 List All Projects
4. 🚪 Exit
```

---

## 4. First Use

### Option A: Quick Test (No Project)

1. Select **"1. Publish"**
2. Press **Enter** (skip project selection)
3. Paste your Google Docs URL
4. Done! Check WordPress for draft post

### Option B: Configure Project (Recommended)

1. Select **"2. Configure New Project"**
2. Follow AI agent prompts:
   - Project ID: `test_project`
   - Project Name: `Test Project`
   - WordPress URL: Your site
   - Credentials: Username + app password
   - Image width: `800`
   - Image quality: `92`
   - Image format: `JPEG`
   - CSS classes: `wp-image aligncenter`
   - Paste sample HTML from your WordPress site
3. AI analyzes and generates patterns
4. Confirm and save

Then publish:
1. Select **"1. Publish"**
2. Select your project
3. Paste Google Docs URL
4. Watch it work!

---

## 5. Publish Your First Post

### Prepare Google Doc

1. Open any Google Doc you have access to
2. Copy the URL from your browser (edit or view URL works!)

Example URLs (all work):
```
https://docs.google.com/document/d/ABC123/edit
https://docs.google.com/document/d/ABC123/view
```

**First Time Only**: Browser opens for Google authentication → Grant access to Drive API

### Publish

```
Select option: 1
Select project: 1 (or press Enter for no-project)
Enter Google Docs URL: [paste URL]
```

Watch the magic happen:
```
[1/6] 📄 Converting Google Docs to HTML... ✓
[2/6] 📝 Extracting post title... ✓
[3/6] 🖼️  Processing images... ✓
[4/6] ⬆️  Uploading images to WordPress... ✓
[5/6] 🔄 Applying HTML transformations... ✓
[6/6] 📤 Creating WordPress post... ✓

✅ WORKFLOW COMPLETED SUCCESSFULLY
🔗 Post URL: https://your-site.com/your-post/
```

---

## Troubleshooting

**"ANTHROPIC_API_KEY not found"**
→ Check `.env` file exists and has correct key

**"WordPress credentials not configured"**
→ Set credentials in `.env` or configure a project

**"Failed to convert Google Docs"**
→ Ensure document is published (File → Share → Publish to web)

**Images not uploading**
→ Check WordPress media permissions

---

## What's Next?

- Read **README.md** for complete documentation
- Read **USAGE.md** for detailed guides
- Check **IMPLEMENTATION_SUMMARY.md** for architecture details

---

**That's it! You're ready to automate SEO publishing.** 🚀
