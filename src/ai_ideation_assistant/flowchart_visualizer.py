import requests
import webbrowser
import openai

# Set OpenAI API endpoint and API key
#openai_endpoint = "https://api.openai.com/v1/engines/davinci-codex/completions"

openai.api_key= "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"


def generate_flowchart(input_text):
    prompt = f"Represent this text in a latex flowchart with only the keypoints mentioned in the flowchart. Also only show the code:  \n\n{input_text}"

    request = {"role": "system", "content": prompt}    
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", max_tokens = 520, messages=[request])

    return response['choices'][0]['message']['content']
        
with open('gpt_output_sample_for_visualizer.txt', 'r') as file:
    input_text = file.read()

output = generate_flowchart(input_text)
print(output)

with open('output_latex.tex', 'w') as f:
    f.write(output)
