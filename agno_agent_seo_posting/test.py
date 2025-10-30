import re
import requests
from typing import Dict, Any
from bs4 import BeautifulSoup

published_url="https://docs.google.com/document/d/e/2PACX-1vTDCwHgnP-VTBgggyE8z8fjBQMblE_clLwRQah2GTdLcnCcetiWNGfQgHaEg05fMg7b7OrJsYSRXGw2/pub"
from tools.google_docs_converter import google_docs_to_html
from utils.html_extractor import extract_title_from_content
print(extract_title_from_content(google_docs_to_html(published_url)['raw_html']))