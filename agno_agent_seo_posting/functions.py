##Install theses necesary packages

##Import packages after installing
#Import for step 2
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import gspread
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

            # Split by comma to get url and main_keyword
            parts = line.split(',', 1)  # Split only on first comma
            if len(parts) != 2:
                raise ValueError(f"Invalid format: '{line}'. Expected 'url,main_keyword'")

            url = parts[0].strip()
            main_keyword = parts[1].strip()
            html_template_docs= parts[2].strip()

            if not url or not main_keyword or not html_template_docs:
                raise ValueError(f"URL and main_keyword and html_template_docs cannot be empty in line: '{line}'")

            docs_url_to_run.append({
                "url": url,
                "main_keyword": main_keyword,
                "html_template_docs": html_template_docs
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

    input_data = step_input.input

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
        filename=f"{img["file_name"]}.jpg"
        src=img["src"]
        path=os.path.join(raw_image_folder_path,filename)
        img["path"] = path
        try:
            urllib.request.urlretrieve(src, path)
            downloaded_images+=1
        except Exception as e:
            failed_images+=1
    return StepOutput(content=f"sucessfully downloaded: {downloaded_images}, failed to download: {failed_images}, {image_tags}")
    
# Function 11: Resize images
def resize_image(step_input: StepInput) -> StepOutput:
    images=step_input.get_step_content("Get image file names")
    
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
        # Define new dimensions (width, height)
        new_size = (800, 600) 
        # Resize the image
        resized_img = img_for_resize.resize(new_size)
        # Create save_path
        save_path=os.path.join(resized_image_folder_path,f"resized_{img['file_name']}.jpg")
        # Save the resized image
      
        size_image=Image.open(save_path)
        width, height = size_image.size
        img["width_resized"]=width
        img["height_resized"]=height
        img["resized_path"]=save_path
        
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
    filetype="jpg"

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