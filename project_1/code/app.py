import streamlit as st
from streamlit_chat import message
import openai
import boto3
import json
import time
import ast

# Set SSM Parameter Store name for the OpenAI API key and the OpenAI Model Engine
API_KEY_PARAMETER_PATH = "./openai/api_key.txt"
# MODEL_ENGINE = "text-davinci-003"
MODEL_ENGINE = "davinci:ft-neurons-lab-2023-01-25-17-40-57"

# history in dict format for the ChatGPT model
history = [
    {
        "date": time.strftime("%Y-%m-%d, %H:%M:%S"),
        "role": "psychologist",
        # "message": """Hello! It's great to meet you. As a professional psychologist, my goal is to help you improve your mental health and wellbeing.
        # To start, how are you feeling today? It's important to check in with ourselves and our emotions on a regular basis."""
        "message": """ 안녕하세요! 만나서 반갑습니다. 저는 전문 심리상담가로써, 여러분의 마음건강을 돌보고 더 나아지도록 돕는걸 목표로 하고 있어요.
                            시작하기 위해 하나만 물어볼게요! 오늘은 어땠나요? 틈틈히 스스로를 살펴보는 건 정말 중요해요.""",
    }
]

MESSAGE_TEMPLATE = """Provide next replica as a professional psychologist for the conversation in the following JSON format:
```json
{{
    "date": "2021-05-01, 12:00:00",
    "role": "psychologist",
    "message": " 안녕하세요! 만나서 반갑습니다. 저는 전문 심리상담가로써, 여러분의 마음건강을 돌보고 더 나아지도록 돕는걸 목표로 하고 있어요.
                            시작하기 위해 하나만 물어볼게요! 오늘은 어땠나요? 틈틈히 스스로를 살펴보는 건 정말 중요해요."
}}
```

ALWAYS include in your message question and engage the conversation continuation. The current conversation presented in JSON format:
```json
{}
```
"""

# Set the page title and icon
st.set_page_config(page_title="Streamlit Chat - Demo", page_icon=":robot:")

# Get the API key from the SSM Parameter Store
with open(API_KEY_PARAMETER_PATH, "r") as f:
    openai.api_key = [line.strip() for line in f][0]

# Set the page header
st.header("Streamlit Chat - Demo")
st.markdown("[Github](https://github.com/kobrinartem/chatgpt-streamlit-demo)")

# Initialize the session state
if "history" not in st.session_state:
    st.session_state["history"] = history


# ChatGPT query function
def query(message):
    response = openai.Completion.create(
        engine=MODEL_ENGINE,
        prompt=message,
        max_tokens=512,
        temperature=0.5,
        frequency_penalty=0.5,
        presence_penalty=0.5,
    ).choices[0]
    return response.text


# Get the user's message and return it as a dict
def get_patient_message():
    message = st.text_input("You:", "")
    if message:
        message_dict = {
            "date": time.strftime("%Y-%m-%d, %H:%M:%S"),
            "role": "patient",
            "message": message,
        }
        return message_dict
    else:
        return {}


# Get the bot's message and return it as a dict
def get_bot_message(json_message):
    # Try to parse the JSON message
    try:
        message = ast.literal_eval(json_message)
    except Exception as e:
        print(e)
        st.markdown(f"**BEGINNING DEBUG**\n```{json_message}```\n**END DEBUG**")
        raise e
    message_dict = {
        "date": time.strftime("%Y-%m-%d, %H:%M:%S"),
        "role": "psychologist",
        "message": message["message"],
    }
    return message_dict


# Create the history for the ChatGPT model
def create_history(history):
    json.dumps(history, indent=4, sort_keys=True)
    return history


# Get the user's message
user_input = get_patient_message()

if user_input:
    st.session_state.history.append(user_input)
    prompt = MESSAGE_TEMPLATE.format(create_history(st.session_state["history"]))
    output = get_bot_message(query(prompt))
    st.session_state.history.append(output)

if st.session_state["history"]:
    history = st.session_state["history"]
    for i in range(len(history)):
        item = history[i]
        st.markdown(f'**{item["role"]} {item["date"]}#**')
        st.markdown(f'{item["message"]}')
