import openai
import os
from dotenv import load_dotenv
from pylatex import Document
import sys

# Load environment variables from .env file
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_flowchart(input_text):
    prompt = f"Represent this text in a latex flowchart with only the keypoints mentioned in the flowchart. \
               Use the tikz and xcolor package. draw a rectangular block around each block and the total diagram  \
               Space the flowchart elements evenly . If there exists a feedback loop process such as refining, feedback , etc add the correct loop in the digram \
               The close loop arrow needs to be the same thickness as the other arrow. \
               Use only 90 degree bends on arrows\
               Only show the code.:  \n\n{input_text}"

    request = {"role": "system", "content": prompt}    
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", max_tokens = 520, messages=[request])

    return response['choices'][0]['message']['content']
        
def latex_to_pdf(latex_file_path):
    # Create a PyLaTeX document object
    doc = Document()

    # Load the LaTeX file into the document object
    with open(latex_file_path, 'r') as f:
        doc.append(f.read())

    # Compile the document to PDF
    pdf_file_path = os.path.splitext(latex_file_path)[0] + '.pdf'
    doc.generate_pdf(pdf_file_path)

    return pdf_file_path


########################################### test ##########################################3###

#Import a test chat gpt output
with open('gpt_output_sample_3.txt', 'r') as file:
    input_text = file.read()

## Generate a latex code from the gpt prompt
output = generate_flowchart(input_text)

## Generate a .tex file with the out
with open('output_latex.tex', 'w') as f:
    f.write(output)

pdf_file_path = latex_to_pdf('output_latex.tex')

#################################################################################################