from langchain.agents import ZeroShotAgent
from langchain.prompts.prompt import PromptTemplate

from .tools import LLM_AGENT_TOOLS

# ============================================================================
# Claude basic chatbot prompt construction
# ============================================================================

_CALUDE_PROMPT_TEMPLATE = """\n\nHuman: The following is a friendly conversation between a human and an AI assistant.
The assistant is polite, helpful, and accurately replies to input messages or questions with specific details from its context.
If the assistant does not know the answer to a question, it truthfully says it does not know.

The previous conversation is within the <chat_history></chat_history> XML tags below, where Hu refers to the human and AI refers to the assistant:
<chat_history>
{history}
</chat_history>

Input: {input}

Assistant:"""

CLAUDE_PROMPT = PromptTemplate(
    input_variables=["history", "input"], template=_CALUDE_PROMPT_TEMPLATE
)

# ============================================================================
# Claude agentic chatbot prompt construction
# ============================================================================
# Inspired by and adapted from
# https://python.langchain.com/docs/modules/agents/how_to/custom_llm_agent

prefix = """\n\nHuman: The following is a conversation between a human and an AI assistant.
The assistant is polite, and responds to the user input and questions acurately and concisely.
The assistant stays on the topic of the user input and does not diverge from it.

You will play the role of the assistant.
You have access to the following tools:
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

suffix = """Remember to respond with your knowledge when the question does not correspond to any tool.

Begin!

The previous conversation is within the <chat_history></chat_history> XML tags below, where Hu refers to the human and AI refers to the assistant:
<chat_history>
{chat_history}
</chat_history>

Question: {input}

Assistant:
{agent_scratchpad}
""".strip()

CALUDE_AGENT_PROMPT = ZeroShotAgent.create_prompt(
    LLM_AGENT_TOOLS,
    prefix=prefix,
    suffix=suffix,
    format_instructions=format_instructions,
    input_variables=["input", "chat_history", "agent_scratchpad"],
)
