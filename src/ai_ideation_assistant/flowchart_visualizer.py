import openai
import os
from dotenv import load_dotenv
import subprocess

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_flowchart(input_text):
    prompt = f"Represent this text in a latex flowchart with only the keypoints mentioned in the flowchart. \
               Use the tikz and xcolor package. draw a rectangular block around each block and the total diagram  \
               Output needs to be only in one page\
               Only show the code.:  \n\n{input_text}"
    
    #Exprimental Prompts 
    #Space the flowchart elements evenly . If there exists a feedback loop process such as refining, feedback , etc add the correct loop in the digram \
    #The close loop arrow needs to be the same thickness as the other arrow. \
    #Use only 90 degree bends on arrows\

    request = {"role": "system", "content": prompt}    
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", max_tokens = 520, messages=[request])

    return response['choices'][0]['message']['content']
        
def latex_to_pdf(latex_file_path):
    # Compile the LaTeX file to a PDF file
    pdf_file_path = os.path.splitext(latex_file_path)[0] + '.pdf'
    subprocess.run(['pdflatex', '-interaction=nonstopmode', latex_file_path], check=True)
    
    return pdf_file_path


########################################### test ##########################################3###

#Import a test chat gpt output
with open('./gpt-sample-outputs/gpt_output_sample_3.txt', 'r') as file:
    input_text = file.read()

## Generate a latex code from the gpt prompt
output = generate_flowchart(input_text)

## Generate a .tex file with the out
with open('output_latex.tex', 'w') as f:
    f.write(output)

pdf_file_path = latex_to_pdf('output_latex.tex')


#################################################################################################