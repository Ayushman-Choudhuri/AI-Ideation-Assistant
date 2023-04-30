import streamlit as st
from streamlit_chat import message
import requests

from utils import summarize_LM

from expert_knowledge import retrieve

import os

import openai

from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")


INITIAL_INSTRUCTOR_PROMPT = 'Consider the following scenario: you are helping a company  \
                            identify beneficial AI use cases based on some domain-specific \
                            inputs they provide you. You have to be the one to start the \
                            conversation, the user will follow your instructions. \
                            Start by greeting the customer. \
                            Do not indulge in extensively explaining the solution. \
                            Ask questions until you feel confident in giving a complete scenario \
                            and use case descriptions. \
                            Also, try to be as concise as possible and explore the problem step by step. \
                            Do not go over 70 tokens for your questioning. \
                            ' 
            

INITIAL_RESPONSE = 'Hello! Thank you for reaching out to us for help in identifying  \
                    beneficial AI use cases. Can you tell me more about your company \
                    and the industry you operate in? '

INITIAL_MAX_TOKENS = 40

PATH_DATABASE= '/Users/andreasbinder/Downloads/Makeathon-Database2.0.xlsx'

FINAL_INSTRUCTOR_PROMPT = lambda summary, additional: f'You are given some history between a user and a chatbot where the \
                            former wants to find out how AI can be used for use cases inside \
                            their company. In addition, you obtain summary snippets relevant \
                            to the current use case. Please write out a two paragraph solution \
                            for the client. \
                            \
                            Here comes the summary of the chat: \
                            {summary} \
                            \
                            Here is some additional information: \
                            {additional} \
                            \
                            Structure the summary based on the problem and the findings. \
                            Output the solution in a step-by-step format. \
                            ' 

@st.cache_data
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
        page_title="Applied AI - Smart",
        page_icon=":robot:"
    )

    st.header("Applied AI - Smart")

    cached_messages = []

    # TODO add first instructor prompt
    # if 'initial' not in st.session_state:
    #     st.session_state['initial'] = True

    cached_messages, response = initialize_LM(cached_messages)
    output_text = response['choices'][0]['message']['content']
    out_msg = set_message(output_text, role="assistant")
    cached_messages.append(out_msg)

    #st.write(cached_messages)

    # TODO add first instructor prompt
    if 'generated' not in st.session_state:
        st.session_state['generated'] = [response['choices'][0]['message']['content']]

    if 'past' not in st.session_state:
        st.session_state['past'] = ['Start of the Conversation']

    with st.sidebar:
        st.sidebar.image("https://www.appliedai.de/assets/static/aai-logo.png", use_column_width=True)


    user_input = get_text()

    if user_input:

        msg = set_message(user_input, role="user")
        #cached_messages = load_cache(cached_messages)

        cached_messages, output = query_LM(msg, cached_messages)
        output_text = output['choices'][0]['message']['content']
        out_msg = set_message(output_text, role="assistant")
        cached_messages.append(out_msg)

        st.session_state.past.append(user_input)
        #st.session_state.generated.append(output["generated_text"])
        st.session_state.generated.append(output_text)

    #st.write("length: " + str(len(st.session_state['generated'])))


    # Start
    if st.session_state['generated']:
        
        for i in range(len(st.session_state['generated'])-1, -1, -1):
            message(st.session_state["generated"][i], key=str(i))
            message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
            

    if st.button('Create Summary'):
        #st.write(cached_messages)

        cached_messages, response = summarize_LM(cached_messages=cached_messages)
        response_text = response['choices'][0]['message']['content']
        
        relevant_summaries = retrieve(query=response_text, top_k=3, path=PATH_DATABASE)

        final_request = FINAL_INSTRUCTOR_PROMPT(response_text, relevant_summaries)

        msg = set_message(final_request, role="system")
        response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                #max_tokens = INITIAL_MAX_TOKENS,
                messages=[msg]
            )
        final_text = response['choices'][0]['message']['content']

        st.write(final_text)

        with open("summary.txt", "w") as text_file:
            text_file.write(final_text)

        file = '/Users/andreasbinder/Documents/NLP/acl2022-zerofewshot-tutorial.pdf'
        import base64
        # Opening file from file path
        with open(file, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')

        # Embedding PDF in HTML
        #pdf_display = F'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf">'
        pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
        # Displaying File
        st.markdown(pdf_display, unsafe_allow_html=True)

if __name__ == "__main__":
    main()