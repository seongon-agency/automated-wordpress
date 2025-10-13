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

## function 1: get credentials
def get_creds():
    creds = None
    SCOPES = [
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    ]
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
        creds = flow.run_local_server(port=0, prompt="consent")  # first run opens browser
        with open("token.json", "w") as f:
            f.write(creds.to_json())
    return creds
creds=get_creds()

## Normalize all words to base characters: (mỹ nhân -> my nhan)
def strip_diacritics(s: str) -> str:
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

## Get slug format of words
def slugify(text: str) -> str:
    t = " ".join(str(text or "").strip().split())
    t = strip_diacritics(t).lower()
    t = re.sub(r"[^a-z0-9]+", "-", t)
    return re.sub(r"-{2,}", "-", t).strip("-")

## Find collumn with wanted names
def find_col(df_cols, candidates):
    norm = {re.sub(r"\s+", "", c).lower(): c for c in df_cols}
    for cand in candidates:
        k = re.sub(r"\s+", "", cand).lower()
        if k in norm:
            return norm[k]
    return None

## Functions used for checking if an url is checked for running but has not been run.
# Function for determining if a value is checked
def is_checked(v):
    s = "" if v is None else str(v).strip().lower()
    return s in {"true", "1", "y", "yes", "✓", "checked", "x"}
# Function for determining if a cell is blank
def is_blank(v):
    return (v is None) or (str(v).strip() == "")

## Functions used for exporting html files from docs id
# Function for extracting docs id from the docs url
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
# Function for exporting html files from docs id
def export_doc_html_bytes(file_id: str) -> bytes:
    drive = build("drive", "v3", credentials=creds)
    meta = drive.files().get(fileId=file_id, fields="id,name,mimeType").execute()
    if meta["mimeType"] != "application/vnd.google-apps.document":
        raise TypeError(f"Not a Google Doc: {meta['name']} [{meta['mimeType']}]")
    return drive.files().export(fileId=file_id, mimeType="text/html").execute(), meta

# Function for saving files using the name of url_docs
def safe_filename(name: str) -> str:
    name = re.sub(r'[\\/:\*\?"<>\|]+', "_", name).strip()
    name = re.sub(r"[-\s]+", "-", name)
    return name or "exported_doc"

#Function for extacting <img tags from html files
def extract_images_from_html_text(html_text: str) -> list[dict]:
    """Return a list of <img> tag attribute dicts from an HTML string."""
    soup = BeautifulSoup(html_text or "", "html.parser")
    return [dict(img.attrs) for img in soup.find_all("img")]

#Function for getting the first n words of a string
def first_n_words(text: str, n: int = 5) -> str:
    if not text:
        return ""
    words = str(text).strip().split()
    return " ".join(words[:n])

#Function for safe_name
def safe_name(s: str) -> str:
    return re.sub(r'[\\/:*?"<>|]+', "_", (s or "").strip()) or "document"

#Function for ensuring unique path
def ensure_unique_path(base_dir: str, filename: str) -> str:
    root, ext = os.path.splitext(filename)
    path = os.path.join(base_dir, filename)
    i = 2
    while os.path.exists(path):
        path = os.path.join(base_dir, f"{root}_{i}{ext}")
        i += 1
    return path

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

#Function for uploading resized images to wordpress
WP_BASE_URL = "https://ngoncareer.com"          # No trailing slash
WP_USERNAME  = "admin_career"
WP_APP_PASS  = "efkV mie6 u3P8 C3mC NyM8 Ickp"   # App password (as shown in WP UI)
wp_pass_clean = (WP_APP_PASS or "").replace(" ", "")  # Remove spaces in the wordpress password
WP_API_BASE = f"{WP_BASE_URL}/wp-json/wp/v2"
WP_MEDIA_EP = f"{WP_API_BASE}/media"
token = base64.b64encode(f"{WP_USERNAME}:{wp_pass_clean}".encode("utf-8")).decode("utf-8")
auth_header = {"Authorization": f"Basic {token}"}
def upload_resized(local_path: str) -> dict:
    """Upload a single *resized* image file to WP and return media JSON."""
    filename = os.path.basename(local_path)
    with open(local_path, "rb") as f:
        data = f.read()
    headers = {
        **auth_header,
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Content-Type": guess_mime(local_path),
    }
    r = requests.post(WP_MEDIA_EP, headers=headers, data=data, timeout=90)
    if r.status_code >= 400:
        raise RuntimeError(f"Upload failed {r.status_code}: {r.text[:400]}")
    return r.json()

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