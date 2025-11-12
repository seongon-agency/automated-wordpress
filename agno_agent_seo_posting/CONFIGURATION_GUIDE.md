# Project Configuration Guide

## Overview

The Configuration Agent helps you set up new projects by guiding you through an interactive workflow. The agent now has tools to save projects directly to the database.

---

## How It Works

When you select **Option 2: Configure New Project** from the main menu, the Configuration Agent will guide you through 5 steps:

### Step 1: Gather Basic Information

The agent will ask for:
- **Project ID**: Unique identifier in slug format (e.g., `client_name_2025`)
- **Project Name**: Display name (e.g., `Client Name Blog`)
- **WordPress URL**: Your WordPress site URL (e.g., `https://client.com`)
- **WordPress Username**: Admin username
- **WordPress Application Password**: Generate from WordPress → Users → Profile → Application Passwords
- **Notes**: Optional notes for future reference

### Step 2: Image Configuration

The agent will ask for image preferences:
- **Target Width**: Image width in pixels (default: 800)
- **Image Quality**: JPEG quality 1-100 (default: 92)
- **Image Format**: JPEG, PNG, or WEBP (default: JPEG)
- **CSS Classes**: Classes to add to `<img>` tags (e.g., `wp-image aligncenter`)
- **Alignment**: left, center, or right (default: center)

The agent will use the `create_image_config_from_preferences` tool to generate the image configuration.

### Step 3: HTML Template Analysis

The agent will ask you to paste a sample of your desired HTML output. For example:

```html
<p class="article-body" style="text-align: justify;">This is a paragraph.</p>
<h2 class="section-header">Subheading</h2>
<strong>Bold text</strong>
<em>Italic text</em>
<ul class="bullet-list">
    <li>List item</li>
</ul>
```

The agent will analyze this sample and generate transformation patterns that convert plain Google Docs HTML into your desired format.

**Pattern Example**:
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
    }
  ]
}
```

### Step 4: Review and Confirmation

The agent will show you:
- All the information you provided
- The generated `html_configs` (transformation patterns)
- The generated `image_configs`

You'll be asked to confirm before saving.

### Step 5: Save Configuration

Once you confirm, the agent will:
1. Use the `save_project_configuration` tool to save everything to the database
2. Confirm that the project was saved successfully
3. Show you the project ID for future reference

---

## What Happens Behind the Scenes

The configuration agent has access to two tools:

1. **`create_image_config_from_preferences`**: Creates the image configuration dict
2. **`save_project_configuration`**: Saves the project to the SQLite database

When you confirm, the agent calls these tools automatically.

---

## After Configuration

Once your project is saved:

1. **View It**: Select Option 3 from the main menu to list all projects
2. **Use It**: Select Option 1 to publish, then choose your project
3. **Update It**: Run the configuration wizard again with the same Project ID (it will update)

---

## Example Session

```
🔧 PROJECT CONFIGURATION WIZARD
================================================================================

Welcome! I'll help you configure a new project.
This involves gathering your WordPress details and analyzing your HTML template.