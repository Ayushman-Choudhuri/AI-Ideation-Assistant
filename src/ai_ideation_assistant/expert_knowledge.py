import openai
import os
import pandas as pd
from numpy import dot
from numpy.linalg import norm
import numpy as np
from dotenv import load_dotenv
import yaml

#load api key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Import configuration parameters from config.yml
with open('config.yml' , 'r') as f:
    config =yaml.safe_load(f)['sokrates']['expert_knowledge']


def cosine_similarity(query, target):
    return  (query @ target)/(norm(query)*norm(target))

def get_embedding(text, model="text-embedding-ada-002"):
    text = text.replace("\n", " ")
    return openai.Embedding.create(input = [text], model=model)['data'][0]['embedding']

def retrieve(query, path=config['database_path'], top_k=config['top_k_results']):
    
    df_raw = pd.read_excel(path)  

    df_raw = df_raw.dropna(subset=['Summary'])
    df_raw = df_raw.reset_index(drop=True)

    df_raw['ada_embedding'] = df_raw['Summary'].apply(lambda x: np.array(get_embedding(x, model='text-embedding-ada-002')))
    query = np.array(get_embedding("Test Input", model='text-embedding-ada-002'))
    df_raw['embedding_dist'] = df_raw['ada_embedding'].apply(lambda target: cosine_similarity(query, target))
    indices = (df_raw['embedding_dist'] * -1 ).argsort()[:top_k] 
    relevant_summaries = [df_raw['Summary'].loc[index] for index in indices]
    return relevant_summaries


if __name__ == "__main__":

    pass