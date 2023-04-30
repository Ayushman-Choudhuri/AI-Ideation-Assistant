import openai

def set_message(message, role):
    return {"role": role, "content": message}

def summarize_LM(cached_messages):

    # SUMMARIZATION_PROMPT = 'Summarize the conversation a chatbot had with a user \
    #                         in a structured manner in the way a consultant would do \
    #                         and emphasize the key insights \
    #                         and solutions to take away.'
    SUMMARIZATION_PROMPT = 'Create a summary of the conversation with the following structure: \
                            Problem | Methods | Solution'
    summarize_message = set_message(SUMMARIZATION_PROMPT, role="system")
    cached_messages.append(summarize_message)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        #max_tokens = INITIAL_MAX_TOKENS,
        messages=cached_messages
    )
    return cached_messages, response
