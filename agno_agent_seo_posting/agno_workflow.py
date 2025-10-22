# Import requirements
from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.workflow import Step, Workflow, StepOutput, StepInput, Parallel
from agno.os import AgentOS

## Reload functions module for updates
import importlib, functions
importlib.reload(functions) 

# Import functions
from functions import get_input_url_keyword
from functions import export_docs_to_html
from functions import slugify
from functions import extract_images_from_html_text
from functions import extract_h1_from_html_text
from functions import clean_html
from functions import create_an_empty_post
from functions import get_file_names
from functions import download_images
from functions import resize_image
from functions import upload_resized_image
from functions import transform_html
# from html_agent_test import html_agent

# Define list of docs url to run containing [{"url":  , "main_keyword": }]
docs_url_to_run=[]

# Frame of the workflow
agent_workflow= Workflow(
    name="Agent đăng bài SEO",
    steps=[
        Step(name="Get url and main keyword from users", executor=get_input_url_keyword),
        Step(name="Export docs to html format", executor=export_docs_to_html),
        Step(name="Extract <img tags", executor=extract_images_from_html_text),
        Step(name="Extract <h1 tags", executor=extract_h1_from_html_text),
        Step(name="Clean raw html ouput", executor=clean_html),
        Step(name="Slugify the main_keyword", executor=slugify),
        Step(name="Creating an empty post", executor=create_an_empty_post),
        Step(name="Get image file names", executor=get_file_names),
        Step(name="Download images", executor=download_images),
        Step(name="Resize downloaded images", executor=resize_image),
        Step(name="Upload resized images to Wordpress", executor=upload_resized_image),
        Step(name="Modify html input following the patterns in the docs", executor=transform_html)
        ]
)

# Replace the list below with your actual document URLs and keywords
docs_input = [
   {"url": "https://docs.google.com/document/d/1c2_xDkdte_NDmG3IJVHOE0-Np2-TeROoU7zwdAio0s8/edit?tab=t.0#heading=h.qaoui0zablj0", "main_keyword": "test", "html_template_docs":"https://docs.google.com/document/d/1oz3LWhZcHE0M_iVkJ0dFfTXJSKmAIKi0CEQa1g5atxE/edit?usp=sharing"}
]

agent_workflow.print_response(docs_input)