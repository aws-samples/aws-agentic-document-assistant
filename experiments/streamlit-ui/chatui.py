import json
from random import randint

from PIL import Image
import streamlit as st
from streamlit_chat import message
import boto3

# Initialize Boto3 clients for Lambda and SSM
lambda_client = boto3.client("lambda")
ssm_client = boto3.client("ssm")

# Define chatbot name
customer_chatbot_name = ":blue[Chatty] :sunglasses:"
session_id = "12347"

st.set_page_config(page_title="Document LLM assistant", page_icon=":robot:")


@st.cache_resource
def get_lambda_function_name():
    lambda_function_name_ssm_parameter = (
        "/AgenticLLMAssistant/AgentExecutorLambdaNameParameter"
    )

    lambda_function_name = ssm_client.get_parameter(
        Name=lambda_function_name_ssm_parameter
    )
    lambda_function_name = lambda_function_name["Parameter"]["Value"]
    return lambda_function_name


lambda_function_name = get_lambda_function_name()

# initialise session variables
if "generated" not in st.session_state:
    st.session_state["generated"] = []

if "past" not in st.session_state:
    st.session_state["past"] = []

if "widget_key" not in st.session_state:
    st.session_state["widget_key"] = str(randint(1000, 100000000))

if "clean_history" not in st.session_state:
    st.session_state["clean_history"] = False

# Sidebar - the clear button is will flush the memory of the conversation
# st.sidebar.image(logo_img, use_column_width="always")
# st.sidebar.title(customer_chatbot_name)
st.sidebar.title(f"{customer_chatbot_name}")
st.sidebar.divider()
st.sidebar.title("Controls")


def call_agent_lambda(user_input, session_id, agent_type, clean_history=False):
    payload = {
        "user_input": user_input,
        "session_id": session_id,
        "chatbot_type": agent_type,
        "clean_history": clean_history,
    }

    try:
        # Call the Lambda function
        lambda_response = lambda_client.invoke(
            FunctionName=lambda_function_name,
            InvocationType="RequestResponse",
            Payload=json.dumps(payload),
        )

        # Parse the Lambda function response
        lambda_result = lambda_response["Payload"].read().decode("utf-8")
        lambda_result = json.loads(lambda_result)

        return lambda_result["body"]
    except Exception as e:
        print(e)


clear_button = st.sidebar.button("Clear conversation", key="clear")

agent_type = st.sidebar.radio(
    "Select a chat mode", ["basic", "agentic"], index=0  # pre-select "basic"
)

if clear_button:
    st.session_state["generated"] = []
    st.session_state["past"] = []
    st.session_state["widget_key"] = str(randint(100, 10000000))
    st.session_state["clean_history"] = True

# The response_container is used to display the response and past conversation
response_container = st.container()
# The input_container is used to
input_container = st.container()

with input_container:
    # Define the input text box
    with st.form(key="my_form", clear_on_submit=True):
        user_input = st.text_area(
            "You:", placeholder="Write your question here.", key="input", height=100
        )
        submit_button = st.form_submit_button(label="Send")

    # When the submit button is pressed we send the user query
    # to the chatchain object and save the chat history
    if submit_button and user_input:
        default_response = "I am not able to respond currently, please try again later."
        try:
            clean_history = st.session_state["clean_history"]
            print(clean_history)
            output = call_agent_lambda(
                user_input, session_id, agent_type, clean_history
            )
            output = output.get("response", default_response)
        except Exception as e:
            print(f"Error: {e}")
            output = default_response

        st.session_state["clean_history"] = False
        st.session_state["past"].append(user_input)
        st.session_state["generated"].append(output)

# This loop is responsible for displaying the chat history
if st.session_state["generated"]:
    with response_container:
        for i in range(len(st.session_state["generated"])):
            message(st.session_state["past"][i], is_user=True, key=str(i) + "_user")
            message(st.session_state["generated"][i], key=str(i))
