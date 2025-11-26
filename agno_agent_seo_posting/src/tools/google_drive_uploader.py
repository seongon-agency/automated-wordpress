"""
Google Drive Uploader

Uploads images to Google Drive folders for backup.
Creates subfolders named after post titles and uploads resized images.
"""

import os
import re
import time
import socket
from typing import Dict, Any, List, Optional
from pathlib import Path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# NOTE: Do NOT set global socket timeout here as it affects all network operations


# OAuth scopes - need write access for uploading
SCOPES = [
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive",
]


def _get_credentials_paths():
    """Get credential file paths at runtime."""
    script_dir = os.path.dirname(os.path.realpath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    credentials_dir = os.path.join(project_root, "credentials")

    token_path = os.path.join(credentials_dir, "token_drive_upload.json")
    client_secrets = os.getenv("GOOGLE_CLIENT_SECRETS",
                                os.path.join(credentials_dir, "client_secret.json"))

    return credentials_dir, token_path, client_secrets


def get_drive_credentials():
    """
    Get or refresh Google Drive API credentials with write access.
    Uses a separate token file to avoid conflicts with read-only credentials.

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
            print("   Refreshing Google Drive credentials...")
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

        print(f"Authenticating with Google Drive API (write access)...")
        flow = InstalledAppFlow.from_client_secrets_file(client_secrets, SCOPES)
        creds = flow.run_local_server(port=0, prompt="consent")

        # Save credentials
        with open(token_path, "w") as f:
            f.write(creds.to_json())
        print(f"✓ Google Drive authentication successful!")

    return creds


def extract_folder_id_from_url(folder_url: str) -> str:
    """
    Extract Google Drive folder ID from various URL formats.

    Args:
        folder_url: Google Drive folder URL

    Returns:
        Folder ID string

    Supported formats:
        - https://drive.google.com/drive/folders/FOLDER_ID
        - https://drive.google.com/drive/u/0/folders/FOLDER_ID
        - https://drive.google.com/drive/folders/FOLDER_ID?usp=sharing
        - Just the folder ID directly
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


def sanitize_folder_name(name: str) -> str:
    """
    Sanitize a string for use as a Google Drive folder name.

    Args:
        name: Original name (e.g., post title)

    Returns:
        Sanitized folder name
    """
    if not name:
        return "Untitled"

    # Remove or replace invalid characters
    # Google Drive allows most characters but some are problematic
    invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']

    sanitized = name
    for char in invalid_chars:
        sanitized = sanitized.replace(char, '-')

    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(' .')

    # Limit length (Google Drive has a 255 char limit)
    if len(sanitized) > 200:
        sanitized = sanitized[:200]

    return sanitized or "Untitled"


def create_drive_folder(
    service,
    parent_folder_id: str,
    folder_name: str
) -> Dict[str, Any]:
    """
    Create a folder in Google Drive.

    Args:
        service: Google Drive API service
        parent_folder_id: ID of parent folder
        folder_name: Name for new folder

    Returns:
        Dict with folder_id and folder_url
    """
    sanitized_name = sanitize_folder_name(folder_name)

    file_metadata = {
        'name': sanitized_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_folder_id]
    }

    folder = service.files().create(
        body=file_metadata,
        fields='id, name, webViewLink'
    ).execute()

    return {
        'folder_id': folder.get('id'),
        'folder_name': folder.get('name'),
        'folder_url': folder.get('webViewLink')
    }


def upload_file_to_drive(
    service,
    folder_id: str,
    file_path: str,
    filename: Optional[str] = None,
    max_retries: int = 3
) -> Dict[str, Any]:
    """
    Upload a file to Google Drive folder with retry logic.

    Args:
        service: Google Drive API service
        folder_id: Target folder ID
        file_path: Local file path
        filename: Optional custom filename (uses original if not provided)
        max_retries: Maximum number of retry attempts

    Returns:
        Dict with file_id, filename, and file_url
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    upload_name = filename or path.name

    # Determine MIME type
    extension = path.suffix.lower()
    mime_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
    }
    mime_type = mime_types.get(extension, 'application/octet-stream')

    file_metadata = {
        'name': upload_name,
        'parents': [folder_id]
    }

    last_error = None

    for attempt in range(max_retries):
        try:
            # Create a fresh MediaFileUpload for each attempt
            media = MediaFileUpload(
                file_path,
                mimetype=mime_type,
                resumable=True,
                chunksize=1024*1024  # 1MB chunks for more reliable uploads
            )

            request = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink'
            )

            # Use resumable upload with progress
            response = None
            while response is None:
                status, response = request.next_chunk()

            return {
                'file_id': response.get('id'),
                'filename': response.get('name'),
                'file_url': response.get('webViewLink')
            }

        except (BrokenPipeError, ConnectionResetError, socket.error) as e:
            last_error = e
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2  # 2, 4, 6 seconds
                print(f"      ⚠️ Connection error, retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
            else:
                raise

        except HttpError as e:
            last_error = e
            if e.resp.status in [500, 502, 503, 504] and attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2
                print(f"      ⚠️ Server error {e.resp.status}, retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
            else:
                raise

        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2
                print(f"      ⚠️ Upload error: {str(e)[:50]}, retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
            else:
                raise

    # If we get here, all retries failed
    raise last_error or Exception("Upload failed after all retries")


def upload_images_to_google_drive(
    parent_folder_url: str,
    post_title: str,
    image_paths: List[str],
    image_filenames: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Upload images to a new Google Drive subfolder.

    Creates a subfolder named after the post title inside the parent folder,
    then uploads all images to that subfolder.

    Args:
        parent_folder_url: Google Drive folder URL or ID
        post_title: Title of the post (used as subfolder name)
        image_paths: List of local image file paths to upload
        image_filenames: Optional list of filenames (uses original names if not provided)

    Returns:
        Dict containing:
        - success: bool
        - folder_id: str (created subfolder ID)
        - folder_url: str (URL to subfolder)
        - uploaded: List[Dict] with file details
        - failed: List[Dict] with errors
    """
    if not parent_folder_url:
        return {
            "success": False,
            "error": "No Google Drive folder URL provided"
        }

    if not image_paths:
        return {
            "success": True,
            "message": "No images to upload",
            "uploaded": [],
            "failed": []
        }

    try:
        # Get credentials and build service
        creds = get_drive_credentials()

        # Build service with default settings (socket timeout is already set globally)
        service = build('drive', 'v3', credentials=creds)

        # Extract parent folder ID
        parent_folder_id = extract_folder_id_from_url(parent_folder_url)
        if not parent_folder_id:
            return {
                "success": False,
                "error": f"Could not extract folder ID from: {parent_folder_url}"
            }

        print(f"   📁 Creating subfolder: {post_title}")

        # Create subfolder
        folder_result = create_drive_folder(service, parent_folder_id, post_title)
        subfolder_id = folder_result['folder_id']
        subfolder_url = folder_result['folder_url']

        print(f"   ✓ Created folder: {folder_result['folder_name']}")
        print(f"   🔗 Folder URL: {subfolder_url}")

        # Upload images
        uploaded = []
        failed = []

        for idx, img_path in enumerate(image_paths):
            try:
                # Use custom filename if provided
                filename = None
                if image_filenames and idx < len(image_filenames):
                    filename = image_filenames[idx]

                print(f"   ⬆️  Uploading: {filename or Path(img_path).name}")

                result = upload_file_to_drive(service, subfolder_id, img_path, filename)
                uploaded.append({
                    'local_path': img_path,
                    'file_id': result['file_id'],
                    'filename': result['filename'],
                    'file_url': result['file_url']
                })

                print(f"   ✓ Uploaded: {result['filename']}")

            except Exception as e:
                failed.append({
                    'local_path': img_path,
                    'error': str(e)
                })
                print(f"   ✗ Failed: {img_path} - {str(e)}")

        return {
            "success": len(failed) == 0,
            "folder_id": subfolder_id,
            "folder_url": subfolder_url,
            "folder_name": folder_result['folder_name'],
            "uploaded": uploaded,
            "failed": failed,
            "total_uploaded": len(uploaded),
            "total_failed": len(failed)
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Google Drive upload failed: {str(e)}"
        }


# Make available as Agno tool
upload_images_to_google_drive.__annotations__ = {
    'parent_folder_url': str,
    'post_title': str,
    'image_paths': List[str],
    'image_filenames': Optional[List[str]],
    'return': Dict[str, Any]
}
