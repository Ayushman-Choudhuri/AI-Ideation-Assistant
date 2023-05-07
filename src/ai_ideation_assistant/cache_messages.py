import streamlit as st
from streamlit_chat import message
import openai
import yaml
from dotenv import load_dotenv
import os

# Set up OpenAI API Key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load Configuration Parameters
with open('config.yml' , 'r') as f:
    config =yaml.safe_load(f)['sokrates']['app']

class cachemessage:

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
        initial_instructor_message = cachemessage.set_message(config['initial_instructor_prompt'], role="system")
        cached_messages.append(initial_instructor_message)

        # Query OpenAI chatbot API with cached messages
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            max_tokens = config['intial_max_tokens'],
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
            cached_messages.append(cachemessage.set_message(user_msg, "user"))

        # Add past assistant messages to cached messages
        for assistance_msg in st.session_state.generated:
            cached_messages.append(cachemessage.set_message(assistance_msg, "assistant"))
            
        return cached_messages