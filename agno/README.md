# WordPress Publishing AI Agent

AI Agent that automatically publishes Google Docs to WordPress.

## Quick Start

### 1. Install Dependencies
```bash
cd agno
pip install -r requirements.txt
```

### 2. Set Environment Variables
Create a `.env` file in the `agno/` directory:
```bash
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### 3. Run the Agent
```bash
python agents.py
```

The agent will start a web interface at `http://localhost:7777`

## Usage

### Via Web Interface
1. Open http://localhost:7777 in your browser
2. Paste a Google Docs URL
3. The agent will:
   - Extract content from the Google Doc
   - Process and upload all images to WordPress
   - Transform HTML to WordPress-compatible format
   - Create a draft post
   - Return the post URL

### Example Conversations

**Single Post:**
```
You: Publish this doc to WordPress: https://docs.google.com/document/d/YOUR_DOC_ID/edit

Agent: [Processes the document]
       ✅ Published to WordPress!
       Post ID: 123
       URL: https://ngoncareer.com/post-title
       Status: draft
       Images uploaded: 5
```

**Batch Publishing:**
```
You: Publish these 3 docs for Client A:
     https://docs.google.com/document/d/ABC123/edit
     https://docs.google.com/document/d/DEF456/edit
     https://docs.google.com/document/d/GHI789/edit

Agent: 📦 BATCH PUBLISHING 3 DOCUMENTS
       Client: Client A - Custom Bold

       [1/3] Processing...
       ✅ Published: "First Article Title"

       [2/3] Processing...
       ✅ Published: "Second Article Title"

       [3/3] Processing...
       ✅ Published: "Third Article Title"

       📊 SUMMARY
       Total: 3
       ✅ Successful: 3
       ❌ Failed: 0
       Success rate: 100%

       All posts published as drafts!
```

## Available Commands

The agent can handle these requests:

1. **Publish a Single Google Doc**
   - "Publish this doc: [URL]"
   - "Publish this doc for Client A: [URL]"  (with custom HTML styling)
   - "Create a WordPress post from this Google Doc: [URL]"

2. **Batch Publish Multiple Docs**
   - "Publish these 5 docs: [URL1], [URL2], [URL3], [URL4], [URL5]"
   - "Publish these docs for Client A: [list of URLs]"
   - "Batch publish all these Google Docs as drafts"

3. **List Available Clients**
   - "What clients are available?"
   - "Show me client configurations"

4. **List Recent Posts**
   - "Show me recent posts"
   - "List the last 5 WordPress posts"

5. **Get Post Details**
   - "Get details for post 123"
   - "Show me post 456"

6. **Update a Post**
   - "Update post 123 title to 'New Title'"
   - "Change post 456 status to publish"
   - "Update post 789 content"

## Client-Specific HTML Customizations

Different WordPress clients may have custom CSS/HTML requirements. Instead of manually editing HTML or wasting tokens on long posts, you can define transformation rules per client.

### Quick Example

```
You: "What clients are available?"
Agent: [Lists: Default WordPress, Client A - Custom Bold, Client B - Custom Headings, etc.]

You: "Publish this doc for Client A: https://docs.google.com/..."
Agent: [Applies Client A's custom HTML transformations automatically]
```

### How It Works

- **Zero AI tokens used** - Transformations are programmatic
- **Instant processing** - No length limits
- **Configuration-driven** - Define rules once, use forever

### Adding New Clients

**Method 1: Let the Agent Create It (Recommended)**

Just show the agent example HTML:

```
You: "I need to create a new client config"

Agent: "Sure! I'll need:
        1. Client name
        2. Client ID (e.g., 'abc-company')
        3. Original HTML (from Google Docs)
        4. Desired HTML (what the client needs)"

You: [Provide the HTML examples]

Agent: [Automatically analyzes differences and creates config]
       "✅ Client 'ABC Company' created! Use client_id 'abc-company' when publishing."
```

The agent uses AI once to analyze the HTML and create the config. After that, all future posts use the config with zero tokens!

**Method 2: Manual Configuration**

See [CLIENT_CUSTOMIZATION_GUIDE.md](CLIENT_CUSTOMIZATION_GUIDE.md) for detailed instructions.

Quick steps:
1. Edit `client_configs.py`
2. Add your transformation rules
3. Test with `python test_client_transforms.py`
4. Use with the agent!

### Example Transformations

- Change `<strong>` to `<b>` with custom styling
- Add specific classes to headings/paragraphs
- Inject consistent styles across all tags
- Wrap elements in custom HTML structures
- Replace class names (e.g., Bootstrap → Tailwind)

See examples in `client_configs.py`

## Tools the Agent Has Access To

1. `publish_google_doc_to_wordpress()` - Main publishing function
2. `get_wordpress_post()` - Retrieve post details
3. `update_wordpress_post()` - Update existing posts
4. `list_recent_posts()` - List recent WordPress posts

## How It Works

```
Google Doc URL
    ↓
Extract file ID
    ↓
Export HTML from Google Docs API
    ↓
Extract images from HTML
    ↓
Download & resize images
    ↓
Upload images to WordPress
    ↓
Transform HTML (remove Google Docs artifacts)
    ↓
Replace image URLs with WordPress URLs
    ↓
Create WordPress post (draft)
    ↓
Return post URL to user
```

## Troubleshooting

### "No module named 'functions'"
Make sure you're running from the `agno/` directory. The `wordpress_tools.py` imports from parent directory.

### "Google OAuth error"
Make sure `client_secret.json` and `token.json` exist in the parent directory.

### "WordPress API error"
Check the WordPress credentials in `wordpress_tools.py` are correct.

### Phoenix Tracing Not Working
Phoenix runs on port 6006. Start it separately:
```bash
python -m phoenix.server.main
```

## Files Structure

```
agno/
├── agents.py           # Main agent definition
├── wordpress_tools.py  # WordPress publishing functions
├── workflow.py         # Test agent (ignore)
├── requirements.txt    # Dependencies
├── .env               # Environment variables (create this)
└── database.db        # Agent memory database (auto-created)
```

## Notes

- Posts are created as **draft** by default for safety
- Images are resized to max 1200x800px
- Temporary images are stored in `temp_images/` and cleaned up after upload
- All conversations are saved to `database.db` for memory
