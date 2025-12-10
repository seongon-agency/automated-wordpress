"""Services module"""

from .google_docs import google_docs_to_html
from .image_processor import process_images_from_html, extract_images_with_alt
from .wordpress import (
    upload_image_to_wordpress,
    upload_images_batch,
    create_wordpress_post,
    replace_image_urls_in_html
)
from .html_transformer import (
    transform_html,
    extract_title_from_html,
    remove_title_from_html
)
from .workflow import execute_publishing_workflow
from .ai_patterns import scan_html_for_patterns, modify_patterns_with_ai

__all__ = [
    "google_docs_to_html",
    "process_images_from_html",
    "extract_images_with_alt",
    "upload_image_to_wordpress",
    "upload_images_batch",
    "create_wordpress_post",
    "replace_image_urls_in_html",
    "transform_html",
    "extract_title_from_html",
    "remove_title_from_html",
    "execute_publishing_workflow",
    "scan_html_for_patterns",
    "modify_patterns_with_ai",
]
