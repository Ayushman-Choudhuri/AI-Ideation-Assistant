import openai
import subprocess
import os
from dotenv import load_dotenv

load_dotenv()

#openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = "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"

def generate_flowchart(input_text):
    prompt = f"Represent this text in a latex flowchart with only the keypoints mentioned in the flowchart. Use the tikz and xcolor package. draw a rectangular block around each block and the total diagram.Space the flowchart elements evenly .Only show the code.:  \n\n{input_text}"

    request = {"role": "system", "content": prompt}    
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", max_tokens = 520, messages=[request])

    return response['choices'][0]['message']['content']

def compile_latex(tex_file):
    """
    Compiles a LaTeX file and opens the resulting PDF in a pop-up window.
    """
    # Build the command to run
    command = ['pdflatex', '-interaction', 'nonstopmode', '-output-directory', '.', tex_file]

    # Run the command in a new subprocess
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()

    # Check for errors
    if proc.returncode != 0:
        print(stderr.decode('utf-8'))
        return None

    # Open the resulting PDF file in a pop-up window
    pdf_file = tex_file.replace('.tex', '.pdf')
    subprocess.Popen(['xdg-open', pdf_file])
        
with open('gpt_output_sample_for_visualizer.txt', 'r') as file:
    input_text = file.read()

output = generate_flowchart(input_text)


with open('output_latex.tex', 'w') as f:
    f.write(output)

compile_latex("output_latex.tex")