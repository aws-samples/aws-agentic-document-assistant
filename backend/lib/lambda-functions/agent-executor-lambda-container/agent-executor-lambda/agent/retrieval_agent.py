# This module implements a set of specialized agents.
import boto3
from langchain.agents import AgentExecutor, Tool, create_react_agent
from langchain.llms.bedrock import Bedrock
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.prompts import PromptTemplate

from .calculator import CustomCalculatorTool
from .config import AgenticAssistantConfig
from .rag import get_rag_chain

config = AgenticAssistantConfig()
bedrock_runtime = boto3.client("bedrock-runtime", region_name=config.bedrock_region)

claude_llm = Bedrock(
    model_id=config.llm_model_id,
    client=bedrock_runtime,
    model_kwargs={"max_tokens_to_sample": 500, "temperature": 0.0},
)

# Tools definition
rag_qa_chain = get_rag_chain(config, claude_llm, bedrock_runtime)
search = DuckDuckGoSearchRun()
custom_calculator = CustomCalculatorTool()

# ============================================================================
# Prepare RetreivalExpert agent
# ============================================================================

RETRIEVAL_EXPERT_TOOLS = [
    Tool(
        name="SemanticSerch",
        func=lambda query: rag_qa_chain({"question": query}),
        description=(
            "Use when you are asked questions about financial reports of companies."
            " The Input should be a correctly formatted question."
        ),
    ),
    Tool(
        name="Search",
        func=search.run,
        description=(
            "Use when you need to answer questions about current events, news or people."
            " You should ask targeted questions."
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

CLAUDE_RETRIEVAL_AGENT_PROMPT_TEMPLATE = """\n
Human: The following is a conversation between a human and an AI assistant.
The assistant is polite, and responds to the user input and questions acurately and concisely.
The assistant stays on the topic of the user input and does not diverge from it.

Human: As an information retrieval expert assistant, your task is to help a user answer questions accurately.
You must respond specifically to the user input using the tools provided below and remain on the topic.

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

CLAUDE_RETREIVAL_AGENT_PROMPT = PromptTemplate.from_template(
    CLAUDE_RETRIEVAL_AGENT_PROMPT_TEMPLATE
)


def get_retreival_expert_agent_chain(verbose=True):
    agent = create_react_agent(
        llm=claude_llm,
        tools=RETRIEVAL_EXPERT_TOOLS,
        prompt=CLAUDE_RETREIVAL_AGENT_PROMPT,
    )

    agent_chain = AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=RETRIEVAL_EXPERT_TOOLS,
        verbose=verbose,
        handle_parsing_errors="Check your output and make sure it conforms!",
    )
    return agent_chain
