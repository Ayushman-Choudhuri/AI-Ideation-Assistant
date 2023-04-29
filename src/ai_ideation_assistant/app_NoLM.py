import streamlit as st
from streamlit_chat import message
import requests

import os

import openai

from dotenv import load_dotenv

# load_dotenv()

# openai.api_key = os.getenv("OPENAI_API_KEY")


INITIAL_INSTRUCTOR_PROMPT = 'Consider the following scenario: you are helping a company  \
                            identify beneficial AI use cases based on some domain-specific \
                            inputs they provide you. You have to be the one to start the \
                            conversation, the user will follow your instructions. \
                            Start by greeting the customer. \
                            Ask questions until you feel confident in giving a complete scenario \
                            and use case descriptions. \
                            Also, try to be as concise as possible and explore the problem step by step. \
                            Try to not use more than 70 tokens per answer. \
                            ' 

INITIAL_RESPONSE = 'Hello! Thank you for reaching out to us for help in identifying  \
                    beneficial AI use cases. Can you tell me more about your company \
                    and the industry you operate in? '

INITIAL_MAX_TOKENS = 100


def initialize_LM(cached_messages):

    initial_instructor_message = set_message(INITIAL_INSTRUCTOR_PROMPT, role="system")
    cached_messages.append(initial_instructor_message)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        max_tokens = INITIAL_MAX_TOKENS,
        messages=cached_messages
    )
    return cached_messages, response


def query_LM(message, cached_messages):

    cached_messages.append(message)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        #max_tokens = INITIAL_MAX_TOKENS,
        messages=cached_messages
    )
    return cached_messages, response

def set_message(message, role):
    return {"role": role, "content": message}

def set_user_message(message):
    return {"role": "user", "content": message}

def get_text():
    input_text = st.text_input("You: ","", key="input")
    return input_text 

def load_cache(cached_messages):
    #cached_messages = []

    for user_msg in st.session_state.past:
        cached_messages.append(set_message(user_msg, "user"))

    for assistance_msg in st.session_state.generated:
        cached_messages.append(set_message(assistance_msg, "assistant"))
        
    return cached_messages

def main():
    st.set_page_config(
        page_title="Streamlit Chat - Demo",
        page_icon=":robot:"
    )

    st.header("Streamlit Chat - Demo")

    cached_messages = []

    # cached_messages, response = initialize_LM(cached_messages)

    # TODO add first instructor prompt
    if 'generated' not in st.session_state:
        st.session_state['generated'] = ['Test']

    if 'past' not in st.session_state:
        st.session_state['past'] = ['Start of the Conversation']

    user_input = get_text()

    if user_input:

        # msg = set_message(user_input, role="user")
        # cached_messages = load_cache(cached_messages)

        # cached_messages, output = query_LM(msg, cached_messages)
        # output_text = output['choices'][0]['message']['content']

        output_text = 'Test'

        st.session_state.past.append(user_input)
        #st.session_state.generated.append(output["generated_text"])
        st.session_state.generated.append(output_text)

    #st.write("length: " + str(len(st.session_state['generated'])))


    # Start
    if st.session_state['generated']:
        
        for i in range(len(st.session_state['generated'])-1, -1, -1):
            message(st.session_state["generated"][i], key=str(i))
            message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
            


if __name__ == "__main__":
    main()