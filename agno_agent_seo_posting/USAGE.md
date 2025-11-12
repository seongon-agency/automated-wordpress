# SEO Publishing System - Usage Guide

Step-by-step guide for using the system.

---

## Table of Contents

1. [Initial Setup](#initial-setup)
2. [Configuring Your First Project](#configuring-your-first-project)
3. [Publishing Content](#publishing-content)
4. [Managing Projects](#managing-projects)
5. [Tips and Best Practices](#tips-and-best-practices)

---

## Initial Setup

### 1. Install Dependencies

```bash
cd agno_agent_seo_posting
pip install -r requirements.txt
```

### 2. Configure Environment

Create `.env` file in `agno_agent_seo_posting/`:

```env
# Required
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Optional (can be set per-project instead)
WP_BASE_URL=https://your-site.com
WP_USERNAME=admin
WP_APP_PASS=xxxx xxxx xxxx xxxx
```

### 3. Get WordPress Application Password

1. Log in to WordPress admin
2. Go to **Users → Profile**
3. Scroll to **Application Passwords**
4. Enter app name (e.g., "SEO Publishing System")
5. Click **Add New Application Password**
6. Copy the generated password (format: `xxxx xxxx xxxx xxxx`)

---

## Configuring Your First Project

### Step 1: Start the Application

```bash
python3 main.py
```

You'll see the main menu:
```
📋 MAIN MENU
1. 📤 Publish Google Docs to WordPress
2. 🔧 Configure New Project
3. 📁 List All Projects
4. 🚪 Exit
```

### Step 2: Select "Configure New Project" (Option 2)

The AI agent will guide you through configuration.

### Step 3: Provide Project Information

**Example interaction**:

```
Agent: "Let's start configuring a new project. First, I need some basic information."

Agent: "What should we call this project? (e.g., 'acme_corp_2025')"
You: acme_corp

Agent: "What's the display name for this project?"
You: Acme Corporation

Agent: "What's the WordPress site URL?"
You: https://acme.com

Agent: "WordPress username?"
You: admin

Agent: "WordPress application password?"
You: [paste your app password]

Agent: "Any notes for future reference?"
You: Main corporate blog
```

### Step 4: Configure Image Settings

```
Agent: "Now let's configure image processing. What target width for images in pixels?"
You: 800

Agent: "Image quality (1-100)?"
You: 92

Agent: "Image format? (JPEG, PNG, WEBP)"
You: JPEG

Agent: "CSS classes for images? (e.g., 'wp-image aligncenter')"
You: wp-image aligncenter

Agent: "Image alignment? (left, center, right)"
You: center
```

### Step 5: Provide HTML Template Sample

This is the most important step! The AI agent will analyze your HTML.

**Preparing Your Sample**:

1. Go to an existing WordPress post on your client's site
2. View page source or inspect element
3. Copy representative HTML (paragraphs, headings, images, lists)
4. Paste when prompted

**Example Sample HTML**:

```html
<p class="entry-content" style="text-align: justify;">
This is a sample paragraph with the client's styling.
</p>

<h2 class="wp-block-heading">Sample Heading</h2>

<img class="wp-image-123 aligncenter" src="..." width="800" loading="lazy" />

<ul class="wp-block-list">
<li>List item one</li>
<li>List item two</li>
</ul>

<table class="wp-block-table">
<tr>
<td>Cell 1</td>
<td>Cell 2</td>
</tr>
</table>
```

**Agent Response**:

```
Agent: "I've analyzed the HTML and found these patterns:

1. Paragraphs: class="entry-content", style="text-align: justify;"
2. H2 headings: class="wp-block-heading"
3. Images: class="wp-image-123 aligncenter", loading="lazy"
4. Lists: class="wp-block-list"
5. Tables: class="wp-block-table"

Generated 8 transformation patterns.

Here's an example transformation:
Before: <p>Hello world</p>
After:  <p class="entry-content" style="text-align: justify;">Hello world</p>

Does this look correct?"
```

### Step 6: Review and Confirm

```
You: Yes, looks good!

Agent: "Perfect! I've saved the configuration for project 'acme_corp'.

Summary:
- Project ID: acme_corp
- WordPress: https://acme.com
- HTML Patterns: 8 patterns configured
- Image Settings: 800px, JPEG, quality 92

You can now publish Google Docs using this project configuration!"
```

---

## Publishing Content

### Step 1: Prepare Your Google Doc

**IMPORTANT**: Your document must be published to the web!

1. Open your Google Doc
2. Go to **File → Share → Publish to web**
3. Click **Publish**
4. Copy the URL (should end with `/pub`)

Example URL:
```
https://docs.google.com/document/d/e/2PACX-1vQxyz.../pub
```

### Step 2: Start Publishing Workflow

From main menu, select **Option 1: Publish Google Docs to WordPress**

### Step 3: Select Project

```
Available projects:
  1. Acme Corporation (acme_corp)
  2. Beta Corp (beta_corp)
  3. No project (skip transformations)

Select project number (or press Enter for no project):
```

Enter: `1` (or project number)

### Step 4: Provide Google Docs URL

```
Enter Google Docs URL (must be published to web):
> https://docs.google.com/document/d/e/2PACX-xxx/pub
```

### Step 5: Watch the Workflow Execute

You'll see real-time progress:

```
================================================================================
🚀 STARTING PUBLISHING WORKFLOW
================================================================================

📁 Loading project: acme_corp
   ✓ Project loaded: Acme Corporation

[1/6] 📄 Converting Google Docs to HTML...
   ✓ Converted (15234 characters)
   ✓ Document: 10 Tips for SEO Success

[2/6] 📝 Extracting post title...
   ✓ Title: 10 Tips for SEO Success

[3/6] 🖼️  Processing images...
   ✓ Processed 3 image(s)

[4/6] ⬆️  Uploading images to WordPress...
   ✓ Uploaded 3 image(s)

[5/6] 🔄 Applying HTML transformations...
   ✓ Applied 8 transformation pattern(s)
   🔗 Replacing image URLs with WordPress media URLs...
   ✓ Replaced 3 image URL(s)

[6/6] 📤 Creating WordPress post...
   ✓ Post created: 456
   ✓ Status: draft

================================================================================
✅ WORKFLOW COMPLETED SUCCESSFULLY
================================================================================

📌 Post Title: 10 Tips for SEO Success
🔗 Post URL: https://acme.com/2025/11/10-tips-for-seo-success/
🖼️  Images: 3 processed
⏱️  Time: 25.3s

================================================================================
```

### Step 6: Review and Publish

1. Click the post URL or go to WordPress admin
2. Review the draft post
3. Check HTML formatting matches your style
4. Verify images are properly placed
5. Click **Publish** when ready

---

## Managing Projects

### Listing Projects

From main menu, select **Option 3: List All Projects**

```
📁 CONFIGURED PROJECTS
================================================================================

🔸 Acme Corporation
   ID: acme_corp
   WordPress: https://acme.com
   Status: active
   HTML Patterns: 8
   Image Width: 800

🔸 Beta Corp
   ID: beta_corp
   WordPress: https://beta.com
   Status: active
   HTML Patterns: 6
   Image Width: 1200

================================================================================
```

### Updating a Project

To update project configuration, run the configuration wizard again with the same project ID. It will replace the existing configuration.

### Deactivating a Project

Projects remain in the database but you can programmatically set status to 'inactive':

```python
from database import update_project

update_project('acme_corp', status='inactive')
```

---

## Tips and Best Practices

### Creating Good HTML Samples

**DO**:
✅ Include all element types you use (p, h2, h3, ul, table, img)
✅ Copy actual HTML from your WordPress site
✅ Include complete tags with all attributes
✅ Provide 2-3 examples of each element type

**DON'T**:
❌ Use simplified HTML without attributes
❌ Mix content from multiple sites
❌ Include JavaScript or CSS blocks
❌ Use placeholder/dummy attributes

### Publishing Workflow Best Practices

1. **Always review drafts** before publishing
2. **Test with simple docs first** when setting up new projects
3. **Keep Google Docs clean** - avoid complex formatting
4. **Use published URLs only** - edit URLs won't work
5. **Check image quality** after first publish to adjust settings

### Troubleshooting Common Issues

#### Images Don't Upload

**Possible causes**:
- Image URLs inaccessible
- WordPress media permissions issue
- Network timeout

**Solution**:
- Verify images visible in Google Docs
- Check WordPress media settings
- Retry the publish

#### HTML Formatting Wrong

**Possible causes**:
- Sample HTML didn't include all element types
- Pattern regex too broad/narrow
- Unexpected HTML structure in Google Docs

**Solution**:
- Reconfigure project with better HTML sample
- Test with simpler document first
- Verify sample HTML is from actual WordPress post

#### WordPress Authentication Failed

**Possible causes**:
- Wrong username/password
- Application password not enabled
- REST API disabled

**Solution**:
- Verify credentials in project config
- Generate new application password
- Contact WordPress admin to enable REST API

---

## Advanced: Programmatic Usage

### Publishing from Python

```python
from workflows import execute_publishing_workflow

# Publish with project
result = execute_publishing_workflow(
    google_docs_url="https://docs.google.com/document/d/e/2PACX-xxx/pub",
    project_id="acme_corp"
)

if result['success']:
    print(f"✅ Published to: {result['post_url']}")
    print(f"📝 Title: {result['post_title']}")
    print(f"🖼️  Images: {result['images_processed']}")
else:
    print(f"❌ Failed: {result['error']}")
```

### No-Project Publishing

```python
# Publish without project (no HTML transformations)
result = execute_publishing_workflow(
    google_docs_url="https://docs.google.com/document/d/e/2PACX-xxx/pub",
    project_id=None  # No project
)
```

### Batch Processing

```python
docs = [
    ("https://docs.google.com/document/d/e/2PACX-aaa/pub", "acme_corp"),
    ("https://docs.google.com/document/d/e/2PACX-bbb/pub", "acme_corp"),
    ("https://docs.google.com/document/d/e/2PACX-ccc/pub", "beta_corp"),
]

for doc_url, project_id in docs:
    result = execute_publishing_workflow(doc_url, project_id)
    print(f"{project_id}: {'✅' if result['success'] else '❌'}")
```

---

## Getting Help

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting-common-issues) section
2. Review your `.env` configuration
3. Verify WordPress credentials and permissions
4. Check publishing history in database for error messages

For development questions, see `CLAUDE.md` and `SOLUTION_PLAN.md`.

---

**Happy Publishing!** 🚀
