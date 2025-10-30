# SEO Blog Publishing Agent - Usage Guide

This guide provides step-by-step instructions for using the SEO Blog Publishing Agent.

## Quick Start (5 Minutes)

### 1. Prerequisites Check

Ensure you have:
- ✅ Python 3.8 or higher installed
- ✅ Anthropic API key ([Get one here](https://console.anthropic.com/))
- ✅ Google Cloud project with Drive API enabled
- ✅ Two Google Docs ready (content + template)

### 2. Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env  # Create from template
# Edit .env and add your ANTHROPIC_API_KEY
```

### 3. First Run

```bash
python seo_agent.py
```

You'll be prompted to:
1. Authenticate with Google (browser will open)
2. Grant permissions to access Google Drive
3. A `token.json` file will be created automatically

### 4. Process Your First Document

Enter when prompted:
- Content Google Docs URL: `https://docs.google.com/document/d/YOUR_DOC_ID/edit`
- Template Google Docs URL: `https://docs.google.com/document/d/YOUR_TEMPLATE_ID/edit`
- Post title: (optional)
- Process images: `y` (yes)
- Target width: `800` (default)

### 5. Get Your HTML

The agent will:
- ✅ Convert both documents to HTML
- ✅ Apply template formatting
- ✅ Process and resize images
- ✅ Generate final HTML

You can then:
- Save to file: `output.html`
- Optionally publish to WordPress

## Detailed Workflow

### Step 1: Prepare Your Content Document

Create a Google Doc with your blog content:

```
Blog Post Title

Introduction paragraph goes here...

Main Heading
Content for this section...

[Insert images]

Subheading
More content...

• List item 1
• List item 2

[Insert tables if needed]

Conclusion paragraph...
```

**Tips:**
- Use Google Docs' native heading styles (Heading 1, Heading 2, etc.)
- Insert images directly in the document
- Add alt text to images for SEO
- Use lists and tables as needed
- Don't worry about formatting - the template handles that

### Step 2: Create Your Template Document

Create a separate Google Doc that defines your HTML formatting:

```
Sample Paragraph
This paragraph demonstrates the text alignment, font, and spacing you want.

[Image Example]
Insert a sample image with desired alignment and styling.

Heading 2 Example
This shows how H2 headings should look.

Heading 3 Example
This shows how H3 headings should look.

List Example:
• List item 1
• List item 2
• List item 3

Table Example:
┌────────┬────────┐
│ Header │ Header │
├────────┼────────┤
│ Cell   │ Cell   │
└────────┴────────┘
```

**Template Best Practices:**
- Include examples of every element you use in content
- Be consistent with formatting
- Set paragraph alignment (justify/center/left)
- Format images with proper classes (e.g., aligncenter)
- Style headings with desired colors, sizes
- Format tables with borders, padding, width

### Step 3: Run the Agent

#### Interactive Mode (Recommended for First Time)

```bash
python seo_agent.py
```

Follow the prompts step by step.

#### Programmatic Mode

```python
from seo_agent import SEOBlogAgent

agent = SEOBlogAgent()

results = agent.process_documents(
    content_url="https://docs.google.com/document/d/CONTENT_ID/edit",
    template_url="https://docs.google.com/document/d/TEMPLATE_ID/edit",
    post_title="My Amazing Blog Post",
    process_images_flag=True,
    target_width=800
)

if results['success']:
    # Save HTML
    agent.save_html_to_file(results['final_html'], "my_post.html")
    print("✅ HTML saved successfully!")
else:
    print(f"❌ Error: {results['errors']}")
```

### Step 4: Review Output

The agent provides:
- **Character count** of final HTML
- **Number of images** processed
- **Preview** of first 500 characters
- **Full HTML** saved to file

### Step 5: Publish (Optional)

#### Option A: Manual Publishing
1. Copy the HTML from output file
2. Paste into your WordPress editor (HTML mode)
3. Publish manually

#### Option B: Automatic Publishing

When prompted by the agent:
```
Publish to WordPress? (y/n, default: n): y
WordPress site URL: https://your-site.com
Post title: My Blog Post
Post status (draft/publish, default: draft): draft
```

Or programmatically:

```python
wp_result = agent.publish_to_wp(
    formatted_html=results['final_html'],
    post_title="My Blog Post",
    wordpress_site_url="https://your-site.com",
    post_status="draft"  # or "publish"
)

if wp_result['success']:
    print(f"✅ Published: {wp_result['post_url']}")
```

## Common Use Cases

### Use Case 1: Simple Blog Post (No Images)

```python
agent = SEOBlogAgent()

results = agent.process_documents(
    content_url="YOUR_CONTENT_URL",
    template_url="YOUR_TEMPLATE_URL",
    post_title="My Post",
    process_images_flag=False  # Skip image processing
)

agent.save_html_to_file(results['final_html'])
```

### Use Case 2: Image-Heavy Article

```python
results = agent.process_documents(
    content_url="YOUR_CONTENT_URL",
    template_url="YOUR_TEMPLATE_URL",
    process_images_flag=True,
    target_width=1200  # Larger images
)
```

### Use Case 3: Batch Processing Multiple Posts

```python
agent = SEOBlogAgent()

posts = [
    {"content": "URL1", "template": "TEMPLATE_URL", "title": "Post 1"},
    {"content": "URL2", "template": "TEMPLATE_URL", "title": "Post 2"},
    {"content": "URL3", "template": "TEMPLATE_URL", "title": "Post 3"},
]

for post in posts:
    results = agent.process_documents(
        content_url=post["content"],
        template_url=post["template"],
        post_title=post["title"]
    )

    if results['success']:
        filename = f"{post['title'].replace(' ', '_')}.html"
        agent.save_html_to_file(results['final_html'], filename)
        print(f"✅ {post['title']} processed")
```

### Use Case 4: Direct WordPress Publishing

```python
results = agent.process_documents(
    content_url="YOUR_CONTENT_URL",
    template_url="YOUR_TEMPLATE_URL",
    post_title="My Post"
)

if results['success']:
    wp_result = agent.publish_to_wp(
        formatted_html=results['final_html'],
        post_title="My Post",
        wordpress_site_url=os.getenv("WP_BASE_URL"),
        post_status="publish",  # Publish immediately
        categories=[1, 5],  # Category IDs
        tags=[10, 15, 20]  # Tag IDs
    )
```

## Advanced Features

### Custom Image Dimensions

Process images with specific dimensions:

```python
from tools.image_processor import process_images

result = process_images(
    html_content=your_html,
    target_width=1200,
    target_height=800  # Exact dimensions (may distort)
)
```

### Extract Template Rules Only

Get formatting rules without processing content:

```python
from utils.template_parser import extract_template_rules

rules = extract_template_rules(template_html)

print("Paragraph rules:", rules['p'])
print("Image rules:", rules['img'])
print("Heading rules:", rules['h2'])
```

### Apply Custom Template Rules

```python
from tools.html_formatter import HTMLFormatter

# Define custom rules
custom_rules = {
    'p': {'dir': 'ltr', 'style': 'text-align: justify; font-size: 16px;'},
    'img': {'class': 'aligncenter size-full'},
    'h2': {'style': 'color: #333; font-weight: bold;'}
}

# Apply to content
formatter = HTMLFormatter(custom_rules)
formatted_html = formatter.format_html(your_content_html)
```

### WordPress-Only Operations

Upload images separately:

```python
from tools.wordpress_publisher import WordPressPublisher

publisher = WordPressPublisher(
    site_url="https://your-site.com",
    username=os.getenv("WP_USERNAME"),
    app_password=os.getenv("WP_APP_PASS")
)

# Upload single image
result = publisher.upload_image(
    image_path="path/to/image.jpg",
    title="My Image",
    alt_text="Description for SEO",
    caption="Image caption"
)

print(f"Image URL: {result['url']}")

# Upload multiple images
results = publisher.upload_images_batch(
    image_paths=["img1.jpg", "img2.jpg", "img3.jpg"],
    metadata=[
        {"alt": "Image 1", "title": "First image"},
        {"alt": "Image 2", "title": "Second image"},
        {"alt": "Image 3", "title": "Third image"}
    ]
)
```

## Tips & Best Practices

### Content Writing
- ✅ Use clear headings hierarchy (H1 → H2 → H3)
- ✅ Add alt text to all images
- ✅ Keep paragraphs concise
- ✅ Use lists for better readability
- ✅ Include relevant links

### Template Creation
- ✅ Create one template per content type (blog post, product page, etc.)
- ✅ Test template with sample content first
- ✅ Keep formatting consistent throughout template
- ✅ Include all element types you'll use

### Image Optimization
- ✅ Use appropriate image widths (800px for blogs, 1200px for featured)
- ✅ Always provide alt text for SEO
- ✅ Consider image file sizes for web performance
- ✅ Use JPEG for photos, PNG for graphics with transparency

### WordPress Publishing
- ✅ Start with "draft" status to review before publishing
- ✅ Upload images separately if you need more control
- ✅ Test with a staging site first
- ✅ Keep application passwords secure

### Performance
- ✅ Process images locally before uploading to save bandwidth
- ✅ Reuse the same template for multiple posts
- ✅ Cache template rules when batch processing
- ✅ Use appropriate image quality settings (92 is good balance)

## Troubleshooting

### Issue: "Could not extract file ID from URL"

**Solution:** Ensure your Google Docs URL is in one of these formats:
- `https://docs.google.com/document/d/DOC_ID/edit`
- `https://docs.google.com/file/d/FILE_ID/view`
- `https://drive.google.com/open?id=FILE_ID`

### Issue: Images not downloading

**Solution:**
1. Check internet connection
2. Verify image URLs are publicly accessible
3. Check `processed_images/` directory exists and is writable
4. Try with smaller images first

### Issue: Template formatting not applied

**Solution:**
1. Verify template URL is correct
2. Check template has formatting examples
3. Ensure template document isn't empty
4. Try with a simpler template first

### Issue: WordPress upload fails

**Solution:**
1. Verify WordPress credentials in `.env`
2. Check WordPress site is accessible
3. Ensure REST API is enabled on WordPress
4. Verify application password is correct
5. Check user permissions in WordPress

### Issue: Google authentication fails

**Solution:**
1. Delete `token.json`
2. Verify `client_secret.json` is correct
3. Check Google Drive API is enabled
4. Try authentication again

## Getting Help

1. **Check the README**: Most common issues are covered
2. **Validate Configuration**: Run `python config/settings.py`
3. **Test Individual Tools**: Test each tool separately
4. **Check Logs**: Look for error messages in console output
5. **Review Documentation**: See Agno docs and API docs

## Next Steps

- Create your first template document
- Process a simple test document
- Experiment with different image sizes
- Try batch processing
- Set up WordPress publishing
- Customize tools for your needs

---

Happy publishing! 🚀
