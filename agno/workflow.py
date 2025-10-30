## import
from agno.workflow import Step, Workflow, StepOutput
from agno.agent import Agent
from agno.models.anthropic import Claude


## for factorial
from math import factorial

## import environment
import os
import dotenv
dotenv.load_dotenv()

from pydantic import BaseModel, Field

def power(x, y):
    """ return x*y """
    result = x * y
    return result

def factorial(x):
    result = factorial(x)
    return result


agent = Agent(
    model=Claude(id="claude-sonnet-4-5", api_key=os.getenv("ANTHROPIC_API_KEY")),
    role="You are a math agent. You can calculate the power of 2 numbers and the factorial of an integer base on the given tools",
    markdown=True,
    tools=[power, factorial],
    debug_mode=True
)


agent.print_response(input(), stream=True)

"""
# workflow = Workflow(
#     name="Wordpress Pipeline",
#     steps=[
#         n8n,
          html_agent,
          wordpress_final
#     ]
# )

"""
# workflow.print_response(input(), markdown=True)