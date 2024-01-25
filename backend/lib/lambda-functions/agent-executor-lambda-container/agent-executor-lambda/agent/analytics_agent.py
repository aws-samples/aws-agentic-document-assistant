# This module implements a set of specialized agents.
import boto3
from langchain.agents import AgentExecutor, Tool, create_react_agent
from langchain.llms.bedrock import Bedrock
from langchain_core.prompts import PromptTemplate

from .calculator import CustomCalculatorTool
from .config import AgenticAssistantConfig
from .sqlqa import get_sql_qa_tool, get_text_to_sql_chain

config = AgenticAssistantConfig()
bedrock_runtime = boto3.client("bedrock-runtime", region_name=config.bedrock_region)

claude_llm = Bedrock(
    model_id=config.llm_model_id,
    client=bedrock_runtime,
    model_kwargs={"max_tokens_to_sample": 500, "temperature": 0.0},
)

custom_calculator = CustomCalculatorTool()

TEXT_TO_SQL_CHAIN = get_text_to_sql_chain(config, claude_llm)

# ============================================================================
# Prepare AnalyticsExpert agent
# ============================================================================

ANALYTICS_EXPERT_TOOLS = [
    Tool(
        name="SQLQA",
        func=lambda question: get_sql_qa_tool(question, TEXT_TO_SQL_CHAIN),
        description=(
            "Use when you are asked analytical questions about financial reports of companies."
            " For example, when asked to give the average or maximum revenue of a company, etc."
            " The input should be a targeted question."
        ),
    ),
    Tool(
        name="Calculator",
        func=custom_calculator,
        description=(
            "Always Use this tool when you need to answer math questions."
            " The input to Calculator can only be an valid math expression, such as 55/3."
        ),
    ),
]

CLAUDE_ANALYTICS_AGENT_PROMPT_TEMPLATE = """\n
Human: As an analytics expert, your task is to help a human answer analytics questions accurately.
You must respond specifically to the user input using the provided tools and remain on the topic.

You have access to the following tools:

{tools}

Use the following format:

Question: the human's input question you must answer
Thought: you should always think about what to do
Action: the action to take, must be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}

Assistant:
{agent_scratchpad}
"""

CLAUDE_ANALYTICS_AGENT_PROMPT = PromptTemplate.from_template(
    CLAUDE_ANALYTICS_AGENT_PROMPT_TEMPLATE
)


def get_analytics_expert_agent_chain(verbose=True):
    agent = create_react_agent(
        llm=claude_llm,
        tools=ANALYTICS_EXPERT_TOOLS,
        prompt=CLAUDE_ANALYTICS_AGENT_PROMPT,
    )

    agent_chain = AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=ANALYTICS_EXPERT_TOOLS,
        verbose=verbose,
        handle_parsing_errors="Check your output and make sure it conforms!",
    )
    return agent_chain
