"""
Configuration settings for SEO Blog Publishing Agent

Supports both Streamlit secrets (for deployment) and .env file (for local development).
Priority: st.secrets > os.getenv > default value
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env (for local development)
load_dotenv()


def get_secret(key: str, default=None):
    """
    Get a secret value with fallback chain:
    1. Streamlit secrets (st.secrets) - for Streamlit Cloud deployment
    2. Environment variable (os.getenv) - for local development or other deployments
    3. Default value

    Args:
        key: The secret/environment variable name
        default: Default value if not found anywhere

    Returns:
        The secret value or default
    """
    # Try Streamlit secrets first (only when running in Streamlit)
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and key in st.secrets:
            return st.secrets[key]
    except (ImportError, Exception):
        # Not running in Streamlit context or st.secrets not available
        pass

    # Fall back to environment variable
    env_value = os.getenv(key)
    if env_value is not None:
        return env_value

    # Return default
    return default


# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
TOOLS_DIR = BASE_DIR / "tools"
UTILS_DIR = BASE_DIR / "utils"
OUTPUT_DIR = BASE_DIR / "output"
IMAGES_DIR = BASE_DIR / "processed_images"

# Create output directories
OUTPUT_DIR.mkdir(exist_ok=True)
IMAGES_DIR.mkdir(exist_ok=True)

# Google Drive API settings
GOOGLE_TOKEN_PATH = get_secret("GOOGLE_TOKEN_PATH", "token.json")
GOOGLE_CLIENT_SECRETS = get_secret(
    "GOOGLE_CLIENT_SECRETS",
    str(BASE_DIR / "client_secret.json")
)
GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/spreadsheets.readonly",
]

# Anthropic API settings
ANTHROPIC_API_KEY = get_secret("ANTHROPIC_API_KEY")

# WordPress API settings
WP_BASE_URL = get_secret("WP_BASE_URL")
WP_USERNAME = get_secret("WP_USERNAME")
WP_APP_PASS = get_secret("WP_APP_PASS")

# Image processing defaults
DEFAULT_IMAGE_WIDTH = int(get_secret("DEFAULT_IMAGE_WIDTH", "800"))
DEFAULT_IMAGE_HEIGHT = None  # Maintain aspect ratio
IMAGE_QUALITY = int(get_secret("IMAGE_QUALITY", "92"))
IMAGE_FORMAT = get_secret("IMAGE_FORMAT", "JPEG")

# Agent settings
AGENT_MODEL = get_secret("AGENT_MODEL", "claude-sonnet-4-5-20250929")
AGENT_DEBUG = str(get_secret("AGENT_DEBUG", "false")).lower() == "true"

# Validation
def validate_config():
    """Validate required configuration."""
    missing = []

    if not ANTHROPIC_API_KEY:
        missing.append("ANTHROPIC_API_KEY")

    if not os.path.exists(GOOGLE_CLIENT_SECRETS):
        missing.append("GOOGLE_CLIENT_SECRETS (client_secret.json file)")

    if missing:
        raise ValueError(
            f"Missing required configuration: {', '.join(missing)}. "
            "Please check your .streamlit/secrets.toml or .env file and ensure all required variables are set."
        )

    return True


if __name__ == "__main__":
    print("Configuration Settings:")
    print(f"  Base Directory: {BASE_DIR}")
    print(f"  Anthropic API Key: {'Set' if ANTHROPIC_API_KEY else 'Missing'}")
    print(f"  Google Client Secrets: {'Found' if os.path.exists(GOOGLE_CLIENT_SECRETS) else 'Not found'}")
    print(f"  WordPress Configured: {'Yes' if all([WP_BASE_URL, WP_USERNAME, WP_APP_PASS]) else 'No'}")
    print(f"  Default Image Width: {DEFAULT_IMAGE_WIDTH}px")
    print(f"  Agent Model: {AGENT_MODEL}")

    try:
        validate_config()
        print("\nConfiguration is valid!")
    except ValueError as e:
        print(f"\nConfiguration error: {e}")
