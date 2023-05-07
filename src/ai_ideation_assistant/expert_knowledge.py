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

with open('config.yml', 'r') as f:
    config = yaml.safe_load(f)
    config_path = config.get('sokrates', {}).get('path', '')
    config_exp_knw = config.get('sokrates', {}).get('expert_knowledge', {})

def cosine_similarity(query, target):
    """
    Compute the cosine similarity between two vectors.

    Parameters
    ----------
    query : numpy.ndarray
        Vector representation of the query.
    target : numpy.ndarray
        Vector representation of the target.

    Returns
    -------
    float
        Cosine similarity between the query and target vectors.
    """
    return  (query @ target)/(norm(query)*norm(target))

def get_embedding(text, model="text-embedding-ada-002"):
    """
    Get the embedding vector for a given text using the specified model.

    Parameters
    ----------
    text : str
        The input text for which the embedding vector is required.
    model : str, optional
        The name of the OpenAI model to be used for generating the embedding, by default "text-embedding-ada-002".

    Returns
    -------
    numpy.ndarray
        Vector representation of the input text generated by the specified model.
    """
    text = text.replace("\n", " ")
    return openai.Embedding.create(input = [text], model=model)['data'][0]['embedding']

def retrieve(query, path=config_path['database_path'], top_k=config_exp_knw['top_k_results']):
    """
    Retrieve the most relevant summary text(s) from the database for the given query.

    Parameters
    ----------
    query : str
        The query text for which relevant summaries are to be retrieved.
    path : str, optional
        The file path to the database of summaries, by default as specified in the config file.
    top_k : int, optional
        The number of top relevant summaries to be retrieved, by default as specified in the config file.

    Returns
    -------
    list
        List of top_k most relevant summary text(s) for the given query.
    """
    
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