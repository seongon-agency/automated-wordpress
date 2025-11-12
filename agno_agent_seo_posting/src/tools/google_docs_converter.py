"""
Google Docs to HTML Converter

Converts Google Docs to HTML using Google Drive API.
Requires OAuth authentication via client_secret.json and token.json.
"""

import os
import re
from typing import Dict, Any
from urllib.parse import urlparse, parse_qs
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import httplib2


# OAuth configuration
TOKEN_PATH = "token.json"
CLIENT_SECRETS = os.getenv("GOOGLE_CLIENT_SECRETS", "client_secret.json")
SCOPES = [
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/spreadsheets.readonly",
]


def get_credentials():
    """
    Get or refresh Google API credentials.

    Returns:
        Google API credentials object
    """
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if not os.path.exists(CLIENT_SECRETS):
            raise FileNotFoundError(
                f"Google client secrets file not found: {CLIENT_SECRETS}. "
                "Please download from Google Cloud Console."
            )

        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS, SCOPES)
        creds = flow.run_local_server(port=0, prompt="consent")

        # Save credentials for next run
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())

    return creds


def extract_file_id(url: str) -> str:
    """
    Extract Google Drive file ID from various URL formats.

    Args:
        url: Google Docs/Drive URL

    Returns:
        File ID string

    Examples:
        /document/d/<ID> → <ID>
        /file/d/<ID> → <ID>
        ?id=<ID> → <ID>
    """
    # Try /document/d/<ID> pattern
    match = re.search(r"/document/d/([a-zA-Z0-9_-]+)", url)
    if match:
        return match.group(1)

    # Try /file/d/<ID> pattern
    match = re.search(r"/file/d/([a-zA-Z0-9_-]+)", url)
    if match:
        return match.group(1)

    # Try query parameter ?id=<ID>
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    if "id" in qs and qs["id"]:
        return qs["id"][0]

    raise ValueError(f"Could not extract file ID from URL: {url}")


def google_docs_to_html(google_docs_url: str) -> Dict[str, Any]:
    """
    Convert a Google Docs URL to HTML using Google Drive API.

    This function uses the proper Google Drive API to export documents as HTML.
    Requires authentication via client_secret.json (first run opens browser).

    Args:
        google_docs_url: Google Docs URL (edit or view URL)

    Returns:
        Dict containing:
        - success: bool
        - raw_html: str (HTML content from Google)
        - document_name: str (document title)
        - file_id: str (Google Drive file ID)
        - error: str (if failed)

    Example:
        result = google_docs_to_html("https://docs.google.com/document/d/ABC123/edit")
        if result['success']:
            html = result['raw_html']
            title = result['document_name']
    """
    try:
        # Extract file ID from URL
        file_id = extract_file_id(google_docs_url)

        # Get credentials and build Drive API client with increased timeout
        creds = get_credentials()

        # Create HTTP object with longer timeout (60 seconds instead of default 10)
        # Using httplib2 for better timeout control
        import socket
        original_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(60)

        try:
            drive = build("drive", "v3", credentials=creds)
        finally:
            # Restore original timeout
            socket.setdefaulttimeout(original_timeout)

        # Get file metadata to verify it's a Google Doc
        meta = drive.files().get(
            fileId=file_id,
            fields="id,name,mimeType"
        ).execute()

        # Verify it's a Google Doc
        if meta["mimeType"] != "application/vnd.google-apps.document":
            return {
                "success": False,
                "error": f"Not a Google Doc. File type: {meta['mimeType']}, Name: {meta['name']}"
            }

        # Export as HTML
        html_bytes = drive.files().export(
            fileId=file_id,
            mimeType="text/html"
        ).execute()

        # Decode to string
        html_text = html_bytes.decode("utf-8", errors="ignore")

        return {
            "success": True,
            "raw_html": html_text,
            "document_name": meta["name"],
            "file_id": file_id
        }

    except FileNotFoundError as e:
        return {
            "success": False,
            "error": str(e)
        }

    except ValueError as e:
        return {
            "success": False,
            "error": str(e)
        }

    except Exception as e:
        error_msg = str(e)

        # Provide helpful error messages for common issues
        if "404" in error_msg:
            return {
                "success": False,
                "error": "Document not found. Check the URL and ensure you have access to this document."
            }
        elif "403" in error_msg or "Permission denied" in error_msg:
            return {
                "success": False,
                "error": "Permission denied. Ensure the document is shared with your Google account."
            }
        else:
            return {
                "success": False,
                "error": f"Failed to export document: {error_msg}"
            }



# Make this function available as an Agno tool
google_docs_to_html.__annotations__ = {
    'google_docs_url': str,
    'return': Dict[str, Any]
}
