##Step 0: Install theses necesary packages
##Install google-api-python-client google-auth google-auth-oauthlib pandas beautifulsoup4 gspread
##install -q pillow

##Step 1: Import packages after installing
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