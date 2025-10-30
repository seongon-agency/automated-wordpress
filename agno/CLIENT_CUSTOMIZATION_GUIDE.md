# Client HTML Customization Guide

This guide explains how to add custom HTML transformations for different WordPress clients without using AI tokens.

## How It Works

**Problem:** Different WordPress clients have custom CSS/HTML that conflicts with standard Google Docs HTML.

**Solution:** Define transformation rules that are applied programmatically (no tokens used, instant processing).

## Quick Start

### 1. View Available Clients

Ask the agent:
```
"What clients are available?"
```

Or use the simple script:
```python
from wordpress_tools import list_client_configurations
print(list_client_configurations())
```

### 2. Publish with a Specific Client

Tell the agent:
```
"Publish this doc for Client A: https://docs.google.com/document/d/..."
```

The agent will automatically apply Client A's HTML customizations.

## Adding a New Client

### Step 1: Open `client_configs.py`

### Step 2: Create Your Configuration

```python
CLIENT_YOUR_NAME = {
    "name": "Your Client Name",
    "description": "Brief description of customizations",
    "transformations": {
        # See configuration options below
    }
}
```

### Step 3: Add to Registry

```python
CLIENT_REGISTRY = {
    "default": DEFAULT_CONFIG,
    # ... existing clients ...
    "your-client": CLIENT_YOUR_NAME  # Add your client here
}
```

## Configuration Options

### 1. Tag Replacements

Replace one HTML tag with another.

**Example:** Change `<strong>` to `<b>`

```python
"tag_replacements": {
    "strong": {
        "new_tag": "b",
        "preserve_content": True,  # Keep the text inside
        "add_class": "custom-bold"  # Optional: add a class
    }
}
```

**Before:**
```html
<p>This is <strong>important</strong> text</p>
```

**After:**
```html
<p>This is <b class="custom-bold">important</b> text</p>
```

### 2. Attribute Rules

Modify attributes of existing tags (add classes, styles, attributes).

**Example:** Add custom class to all headings

```python
"attribute_rules": {
    "h2": {
        "add_class": "section-heading",
        "add_style": "color: #e74c3c; margin-bottom: 20px;"
    },
    "p": {
        "add_class": "content-paragraph",
        "add_attribute": {"data-aos": "fade-up"}  # Add any attribute
    }
}
```

**Before:**
```html
<h2>Heading</h2>
<p>Paragraph</p>
```

**After:**
```html
<h2 class="section-heading" style="color: #e74c3c; margin-bottom: 20px;">Heading</h2>
<p class="content-paragraph" data-aos="fade-up">Paragraph</p>
```

**Available Options:**
- `add_class` - Add CSS class(es)
- `add_style` - Add inline styles
- `add_attribute` - Add any HTML attribute
- `remove_style` - Remove all inline styles (True/False)
- `remove_attribute` - Remove specific attributes (list)

### 3. Style Injections

Add inline styles to all instances of a tag.

**Example:** Consistent styling for all blockquotes

```python
"style_injections": {
    "blockquote": "border-left: 4px solid #3498db; padding-left: 20px; font-style: italic;",
    "p": "line-height: 1.8; margin-bottom: 16px;"
}
```

### 4. Class Mappings

Replace one class name with another.

**Example:** Replace WordPress alignment classes

```python
"class_mappings": {
    "aligncenter": "text-center custom-center",
    "alignright": "text-end",
    "wp-image-123": "responsive-img img-fluid"
}
```

**Before:**
```html
<img class="aligncenter wp-image-123" src="...">
```

**After:**
```html
<img class="text-center custom-center responsive-img img-fluid" src="...">
```

### 5. Custom Wrappers

Wrap specific tags in custom HTML structure.

**Example:** Wrap headings in containers

```python
"custom_wrappers": [
    {
        "wrap_tag": "h2",
        "wrapper": "<div class='heading-container'>{content}</div>"
    },
    {
        "wrap_tag": "ul",
        "wrapper": "<div class='list-wrapper'><div class='list-inner'>{content}</div></div>"
    }
]
```

**Before:**
```html
<h2>My Heading</h2>
```

**After:**
```html
<div class='heading-container'><h2>My Heading</h2></div>
```

## Complete Example

Here's a real client with multiple customizations:

```python
CLIENT_ECOMMERCE = {
    "name": "E-Commerce Client",
    "description": "Custom styling for product pages",
    "transformations": {
        # Change strong to span with class
        "tag_replacements": {
            "strong": {
                "new_tag": "span",
                "preserve_content": True,
                "add_class": "fw-700"
            }
        },

        # Add classes to headings and paragraphs
        "attribute_rules": {
            "h2": {
                "add_class": "product-title",
                "add_style": "color: #2c3e50; font-size: 28px;"
            },
            "h3": {
                "add_class": "product-subtitle"
            },
            "p": {
                "add_class": "product-description"
            },
            "img": {
                "add_class": "product-image img-fluid",
                "add_attribute": {"loading": "lazy"}
            }
        },

        # Inject consistent styles
        "style_injections": {
            "ul": "list-style: none; padding-left: 0;",
            "li": "padding: 8px 0; border-bottom: 1px solid #eee;"
        },

        # Replace old classes
        "class_mappings": {
            "aligncenter": "text-center mx-auto",
            "alignright": "text-end ms-auto"
        },

        # Wrap lists in containers
        "custom_wrappers": [
            {
                "wrap_tag": "ul",
                "wrapper": "<div class='feature-list'>{content}</div>"
            }
        ]
    }
}

# Add to registry
CLIENT_REGISTRY["ecommerce"] = CLIENT_ECOMMERCE
```

## Testing Your Configuration

### Method 1: Use the Agent

```
User: "List available clients"
Agent: [Shows all clients including yours]

User: "Publish this doc for ecommerce client: [URL]"
Agent: [Applies your customizations automatically]
```

### Method 2: Test Directly

```python
from html_transformer import HTMLTransformer
from client_configs import CLIENT_ECOMMERCE

# Your test HTML
test_html = """
<h2>Product Title</h2>
<p>This is <strong>very important</strong> information.</p>
<ul>
    <li>Feature 1</li>
    <li>Feature 2</li>
</ul>
"""

# Apply transformations
transformer = HTMLTransformer(CLIENT_ECOMMERCE)
result = transformer.transform(test_html)

print(result)
```

## Common Use Cases

### Use Case 1: Client Uses Bootstrap

```python
"tag_replacements": {
    "strong": {"new_tag": "span", "preserve_content": True, "add_class": "fw-bold"},
    "em": {"new_tag": "span", "preserve_content": True, "add_class": "fst-italic"}
},
"attribute_rules": {
    "img": {"add_class": "img-fluid"},
    "table": {"add_class": "table table-striped"}
}
```

### Use Case 2: Client Uses Tailwind CSS

```python
"attribute_rules": {
    "h2": {"add_class": "text-3xl font-bold text-gray-800 mb-4"},
    "p": {"add_class": "text-base leading-relaxed mb-4"},
    "img": {"add_class": "rounded-lg shadow-md"}
}
```

### Use Case 3: Client Needs Specific Color Scheme

```python
"style_injections": {
    "h2": "color: #FF6B6B;",
    "h3": "color: #4ECDC4;",
    "p": "color: #2C3E50;",
    "a": "color: #3498DB; text-decoration: underline;"
}
```

### Use Case 4: Client Uses Custom Components

```python
"custom_wrappers": [
    {
        "wrap_tag": "blockquote",
        "wrapper": "<div class='quote-component'><div class='quote-icon'>\"</div>{content}</div>"
    },
    {
        "wrap_tag": "img",
        "wrapper": "<div class='image-component'>{content}<div class='image-overlay'></div></div>"
    }
]
```

## Performance Notes

- **Zero AI tokens used** - All transformations are programmatic
- **Instant processing** - Even for very long posts
- **No length limits** - Works with posts of any size
- **Efficient** - Uses BeautifulSoup DOM manipulation

## Troubleshooting

### Issue: Transformations Not Applied

**Check:**
1. Is the client_id correct?
2. Did you add it to `CLIENT_REGISTRY`?
3. Restart the agent after making changes

### Issue: HTML Looks Wrong

**Solution:** Test your configuration on a small sample first:

```python
test_html = "<p>Simple <strong>test</strong></p>"
transformer = HTMLTransformer(YOUR_CONFIG)
print(transformer.transform(test_html))
```

### Issue: Classes Not Appearing

**Check:** Make sure you're using `add_class`, not `class`:

```python
# Wrong
"h2": {"class": "my-class"}

# Correct
"h2": {"add_class": "my-class"}
```

## Best Practices

1. **Start Simple** - Add one transformation at a time and test
2. **Use Descriptive Names** - `client-ecommerce-store` is better than `client1`
3. **Document Requirements** - Add clear description of what the client needs
4. **Test on Sample HTML** - Before applying to real posts
5. **Keep Backups** - Save original HTML if making major changes

## Need Help?

The transformation engine supports:
- ✅ Tag replacements
- ✅ Adding/removing classes
- ✅ Adding/removing styles
- ✅ Adding/removing any attribute
- ✅ Class name mappings
- ✅ Wrapping in custom HTML
- ✅ Multiple transformations in sequence

If you need a transformation that's not listed here, you can extend the `HTMLTransformer` class in `html_transformer.py`.
