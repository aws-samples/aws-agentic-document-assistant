# This module define how the orechstrator agent, or agent of agents, works.
from langchain.agents import ZeroShotAgent
from .specialized_agents import SPECIALIZED_AGENTS

# ============================================================================
# Claude agent of agents - agent orchestrator chatbot prompt construction
# ============================================================================
# Inspired by and adapted from
# https://python.langchain.com/docs/modules/agents/how_to/custom_llm_agent

prefix = """\n\nHuman: The following is a conversation between a human and an AI assistant.
The assistant is polite, and responds to the user input and questions acurately and concisely.
The assistant remains on the topic and leverage available options efficiently.

You will play the role of the assistant.
You have access to the following tools, which are specialized agents:
"""

format_instructions = """
Use the following format:

Question: the human's input question you must answer
Thought: you should always think about what to do
Action: the action to take, must be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

"""

suffix = """Remember to respond with your knowledge when the question does not correspond to any specialized tool/agent.

Begin!

The conversation history is within the <chat_history></chat_history> XML tags, where Hu refers to the human and AI refers to the assistant:

<chat_history>
{chat_history}
</chat_history>

Question: {input}

Assistant:
{agent_scratchpad}
""".strip()

CALUDE_AGENT_OF_AGENTS_PROMPT = ZeroShotAgent.create_prompt(
    SPECIALIZED_AGENTS,
    prefix=prefix,
    suffix=suffix,
    format_instructions=format_instructions,
    input_variables=["input", "chat_history", "agent_scratchpad"],
)
