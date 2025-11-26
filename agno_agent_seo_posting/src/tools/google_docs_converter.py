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


# OAuth scopes
SCOPES = [
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/spreadsheets.readonly",
]


def _get_credentials_paths():
    """
    Calculate credential file paths at runtime (not module load time).
    This ensures paths are always fresh and not cached by Streamlit.

    Returns:
        tuple: (credentials_dir, token_path, client_secrets_path)
    """
    # Calculate paths relative to this file
    script_dir = os.path.dirname(os.path.realpath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    credentials_dir = os.path.join(project_root, "credentials")

    token_path = os.path.join(credentials_dir, "token.json")
    client_secrets = os.getenv("GOOGLE_CLIENT_SECRETS",
                                os.path.join(credentials_dir, "client_secret.json"))

    return credentials_dir, token_path, client_secrets


def get_credentials():
    """
    Get or refresh Google API credentials.

    Returns:
        Google API credentials object
    """
    # Get paths at runtime (not from module-level constants)
    credentials_dir, token_path, client_secrets = _get_credentials_paths()

    # Debug output
    print(f"[get_credentials] credentials_dir: {credentials_dir}")
    print(f"[get_credentials] token_path: {token_path}")
    print(f"[get_credentials] client_secrets: {client_secrets}")
    print(f"[get_credentials] client_secrets exists: {os.path.exists(client_secrets)}")

    # Ensure credentials directory exists
    os.makedirs(credentials_dir, exist_ok=True)

    creds = None
    if os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        except Exception as e:
            print(f"Warning: Could not load existing token: {e}")
            creds = None

    if not creds or not creds.valid:
        if not os.path.exists(client_secrets):
            raise FileNotFoundError(
                f"Google client secrets file not found: {client_secrets}\n"
                f"Please place your 'client_secret.json' file in: {credentials_dir}\n"
                "Download from Google Cloud Console: https://console.cloud.google.com/apis/credentials"
            )

        print(f"Authenticating with Google API...")
        print(f"Using client secrets from: {client_secrets}")
        flow = InstalledAppFlow.from_client_secrets_file(client_secrets, SCOPES)
        creds = flow.run_local_server(port=0, prompt="consent")

        # Save credentials for next run
        print(f"Saving token to: {token_path}")
        with open(token_path, "w") as f:
            f.write(creds.to_json())
        print(f"✓ Authentication successful!")

    return creds


def convert_css_classes_to_inline_styles(html: str) -> str:
    """
    Convert CSS classes to inline styles in HTML.

    This handles the new Google Docs published format where styles are in <style> tags
    with class names, rather than inline styles.

    Args:
        html: HTML content with CSS classes

    Returns:
        HTML with inline styles instead of classes
    """
    import re

    print(f"   Converting CSS classes to inline styles...")

    # Step 1: Extract ALL CSS from style tags
    css_blocks = []
    style_regex = re.compile(r'<style[^>]*>([\s\S]*?)</style>', re.IGNORECASE)

    for match in style_regex.finditer(html):
        css_blocks.append(match.group(1))

    all_css = '\n\n'.join(css_blocks)
    print(f"   Found {len(css_blocks)} CSS block(s)")

    # Step 2: Parse all CSS class definitions
    class_styles = {}
    class_regex = re.compile(r'\.([a-z0-9_-]+)\s*\{([^}]+)\}', re.IGNORECASE | re.DOTALL)

    for match in class_regex.finditer(all_css):
        class_name = match.group(1)
        rules = match.group(2).replace('\n', ' ').replace(r'\s+', ' ').strip()
        class_styles[class_name] = rules

    print(f"   Parsed {len(class_styles)} CSS class(es)")

    # Step 3: Function to get merged styles for multiple classes
    def get_styles_for_classes(class_list):
        style_map = {}

        for class_name in class_list:
            if class_name not in class_styles:
                continue

            rules = class_styles[class_name].split(';')

            for rule in rules:
                trimmed = rule.strip()
                if not trimmed:
                    continue

                colon_index = trimmed.find(':')
                if colon_index == -1:
                    continue

                prop = trimmed[:colon_index].strip()
                value = trimmed[colon_index + 1:].strip()

                if prop and value:
                    style_map[prop] = value

        if not style_map:
            return ''

        return '; '.join(f"{prop}: {val}" for prop, val in style_map.items())

    # Step 4: Replace all class attributes with inline styles
    processed_html = html
    tag_regex = re.compile(r'<(\w+)([^>]*?)\sclass="([^"]+)"([^>]*?)>', re.IGNORECASE)

    def replace_class_with_style(match):
        tag_name = match.group(1)
        before_class = match.group(2)
        class_names = match.group(3)
        after_class = match.group(4)

        class_list = class_names.strip().split()
        inline_styles = get_styles_for_classes(class_list)

        new_tag = f"<{tag_name}{before_class}{after_class}"

        # Check if there's already a style attribute
        existing_style_regex = re.compile(r'\sstyle="([^"]*)"', re.IGNORECASE)
        existing_match = existing_style_regex.search(before_class + after_class)

        if existing_match:
            # Merge with existing
            existing_style = existing_match.group(1)
            merged_style = f"{inline_styles}; {existing_style}" if inline_styles else existing_style
            new_tag = existing_style_regex.sub(f' style="{merged_style}"', new_tag)
        else:
            # Add new style attribute
            if inline_styles:
                new_tag += f' style="{inline_styles}"'

        new_tag += '>'
        return new_tag

    processed_html = tag_regex.sub(replace_class_with_style, processed_html)

    # Step 5: Clean up - Remove style tags
    processed_html = re.sub(r'<style[^>]*>[\s\S]*?</style>', '', processed_html, flags=re.IGNORECASE)

    # Step 6: Clean up - Remove class attributes
    processed_html = re.sub(r'\sclass="[^"]*"', '', processed_html, flags=re.IGNORECASE)

    # Step 7: Clean up - Remove scripts and unnecessary elements
    processed_html = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', processed_html, flags=re.IGNORECASE)
    processed_html = re.sub(r'<noscript\b[^<]*(?:(?!<\/noscript>)<[^<]*)*<\/noscript>', '', processed_html, flags=re.IGNORECASE)

    print(f"   ✓ CSS classes converted to inline styles")

    return processed_html


def clean_published_html(html: str) -> str:
    """
    Clean published Google Docs HTML by extracting content from first H1 to last div.

    Args:
        html: HTML content

    Returns:
        Cleaned HTML content
    """
    print(f"   Cleaning published HTML...")

    # Find first <h1> tag
    h1_match = re.search(r'<h1\b', html, re.IGNORECASE)
    if not h1_match:
        print(f"   ⚠️  No <h1> found, returning original HTML")
        return html

    start_index = h1_match.start()

    # Find last </div> tag
    last_div_index = html.lower().rfind('</div>')
    if last_div_index == -1 or last_div_index <= start_index:
        print(f"   ⚠️  No closing </div> found after <h1>, returning from <h1> onwards")
        return html[start_index:]

    # Extract content from <h1> to last </div> (inclusive)
    cleaned = html[start_index:last_div_index + 6]  # 6 = len('</div>')

    print(f"   ✓ Cleaned HTML: extracted {len(cleaned)} characters (was {len(html)})")

    return cleaned


def extract_file_id(url: str) -> str:
    """
    Extract Google Drive file ID from various URL formats.

    Args:
        url: Google Docs/Drive URL

    Returns:
        File ID string

    Examples:
        /document/d/<ID>/edit → <ID>
        /document/d/<ID>/view → <ID>
        /document/d/e/<PUBLISHED_ID>/pub → <PUBLISHED_ID>
        /file/d/<ID> → <ID>
        ?id=<ID> → <ID>
    """
    # Try published document pattern: /document/d/e/<ID>/pub
    match = re.search(r"/document/d/e/([a-zA-Z0-9_-]+)/pub", url)
    if match:
        return match.group(1)

    # Try regular document pattern: /document/d/<ID>/edit or /document/d/<ID>/view
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

    raise ValueError(
        f"Could not extract file ID from URL: {url}\n"
        "Supported formats:\n"
        "  - Edit URL: https://docs.google.com/document/d/<ID>/edit\n"
        "  - View URL: https://docs.google.com/document/d/<ID>/view\n"
        "  - Published URL: https://docs.google.com/document/d/e/<ID>/pub"
    )


def google_docs_to_html(google_docs_url: str) -> Dict[str, Any]:
    """
    Convert a Google Docs URL to HTML using Google Drive API or direct HTTP fetch.

    This function supports two methods:
    1. Published URLs: Fetches HTML directly via HTTP (no authentication needed)
    2. Edit/View URLs: Uses Google Drive API (requires authentication)

    Supports both published and non-published Google Docs URLs:
    - Edit URL: https://docs.google.com/document/d/<ID>/edit
    - View URL: https://docs.google.com/document/d/<ID>/view
    - Published URL: https://docs.google.com/document/d/e/<ID>/pub

    Args:
        google_docs_url: Google Docs URL (edit, view, or published URL)

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
        # Check if this is a published URL (ends with /pub)
        if google_docs_url.strip().endswith('/pub'):
            print(f"   Detected published URL - fetching directly via HTTP...")
            import requests
            from bs4 import BeautifulSoup

            try:
                response = requests.get(google_docs_url, timeout=60)
                response.raise_for_status()
                html_text = response.text

                # Extract document title from HTML (before processing)
                soup = BeautifulSoup(html_text, 'html.parser')
                title_tag = soup.find('title')
                document_name = title_tag.get_text() if title_tag else "Untitled Document"

                # Extract file ID from URL
                file_id = extract_file_id(google_docs_url)

                print(f"   ✓ Published document fetched successfully ({len(html_text)} characters)")

                # STEP 1: Convert CSS classes to inline styles
                # This handles the new Google Docs format where styles are in <style> tags
                html_text = convert_css_classes_to_inline_styles(html_text)

                # STEP 2: Clean HTML (extract from first <h1> to last </div>)
                html_text = clean_published_html(html_text)

                print(f"   ✓ Published document processed successfully")

                return {
                    "success": True,
                    "raw_html": html_text,
                    "document_name": document_name,
                    "file_id": file_id
                }
            except requests.exceptions.RequestException as e:
                return {
                    "success": False,
                    "error": f"Failed to fetch published document: {str(e)}"
                }

        # For edit/view URLs, use Google Drive API
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

        # Export as HTML with retry logic for timeout issues
        max_retries = 3
        retry_delay = 2
        last_error = None

        for attempt in range(max_retries):
            try:
                print(f"   Attempting to export document (attempt {attempt + 1}/{max_retries})...")

                # Create HTTP object with longer timeout
                # Use google-auth-httplib2 for proper integration
                from google_auth_httplib2 import AuthorizedHttp
                import httplib2

                http = httplib2.Http(timeout=120)  # 2-minute timeout
                authorized_http = AuthorizedHttp(creds, http=http)

                # Create service with custom HTTP
                drive_with_timeout = build("drive", "v3", http=authorized_http)

                html_bytes = drive_with_timeout.files().export(
                    fileId=file_id,
                    mimeType="text/html"
                ).execute()

                print(f"   ✓ Document exported successfully")
                break  # Success, exit retry loop

            except Exception as e:
                last_error = e
                if "timed out" in str(e).lower() or "timeout" in str(e).lower():
                    if attempt < max_retries - 1:
                        print(f"   ⚠ Timeout on attempt {attempt + 1}, retrying in {retry_delay}s...")
                        import time
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                        continue
                    else:
                        print(f"   ❌ All retry attempts failed")
                        raise Exception(f"Failed to export document after {max_retries} attempts: {str(e)}")
                else:
                    # Not a timeout error, don't retry
                    raise

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
