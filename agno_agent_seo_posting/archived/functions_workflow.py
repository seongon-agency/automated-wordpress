##Install theses necesary packages

##Import packages after installing
#Import for step 2
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import gspread
import textwrap
#Import for step 3
import re, unicodedata
import pandas as pd
#Import for step 5
import re
from urllib.parse import urlparse, parse_qs
#Import for step 6
import re
from googleapiclient.http import MediaInMemoryUpload
#Import for step 7
import os
from bs4 import BeautifulSoup
#Import for step 8
import base64
import io
import requests
#Import for step 9
import unicodedata
#Import for step 10
from urllib.parse import urlparse
#Import for step 11
from PIL import Image, UnidentifiedImageError
#Import for step 14
from bs4 import BeautifulSoup
import re
#Import for step 17
from bs4 import BeautifulSoup, NavigableString
import html
#Import for step 18
from bs4 import BeautifulSoup, NavigableString
from urllib.parse import urlparse, parse_qs, unquote
import re
from agno.workflow import Step, Workflow, StepOutput, StepInput, Parallel
import urllib.request
from pathlib import Path
from PIL import Image

# Global constants for Drive API
TOKEN_PATH = "token.json"
CLIENT_SECRETS = "/Users/haxuanbach/VSCode/Agno_agent_SEO_posting/client_secret.json"
SCOPES = [
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/spreadsheets.readonly",
]

# Function 2: Accept url and main keyword list from workflow input
def get_input_url_keyword(step_input: StepInput) -> StepOutput:
    """
    Accept a string in format "url,main_keyword" (or multiple lines for multiple entries).
    Transforms it to a list of dicts: [{"url": "...", "main_keyword": "..."}, ...]
    Returns the list for next steps.
    """
    input_data = step_input.input

    # If input is already a list of dicts, pass it through (backward compatibility)
    if isinstance(input_data, list):
        if input_data and isinstance(input_data[0], dict):
            return StepOutput(content=input_data)
        else:
            raise TypeError(f"Expected list of dicts or string, got list of {type(input_data[0])}")

    # If input is a string, parse it
    if isinstance(input_data, str):
        docs_url_to_run = []

        # Split by newlines to handle multiple entries
        lines = input_data.strip().split('\n')

        for line in lines:
            line = line.strip()
            if not line:  # Skip empty lines
                continue

            # Split by comma to get url, main_keyword, and html_template
            parts = line.split(',', 2)  # Split on first two commas to get 3 parts
            if len(parts) != 3:
                raise ValueError(f"Invalid format: '{line}'. Expected 'url,main_keyword,html_template'")

            url = parts[0].strip()
            main_keyword = parts[1].strip()
            html_template = parts[2].strip()

            if not url or not main_keyword or not html_template:
                raise ValueError(f"URL, main_keyword, and html_template cannot be empty in line: '{line}'")

            docs_url_to_run.append({
                "url": url,
                "main_keyword": main_keyword,
                "html_template": html_template
            })

        if not docs_url_to_run:
            raise ValueError("No valid entries found in input string")

        print(f"[INFO] Parsed {len(docs_url_to_run)} entry/entries from input string")
        return StepOutput(content=docs_url_to_run)

    # If neither string nor list, raise error
    raise TypeError(f"Expected string or list of dicts, got {type(input_data)}: {input_data}")

# Function 3: Export docs to html format
def export_docs_to_html(step_input: StepInput) -> StepOutput:
    docs_url_to_run = step_input.previous_step_content
    drive=None
    
    # Debug: Print what we received
    print(f"[DEBUG] export_docs_to_html received type: {type(docs_url_to_run)}")
    print(f"[DEBUG] export_docs_to_html content: {docs_url_to_run}")

    # Validate input
    if not docs_url_to_run:
        print("No documents to export.")
        return StepOutput(content=None)

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
                creds = flow.run_local_server(port=0, prompt="consent")  # first run opens browser
                with open(TOKEN_PATH, "w") as f:
                    f.write(creds.to_json())
            return creds

        creds = get_creds()
        drive = build("drive", "v3", credentials=creds)  # Set global drive client
        return drive

    drive = build_drive()
    
    def extract_file_id(url: str) -> str:   #Extract a Drive fileId from common Docs/Drive URLs
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

    def export_doc_html_bytes(file_id: str) -> bytes:
        # Use the global drive client (must be initialized by build_drive() first)
        if drive is None:
            raise RuntimeError("Drive client not initialized. Run build_drive() first.")

        meta = drive.files().get(fileId=file_id, fields="id,name,mimeType").execute()
        if meta["mimeType"] != "application/vnd.google-apps.document":
            raise TypeError(f"Not a Google Doc: {meta['name']} [{meta['mimeType']}]")
        return drive.files().export(fileId=file_id, mimeType="text/html").execute(), meta

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
        return StepOutput(content=None)

    # Check if the first document has HTML content
    if not exported_html_docs[0].get("html"):
        print("Empty HTML content")
        return StepOutput(content=None)

    print(exported_html_docs[0]["html"])
    return StepOutput(content=exported_html_docs[0]["html"])


## Function 4: Get slug format of words
def slugify(step_input: StepInput) -> StepOutput:
    """
    Get the main_keyword from the input and convert it to a slug.
    Accepts either:
    - A string in format "url,main_keyword" (or multiple lines)
    - A list of dicts with "main_keyword" key
    """
    # Debug logging
    print(f"[DEBUG] slugify received input type: {type(step_input.input)}")
    print(f"[DEBUG] slugify input content: {step_input.input}")

    # Get data from the first step instead of raw workflow input
    input_data = step_input.get_step_content("Get url and main keyword from users")

    # If input is a string, parse it into list of dicts
    if isinstance(input_data, str):
        docs_url_to_run = []

        # Split by newlines to handle multiple entries
        lines = input_data.strip().split('\n')

        for line in lines:
            line = line.strip()
            if not line:  # Skip empty lines
                continue

            # Split by comma to get url and main_keyword
            parts = line.split(',', 1)  # Split only on first comma
            if len(parts) != 2:
                raise ValueError(f"Invalid format: '{line}'. Expected 'url,main_keyword'")

            url = parts[0].strip()
            main_keyword = parts[1].strip()

            if not url or not main_keyword:
                raise ValueError(f"URL and main_keyword cannot be empty in line: '{line}'")

            docs_url_to_run.append({
                "url": url,
                "main_keyword": main_keyword
            })

        if not docs_url_to_run:
            raise ValueError("No valid entries found in input string")

        print(f"[INFO] slugify parsed {len(docs_url_to_run)} entry/entries from input string")
        exported_html_docs = docs_url_to_run

    # If input is already a list, use it directly
    elif isinstance(input_data, list):
        exported_html_docs = input_data
    else:
        raise TypeError(f"Expected string or list of dicts, got {type(input_data)}: {input_data}")

    # Validate and extract main_keyword
    if not exported_html_docs:
        raise ValueError("Input list is empty")

    if not isinstance(exported_html_docs[0], dict):
        raise TypeError(f"Expected dict in list, got {type(exported_html_docs[0])}")

    main_keyword = exported_html_docs[0].get("main_keyword")
    def strip_diacritics(s: str) -> str: ## Normalize all words to base characters: (mỹ nhân -> my nhan)
        # Vietnamese character mappings for precomposed characters
        vietnamese_map = {
            'à': 'a', 'á': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a',
            'ă': 'a', 'ằ': 'a', 'ắ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ặ': 'a',
            'â': 'a', 'ầ': 'a', 'ấ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ậ': 'a',
            'è': 'e', 'é': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e',
            'ê': 'e', 'ề': 'e', 'ế': 'e', 'ể': 'e', 'ễ': 'e', 'ệ': 'e',
            'ì': 'i', 'í': 'i', 'ỉ': 'i', 'ĩ': 'i', 'ị': 'i',
            'ò': 'o', 'ó': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o',
            'ô': 'o', 'ồ': 'o', 'ố': 'o', 'ổ': 'o', 'ỗ': 'o', 'ộ': 'o',
            'ơ': 'o', 'ờ': 'o', 'ớ': 'o', 'ở': 'o', 'ỡ': 'o', 'ợ': 'o',
            'ù': 'u', 'ú': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u',
            'ư': 'u', 'ừ': 'u', 'ứ': 'u', 'ử': 'u', 'ữ': 'u', 'ự': 'u',
            'ỳ': 'y', 'ý': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y',
            'đ': 'd', 'Đ': 'd',
        }

        # Apply Vietnamese character mapping
        result = ""
        for char in (s or ""):
            result += vietnamese_map.get(char.lower(), char)

        # Then apply NFD normalization for any remaining diacritics
        nfkd = unicodedata.normalize("NFD", result)
        return "".join(ch for ch in nfkd if unicodedata.category(ch) != "Mn")
    t = " ".join(str(main_keyword or "").strip().split())
    t = strip_diacritics(t).lower()
    t = re.sub(r"[^a-z0-9]+", "-", t)
    return StepOutput(content=re.sub(r"-{2,}", "-", t).strip("-"))

#Function 5: for extacting <img tags from html files
def extract_images_from_html_text(step_input: StepInput) -> StepOutput:
    """Return a list of <img> tag attribute dicts from an HTML string."""
    # Accept HTML from input (string) or previous_step_content
    html_content = step_input.get_step_content("Export docs to html format")
    soup = BeautifulSoup(html_content or "", "html.parser")
    return StepOutput(content=[dict(img.attrs) for img in soup.find_all("img")])

#Function 6: for extracting <h1> tags from html files
def extract_h1_from_html_text(step_input: StepInput) -> StepOutput:
    def clean_h1_text(text: str) -> str:
        """
        Clean and normalize h1 text by:
        - Replacing non-breaking spaces with regular spaces
        - Removing zero-width characters
        - Removing box-drawing characters
        - Normalizing Unicode to NFC form
        - Collapsing runs of whitespace
        - Trimming leading/trailing whitespace
        """
        if not text:
            return ""

        # Replace non-breaking space with regular space
        text = text.replace('\u00a0', ' ')

        # Remove zero-width characters [\u200B-\u200D\uFEFF]
        text = re.sub(r'[\u200B-\u200D\uFEFF]', '', text)

        # Remove box-drawing characters [\u2500-\u257F]
        text = re.sub(r'[\u2500-\u257F]', '', text)

        # Normalize Unicode to NFC (combine accents properly)
        text = unicodedata.normalize('NFC', text)

        # Collapse runs of spaces
        text = re.sub(r'\s+', ' ', text)

        # Trim leading/trailing whitespace
        return text.strip()
    """Return a list of <h1> tag text content from an HTML string."""
    # Accept HTML from input (string) or previous_step_content
    html_content = step_input.get_step_content("Export docs to html format")
    soup = BeautifulSoup(html_content or "", "html.parser")
    h1_texts = []
    for h1 in soup.find_all("h1"):
        text = h1.get_text(strip=True)
        # Decode Unicode escape sequences (e.g., \u00ed -> í)
        try:
            # If the text contains literal \u sequences, decode them
            if '\\u' in text:
                text = text.encode('utf-8').decode('unicode_escape')
        except Exception:
            # If decoding fails, keep original text
            pass
        h1_texts.append(text)
    # Clean and normalize each h1 text
    cleaned_h1_texts = [clean_h1_text(text) for text in h1_texts]
    return StepOutput(content=cleaned_h1_texts)

# Function 7: Remove <h1>, content notes out of the html output
def clean_html(step_input: StepInput) -> StepOutput:
    import re
    html=step_input.get_step_content("Export docs to html format")
    
    # 1. REMOVE <h1> tags
    html = re.sub(r'<h1[^>]*>.*?</h1>', ' ', html, flags=re.IGNORECASE | re.DOTALL).strip()

    # 2. REMOVE TITLE paragraphs (<p class="title">...</p>)
    html = re.sub(r'<p\b[^>]*\bclass=["\']title["\'][^>]*>[\s\S]*?</p>', '', html, flags=re.IGNORECASE)

    # 3. TABLE MAX WIDTH — add width: 100%; to style attribute
    html = re.sub(r'<table\s+[^>]*?style="([^"]*)"', r'<table style="\1;width: 100%;"', html, flags=re.IGNORECASE)

    # 4. REMOVE <style> blocks, &nbsp;, and extra whitespace
    html = re.sub(r'<style[\s\S]*?</style>', '', html, flags=re.IGNORECASE)
    html = re.sub(r'&nbsp;', ' ', html, flags=re.IGNORECASE)
    html = re.sub(r'\s+', ' ', html).strip()

    # 5. REMOVE FIRST ROW SPACE (leading &nbsp;)
    html = re.sub(r'^(\s*&nbsp;\s*)+', '', html, flags=re.IGNORECASE)

    # 6. REMOVE google.com tracking URLs from links
    html = re.sub(
        r'<a\s+[^>]*?href="https:\/\/www\.google\.com\/url\?q=([^&"]*)[^"]*"',
        r'<a href="\1"',
        html,
        flags=re.IGNORECASE
    )
    
    # 7. REMOVE FONT FAMILY / FONT SIZE from inline styles
    html = re.sub(r'font-(family|size):\s*[^;"\']+;?', '', html, flags=re.IGNORECASE)

    # 8. FIX ITALIC FONT-STYLE
    def fix_italic(match):
        tag = match.group(1)
        before_style = match.group(2)
        pre_style = match.group(3).strip()
        post_style = match.group(4).strip()
        after_style = match.group(5)
        content = match.group(6)
        
        new_style = '; '.join(filter(None, [pre_style, post_style]))
        if new_style:
            new_tag = f'<{tag} {before_style}style="{new_style}"{after_style}>'
        else:
            new_tag = f'<{tag} {before_style}{after_style}>'
        
        return f'{new_tag}<em>{content}</em></{tag}>'

    html = re.sub(
        r'<([^>]+)\s+([^>]*)style="([^"]*?)font-style:\s*italic;?([^"]*?)"([^>]*)>(.*?)</\1>',
        fix_italic,
        html,
        flags=re.IGNORECASE | re.DOTALL
    )

    # 9. REMOVE COMMENTS (superscript tags)
    html = re.sub(r'<sup\b[^>]*>[\s\S]*?</sup>', '', html, flags=re.IGNORECASE)

    return StepOutput(content=html)
    
# Function 8: Create an empty post in wordpress
def create_an_empty_post(step_input: StepInput) -> StepOutput:
    import dotenv
    dotenv.load_dotenv()
    WP_BASE_URL = os.getenv("WP_BASE_URL")         # No trailing slash
    WP_USERNAME = os.getenv("WP_USERNAME")
    WP_APP_PASS = os.getenv("WP_APP_PASS")   # App password (as shown in WP UI)
    WP_API_BASE = f"{WP_BASE_URL}/wp-json/wp/v2"
    WP_MEDIA_EP = f"{WP_API_BASE}/media"
    WP_POST_EP = f"{WP_API_BASE}/posts"
    token = base64.b64encode(f"{WP_USERNAME}:{WP_APP_PASS}".encode("utf-8")).decode("utf-8")
    auth_header = {"Authorization": f"Basic {token}"}
    
    # Input from previous steps
    main_keyword_slug=step_input.get_step_content("Slugify the main_keyword")
    heading_1=str(step_input.get_step_content("Extract <h1 tags")[0])
    
    # Build parameters for sending a request
    payload={"title":heading_1, "slug":main_keyword_slug, "status":"draft", "content":""}
    
    # Send request to create an empty post
    create_request=requests.post(WP_POST_EP, json=payload, headers=auth_header)
    
    # Print status
    post_data_list=[]
    post_data_dict={}
    if create_request.status_code >= 400:
        print(f"Error: {create_request.status_code} - {create_request.text}")
        return StepOutput(content=f"Failed: {create_request.text}")
    else:
        post_data_dict={"post_id":(create_request.json()["id"]), "post_link":(create_request.json()["guid"]["raw"])}
        post_data_list.append(post_data_dict)
        return StepOutput(content=post_data_list)

# Function 9: Get main_keyword_slug to name images and append to images list:
def get_file_names(step_input: StepInput) -> StepOutput:
    main_keyword_slug=step_input.get_step_content("Slugify the main_keyword")
    image_tags=step_input.get_step_content("Extract <img tags")
    num=len(image_tags)-1
    for i in image_tags:
        image_index=image_tags.index(i)
        if image_index <= num:
            file_name=f"{main_keyword_slug}-{image_index+1}"
            i["file_name"] = file_name
        else:
            print("Finished getting file names for images")
    return StepOutput(content=image_tags)

# Function 10: download images from links
def download_images(step_input: StepInput) -> StepOutput:
    image_tags=step_input.get_step_content("Get image file names")    
    downloaded_images=0
    failed_images=0
    
    # Get the absolute path of the current script's directory
    script_dir = Path(__file__).resolve().parent

    # Define the name of the new folder
    raw_image_folder = "raw_images"

    # Create the full path for the new folder
    raw_image_folder_path = script_dir / raw_image_folder

    # Create the new folder if it doesn't already exist
    raw_image_folder_path.mkdir(exist_ok=True)
    
    for img in image_tags:
        filename=f"{img["file_name"]}.png"
        src=img["src"]
        path=os.path.join(raw_image_folder_path,filename)
        img["path"] = path
        try:
            urllib.request.urlretrieve(src, path)
            downloaded_images+=1
        except Exception as e:
            failed_images+=1
            print(f"Failed to download {filename}: {e}")

    print(f"Successfully downloaded: {downloaded_images}, failed to download: {failed_images}")
    return StepOutput(content=image_tags)
    
# Function 11: Resize images
def resize_image(step_input: StepInput) -> StepOutput:
    images=step_input.get_step_content("Download images")
    
    #Create resized images folder
    # Get the absolute path of the current script's directory
    script_dir = Path(__file__).resolve().parent
    # Define the name of the new folder
    resized_image_folder = "resized_images"
    # Create the full path for the new folder
    resized_image_folder_path = script_dir / resized_image_folder
    # Create the new folder if it doesn't already exist
    resized_image_folder_path.mkdir(exist_ok=True)
    
    resized_images=0
    fail_to_resize_images=0
    
    for img in images:
        # Open the image
        img_for_resize = Image.open(img["path"])
        # Change the image mode to RGB
        # img_for_resize_rgb= img_for_resize.convert("RBG")
        # Define new dimensions (width, height)
        new_size = (800, 600)
        # Resize the image
        resized_img = img_for_resize.resize(new_size)
        # Create save_path
        save_path=os.path.join(resized_image_folder_path,f"resized_{img['file_name']}.png")


        # Get dimensions from the resized image object
        width, height = resized_img.size
        img["width_resized"]=width
        img["height_resized"]=height
        img["resized_path"]=save_path

        # Save the resized image
        try:
            resized_img.save(save_path)
            resized_images+=1
        except Exception as e:
            fail_to_resize_images+=1
            print(f"Error: {e}")
    
    print(f"Sucessfully saved: {resized_images} images, Fail to save: {fail_to_resize_images} images")
    return StepOutput(content=images)

# Function 12: Upload images to wordpress
def upload_resized_image(step_input: StepInput) -> StepOutput:
    images=step_input.get_step_content("Resize downloaded images")
    post_id=step_input.get_step_content("Creating an empty post")[0]['post_id']
    import dotenv
    dotenv.load_dotenv()
    WP_BASE_URL = os.getenv("WP_BASE_URL")         # No trailing slash
    WP_USERNAME = os.getenv("WP_USERNAME")
    WP_APP_PASS = os.getenv("WP_APP_PASS")   # App password (as shown in WP UI)
    WP_API_BASE = f"{WP_BASE_URL}/wp-json/wp/v2"
    WP_MEDIA_EP = f"{WP_API_BASE}/media"
    token = base64.b64encode(f"{WP_USERNAME}:{WP_APP_PASS}".encode("utf-8")).decode("utf-8")

    # Prepare inputs for sending requests of uploading images
    uploaded_results = []
    filetype="png"

    for img in images:
        file_name=f"{img['file_name']}.{filetype}"
        title=img.get("title", "")
        alt_text=img.get("alt", "")
        description=img.get("alt", "")
        caption=img.get("alt","")
        resized_path=img["resized_path"]

        with open(resized_path, 'rb') as f:
            image_data=f.read()

        # Correct headers format - Authorization must be a string, not a dict
        headers={
            'Content-Type': 'image/jpeg',
            'Content-Disposition': f'attachment; filename={file_name}',
            'Authorization': f'Basic {token}'  # String, not dict!
        }

        # Send metadata as URL parameters
        params = {
            'title': title,
            'alt_text': alt_text,
            'description': description,
            'caption': caption,
            "post": post_id
        }
        
        try:
            # Send image data in body, metadata in params (not json)
            request=requests.post(
                WP_MEDIA_EP,
                headers=headers,
                data=image_data,  # Binary image data
                params=params     # Metadata as URL params
            )
            request.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            uploaded_results.append(request.json())
            print(f"Successfully uploaded: {file_name}")
            for i in uploaded_results:
                img['new_src']=i['guid']['rendered']
                img['id']=i['id']
        except requests.exceptions.RequestException as e:
            print(f"Error uploading image {file_name}: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            uploaded_results.append(None)

    return StepOutput(content=images)   

# Function 13: Transform the html using an agent
def transform_html(step_input: StepInput) -> StepOutput:
    url=step_input.get_step_content("Get url and main keyword from users")[0]["url"]
    html=step_input.get_step_content("Clean raw html ouput")
    
    from agno.agent import Agent
    from agno.models.anthropic import Claude
    from agno.tools.hackernews import HackerNewsTools
    from pydantic import BaseModel
    import dotenv
    dotenv.load_dotenv()

    class agnet_input(BaseModel):
        url: str
        
    html_agent=Agent(
        model=Claude(id="claude-sonnet-4-5-20250929", api_key=os.getenv("ANTHROPIC_API_KEY")),
        description="You are an expert in transforming a google docx to html",
        instructions=[
            "Transform docs to html"
            "output the html"
            ],
            # "READ the given html template docs then return the shared format of all kinds of tags: <p, <img, <ul, <li, <ol, <table, <td, <tr, <h2, <h3, <h4,...",
            # "output the general form of each kind of tag, one kind only has one format, if more than one exist, choose one",
            # 'each form might have some variables, Eg: <p tag can be <p dir="ltr" style="text-align: justify;"> or <p dir="ltr" style="text-align: center;">"'],
        markdown=True
        )

    response=html_agent.print_response(input=agnet_input(url=url))
    return StepOutput(content=response)

# Function 14: Replace all original <img src by new src after uploading onto wordpress
def update_new_src(stepinput: StepInput) -> StepOutput:
    html=stepinput.get_step_content("Clean raw html ouput")
    images=stepinput.get_step_content("Upload resized images to Wordpress")

    # Create a mapping of old src to new src and other attributes for quick lookup
    src_mapping = {}
    for img in images:
        old_src = img.get('src')
        new_src = img.get('new_src')
        if old_src and new_src:
            src_mapping[old_src] = {
                'new_src': new_src,
                'width': img.get('width_resized'),
                'height': img.get('height_resized'),
                'alt': img.get('alt', ''),
                'id': img.get('id')
            }

    # Parse the HTML
    soup = BeautifulSoup(html, 'html.parser')

    # Find all img tags and replace their src with new WordPress URLs
    updated_count = 0
    for img_tag in soup.find_all('img'):
        old_src = img_tag.get('src')
        if old_src and old_src in src_mapping:
            # Update src to new WordPress URL
            img_tag['src'] = src_mapping[old_src]['new_src']

            # Optionally update width and height if available
            if src_mapping[old_src]['width']:
                img_tag['width'] = src_mapping[old_src]['width']
            if src_mapping[old_src]['height']:
                img_tag['height'] = src_mapping[old_src]['height']

            updated_count += 1

    # Convert back to string
    html = str(soup)

    print(f"Updated {updated_count} image source(s) with new WordPress URLs")
    return StepOutput(content=html)

# Function 15: Apply HTML template formatting using the html_formatter tool
def process_html(stepinput: StepInput) -> StepOutput:
    """
    Apply HTML template formatting using the robust html_formatter tool.
    This replaces the agent-based approach which was error-prone.
    """
    from tools.html_formatter import format_html_with_template

    # Get the HTML content and template
    html = stepinput.get_step_content("Replace original src by new src")
    html_template = stepinput.get_step_content("Get the html template")

    # Debug: Print input
    print(f"[DEBUG] Input HTML length: {len(html)}")
    print(f"[DEBUG] Template HTML length: {len(html_template)}")
    print(f"[DEBUG] Input HTML preview (first 500 chars):\n{html[:500]}\n")

    # Apply template formatting using the html_formatter tool
    result = format_html_with_template(html, html_template)

    if not result["success"]:
        print(f"[ERROR] HTML formatting failed: {result['error']}")
        print(f"[ERROR] Returning original HTML")
        return StepOutput(content=html)

    transformed_html = result["formatted_html"]

    # Debug: Print output HTML preview
    print(f"[DEBUG] Output HTML length: {len(transformed_html)}")
    print(f"[DEBUG] Output HTML preview (first 500 chars):\n{transformed_html[:500]}\n")

    # Validate that transformation actually happened
    if transformed_html == html:
        print("[WARNING] HTML was not transformed - output is identical to input")
    elif len(transformed_html) < len(html) * 0.5:
        print(f"[WARNING] Output HTML is significantly shorter ({len(transformed_html)} vs {len(html)} chars)")
        print("[WARNING] This might indicate data loss during transformation")
    else:
        print("[SUCCESS] HTML transformation completed")

    # Debug: Check if output matches template format
    print("\n[DEBUG] Checking if output matches template format...")
    print(f"[DEBUG] Template has 'dir=\"ltr\"': {'dir=\"ltr\"' in html_template}")
    print(f"[DEBUG] Output has 'dir=\"ltr\"': {'dir=\"ltr\"' in transformed_html}")
    print(f"[DEBUG] Template has 'data-thumb': {'data-thumb' in html_template}")
    print(f"[DEBUG] Output has 'data-thumb': {'data-thumb' in transformed_html}")

    print(transformed_html)
    return StepOutput(content=transformed_html)

# Function 16: Get the html template
def get_html_template(stepinput: StepInput) -> StepOutput:
    html_template=stepinput.get_step_content("Get url and main keyword from users")[0]["html_template"]
    return StepOutput(content=html_template)

# Function 17: Clean the html transformer output
def clean_html_transformer(stepinput: StepInput) -> StepOutput:
    html_transformer=stepinput.get_step_content("Get the html transformer")

    if not isinstance(html_transformer, str):
        return StepOutput(content=html_transformer)

    # Debug: Print what we received
    print(f"[DEBUG clean_html_transformer] Input length: {len(html_transformer)}")
    print(f"[DEBUG clean_html_transformer] Input preview: {html_transformer[:300]}")

    # Extract content between "## Function Output" and end if present
    if "## Function Output" in html_transformer or "Function Output" in html_transformer:
        # Try to find the function output section
        function_output_match = re.search(
            r'##?\s*Function Output.*?```(?:python|json)?\s*(\{.*?\})\s*```',
            html_transformer,
            re.DOTALL | re.IGNORECASE
        )

        if function_output_match:
            # Extract the JSON/dict content from the code block
            html_transformer = function_output_match.group(1)
            print(f"[DEBUG] Extracted function output from reasoning block")
        else:
            # Fallback: try to find any JSON-like structure with function_name and function_code
            json_match = re.search(
                r'\{[^{}]*"function_name"[^{}]*"function_code"[^{}]*\}',
                html_transformer,
                re.DOTALL
            )
            if json_match:
                html_transformer = json_match.group(0)
                print(f"[DEBUG] Extracted JSON structure from text")

    # Remove markdown code block markers
    html_transformer = html_transformer.strip()

    # Remove starting ```python, ```json, or ```
    if html_transformer.startswith("```python"):
        html_transformer = html_transformer[9:]  # Remove "```python"
    elif html_transformer.startswith("```json"):
        html_transformer = html_transformer[7:]  # Remove "```json"
    elif html_transformer.startswith("```"):
        html_transformer = html_transformer[3:]  # Remove "```"

    # Remove trailing ```
    if html_transformer.endswith("```"):
        html_transformer = html_transformer[:-3]  # Remove ending "```"

    # Strip any remaining whitespace
    html_transformer = html_transformer.strip()

    print(f"[DEBUG clean_html_transformer] Cleaned output length: {len(html_transformer)}")
    print(f"[DEBUG clean_html_transformer] Cleaned output preview: {html_transformer[:300]}")

    return StepOutput(content=html_transformer)
    
# Function 18: Check the class of the output from the agent
def get_class_type(stepinput: StepInput) -> StepOutput:
    input=stepinput.get_step_content("Get the html transformer")
    input_type=type(input)
    return StepOutput(content=input_type)


# Function 19: Parsing function blocks from agent output (single block)
def parse_function_block_one(step_input: StepInput) -> StepOutput:
    """
    Parse the first function block found in the input text and return:
    {
        "function_name": ...,
        "function_code": ...
    }

    Input: Can be:
    1. Already a dictionary with function_name and function_code
    2. JSON string
    3. Text containing function_name and function_code with quotes
    """
    import json
    import ast

    # Get input text - can come from input or previous step
    text = step_input.get_step_content("Clean the html transformer")

    print(f"[DEBUG parse_function_block_one] Input type: {type(text)}")
    print(f"[DEBUG parse_function_block_one] Input preview: {str(text)[:200]}")

    # If it's already a dictionary, validate and return it
    if isinstance(text, dict):
        if "function_name" in text and "function_code" in text:
            print(f"[DEBUG] Input is already a dictionary")
            return StepOutput(content=text)
        else:
            raise ValueError(f"Dictionary missing required keys. Got: {list(text.keys())}")

    # Convert to string if not already
    if not isinstance(text, str):
        text = str(text)

    # Try parsing as Python dict literal first (handles triple-quoted strings)
    try:
        cleaned_text = text.strip()
        parsed = ast.literal_eval(cleaned_text)
        if isinstance(parsed, dict) and "function_name" in parsed and "function_code" in parsed:
            print(f"[DEBUG] Successfully parsed as Python dict literal")
            result = {
                "function_name": parsed["function_name"],
                "function_code": parsed["function_code"]
            }
            return StepOutput(content=_fix_indentation(result))
    except (ValueError, SyntaxError) as e:
        print(f"[DEBUG] Not a valid Python dict literal, trying JSON parsing: {e}")

    # Try parsing as JSON first (with triple-quote handling)
    try:
        # Remove any leading/trailing whitespace and common decorations
        cleaned_text = text.strip()

        # First, try direct JSON parse
        try:
            parsed = json.loads(cleaned_text)
            if isinstance(parsed, dict) and "function_name" in parsed and "function_code" in parsed:
                print(f"[DEBUG] Successfully parsed as JSON")
                result = {
                    "function_name": parsed["function_name"],
                    "function_code": parsed["function_code"]
                }
                return StepOutput(content=_fix_indentation(result))
        except json.JSONDecodeError:
            # If direct parse fails, try converting triple-quoted strings to regular strings
            # Replace triple-quoted strings with JSON-compatible escaped strings
            # This is a complex regex that captures: "key": """value"""
            def replace_triple_quotes(match):
                key = match.group(1)
                value = match.group(2)
                # Escape backslashes and quotes in the value
                value_escaped = value.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
                return f'"{key}": "{value_escaped}"'

            # Pattern to match: "function_code": """..."""
            triple_quote_pattern = r'"(function_code)"\s*:\s*"""(.*?)"""'
            cleaned_with_single_quotes = re.sub(
                triple_quote_pattern,
                replace_triple_quotes,
                cleaned_text,
                flags=re.DOTALL
            )

            # Try parsing again
            parsed = json.loads(cleaned_with_single_quotes)
            if isinstance(parsed, dict) and "function_name" in parsed and "function_code" in parsed:
                print(f"[DEBUG] Successfully parsed as JSON after triple-quote conversion")
                result = {
                    "function_name": parsed["function_name"],
                    "function_code": parsed["function_code"]
                }
                return StepOutput(content=_fix_indentation(result))
    except (json.JSONDecodeError, ValueError) as e:
        print(f"[DEBUG] Not valid JSON, trying regex parsing: {e}")

    # If JSON parsing failed, try regex-based parsing
    def _strip_decorations(line: str) -> str:
        """Remove common leading decoration characters like │, ┃, etc."""
        return re.sub(r'^[\s┃│╏╎╽╿┆┇┊┋]+', '', line)

    def _preprocess(text: str) -> str:
        """Normalize the raw text so the regex can work reliably."""
        lines = text.splitlines()
        cleaned_lines = [_strip_decorations(l) for l in lines]
        return "\n".join(cleaned_lines)

    cleaned = _preprocess(text)

    # Try multiple regex patterns to handle different formats
    patterns = [
        # Pattern 1: Triple-quoted function_code
        re.compile(
            r'"function_name"\s*:\s*"(?P<name>[^"]+)"\s*,.*?'
            r'"function_code"\s*:\s*"""\s*(?P<code>.*?)\s*"""',
            re.DOTALL
        ),
        # Pattern 2: Single-quoted or escaped quotes
        re.compile(
            r'["\']function_name["\']\s*:\s*["\'](?P<name>[^"\']+)["\'].*?'
            r'["\']function_code["\']\s*:\s*["\'](?P<code>.*?)["\']',
            re.DOTALL
        ),
        # Pattern 3: Look for function definition directly
        re.compile(
            r'(?P<code>def\s+(?P<name>\w+)\s*\([^)]*\):.*?)(?=\n\s*\}|\n\s*$|$)',
            re.DOTALL
        ),
    ]

    match = None
    for i, pattern in enumerate(patterns):
        match = pattern.search(cleaned)
        if match:
            print(f"[DEBUG] Matched with pattern {i+1}")
            break

    if not match:
        # Last resort: try to find JSON-like structure in the text
        json_match = re.search(r'\{[^}]*"function_name"[^}]*"function_code"[^}]*\}', cleaned, re.DOTALL)
        if json_match:
            try:
                # Extract the JSON-like portion and try to parse it
                json_str = json_match.group(0)
                # Replace triple quotes with regular quotes for JSON compatibility
                json_str = re.sub(r'"""', '"', json_str)
                parsed = json.loads(json_str)
                if "function_name" in parsed and "function_code" in parsed:
                    print(f"[DEBUG] Extracted JSON from text")
                    result = {
                        "function_name": parsed["function_name"],
                        "function_code": parsed["function_code"]
                    }
                    return StepOutput(content=_fix_indentation(result))
            except Exception as e:
                print(f"[DEBUG] Failed to parse extracted JSON: {e}")

        print(f"[DEBUG] No function block found. Cleaned text:\n{cleaned[:500]}")
        raise ValueError("No valid function block found in input text. Please check the agent output format.")

    # Extract function name and code
    if "name" in match.groupdict() and "code" in match.groupdict():
        function_name = match.group("name")
        function_code_raw = match.group("code")
    else:
        raise ValueError("Failed to extract function_name and function_code from match")

    result = {
        "function_name": function_name,
        "function_code": function_code_raw,
    }

    return StepOutput(content=_fix_indentation(result))


def _fix_indentation(result: dict) -> dict:
    """
    Helper function to fix indentation of function code.
    This is a robust parser that handles various malformed code from agents.
    """
    function_code_raw = result["function_code"]

    # Step 1: Normalize whitespace
    # Replace tabs with 4 spaces
    function_code_raw = function_code_raw.replace('\t', '    ')
    # Remove any leading/trailing whitespace from the entire code block
    function_code_raw = function_code_raw.strip()

    # Step 2: Split into lines and clean up
    lines = function_code_raw.splitlines()
    if not lines:
        result["function_code"] = ""
        return result

    # Step 3: Find the function definition
    func_def_idx = -1
    for i, line in enumerate(lines):
        if line.strip().startswith('def '):
            func_def_idx = i
            break

    if func_def_idx == -1:
        print("[WARNING] No function definition found")
        # Try to salvage by treating first line as function def
        func_def_idx = 0

    # Step 4: Rebuild the code with proper indentation
    # Use a stack-based approach to track indentation levels
    fixed_lines = []
    indent_stack = [0]  # Stack to track current indentation level

    # Add function definition with no leading whitespace
    func_def_line = lines[func_def_idx].lstrip()
    fixed_lines.append(func_def_line)

    # If function def doesn't end with colon, something is very wrong
    if not func_def_line.rstrip().endswith(':'):
        print(f"[WARNING] Function definition doesn't end with colon: {func_def_line}")
        func_def_line += ':'
        fixed_lines[-1] = func_def_line

    # Process each line after the function definition
    for idx in range(func_def_idx + 1, len(lines)):
        line = lines[idx]
        stripped = line.strip()

        # Skip completely empty lines
        if not stripped:
            fixed_lines.append("")
            continue

        # Determine if this is a dedent keyword
        dedent_keywords = ['else:', 'elif ', 'except:', 'except ', 'finally:']
        is_dedent = any(stripped.startswith(kw) for kw in dedent_keywords)

        # Calculate the appropriate indentation
        if is_dedent and len(indent_stack) > 1:
            # Pop back to the previous level for dedent keywords
            indent_stack.pop()

        # Current indentation should be the top of stack + 4
        current_indent = indent_stack[-1] + 4

        # Add the line with proper indentation
        fixed_lines.append(" " * current_indent + stripped)

        # Check if this line should increase indent for next line
        if stripped.endswith(':'):
            # Push new indent level onto stack
            indent_stack.append(current_indent)

        # Check if this line decreases indent for next line
        # (statements that end a block: return, break, continue, pass, raise)
        terminal_keywords = ['return', 'break', 'continue', 'pass', 'raise']
        is_terminal = any(stripped.startswith(kw + ' ') or stripped == kw for kw in terminal_keywords)

        if is_terminal:
            # Peek ahead to see if next line is a dedent
            if idx + 1 < len(lines):
                next_stripped = lines[idx + 1].strip()
                # If next line is a dedent keyword or less indented, pop the stack
                next_is_dedent = any(next_stripped.startswith(kw) for kw in dedent_keywords + ['def ', 'class '])
                if next_is_dedent and len(indent_stack) > 1:
                    indent_stack.pop()

    function_code_fixed = "\n".join(fixed_lines)

    # Step 5: Validate and add missing bodies for control structures
    lines_to_check = function_code_fixed.split('\n')
    i = 0
    while i < len(lines_to_check):
        line = lines_to_check[i].rstrip()

        if not line.strip():
            i += 1
            continue

        # Check if line ends with colon (control structure)
        if line.endswith(':'):
            current_indent = len(line) - len(line.lstrip())

            # Find the next non-empty line
            next_non_empty_idx = i + 1
            while next_non_empty_idx < len(lines_to_check):
                if lines_to_check[next_non_empty_idx].strip():
                    break
                next_non_empty_idx += 1

            # Check if there's a properly indented body
            if next_non_empty_idx >= len(lines_to_check):
                # No body found, add pass
                print(f"[FIX] Adding 'pass' for line {i+1}: {line.strip()}")
                lines_to_check.insert(i + 1, " " * (current_indent + 4) + "pass")
            else:
                next_line = lines_to_check[next_non_empty_idx]
                next_indent = len(next_line) - len(next_line.lstrip())

                if next_indent <= current_indent:
                    # Body is not properly indented, add pass
                    print(f"[FIX] Adding 'pass' for unindented body at line {i+1}: {line.strip()}")
                    lines_to_check.insert(i + 1, " " * (current_indent + 4) + "pass")

        i += 1

    function_code_fixed = "\n".join(lines_to_check)

    # Step 6: Final validation - try to compile the code
    try:
        compile(function_code_fixed, '<string>', 'exec')
        print("[SUCCESS] Generated code compiles successfully")
    except SyntaxError as e:
        print(f"[WARNING] Generated code still has syntax error: {e}")
        print(f"[WARNING] Error at line {e.lineno}: {e.text}")

    result["function_code"] = function_code_fixed

    print(f"[DEBUG parse_function_block_one] Extracted function_name: {result['function_name']}")
    print(f"[DEBUG parse_function_block_one] Extracted function_code:\n{result['function_code']}\n")
    print(f"[DEBUG parse_function_block_one] Code length: {len(result['function_code'])}")

    return result


# Function for parsing function blocks from agent output (multiple blocks)
def parse_function_blocks_many(step_input: StepInput) -> StepOutput:
    """
    Parse all function blocks found in the input text.
    Returns a list of dicts:
    [
        {"function_name": ..., "function_code": ...},
        {"function_name": ..., "function_code": ...},
        ...
    ]

    Input: Text containing one or more function blocks in the format:
        "function_name": "name",
        "function_code": \"\"\"...\"\"\"
    """
    # Get input text - can come from input or previous step
    text = step_input.input if hasattr(step_input, 'input') and step_input.input else step_input.previous_step_content

    if not isinstance(text, str):
        # If it's already a dict or list, try to extract string representation
        text = str(text)

    def _strip_decorations(line: str) -> str:
        """Remove common leading decoration characters like │, ┃, etc."""
        return re.sub(r'^[\s┃│╏╎╽╿┆┇┊┋]+', '', line)

    def _preprocess(text: str) -> str:
        """Normalize the raw text so the regex can work reliably."""
        lines = text.splitlines()
        cleaned_lines = [_strip_decorations(l) for l in lines]
        return "\n".join(cleaned_lines)

    # Regex to capture function_name and triple-quoted function_code
    block_pattern = re.compile(
        r'"function_name"\s*:\s*"(?P<name>[^"]+)"\s*,.*?'
        r'"function_code"\s*:\s*"""\s*(?P<code>.*?)\s*"""',
        re.DOTALL
    )

    cleaned = _preprocess(text)
    results = []

    for m in block_pattern.finditer(cleaned):
        results.append({
            "function_name": m.group("name"),
            "function_code": m.group("code"),
        })

    if not results:
        raise ValueError("No valid function blocks found in input text.")

    return StepOutput(content=results)

#Function 21: Update the html to the empty post
def upload_html_to_post(step_input: StepInput) -> StepOutput:
    """
    Upload the transformed HTML content to the empty post that was created.
    Returns the link to the updated post.

    Args:
        step_input: Contains references to previous steps:
            - "Creating an empty post": Contains post_id and post_link
            - "Process html": Contains the transformed HTML content

    Returns:
        StepOutput with the post link (URL) or error message
    """
    import dotenv
    dotenv.load_dotenv()

    # Get WordPress credentials and endpoints
    WP_BASE_URL = os.getenv("WP_BASE_URL")
    WP_USERNAME = os.getenv("WP_USERNAME")
    WP_APP_PASS = os.getenv("WP_APP_PASS")
    WP_API_BASE = f"{WP_BASE_URL}/wp-json/wp/v2"
    WP_POST_EP = f"{WP_API_BASE}/posts"

    # Create authorization header
    token = base64.b64encode(f"{WP_USERNAME}:{WP_APP_PASS}".encode("utf-8")).decode("utf-8")
    auth_header = {"Authorization": f"Basic {token}"}

    # Get the post_id from the empty post that was created
    post_data = step_input.get_step_content("Creating an empty post")
    if not post_data or not isinstance(post_data, list) or not post_data:
        return StepOutput(content="Error: No post data found from empty post creation")

    post_id = post_data[0].get("post_id")
    post_link = post_data[0].get("post_link")

    if not post_id:
        return StepOutput(content="Error: No post_id found in post data")

    # Get the transformed HTML content
    transformed_html = step_input.get_step_content("Get the final html transformer function")
    if not transformed_html:
        return StepOutput(content="Error: No transformed HTML content found")

    # Prepare the update payload with the HTML content
    update_payload = {
        "content": transformed_html
    }

    # Send PUT/POST request to update the post
    try:
        update_request = requests.post(
            f"{WP_POST_EP}/{post_id}",
            json=update_payload,
            headers=auth_header,
            timeout=60
        )

        # Check if the request was successful
        if update_request.status_code >= 400:
            error_msg = f"Error {update_request.status_code}: {update_request.text}"
            print(error_msg)
            return StepOutput(content=f"Failed to update post: {error_msg}")

        # Get the response data
        response_data = update_request.json()
        updated_post_link = response_data.get("link") or post_link

        print(f"Successfully updated post {post_id}")
        print(f"Post URL: {updated_post_link}")

        # Return the post link
        return StepOutput(content=updated_post_link)

    except requests.exceptions.Timeout:
        return StepOutput(content="Error: Request timed out while updating the post")
    except requests.exceptions.RequestException as e:
        return StepOutput(content=f"Error: Request failed - {str(e)}")
    except Exception as e:
        return StepOutput(content=f"Error: Unexpected error - {str(e)}")










#Test function
def get_input(stepinput: StepInput) -> StepOutput:
    input=stepinput.input
    return StepOutput(content=input)

#Function for getting the first n words of a string
def first_n_words(text: str, n: int = 5) -> str:
    if not text:
        return ""
    words = str(text).strip().split()
    return " ".join(words[:n])

#Function for safe_name
def safe_name(s: str) -> str:
    return re.sub(r'[\\/:*?"<>|]+', "_", (s or "").strip()) or "document"


#Function for taking the file type from the url
def guess_ext_from_url(u: str) -> str:
    ext = os.path.splitext(urlparse(u or "").path)[1].lower()
    if ext:
        return ext
    u = (u or "").lower()
    if "png" in u:  return ".png"
    if "gif" in u:  return ".gif"
    if "webp" in u: return ".webp"
    if "svg" in u:  return ".svg"
    return ".jpg"

#Function for downloading images to file
def download_to_file(url: str, dst_path: str, timeout: int = 60):
    with requests.get(url, stream=True, timeout=timeout) as r:
        r.raise_for_status()
        with open(dst_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

#Function for downloading images to memory (BytesIO)
def download_to_memory(url: str, timeout: int = 60) -> io.BytesIO:
    """Download image directly to memory and return BytesIO object."""
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return io.BytesIO(response.content)
                    
#Function for resizing images from file
def resize_fit(src_path: str, dst_path: str, max_w: int, max_h: int):
    with Image.open(src_path) as im:
        w, h = im.size
        # no upscaling
        scale = min(max_w / w, max_h / h, 1.0)
        new_size = (max(1, int(w * scale)), max(1, int(h * scale)))

        # convert + resize
        im = im.convert("RGBA").resize(new_size, Image.LANCZOS)

        # choose save format based on extension
        ext = os.path.splitext(dst_path)[1].lower()
        if ext in {".jpg", ".jpeg"}:
            # flatten alpha for JPEG
            bg = Image.new("RGB", im.size, (255, 255, 255))
            bg.paste(im, mask=im.split()[-1])
            bg.save(dst_path, format="JPEG", quality=92, optimize=True)
        elif ext == ".png":
            im.save(dst_path, format="PNG", optimize=True)
        elif ext == ".webp":
            im.save(dst_path, format="WEBP", quality=90, method=6)
        else:
            im.save(dst_path)  # fallback: keep detected format

#Function for resizing images from memory (BytesIO) - EXACT dimensions
def resize_fit_memory(img_bytes: io.BytesIO, dst_path: str, max_w: int, max_h: int):
    """Resize image from BytesIO to EXACT dimensions and save to file."""
    with Image.open(img_bytes) as im:
        # Force exact dimensions (may distort aspect ratio)
        new_size = (max_w, max_h)

        # convert + resize to exact dimensions
        im = im.convert("RGBA").resize(new_size, Image.LANCZOS)

        # choose save format based on extension
        ext = os.path.splitext(dst_path)[1].lower()
        if ext in {".jpg", ".jpeg"}:
            # flatten alpha for JPEG
            bg = Image.new("RGB", im.size, (255, 255, 255))
            bg.paste(im, mask=im.split()[-1])
            bg.save(dst_path, format="JPEG", quality=92, optimize=True)
        elif ext == ".png":
            im.save(dst_path, format="PNG", optimize=True)
        elif ext == ".webp":
            im.save(dst_path, format="WEBP", quality=90, method=6)
        else:
            im.save(dst_path)  # fallback: keep detected format
            
#Function for getting the minetype
def guess_mime(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    return {
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".png": "image/png", ".gif": "image/gif",
        ".webp": "image/webp", ".svg": "image/svg+xml",
    }.get(ext, "application/octet-stream")

#Function for creating shortcode
DEFAULT_ALIGN = "aligncenter"
DEFAULT_SIZE_CLASS = "size-full"
def build_caption_shortcode(info: dict) -> str:
    """
    Build a WP [caption]...[/caption] shortcode string containing a full <img .../> with:
      - class="aligncenter size-full wp-image-{id}" (if id available)
      - title="" (empty, to match your pattern)
      - src, alt, width, height (when present)
    """
    new_src   = info.get("new_src") or info.get("new_url")
    new_alt   = (info.get("alt") or "").strip()
    new_width = info.get("width") or info.get("new_width")
    new_height= info.get("height") or info.get("new_height")
    media_id  = info.get("uploaded_media_id")

    classes = f'{DEFAULT_ALIGN} {DEFAULT_SIZE_CLASS}'
    if media_id:
        classes += f' wp-image-{media_id}'

    bits = [f'<img class="{classes}" title="" src="{new_src}"']
    if new_alt:
        bits.append(f' alt="{new_alt}"')
    if new_width is not None:
        try: bits.append(f' width="{int(new_width)}"')
        except Exception: bits.append(f' width="{new_width}"')
    if new_height is not None:
        try: bits.append(f' height="{int(new_height)}"')
        except Exception: bits.append(f' height="{new_height}"')
    bits.append(" />")
    inner_img = "".join(bits)

    cap_width = ""
    if new_width is not None:
        try: cap_width = str(int(new_width))
        except Exception: cap_width = str(new_width)

    return f'[caption id="attachment_{media_id or ""}" align="{DEFAULT_ALIGN}" width="{cap_width}"]{inner_img} {new_alt}[/caption]'

# Function for removing styles
def _parse_style(style_str: str) -> dict:
    """Turn inline style string into a dict; case-insensitive keys."""
    out = {}
    if not style_str:
        return out
    for frag in style_str.split(";"):
        if not frag.strip():
            continue
        if ":" not in frag:
            continue
        k, v = frag.split(":", 1)
        out[k.strip().lower()] = v.strip()
    return out

# Function for turning style to string
def _style_to_str(style_dict: dict) -> str:
    """Back to 'k: v; k2: v2' (preserve order not needed)."""
    if not style_dict:
        return ""
    return "; ".join(f"{k}: {v}" for k, v in style_dict.items())

# Function for modifying html code
def transform_html_dom(html_in: str) -> str:
    html_in = html_in or ""
    soup = BeautifulSoup(html_in, "html.parser")

    changed = {
        "img_style_removed": 0,
        "cmnt_blocks_removed": 0,
        "h1_removed": 0,
        "p_normalized":0,
        "p_img_centered_wrapped":0,
        "p_title_removed": 0,
        "table_width_added": 0,
        "style_tags_removed": 0,
        "span_bold_to_strong":0,
        "span_unwrapped":0,
        "links_unwrapped": 0,
        "font_props_removed": 0,
        "italic_wrapped": 0,
    }
  
    # 0) Mark italic nodes BEFORE we strip styles
    for el in soup.select("[style]"):
        st = el.get("style", "")
        if "font-style" in st.lower() and "italic" in st.lower():
            el["data-italic-mark"] = "1"

    # 1) REMOVE <img style="...">
    for img in soup.find_all("img"):
        if "style" in img.attrs:
            del img.attrs["style"]
            changed["img_style_removed"] += 1

    # 2) REMOVE COMMENTS BLOCKS like: <div><p><a id="cmnt123">[...]</a><span>...</span></p></div>
    #    We'll remove the nearest wrapping <div> that contains that pattern.
    for a in soup.find_all("a", id=re.compile(r"^cmnt\d+$", re.IGNORECASE)):
        # try to match the structure div > p > a + span
        div = a.find_parent("div")
        if not div:
            continue
        p = a.find_parent("p")
        if not p or p.find_parent("div") is not div:
            continue
        span = p.find("span")
        if not span:
            continue
        div.decompose()
        changed["cmnt_blocks_removed"] += 1

    # 3) REMOVE ALL <h1>
    for h1 in soup.find_all("h1"):
        h1.decompose()
        changed["h1_removed"] += 1

    # 4) REMOVE <p class="title">...</p> (case-insensitive)
    for p in list(soup.find_all("p")):
        cls = p.get("class", [])
        if isinstance(cls, str):
            cls = [cls]
        cls_lower = {c.lower() for c in cls}
        if "title" in cls_lower:
            p.decompose()
            changed["p_title_removed"] += 1
    # 4a) Normalize ALL <p> tags to dir="ltr" + text-align (center/justify/right; default justify)
    for p in soup.find_all("p"):
        st = _parse_style(p.get("style", ""))
        align_attr = (p.get("align") or "").strip().lower()
        style_align = (st.get("text-align") or "").strip().lower()

        has_center  = (style_align == "center")  or (align_attr == "center")
        has_justify = (style_align == "justify") or (align_attr == "justify")
        has_right   = (style_align == "right")   or (align_attr == "right")

        p["dir"] = "ltr"
        new_style = {}
        if has_center:
            new_style["text-align"] = "center"
        elif has_justify:
            new_style["text-align"] = "justify"
        elif has_right:
            new_style["text-align"] = "right"
        else:
            new_style["text-align"] = "justify"

        p["style"] = _style_to_str(new_style)
        if "align" in p.attrs:
            del p.attrs["align"]
        changed["p_normalized"] += 1

    # 4b) Ensure any <p> that contains an <img> gets centered and wrapped with <span style="font-weight: 400">…</span>
    for p in soup.find_all("p"):
        if p.find("img"):
            # strip existing style, then enforce center
            if "style" in p.attrs:
                del p.attrs["style"]
            p["style"] = "text-align: center;"

            # avoid double-wrap if already exactly wrapped
            only_child = p.contents[0] if p.contents else None
            already_wrapped = (
                len(p.contents) == 1
                and getattr(only_child, "name", "") == "span"
                and (only_child.get("style") or "").replace(" ", "").rstrip(";") == "font-weight:400"
            )
            if not already_wrapped:
                wrapper = soup.new_tag("span")
                wrapper["style"] = "font-weight: 400"
                while p.contents:
                    wrapper.append(p.contents[0].extract())
                p.append(wrapper)
                changed["p_img_centered_wrapped"] += 1

    # 5) TABLE MAX WIDTH (ensure width:100% present in style)
    for table in soup.find_all("table"):
        sd = _parse_style(table.get("style", ""))
        # Only add width:100% if not already present
        has_width = any(k.lower() == "width" for k in sd)
        if not has_width:
            sd["width"] = "100%"
            table["style"] = _style_to_str(sd)
            changed["table_width_added"] += 1
        else:
            # keep existing style but don't count as change
            table["style"] = _style_to_str(sd)

    # 6) REMOVE all <style>…</style> blocks
    for st in soup.find_all("style"):
        st.decompose()
        changed["style_tags_removed"] += 1

    # 7) REMOVE google.com redirect in hrefs
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("https://www.google.com/url?"):
            qs = parse_qs(urlparse(href).query)
            q = qs.get("q", [None])[0]
            if q:
                a["href"] = unquote(q)
                changed["links_unwrapped"] += 1

    # 8) REMOVE FONT FAMILY / SIZE and font-style: italic in inline style
    for el in soup.select("[style]"):
        sd = _parse_style(el.get("style", ""))
        before = sd.copy()
        sd.pop("font-family", None)
        sd.pop("font-size", None)
        # remove font-style entirely (the italic will be handled by wrapping below)
        if "font-style" in sd:
            del sd["font-style"]
        if sd:
            el["style"] = _style_to_str(sd)
        else:
            del el.attrs["style"]
        if sd != before:
            changed["font_props_removed"] += 1
    # 8a) CHANGE <span style="font-weight: bold|700">…</span> → <strong>…</strong>
    for span in list(soup.find_all("span")):
        st = _parse_style(span.get("style", ""))
        fw = (st.get("font-weight") or "").strip().lower()
        if fw in {"bold", "700"}:
            strong = soup.new_tag("strong")
            while span.contents:
                strong.append(span.contents[0].extract())
            span.replace_with(strong)
            changed["span_bold_to_strong"] += 1

    # 8b) Remove (unwrap) any remaining <span> tags while keeping content
    for span in list(soup.find_all("span")):
        span.unwrap()
        changed["span_unwrapped"] += 1

    # 9) FIX ITALIC: wrap contents of marked nodes in <em>…</em>
    for el in soup.find_all(attrs={"data-italic-mark": True}):
        # Avoid double wrapping: if already has a single child <em> covering all, skip
        if len(el.contents) == 1 and getattr(el.contents[0], "name", "") == "em":
            pass
        else:
            em = soup.new_tag("em")
            while el.contents:
                em.append(el.contents[0].extract())
            el.append(em)
            changed["italic_wrapped"] += 1
        del el.attrs["data-italic-mark"]

    # 10) Serialize
    out = str(soup)

    # 11) Replace &nbsp; (entity and unicode) and collapse front row leading space as per your JS
    out = out.replace("&nbsp;", " ").replace("\u00a0", " ")
    out = re.sub(r"^(\s*)", lambda m: m.group(1).replace("\u00a0", " "), out)  # safety
    out = re.sub(r"^(\s*&nbsp;\s*)+", "", out, flags=re.IGNORECASE)

    # (Your JS also collapsed ALL whitespace globally; that can break HTML formatting.
    # If you truly want it, uncomment the next two lines.)
    # out = re.sub(r"\s+", " ", out).strip()

    # Quick summary so you can verify it actually did work:
    print("Transform summary:", {k: v for k, v in changed.items() if v})

    return out


