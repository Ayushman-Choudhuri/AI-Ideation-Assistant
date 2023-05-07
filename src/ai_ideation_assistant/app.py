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
from cache_messages import cachemessage

# Set up OpenAI API Key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load Configuration Parameters
with open('config.yml' , 'r') as f:
    config =yaml.safe_load(f)['sokrates']['app']

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

    cached_messages, response = cachemessage.initialize_LM(cached_messages)
    output_text = response['choices'][0]['message']['content']
    out_msg = cachemessage.set_message(output_text, role="assistant")
    cached_messages.append(out_msg)

    #st.write(cached_messages)

    # TODO add first instructor prompt
    if 'generated' not in st.session_state:
        st.session_state['generated'] = [response['choices'][0]['message']['content']]

    if 'past' not in st.session_state:
        st.session_state['past'] = ['Start of the Conversation']

    with st.sidebar:
        st.sidebar.image(config['sidebar_image_link'], use_column_width=True)


    user_input = cachemessage.get_text()

    if user_input:

        msg = cachemessage.set_message(user_input, role="user")
        cached_messages, output = cachemessage.query_LM(msg, cached_messages)
        output_text = output['choices'][0]['message']['content']
        out_msg = cachemessage.set_message(output_text, role="assistant")
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

        msg = cachemessage.set_message(final_request, role="system")
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