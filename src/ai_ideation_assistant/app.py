import streamlit as st
from streamlit_chat import message
from flowchart_visualizer import generate_flowchart , latex_to_pdf
from utils import summarize_LM
from expert_knowledge import retrieve
import os
import openai
import yaml
from dotenv import load_dotenv
import base64

# Set up OpenAI API Key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load Configuration Parameters
with open('config.yml' , 'r') as f:
    config =yaml.safe_load(f)['sokrates']['app']

# Constants for chat initialization
INITIAL_INSTRUCTOR_PROMPT = config['initial_instructor_prompt']
INITIAL_RESPONSE = config['initial_response']
INITIAL_MAX_TOKENS = config['intial_max_tokens']
PATH_DATABASE= config['database_path']
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
# Set up Streamlit cache decorator
@st.cache_data
def initialize_LM(cached_messages):
    """
    Initialize the OpenAI chatbot model with a set of cached messages.

    Args:
        cached_messages (list): A list of messages to initialize the chatbot with.

    Returns:
        A tuple containing the updated list of cached messages and the response from the chatbot API.
    """
    # Add initial instructor message to cached messages
    initial_instructor_message = set_message(INITIAL_INSTRUCTOR_PROMPT, role="system")
    cached_messages.append(initial_instructor_message)

    # Query OpenAI chatbot API with cached messages
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        max_tokens = INITIAL_MAX_TOKENS,
        messages=cached_messages
    )

    # Return updated cached messages and chatbot response
    return cached_messages, response


def query_LM(message, cached_messages):
    """
    Query the OpenAI chatbot model with a new message and a set of cached messages.

    Args:
        message (str): The new message to query the chatbot with.
        cached_messages (list): A list of previously cached messages.

    Returns:
        A tuple containing the updated list of cached messages and the response from the chatbot API.
    """

    # Add user message to cached messages
    cached_messages.append(message)

    # Query OpenAI chatbot API with cached messages
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        #max_tokens = INITIAL_MAX_TOKENS,
        messages=cached_messages
    )
    
    # Return updated cached messages and chatbot response
    return cached_messages, response

def set_message(message, role):

    """
    Set the role of a message (user or system) for the OpenAI chatbot API.

    Args:
        message (str): The message content to set the role for.
        role (str): The role to set for the message (either "user" or "system").

    Returns:
        A dictionary containing the message content and role.
    """
    return {"role": role, "content": message}

def get_text():
    """
    Get user input text from Streamlit text input widget.

    Returns:
        The user input text as a string.
    """
    input_text = st.text_input("You: ","", key="input")
    return input_text 

def load_cache(cached_messages):
    """
    Load the chat cache with past user and assistant messages from Streamlit session state.

    Args:
        cached_messages (list): The current list of cached messages.

    Returns:
        The updated list of cached messages.
    """
    # Add past user messages to cached messages
    for user_msg in st.session_state.past:
        cached_messages.append(set_message(user_msg, "user"))

    # Add past assistant messages to cached messages
    for assistance_msg in st.session_state.generated:
        cached_messages.append(set_message(assistance_msg, "assistant"))
        
    return cached_messages


def main():
    
    # Set app page parameters 
    st.set_page_config(
        page_title= config['page_title'],
        page_icon=config['page_icon']
    )
    st.header(config['page_title'])
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
        st.sidebar.image(config['sidebar_image_link'], use_column_width=True)


    user_input = get_text()

    if user_input:

        msg = set_message(user_input, role="user")
        cached_messages, output = query_LM(msg, cached_messages)
        output_text = output['choices'][0]['message']['content']
        out_msg = set_message(output_text, role="assistant")
        cached_messages.append(out_msg)
        st.session_state.past.append(user_input)
        st.session_state.generated.append(output_text)


    # Start
    if st.session_state['generated']:
        
        for i in range(len(st.session_state['generated'])-1, -1, -1):
            message(st.session_state["generated"][i], key=str(i))
            message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
            

    if st.button('Create Summary'):

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

        ## Generation of final report
        with open("summary.txt", "w") as text_file:
            text_file.write(final_text)

        with open('summary.txt', 'r') as file:
            input_text = file.read()

        output_flowchart_latex = generate_flowchart(input_text)

        ## Generate a .tex file with the out
        with open('output_flowchart_latex.tex', 'w') as f:
            f.write(output_flowchart_latex)

        ## Generate a pdf from the .tex output file
        pdf_file_path = latex_to_pdf(config['latex_output_file_path'])

        # Opening file from file path
        with open(config['pdf_output_file_path'], "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
        # Embedding PDF in HTML
        pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
        # Display File
        st.markdown(pdf_display, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

