# This module implements a set of specialized agents.
import boto3
from langchain.agents import Tool
from langchain.llms.bedrock import Bedrock

from .analytics_agent import get_analytics_expert_agent_chain
from .config import AgenticAssistantConfig
from .retrieval_agent import get_retreival_expert_agent_chain

config = AgenticAssistantConfig()
bedrock_runtime = boto3.client("bedrock-runtime", region_name=config.bedrock_region)

claude_llm = Bedrock(
    model_id=config.llm_model_id,
    client=bedrock_runtime,
    model_kwargs={"max_tokens_to_sample": 500, "temperature": 0.0},
)

retreival_expert_agent_chain = get_retreival_expert_agent_chain()
analytics_expert_agent_chain = get_analytics_expert_agent_chain()

# ============================================================================
# Prepare Specialized agents as tools for the Orchestrator agent
# ============================================================================

SPECIALIZED_AGENTS = [
    Tool(
        name="RetreivalExpert",
        func=lambda question: retreival_expert_agent_chain.invoke({"input": question}),
        description=(
            "Use when you are asked questions about specific people, location, or financial reports of companies."
            " The Input should be a correctly formatted question."
        ),
    ),
    Tool(
        name="AnalyticsExpert",
        func=lambda question: analytics_expert_agent_chain.invoke({"input": question}),
        description=(
            "Use when you are asked analytical questions about financial reports of companies."
            " For example, when asked to give the average or maximum revenue of a company, etc."
            " The input should a specific question."
        ),
    ),
]
