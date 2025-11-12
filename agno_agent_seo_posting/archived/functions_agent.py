import os
import re
from urllib.parse import urlparse, parse_qs
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


def export_docs_to_html(docs_url_to_run: list[dict]) -> str | None:
    """
    Export Google Docs to HTML format.
    
    Args:
        docs_url_to_run: List of dicts with 'url' and 'main_keyword' keys
                        Example: [{"url": "https://docs.google.com/...", "main_keyword": "SEO"}]
    
    Returns:
        HTML content of the first exported document as string, or None if no documents were exported
    """
    drive = None
    
    # Debug: Print what we received
    print(f"[DEBUG] export_docs_to_html received type: {type(docs_url_to_run)}")
    print(f"[DEBUG] export_docs_to_html content: {docs_url_to_run}")

    # Validate input
    if not docs_url_to_run:
        print("No documents to export.")
        return None

    if not isinstance(docs_url_to_run, list):
        raise TypeError(f"Expected list of dicts, got {type(docs_url_to_run)}: {docs_url_to_run}")
    
    def build_drive():
        """Build and authenticate Google Drive service."""
        TOKEN_PATH = "token.json"
        CLIENT_SECRETS = "/Users/haxuanbach/VSCode/Agno_agent_SEO_posting/client_secret.json"
        SCOPES = [
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/drive.readonly",
            "https://www.googleapis.com/auth/spreadsheets.readonly",
        ]
        
        def get_creds():
            creds = None
            if os.path.exists(TOKEN_PATH):
                creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
            if not creds or not creds.valid:
                flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS, SCOPES)
                creds = flow.run_local_server(port=0, prompt="consent")  # first run opens browser
                with open(TOKEN_PATH, "w") as f:
                    f.write(creds.to_json())
            return creds

        creds = get_creds()
        drive = build("drive", "v3", credentials=creds)
        return drive

    drive = build_drive()
    
    def extract_file_id(url: str) -> str:
        """Extract a Drive fileId from common Docs/Drive URLs."""
        # /document/d/<ID>
        m = re.search(r"/document/d/([a-zA-Z0-9_-]+)", url)
        if m:
            return m.group(1)
        # /file/d/<ID>
        m = re.search(r"/file/d/([a-zA-Z0-9_-]+)", url)
        if m:
            return m.group(1)
        # ...?id=<ID>
        qs = parse_qs(urlparse(url).query)
        if "id" in qs and qs["id"]:
            return qs["id"][0]
        raise ValueError(f"Could not extract file ID from URL: {url}")

    def export_doc_html_bytes(file_id: str) -> tuple[bytes, dict]:
        """Export a Google Doc to HTML bytes."""
        if drive is None:
            raise RuntimeError("Drive client not initialized. Run build_drive() first.")

        meta = drive.files().get(fileId=file_id, fields="id,name,mimeType").execute()
        if meta["mimeType"] != "application/vnd.google-apps.document":
            raise TypeError(f"Not a Google Doc: {meta['name']} [{meta['mimeType']}]")
        
        html_bytes = drive.files().export(fileId=file_id, mimeType="text/html").execute()
        return html_bytes, meta

    # Create list for storing html files
    exported_html_docs = []  # list of dicts: {url, file_id, name, html, main_keyword}

    # Downloading docs in html
    for doc in docs_url_to_run:
        url = doc["url"]
        main_keyword = doc["main_keyword"]
        
        try:
            fid = extract_file_id(url)
            html_bytes, meta = export_doc_html_bytes(fid)
            html_text = html_bytes.decode("utf-8", errors="ignore")

            exported_html_docs.append({
                "url": url,
                "file_id": fid,
                "name": meta["name"],
                "html": html_text,
                "main_keyword": main_keyword
            })

            print(f"Exported: {meta['name']} (keyword: {main_keyword})")
        except TypeError as e:
            print(f"Skipping (not a Google Doc): {url} | {e}")
        except Exception as e:
            print(f"Failed: {url} | {e}")

    print(f"\nDone. Exported {len(exported_html_docs)} Google Doc(s).")

    # Check if any documents were exported
    if not exported_html_docs:
        print("No documents were successfully exported.")
        return None

    # Check if the first document has HTML content
    if not exported_html_docs[0].get("html"):
        print("Empty HTML content")
        return None

    return exported_html_docs[0]["html"]


# Optional: If you want to return all exported documents instead of just the first one
def export_all_docs_to_html(docs_url_to_run: list[dict]) -> list[dict] | None:
    """
    Export multiple Google Docs to HTML format.
    
    Args:
        docs_url_to_run: List of dicts with 'url' and 'main_keyword' keys
    
    Returns:
        List of dicts with exported document data, or None if no documents were exported
        Each dict contains: {url, file_id, name, html, main_keyword}
    """
    drive = None
    
    print(f"[DEBUG] export_all_docs_to_html received type: {type(docs_url_to_run)}")
    print(f"[DEBUG] export_all_docs_to_html content: {docs_url_to_run}")

    if not docs_url_to_run:
        print("No documents to export.")
        return None

    if not isinstance(docs_url_to_run, list):
        raise TypeError(f"Expected list of dicts, got {type(docs_url_to_run)}: {docs_url_to_run}")
    
    def build_drive():
        TOKEN_PATH = "token.json"
        CLIENT_SECRETS = "/Users/haxuanbach/VSCode/Agno_agent_SEO_posting/client_secret.json"
        SCOPES = [
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/drive.readonly",
            "https://www.googleapis.com/auth/spreadsheets.readonly",
        ]
        
        def get_creds():
            creds = None
            if os.path.exists(TOKEN_PATH):
                creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
            if not creds or not creds.valid:
                flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS, SCOPES)
                creds = flow.run_local_server(port=0, prompt="consent")
                with open(TOKEN_PATH, "w") as f:
                    f.write(creds.to_json())
            return creds

        creds = get_creds()
        drive = build("drive", "v3", credentials=creds)
        return drive

    drive = build_drive()
    
    def extract_file_id(url: str) -> str:
        m = re.search(r"/document/d/([a-zA-Z0-9_-]+)", url)
        if m:
            return m.group(1)
        m = re.search(r"/file/d/([a-zA-Z0-9_-]+)", url)
        if m:
            return m.group(1)
        qs = parse_qs(urlparse(url).query)
        if "id" in qs and qs["id"]:
            return qs["id"][0]
        raise ValueError(f"Could not extract file ID from URL: {url}")

    def export_doc_html_bytes(file_id: str) -> tuple[bytes, dict]:
        if drive is None:
            raise RuntimeError("Drive client not initialized.")

        meta = drive.files().get(fileId=file_id, fields="id,name,mimeType").execute()
        if meta["mimeType"] != "application/vnd.google-apps.document":
            raise TypeError(f"Not a Google Doc: {meta['name']} [{meta['mimeType']}]")
        
        html_bytes = drive.files().export(fileId=file_id, mimeType="text/html").execute()
        return html_bytes, meta

    exported_html_docs = []

    for doc in docs_url_to_run:
        url = doc["url"]
        main_keyword = doc["main_keyword"]
        
        try:
            fid = extract_file_id(url)
            html_bytes, meta = export_doc_html_bytes(fid)
            html_text = html_bytes.decode("utf-8", errors="ignore")

            exported_html_docs.append({
                "url": url,
                "file_id": fid,
                "name": meta["name"],
                "html": html_text,
                "main_keyword": main_keyword
            })

            print(f"Exported: {meta['name']} (keyword: {main_keyword})")
        except TypeError as e:
            print(f"Skipping (not a Google Doc): {url} | {e}")
        except Exception as e:
            print(f"Failed: {url} | {e}")

    print(f"\nDone. Exported {len(exported_html_docs)} Google Doc(s).")

    if not exported_html_docs:
        print("No documents were successfully exported.")
        return None

    return exported_html_docs