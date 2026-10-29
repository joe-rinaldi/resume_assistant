from google.adk import Agent
from google.adk.models import Gemini

root_agent = Agent(
    name="resume_assistant",
    model="gemini-2.5-flash",
    description=(
        "Resume Assistant tool"
    ),
    instruction="""
    You are a helpful assistant.
    Answer user questions accurately.
    """
)