"""
Google Docs Creator

Creates Google Docs files containing processed HTML content.
Used to save a copy of the published content in Google Drive.
"""

import os
import re
import time
from typing import Dict, Any, Optional
from datetime import datetime

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# OAuth scopes - need Docs and Drive access
SCOPES = [
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/documents",
]


def _get_credentials_paths():
    """Get credential file paths at runtime."""
    script_dir = os.path.dirname(os.path.realpath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    credentials_dir = os.path.join(project_root, "credentials")

    token_path = os.path.join(credentials_dir, "token_docs_creator.json")
    client_secrets = os.getenv("GOOGLE_CLIENT_SECRETS",
                                os.path.join(credentials_dir, "client_secret.json"))

    return credentials_dir, token_path, client_secrets


def get_docs_credentials():
    """
    Get or refresh Google Docs API credentials with write access.
    Uses a separate token file to avoid conflicts with other credentials.

    Returns:
        Google API credentials object
    """
    from google.auth.transport.requests import Request

    credentials_dir, token_path, client_secrets = _get_credentials_paths()

    os.makedirs(credentials_dir, exist_ok=True)

    creds = None
    if os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        except Exception as e:
            print(f"Warning: Could not load existing token: {e}")
            creds = None

    # Check if credentials need refresh
    if creds and creds.expired and creds.refresh_token:
        try:
            print("   Refreshing Google Docs credentials...")
            creds.refresh(Request())
            # Save refreshed credentials
            with open(token_path, "w") as f:
                f.write(creds.to_json())
            print("   ✓ Credentials refreshed")
        except Exception as e:
            print(f"   Warning: Could not refresh credentials: {e}")
            creds = None

    if not creds or not creds.valid:
        if not os.path.exists(client_secrets):
            raise FileNotFoundError(
                f"Google client secrets file not found: {client_secrets}\n"
                f"Please place your 'client_secret.json' file in: {credentials_dir}"
            )

        print(f"Authenticating with Google Docs API...")
        flow = InstalledAppFlow.from_client_secrets_file(client_secrets, SCOPES)
        creds = flow.run_local_server(port=0, prompt="consent")

        # Save credentials
        with open(token_path, "w") as f:
            f.write(creds.to_json())
        print(f"✓ Google Docs authentication successful!")

    return creds


def extract_folder_id_from_url(folder_url: str) -> str:
    """
    Extract Google Drive folder ID from various URL formats.

    Args:
        folder_url: Google Drive folder URL

    Returns:
        Folder ID string
    """
    if not folder_url:
        return ""

    # If it's already just an ID (no slashes or dots)
    if re.match(r'^[\w-]+$', folder_url) and len(folder_url) > 20:
        return folder_url

    # Extract from URL
    patterns = [
        r'/folders/([a-zA-Z0-9_-]+)',
        r'id=([a-zA-Z0-9_-]+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, folder_url)
        if match:
            return match.group(1)

    return folder_url  # Return as-is if no pattern matches


def sanitize_doc_title(title: str) -> str:
    """
    Sanitize a string for use as a Google Docs title.

    Args:
        title: Original title (e.g., post title)

    Returns:
        Sanitized document title
    """
    if not title:
        return "Untitled"

    # Remove or replace invalid characters
    invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']

    sanitized = title
    for char in invalid_chars:
        sanitized = sanitized.replace(char, '-')

    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(' .')

    # Limit length (Google Docs has limits)
    if len(sanitized) > 200:
        sanitized = sanitized[:200]

    return sanitized or "Untitled"


def create_google_doc_with_html(
    folder_url: str,
    doc_title: str,
    html_content: str,
    wordpress_post_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a Google Docs file containing the processed HTML content.

    The document will contain:
    1. A header with the post title and metadata
    2. The raw HTML content (as text, so it can be copied)
    3. A link to the WordPress post if available

    Args:
        folder_url: Google Drive folder URL or ID
        doc_title: Title for the document (usually post title)
        html_content: The processed HTML content to save
        wordpress_post_url: Optional URL to the published WordPress post

    Returns:
        Dict containing:
        - success: bool
        - doc_id: str (Google Docs document ID)
        - doc_url: str (URL to view/edit the document)
        - error: str (if failed)
    """
    if not folder_url:
        return {
            "success": False,
            "error": "No Google Docs folder URL provided"
        }

    if not html_content:
        return {
            "success": False,
            "error": "No HTML content provided"
        }

    try:
        # Get credentials and build services
        creds = get_docs_credentials()
        drive_service = build('drive', 'v3', credentials=creds)
        docs_service = build('docs', 'v1', credentials=creds)

        # Extract folder ID
        folder_id = extract_folder_id_from_url(folder_url)
        if not folder_id:
            return {
                "success": False,
                "error": f"Could not extract folder ID from: {folder_url}"
            }

        # Sanitize document title
        sanitized_title = sanitize_doc_title(doc_title)

        # Add timestamp to make unique
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        full_title = f"{sanitized_title} - HTML ({timestamp})"

        print(f"   📄 Creating Google Doc: {full_title}")

        # Step 1: Create a new Google Doc in the specified folder
        file_metadata = {
            'name': full_title,
            'mimeType': 'application/vnd.google-apps.document',
            'parents': [folder_id]
        }

        doc_file = drive_service.files().create(
            body=file_metadata,
            fields='id, name, webViewLink'
        ).execute()

        doc_id = doc_file.get('id')
        doc_url = doc_file.get('webViewLink')

        print(f"   ✓ Document created: {doc_file.get('name')}")

        # Step 2: Add content to the document
        # Build the document content with metadata header and HTML
        requests = []

        # Start position for inserting text
        index = 1

        # Add header with post info
        header_text = f"📝 {sanitized_title}\n\n"
        header_text += f"📅 Tạo lúc: {timestamp}\n"
        if wordpress_post_url:
            header_text += f"🔗 WordPress: {wordpress_post_url}\n"
        header_text += "\n" + "="*60 + "\n\n"
        header_text += "HTML Content:\n\n"

        requests.append({
            'insertText': {
                'location': {'index': index},
                'text': header_text
            }
        })
        index += len(header_text)

        # Add HTML content
        requests.append({
            'insertText': {
                'location': {'index': index},
                'text': html_content
            }
        })

        # Execute the batch update
        docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': requests}
        ).execute()

        print(f"   ✓ Content added to document")
        print(f"   🔗 Document URL: {doc_url}")

        return {
            "success": True,
            "doc_id": doc_id,
            "doc_url": doc_url,
            "doc_title": full_title
        }

    except HttpError as e:
        error_msg = f"Google API error: {e.resp.status} - {e._get_reason()}"
        print(f"   ✗ {error_msg}")
        return {
            "success": False,
            "error": error_msg
        }

    except Exception as e:
        error_msg = f"Failed to create Google Doc: {str(e)}"
        print(f"   ✗ {error_msg}")
        return {
            "success": False,
            "error": error_msg
        }


# Make available as tool
create_google_doc_with_html.__annotations__ = {
    'folder_url': str,
    'doc_title': str,
    'html_content': str,
    'wordpress_post_url': Optional[str],
    'return': Dict[str, Any]
}
