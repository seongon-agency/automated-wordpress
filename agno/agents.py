'''
Name: WordPress Publishing AI Agent
Author: Hoang Duc Viet
Description: AI Agent that publishes Google Docs to WordPress automatically.
Version: 0.2.0
Latest changes:
- Added WordPress publishing functionality
- Integrated with existing functions.py pipeline
- Connected to Arize Phoenix for tracing and evaluation
'''

from agno.agent import Agent
from agno.team import Team
from agno.os import AgentOS

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

# WordPress publishing tools
from wordpress_tools import (
    publish_google_doc_to_wordpress,
    batch_publish_google_docs,
    get_wordpress_post,
    update_wordpress_post,
    list_recent_posts,
    list_client_configurations,
    create_new_client_config
)

# tracing and evaluation
from phoenix.otel import register

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
WORDPRESS PUBLISHING AGENT

Publishes Google Docs to WordPress automatically
"""
def create_wordpress_agent():
    """Create the WordPress publishing agent."""

    wordpress_agent = Agent(
        name="WordPress Publisher",
        role="Publish Google Docs to WordPress automatically",
        model=Claude(id="claude-sonnet-4-5-20250929", api_key=os.getenv("ANTHROPIC_API_KEY")),
        description=(
            "You are a WordPress publishing agent. You take Google Docs URLs and publish them "
            "to WordPress. You extract content, process images, transform HTML, and create posts."
        ),
        instructions=[
            "When user provides a Google Docs URL, ask which client they're publishing for",
            "Use list_client_configurations to show available client HTML customizations",
            "If user wants to create a new client config, ask for example HTML (before and after)",
            "Use create_new_client_config to automatically generate client rules from HTML examples",
            "For single posts, use publish_google_doc_to_wordpress with the appropriate client_id",
            "For multiple posts, use batch_publish_google_docs with a list of URLs",
            "By default, create posts as 'draft' status for user review",
            "After publishing, tell the user the post URL, ID, and which client customizations were applied",
            "For batch publishing, show a summary with success rate and list of published posts",
            "You can also list recent posts, get post details, and update existing posts",
            "Be concise and informative in your responses"
        ],
        tools=[
            publish_google_doc_to_wordpress,
            batch_publish_google_docs,
            get_wordpress_post,
            update_wordpress_post,
            list_recent_posts,
            list_client_configurations,
            create_new_client_config
        ],
        db=db,
        add_history_to_context=True,
        read_chat_history=True,
        num_history_runs=3,
        search_session_history=True,
        markdown=True,
        debug_mode=True,
        cache_session=True
    )

    agent_os = AgentOS(
        id="wordpress_publisher",
        description="WordPress Publishing Agent - Publishes Google Docs to WordPress",
        agents=[wordpress_agent]
    )

    return agent_os


# Create the agent instance
os_instance = create_wordpress_agent()
app = os_instance.get_app()

if __name__ == "__main__":
    print("🚀 Starting WordPress Publishing Agent...")
    print("📝 Ready to publish Google Docs to WordPress!")
    print("🌐 Access at: http://localhost:7777")
    os_instance.serve(app="agents:app", reload=False)
