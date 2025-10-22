from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.tools.hackernews import HackerNewsTools

html_agent=Agent(
    model=Claude(id=""),
    description="You are an expert in writing python codes to transform html from raw version to specific template",
    instructions="Read the given html template then transform raw html in accordance to that template regarding <p tags, <img tags, caption, bullets with <ul, <ol, <li, <table, <td, <tr, <a tags, output the processed html",
    markdown=True
)

agent.print_response("Trendings in different majors of business")
