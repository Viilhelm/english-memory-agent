import os
from google.adk.agents import Agent
from google.adk.models import Gemini
from google.genai import types

from english_memory_agent.agents.schemas import EnglishAnalysisResult, RouterIntent
from english_memory_agent.agents.prompts import (
    ROUTER_AGENT_INSTRUCTION,
    CORRECTION_AGENT_INSTRUCTION,
    REWRITE_AGENT_INSTRUCTION,
    EXPLANATION_AGENT_INSTRUCTION,
    ORGANIZER_AGENT_INSTRUCTION
)



if os.environ.get("GOOGLE_GENAI_USE_ENTERPRISE", "").lower() == "true":
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
    if "GOOGLE_CLOUD_PROJECT" in os.environ:
        os.environ["GOOGLE_CLOUD_PROJECT"] = os.environ["GOOGLE_CLOUD_PROJECT"].strip('"\'')


MODEL_NAME = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
retry_opts = types.HttpRetryOptions(attempts=3)

# 1. Router Agent
router_agent = Agent(
    model=Gemini(model=MODEL_NAME, retry_options=retry_opts),
    name="router_agent",
    description="Determines user intent and extracts parameters (search queries, card IDs).",
    instruction=ROUTER_AGENT_INSTRUCTION,
    output_schema=RouterIntent
)

# 2. Correction Agent
correction_agent = Agent(
    model=Gemini(model=MODEL_NAME, retry_options=retry_opts),
    name="correction_agent",
    description="Checks the input text for grammar, spelling, collocation, or naturalness errors.",
    instruction=CORRECTION_AGENT_INSTRUCTION
)

# 3. Rewrite Agent
rewrite_agent = Agent(
    model=Gemini(model=MODEL_NAME, retry_options=retry_opts),
    name="rewrite_agent",
    description="Generates corrected, natural, IELTS academic, and formal versions of the sentence.",
    instruction=REWRITE_AGENT_INSTRUCTION
)

# 4. Explanation Agent
explanation_agent = Agent(
    model=Gemini(model=MODEL_NAME, retry_options=retry_opts),
    name="explanation_agent",
    description="Explains grammar errors or expression usage in Chinese.",
    instruction=EXPLANATION_AGENT_INSTRUCTION
)

# 5. Card Organizer Agent
organizer_agent = Agent(
    model=Gemini(model=MODEL_NAME, retry_options=retry_opts),
    name="organizer_agent",
    description="Structures all gathered feedback, rewrites, and explanations into a structured card.",
    instruction=ORGANIZER_AGENT_INSTRUCTION,
    output_schema=EnglishAnalysisResult
)


