"""
Configuration package for SEO Blog Publishing Agent
"""

from .settings import (
    BASE_DIR,
    TOOLS_DIR,
    UTILS_DIR,
    OUTPUT_DIR,
    IMAGES_DIR,
    ANTHROPIC_API_KEY,
    WP_BASE_URL,
    WP_USERNAME,
    WP_APP_PASS,
    DEFAULT_IMAGE_WIDTH,
    IMAGE_QUALITY,
    validate_config
)

__all__ = [
    'BASE_DIR',
    'TOOLS_DIR',
    'UTILS_DIR',
    'OUTPUT_DIR',
    'IMAGES_DIR',
    'ANTHROPIC_API_KEY',
    'WP_BASE_URL',
    'WP_USERNAME',
    'WP_APP_PASS',
    'DEFAULT_IMAGE_WIDTH',
    'IMAGE_QUALITY',
    'validate_config'
]
