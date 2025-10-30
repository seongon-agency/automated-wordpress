"""
Client-Specific HTML Transformation Configurations

Each client can have custom HTML/CSS rules that are applied BEFORE publishing to WordPress.
This prevents token waste by using programmatic transformations instead of AI processing.

Configuration Structure:
- tag_replacements: Replace HTML tags (e.g., <strong> -> <b>)
- attribute_transformations: Modify tag attributes
- style_rules: Add/modify inline styles
- class_mappings: Replace or add CSS classes
- custom_wrappers: Wrap content in specific structures
"""

# Default configuration (standard WordPress, same as current behavior)
DEFAULT_CONFIG = {
    "name": "Default WordPress",
    "description": "Standard WordPress HTML format",
    "transformations": {
        "tag_replacements": {},  # No replacements
        "attribute_rules": {},
        "style_injections": {},
        "class_mappings": {},
        "custom_wrappers": []
    }
}

# Example: Client with custom bold styling
CLIENT_CUSTOM_BOLD = {
    "name": "Client A - Custom Bold",
    "description": "Uses <b> instead of <strong>, custom color for bold text",
    "transformations": {
        "tag_replacements": {
            "strong": {"new_tag": "b", "preserve_content": True}
        },
        "attribute_rules": {
            "b": {
                "add_style": "font-weight: 700; color: #2c3e50;"
            }
        },
        "style_injections": {},
        "class_mappings": {},
        "custom_wrappers": []
    }
}

# Example: Client with custom heading styles
CLIENT_CUSTOM_HEADINGS = {
    "name": "Client B - Custom Headings",
    "description": "Custom heading styles with specific classes",
    "transformations": {
        "tag_replacements": {},
        "attribute_rules": {
            "h2": {
                "add_class": "custom-heading-2",
                "add_style": "color: #e74c3c; font-family: 'Montserrat', sans-serif;"
            },
            "h3": {
                "add_class": "custom-heading-3",
                "add_style": "color: #3498db; font-weight: 600;"
            }
        },
        "style_injections": {
            "p": "line-height: 1.8; margin-bottom: 20px;"
        },
        "class_mappings": {},
        "custom_wrappers": []
    }
}

# Example: Client with custom list styling
CLIENT_CUSTOM_LISTS = {
    "name": "Client C - Custom Lists",
    "description": "Custom bullet points and list styling",
    "transformations": {
        "tag_replacements": {},
        "attribute_rules": {
            "ul": {
                "add_class": "custom-list-style"
            },
            "li": {
                "add_style": "margin-bottom: 12px; padding-left: 10px;"
            }
        },
        "style_injections": {},
        "class_mappings": {},
        "custom_wrappers": [
            {
                "wrap_tag": "ul",
                "wrapper": "<div class='list-container'>{content}</div>"
            }
        ]
    }
}

# Example: Client with completely custom structure
CLIENT_ADVANCED = {
    "name": "Client D - Advanced Custom",
    "description": "Complex custom HTML structure with specific requirements",
    "transformations": {
        "tag_replacements": {
            "strong": {"new_tag": "span", "preserve_content": True, "add_class": "fw-bold"},
            "em": {"new_tag": "span", "preserve_content": True, "add_class": "font-italic"}
        },
        "attribute_rules": {
            "p": {
                "add_class": "content-paragraph",
                "add_style": "font-size: 16px; color: #333;"
            },
            "h2": {
                "add_class": "section-title",
                "remove_style": True  # Remove all inline styles
            },
            "img": {
                "add_class": "responsive-image",
                "add_attribute": {"loading": "lazy"}
            }
        },
        "style_injections": {
            "blockquote": "border-left: 4px solid #3498db; padding-left: 20px; font-style: italic; color: #555;"
        },
        "class_mappings": {
            "aligncenter": "text-center custom-center",
            "alignright": "text-right custom-right"
        },
        "custom_wrappers": [
            {
                "wrap_tag": "h2",
                "wrapper": "<div class='heading-wrapper'>{content}</div>"
            }
        ]
    }
}

# Registry of all available clients
CLIENT_REGISTRY = {
    "default": DEFAULT_CONFIG,
    "client-a": CLIENT_CUSTOM_BOLD,
    "client-b": CLIENT_CUSTOM_HEADINGS,
    "client-c": CLIENT_CUSTOM_LISTS,
    "client-d": CLIENT_ADVANCED
}


def get_client_config(client_id: str) -> dict:
    """
    Get configuration for a specific client.

    Args:
        client_id: Client identifier (e.g., 'client-a', 'default')

    Returns:
        Client configuration dictionary
    """
    return CLIENT_REGISTRY.get(client_id, DEFAULT_CONFIG)


def list_available_clients() -> list[dict]:
    """
    List all available client configurations.

    Returns:
        List of dicts with client_id, name, and description
    """
    clients = []
    for client_id, config in CLIENT_REGISTRY.items():
        clients.append({
            "client_id": client_id,
            "name": config["name"],
            "description": config["description"]
        })
    return clients


def add_client_config(client_id: str, config: dict) -> bool:
    """
    Add a new client configuration dynamically.

    Args:
        client_id: Unique identifier for the client
        config: Configuration dictionary

    Returns:
        True if added successfully
    """
    if client_id in CLIENT_REGISTRY:
        return False  # Already exists

    CLIENT_REGISTRY[client_id] = config
    return True


# Example of how to create a new client config
"""
NEW_CLIENT = {
    "name": "Your Client Name",
    "description": "Description of custom requirements",
    "transformations": {
        "tag_replacements": {
            # "old_tag": {"new_tag": "new_tag", "preserve_content": True}
        },
        "attribute_rules": {
            # "tag_name": {
            #     "add_class": "class-name",
            #     "add_style": "style-string",
            #     "add_attribute": {"attr": "value"}
            # }
        },
        "style_injections": {
            # "tag_name": "inline-style-string"
        },
        "class_mappings": {
            # "old-class": "new-class"
        },
        "custom_wrappers": [
            # {
            #     "wrap_tag": "tag_to_wrap",
            #     "wrapper": "<div class='wrapper'>{content}</div>"
            # }
        ]
    }
}

# Add it to registry
CLIENT_REGISTRY['your-client-id'] = NEW_CLIENT
"""
