# Example: Creating a Client Config with the Agent

This example shows how to create a new client configuration by providing HTML examples to the agent.

## Scenario

You have a client "TechBlog Co" that needs:
- Use `<b>` instead of `<strong>` for bold text
- Add custom classes to headings
- Add specific styling to paragraphs

## Step-by-Step Conversation

### Step 1: Tell the agent you want to create a config

```
You: "I need to create a new client configuration for TechBlog Co"
```

### Step 2: Agent asks for details

```
Agent: "I can help you create a client configuration! I'll need:

1. **Client Name**: Display name (e.g., "TechBlog Co")
2. **Client ID**: Unique identifier (lowercase with dashes, e.g., "techblog-co")
3. **Description**: What customizations are needed
4. **Original HTML**: Example HTML from Google Docs (the 'before' state)
5. **Desired HTML**: Example HTML the client needs (the 'after' state)

Please provide these details."
```

### Step 3: Provide the information

```
You: "Here are the details:

Client Name: TechBlog Co
Client ID: techblog-co
Description: Uses <b> tags, custom heading classes, and specific paragraph styling

Original HTML:
<h2>Product Features</h2>
<p>This product has <strong>amazing</strong> capabilities.</p>
<ul>
  <li>Feature one</li>
  <li>Feature two</li>
</ul>

Desired HTML:
<h2 class="tech-heading" style="color: #2c3e50; font-size: 32px;">Product Features</h2>
<p class="tech-content" style="line-height: 1.8;">This product has <b class="fw-700">amazing</b> capabilities.</p>
<ul class="tech-list">
  <li>Feature one</li>
  <li>Feature two</li>
</ul>
"
```

### Step 4: Agent analyzes and creates config

```
Agent: "I'll analyze the HTML differences and create the configuration for you..."

[Agent calls create_new_client_config()]

✅ Client configuration created successfully!

**Client Name**: TechBlog Co
**Client ID**: techblog-co

**Detected Transformations**:
- Tag replacement: `<strong>` → `<b>` with class "fw-700"
- H2 tags get class "tech-heading" and custom styling
- Paragraphs get class "tech-content" and line-height styling
- UL tags get class "tech-list"

The configuration has been saved to `client_configs.py`.

You can now use it by saying:
"Publish this doc for techblog-co: [Google Docs URL]"
```

### Step 5: Use the new config

```
You: "Publish this doc for techblog-co: https://docs.google.com/document/d/ABC123/edit"

Agent: 🎨 Applying client customizations: TechBlog Co
       [Processes with custom transformations]
       ✅ Published! All HTML follows TechBlog Co's requirements.
```

## What Happens Behind the Scenes

1. **Agent analyzes** the differences between original and desired HTML
2. **Detects patterns**:
   - Tag replacements (`strong` → `b`)
   - Attribute additions (classes, styles)
   - Structural changes
3. **Generates configuration** in Python format
4. **Saves** to `client_configs.py`
5. **Immediately available** for use

## Benefits

✅ **One-time AI usage** - Uses tokens once to create config
✅ **Zero tokens after** - All future posts use the config programmatically
✅ **No manual coding** - Agent figures out the transformation rules
✅ **Instant results** - Config is ready to use immediately

## Real Example

Here's what actually gets added to `client_configs.py`:

```python
# Auto-generated configuration for TechBlog Co
CLIENT_TECHBLOG_CO = {
    "name": "TechBlog Co",
    "description": "Uses <b> tags, custom heading classes, and specific paragraph styling",
    "transformations": {
        "tag_replacements": {
            "strong": {
                "new_tag": "b",
                "preserve_content": true,
                "add_class": "fw-700"
            }
        },
        "attribute_rules": {
            "h2": {
                "add_class": "tech-heading",
                "add_style": "color: #2c3e50; font-size: 32px;"
            },
            "p": {
                "add_class": "tech-content",
                "add_style": "line-height: 1.8;"
            },
            "ul": {
                "add_class": "tech-list"
            }
        },
        "style_injections": {},
        "class_mappings": {},
        "custom_wrappers": []
    }
}

# Add to registry
CLIENT_REGISTRY["techblog-co"] = CLIENT_TECHBLOG_CO
```

## Tips for Best Results

1. **Provide clear examples** - Show at least 2-3 different elements (headings, paragraphs, lists)
2. **Be consistent** - Make sure your "desired HTML" follows a consistent pattern
3. **Test first** - After creation, test with a sample post before using in production
4. **Start simple** - Begin with basic transformations, add complexity later

## Testing the Generated Config

After the agent creates the config, test it:

```bash
cd agno
python test_client_transforms.py techblog-co
```

This will show you exactly how your HTML will be transformed.

## Editing Later

If you need to adjust the config:

1. Open `client_configs.py`
2. Find `CLIENT_TECHBLOG_CO`
3. Edit the transformation rules
4. Restart the agent

The agent can also help you edit existing configs by creating a new one and merging the rules.
