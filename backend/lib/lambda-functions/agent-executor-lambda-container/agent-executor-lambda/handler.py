import logging
import traceback

import boto3
from agent.agent_of_agents import CLAUDE_AGENT_OF_AGENTS_PROMPT
from agent.config import AgenticAssistantConfig
from agent.prompts import CLAUDE_AGENT_PROMPT, CLAUDE_PROMPT
from agent.specialized_agents import SPECIALIZED_AGENTS
from agent.tools import LLM_AGENT_TOOLS
from langchain.agents import AgentExecutor, create_react_agent
from langchain.chains import ConversationChain
from langchain.llms.bedrock import Bedrock
from langchain.memory import ConversationBufferMemory

from langchain_community.chat_message_histories import DynamoDBChatMessageHistory

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ssm = boto3.client("ssm")
config = AgenticAssistantConfig()

bedrock_runtime = boto3.client("bedrock-runtime", region_name=config.bedrock_region)

claude_llm = Bedrock(
    model_id=config.llm_model_id,
    client=bedrock_runtime,
    model_kwargs={"max_tokens_to_sample": 500, "temperature": 0.0},
)


def get_basic_chatbot_conversation_chain(
    user_input, session_id, clean_history, verbose=True
):
    message_history = DynamoDBChatMessageHistory(
        table_name=config.chat_message_history_table_name, session_id=session_id
    )

    if clean_history:
        message_history.clear()

    memory = ConversationBufferMemory(
        memory_key="history",
        chat_memory=message_history,
        ai_prefix="AI",
        # Change the human_prefix from Human to something else
        # to not conflict with Human keyword in Anthropic Claude model.
        human_prefix="Hu",
        return_messages=False,
    )

    conversation_chain = ConversationChain(
        prompt=CLAUDE_PROMPT, llm=claude_llm, verbose=verbose, memory=memory
    )

    return conversation_chain


def get_agent_of_agents_chatbot_conversation_chain(
    user_input, session_id, clean_history, verbose=True
):
    """Define an LLM assistant implementing an agent of agents design pattern."""
    message_history = DynamoDBChatMessageHistory(
        table_name=config.chat_message_history_table_name, session_id=session_id
    )

    if clean_history:
        message_history.clear()

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        chat_memory=message_history,
        ai_prefix="AI",
        # change the human_prefix from Human to something else
        # to not conflict with Human keyword in Anthropic Claude model.
        human_prefix="Hu",
        return_messages=False,
    )

    agent = create_react_agent(
        llm=claude_llm,
        tools=SPECIALIZED_AGENTS,
        prompt=CLAUDE_AGENT_OF_AGENTS_PROMPT,
    )

    agent_of_agents_chain = AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=SPECIALIZED_AGENTS,
        verbose=verbose,
        memory=memory,
        handle_parsing_errors="Check your output and make sure it conforms!",
    )
    return agent_of_agents_chain


def get_agentic_chatbot_conversation_chain(
    user_input, session_id, clean_history, verbose=True
):
    message_history = DynamoDBChatMessageHistory(
        table_name=config.chat_message_history_table_name, session_id=session_id
    )
    if clean_history:
        message_history.clear()

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        chat_memory=message_history,
        ai_prefix="AI",
        # change the human_prefix from Human to something else
        # to not conflict with Human keyword in Anthropic Claude model.
        human_prefix="Hu",
        return_messages=False,
    )

    agent = create_react_agent(
        llm=claude_llm,
        tools=LLM_AGENT_TOOLS,
        prompt=CLAUDE_AGENT_PROMPT,
    )

    agent_chain = AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=LLM_AGENT_TOOLS,
        verbose=verbose,
        memory=memory,
        handle_parsing_errors="Check your output and make sure it conforms!",
    )
    return agent_chain


def lambda_handler(event, context):
    logger.info(event)
    user_input = event["user_input"]
    session_id = event["session_id"]
    chatbot_type = event.get("chatbot_type", "basic")
    chatbot_types = ["basic", "agentic"]
    clean_history = event.get("clean_history", False)

    if chatbot_type == "basic":
        conversation_chain = get_basic_chatbot_conversation_chain(
            user_input, session_id, clean_history
        ).predict
    elif chatbot_type == "agentic":
        conversation_chain = get_agentic_chatbot_conversation_chain(
            user_input, session_id, clean_history
        ).invoke
    elif chatbot_type == "agent-of-agents":
        conversation_chain = get_agent_of_agents_chatbot_conversation_chain(
            user_input, session_id, clean_history
        ).invoke
    else:
        return {
            "statusCode": 200,
            "response": (
                f"The chatbot_type {chatbot_type} is not supported."
                f" Please use one of the following types: {chatbot_types}"
            ),
        }

    try:
        response = conversation_chain({"input": user_input})
    except Exception:
        response = (
            "Unable to respond due to an internal issue." " Please try again later"
        )
        print(traceback.format_exc())

    return {"statusCode": 200, "response": response}
