"""
Configuration settings for SEO Blog Publishing Agent
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
GOOGLE_TOKEN_PATH = os.getenv("GOOGLE_TOKEN_PATH", "token.json")
GOOGLE_CLIENT_SECRETS = os.getenv(
    "GOOGLE_CLIENT_SECRETS",
    str(BASE_DIR / "client_secret.json")
)
GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/spreadsheets.readonly",
]

# Anthropic API settings
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# WordPress API settings
WP_BASE_URL = os.getenv("WP_BASE_URL")
WP_USERNAME = os.getenv("WP_USERNAME")
WP_APP_PASS = os.getenv("WP_APP_PASS")

# Image processing defaults
DEFAULT_IMAGE_WIDTH = int(os.getenv("DEFAULT_IMAGE_WIDTH", "800"))
DEFAULT_IMAGE_HEIGHT = None  # Maintain aspect ratio
IMAGE_QUALITY = int(os.getenv("IMAGE_QUALITY", "92"))
IMAGE_FORMAT = os.getenv("IMAGE_FORMAT", "JPEG")

# Agent settings
AGENT_MODEL = os.getenv("AGENT_MODEL", "claude-sonnet-4-5-20250929")
AGENT_DEBUG = os.getenv("AGENT_DEBUG", "false").lower() == "true"

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
            "Please check your .env file and ensure all required variables are set."
        )

    return True


if __name__ == "__main__":
    print("Configuration Settings:")
    print(f"  Base Directory: {BASE_DIR}")
    print(f"  Anthropic API Key: {'✓ Set' if ANTHROPIC_API_KEY else '✗ Missing'}")
    print(f"  Google Client Secrets: {'✓ Found' if os.path.exists(GOOGLE_CLIENT_SECRETS) else '✗ Not found'}")
    print(f"  WordPress Configured: {'✓ Yes' if all([WP_BASE_URL, WP_USERNAME, WP_APP_PASS]) else '✗ No'}")
    print(f"  Default Image Width: {DEFAULT_IMAGE_WIDTH}px")
    print(f"  Agent Model: {AGENT_MODEL}")

    try:
        validate_config()
        print("\n✅ Configuration is valid!")
    except ValueError as e:
        print(f"\n❌ Configuration error: {e}")
