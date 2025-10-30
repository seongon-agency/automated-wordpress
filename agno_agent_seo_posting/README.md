# SEO Blog Publishing Agent

An AI-powered agent built with the [Agno framework](https://docs.agno.com/introduction) that converts Google Docs to SEO-optimized HTML and optionally publishes to WordPress.

## 🎯 Features

- **Dual Google Docs Input**: Separates content from formatting using two Google Docs:
  - **Content Doc**: Your blog post content
  - **Template Doc**: HTML formatting rules and styles

- **Intelligent HTML Processing**:
  - Converts Google Docs to clean HTML
  - Applies template-based formatting automatically
  - Preserves document structure (headings, lists, tables)

- **Image Optimization**:
  - Automatic image download and resizing
  - Configurable dimensions (default: 800px width)
  - SEO-friendly img tag generation with alt text
  - WordPress media library integration

- **WordPress Integration** (Optional):
  - Direct publishing to WordPress via REST API
  - Draft or immediate publishing
  - Category and tag management
  - Automatic image uploads

- **User-Friendly Output**:
  - Clean, formatted HTML ready to use
  - Download as .html file
  - Copy-to-clipboard ready
  - Preview before publishing

## 📁 Project Structure

```
agno_agent_seo_posting/
├── seo_agent.py                 # Main agent implementation
├── tools/
│   ├── __init__.py
│   ├── google_docs_converter.py # Tool 1: Google Docs → HTML
│   ├── image_processor.py       # Tool 2: Image processing
│   ├── html_formatter.py        # Tool 3: Template formatting
│   └── wordpress_publisher.py   # Tool 4: WordPress publishing
├── utils/
│   ├── __init__.py
│   └── template_parser.py       # Template rule extraction
├── config/
│   └── settings.py              # Configuration management
├── requirements.txt
├── .env                         # Environment variables (create this)
└── README.md
```

## 🚀 Installation

### 1. Clone or Download

```bash
cd agno_agent_seo_posting
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Publish Your Google Docs

**No Google Cloud credentials needed!** Simply publish your documents to the web:

1. Open your Google Doc (content or template)
2. Go to **File → Share → Publish to web**
3. Click the **Publish** button
4. Copy the published URL (it will end with `/pub`)
   - Example: `https://docs.google.com/document/d/e/2PACX-xxx/pub`
5. Use this URL when running the agent

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Required: Anthropic API Key
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional: WordPress Settings (only if publishing to WP)
WP_BASE_URL=https://your-wordpress-site.com
WP_USERNAME=your_wordpress_username
WP_APP_PASS=your_wordpress_app_password

# Optional: Image Processing Defaults
DEFAULT_IMAGE_WIDTH=800
IMAGE_QUALITY=92
IMAGE_FORMAT=JPEG
```

**Note:** Google Docs are now accessed via published URLs - no OAuth or API credentials required!

## 📖 Usage

### Running the Agent

Start the agent server:

```bash
python seo_agents.py
```

Or using the Agno CLI:

```bash
agno serve seo_agents:app --reload
```

### Using the Agent

When prompted, provide:
1. **Content Google Docs URL** (published URL ending in `/pub`)
2. **Template Google Docs URL** (published URL ending in `/pub`)

The agent will automatically:
1. Convert both Google Docs to HTML
2. Extract the post title from the content
3. Process and optimize images
4. Apply template formatting
5. Publish to WordPress (as a draft)

### Example URLs

**Content Doc:**
```
https://docs.google.com/document/d/e/2PACX-1vQxyz.../pub
```

**Template Doc:**
```
https://docs.google.com/document/d/e/2PACX-1vQabc.../pub
```

### Testing the Converter

Test the Google Docs converter independently:

```bash
python test_google_docs_converter.py
```

### Programmatic Usage

```python
from tools.google_docs_converter import google_docs_to_html

# Convert a published Google Doc to HTML
result = google_docs_to_html(
    google_docs_url="https://docs.google.com/document/d/e/2PACX-xxx/pub"
)

# Check results
if result['success']:
    print(f"Document: {result['name']}")
    print(f"HTML Length: {len(result['raw_html'])} characters")
    print(f"Final HTML: {results['final_html'][:500]}...")

    # Save to file
    agent.save_html_to_file(results['final_html'], "my_blog_post.html")

    # Optionally publish to WordPress
    wp_result = agent.publish_to_wp(
        formatted_html=results['final_html'],
        post_title="My Blog Post",
        wordpress_site_url="https://your-site.com",
        post_status="draft"
    )
else:
    print(f"Failed: {results['errors']}")
```

### Using Individual Tools

Each tool can be used independently:

```python
# Tool 1: Convert Google Doc to HTML
from tools.google_docs_converter import google_docs_to_html

result = google_docs_to_html("https://docs.google.com/document/d/DOC_ID/edit")
print(result['raw_html'])

# Tool 2: Process images
from tools.image_processor import process_images

result = process_images(
    html_content="<html>...</html>",
    target_width=800
)

# Tool 3: Apply template formatting
from tools.html_formatter import format_html_with_template

result = format_html_with_template(
    content_html="<html>content...</html>",
    template_html="<html>template...</html>"
)

# Tool 4: Publish to WordPress
from tools.wordpress_publisher import publish_to_wordpress

result = publish_to_wordpress(
    formatted_html="<html>...</html>",
    wordpress_site_url="https://your-site.com",
    post_title="My Post",
    post_status="draft"
)
```

## 📝 Creating Template Google Docs

Your template Google Doc defines the formatting rules that will be applied to your content. Here's how to create one:

### Template Structure

Create a Google Doc with examples of each HTML element you want to style:

```
Paragraph Example
This is a sample paragraph with the desired formatting.

[Insert an image with desired class/alignment]

Heading 2 Example
List Example:
• List item 1
• List item 2

[Table example with desired styling]
```

### Key Elements to Include

1. **Paragraphs**:
   - Set text alignment (justify, center, left, right)
   - Apply any desired spacing or styles

2. **Images**:
   - Insert a placeholder image
   - Apply desired alignment (center, left, right)
   - Set any CSS classes or attributes

3. **Headings** (H2-H6):
   - Format each heading level you'll use
   - Apply colors, sizes, weights

4. **Lists**:
   - Create both ordered (1,2,3) and unordered (•) lists
   - Format list items as desired

5. **Tables**:
   - Create a sample table
   - Format cells, borders, padding

### Template Tips

- The agent extracts the **most common** formatting for each element type
- Be consistent in your template formatting
- If multiple styles exist for the same element, the most frequent one is used
- Content-specific attributes (href, src, alt) are preserved from your content doc

### Example Template

See `docs/template_example.md` for a complete template example.

## 🔧 Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Your Anthropic API key for Claude |
| `GOOGLE_CLIENT_SECRETS` | Yes | Path to Google OAuth client secrets |
| `GOOGLE_TOKEN_PATH` | No | Path to store Google auth token (default: token.json) |
| `WP_BASE_URL` | No* | WordPress site URL (required for publishing) |
| `WP_USERNAME` | No* | WordPress username (required for publishing) |
| `WP_APP_PASS` | No* | WordPress app password (required for publishing) |
| `DEFAULT_IMAGE_WIDTH` | No | Default image width in pixels (default: 800) |
| `IMAGE_QUALITY` | No | JPEG quality 1-100 (default: 92) |

*Required only if you want to publish to WordPress

### WordPress Application Password

To publish to WordPress:

1. Log in to your WordPress admin panel
2. Go to Users → Profile
3. Scroll to "Application Passwords"
4. Create a new application password
5. Copy the generated password (format: `xxxx xxxx xxxx xxxx xxxx xxxx`)
6. Use this as `WP_APP_PASS` in your `.env` file

## 🎨 Workflow

```
┌─────────────────┐
│  Content Doc    │ (Google Docs)
│  Blog content   │
└────────┬────────┘
         │
         ├─────────► Convert to HTML
         │
         ▼
┌─────────────────┐
│  Template Doc   │ (Google Docs)
│  Format rules   │
└────────┬────────┘
         │
         ├─────────► Extract formatting rules
         │
         ▼
┌─────────────────┐
│ Apply Template  │
│   Formatting    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Process Images  │
│ Resize & Upload │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Final HTML     │ ───► Save to file
│  SEO-Optimized  │ ───► Publish to WP
└─────────────────┘
```

## 🧪 Testing

Test individual components:

```bash
# Test Google Docs converter
python tools/google_docs_converter.py

# Test image processor
python tools/image_processor.py

# Test template parser
python utils/template_parser.py

# Test HTML formatter
python tools/html_formatter.py

# Test WordPress publisher
python tools/wordpress_publisher.py

# Validate configuration
python config/settings.py
```

## 🐛 Troubleshooting

### "ANTHROPIC_API_KEY not found"
- Ensure `.env` file exists in project root
- Check that `ANTHROPIC_API_KEY` is set correctly
- Run: `python config/settings.py` to validate

### Google Authentication Issues
- Delete `token.json` and re-authenticate
- Verify `client_secret.json` is in project root
- Check that Google Drive API is enabled in your Google Cloud project

### WordPress Publishing Fails
- Verify WordPress credentials in `.env`
- Ensure WordPress REST API is enabled
- Check that your WordPress user has permission to create posts
- Verify application password is correct (no spaces)

### Images Not Processing
- Check image URLs are accessible
- Verify sufficient disk space for image downloads
- Check `processed_images/` directory is writable

### Template Not Applied
- Ensure template Google Doc has formatting examples for all elements
- Verify template URL is correct and accessible
- Check that both documents were successfully converted to HTML

## 📚 Documentation

- [Agno Framework Documentation](https://docs.agno.com/introduction)
- [Google Docs API](https://developers.google.com/docs/api)
- [WordPress REST API](https://developer.wordpress.org/rest-api/)

## 🤝 Contributing

This is a custom implementation. Feel free to:
- Fork and modify for your needs
- Report issues you encounter
- Suggest improvements
- Share template examples

## 📄 License

This project is for personal/internal use. Modify as needed for your requirements.

## 🙏 Acknowledgments

- Built with [Agno](https://docs.agno.com/) - AI agent framework by Anthropic
- Uses Claude Sonnet 4.5 for intelligent processing
- Inspired by the need for better blog publishing workflows

## 📞 Support

For issues related to:
- **Agno Framework**: See [Agno Documentation](https://docs.agno.com/)
- **This Implementation**: Check troubleshooting section above
- **Google APIs**: See [Google Cloud Console](https://console.cloud.google.com/)
- **WordPress**: See [WordPress Documentation](https://wordpress.org/support/)

---

**Version**: 1.0.0
**Last Updated**: 2025-10-28
**Built with**: Agno Framework + Claude Sonnet 4.5
