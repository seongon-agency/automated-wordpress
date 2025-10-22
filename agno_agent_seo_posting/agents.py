'''
Name: Content SEO AI Agents
Author: Hoang Duc Viet
Description: AI Agentic System for SEO content creation with Agno.
Version: 0.1.0
Latest changes: 
- connected to Arize Phoenix for tracing and evaluation.
NOTES:
- not being able to trace total token usage and costs due to agno itself.

TODO: 
- RAG

'''

from agno.agent import Agent
from agno.team import Team
from agno.os import AgentOS
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
from functions import create_an_empty_post
from functions import get_file_names
from functions import download_images
from functions import resize_image
from functions import upload_resized_image

# Model
from agno.models.anthropic import Claude

# SQLite Database
from agno.db.sqlite import SqliteDb

# RAG Chromadb Database
# import chromadb
# from agno.knowledge.knowledge import Knowledge
# from agno.vectordb.chroma import ChromaDb
# from agno.knowledge.embedder.cohere import CohereEmbedder
# from chromadb.config import Settings
# import chromadb.utils.embedding_functions as embedding_functions


# Tools
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.mcp import MultiMCPTools

# async run for MCP
import asyncio


# Load environment variables
import os
import dotenv
dotenv.load_dotenv()

# Declare database

db = SqliteDb(
    db_file="database.db",
    # Table to store your Agent, Team and Workflow sessions and runs
    session_table="sessions",
    # Table to store all user memories
    memory_table="memory",
    # Table to store all metrics aggregations
    metrics_table="metrics",
    # Table to store all your evaluation data
    eval_table="evals",
    # Table to store all your knowledge content
    knowledge_table="knowledge",
)

# Configure RAG database with Chroma

## embedding with Cohere
# cohere_ef = embedding_functions.CohereEmbeddingFunction(
#     api_key=os.getenv('COHERE_API_KEY'),
#     model_name="embed-v4.0"
#     )

# client = chromadb.CloudClient(
#   api_key = "ck-5h8C36CwzBp81NwGoNjvZkNyrzEmjQcg5kkfPZVoQ8Pu",
#   tenant = 'de163e20-bb6f-4dc9-a7e8-51eab137d1ca',
#   database = 'agno'
# )

# knowledge = Knowledge(
#     name = "Story writing knowledge",
#     description = "Guidance on how to write effective short stories",
#     vector_db = ChromaDb(
#         collection="sample_collection",
#         embedder=CohereEmbedder(id="embed-v4.0", api_key="wiZKEho6gTFN97xutVtDKFp7pHIo7XDte10WXZfH"),
#         settings = Settings(
#             chroma_api_impl = "chromadb.api.fastapi.FastAPI",
#             chroma_server_host = "de163e20-bb6f-4dc9-a7e8-51eab137d1ca.api.trychroma.com",
#             chroma_server_http_port = 443,
#             chroma_server_ssl_enabled = True,
#             chroma_client_auth_provider="chromadb.auth.token_authn.TokenAuthClientProvider",
#             chroma_client_auth_credentials="ck-5h8C36CwzBp81NwGoNjvZkNyrzEmjQcg5kkfPZVoQ8Pu"
#         )
#     )
# )



"""
SEO CONTENT CREATION TEAM

Members:
- Outline Agent
- Content Writer Agent
"""
def content_team():
    """Run AI Agent team."""
    ## Declare MCP tools
    content_env = {
            **os.environ,
            # 'FREEPIK_API_KEY': os.getenv('FREEPIK_API_KEY'),
            # 'DATAFORSEO_USERNAME': os.getenv('DATAFORSEO_USERNAME'),
            # 'DATAFORSEO_PASSWORD': os.getenv('DATAFORSEO_PASSWORD'),
            # 'BRAVE_API_KEY': os.getenv('BRAVE_API_KEY'),
            "MAPBOX_ACCESS_TOKEN": os.getenv("MAPBOX_ACCESS_TOKEN")
    }

    # content_mcp_tools = MultiMCPTools(
    #     commands=[
    #         "npx -y @mapbox/mcp-server",
    #     ],
    #     env=content_env
    # )

    outline_agent = Agent(
        name = "Outline Agent",
        role = "Create a short story outline based on a given topic",
        model = Claude(id="claude-sonnet-4-5-20250929", api_key=os.getenv("ANTHROPIC_API_KEY")),
        description="You are short story idea creator. You generate an idea and suggest a clear outline base on a given topic",
        instructions = [
            "When asked to write a story, only return the story and nothing else.",
            "Don't use icons and emojis"
            ],
        tools = [DuckDuckGoTools()],
        # reasoning=True,
        # reasoning_max_steps=10,
        db = db,
        add_history_to_context=True, ## retrieve conversaion history -> memory
        read_chat_history=True, ## enables agent to read the chat history that were previously stored
        # enable_session_summaries=True, ## summarizes the content of a long conversaion to storage
        num_history_runs=2,
        search_session_history=True, ## allow searching through past sessions
        # num_history_sessions=2, ## retrieve only the 2 lastest sessions of the agent
        markdown=True,
        debug_mode=True,
        cache_session=True
    )

    content_writer = Agent(
        name = "Content Writer Agent",
        role = "Write story based on a given outline",
        model = Claude(id="claude-sonnet-4-5-20250929", api_key=os.getenv("ANTHROPIC_API_KEY")),
        description="You are a short storywriter. Base on a given outline, you write a short compelling story.",
        instructions=[
            "When asked to write a story, only return the story itself and nothing else.",
            "Never use emojis or icons."
        ],
        tools = [],
        # reasoning=True,
        # reasoning_max_steps=10,
        db = db,
        add_history_to_context=True, ## retrieve conversaion history -> memory
        read_chat_history=True, ## enables agent to read the chat history that were previously stored
        # enable_session_summaries=True, ## summarizes the content of a long conversaion to storage
        num_history_runs=2,
        search_session_history=True, ## allow searching through past sessions
        # num_history_sessions=2, ## retrieve only the 2 lastest sessions of the agent
        markdown=True,
        debug_mode=True,
        cache_session=True
    )

    content_team = Team(
        name="AI SEO Content Team",
        role="Coordinate the team members",
        model = Claude(id="claude-sonnet-4-5-20250929", api_key=os.getenv("ANTHROPIC_API_KEY")),
        description="",
        instructions=[
            "use outline agent to generate outline",
            "use writer agent to produce story from outline",
            "return ONLY the final story of the writer agent, DO NOT add extra words or explaining.",
            "dont use any icons or emojies"
        ],
        tools = [],
        db = db,
        # knowledge = knowledge,

        add_history_to_context=True, ## retrieve conversaion history -> memory
        read_team_history=True,
        # enable_session_summaries=True, ## summarizes the content of a long conversaion to storage
        num_history_runs=2,
        search_session_history=True, ## allow searching through past sessions


        # num_history_sessions=2, ## retrieve only the 2 lastest sessions of the agent
        markdown=True,
        debug_mode=True,
        cache_session=True,


        members=[outline_agent, content_writer], 
        # reasoning=True,
        # reasoning_max_steps = 2,
    )
    
    agent_workflow= Workflow(
        name="Agent đăng bài SEO",
        steps=[
            Step(name="Get url and main keyword from users", executor=get_input_url_keyword),
            Step(name="Export docs to html format", executor=export_docs_to_html),
            Step(name="Extract <img tags", executor=extract_images_from_html_text),
            Step(name="Extract <h1 tags", executor=extract_h1_from_html_text),
            Step(name="Slugify the main_keyword", executor=slugify),
            Step(name="Creating an empty post", executor=create_an_empty_post),
            Step(name="Get image file names", executor=get_file_names),
            Step(name="Download images", executor=download_images),
            Step(name="Resize downloaded images", executor=resize_image),
            Step(name="Upload resized images to Wordpress", executor=upload_resized_image)
        ],
        debug_mode=True
    )

    agent_os = AgentOS(
        id="my os",
        description="My AgentOS",
        # agents=[assistant],
        teams=[content_team],
        agents=[outline_agent, content_writer],
        workflows=[agent_workflow]
    )

    return agent_os

os_instance = content_team()
app = os_instance.get_app()

if __name__ == "__main__":
    os_instance.serve(app="agents:app", reload=False)