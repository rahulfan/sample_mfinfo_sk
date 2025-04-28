from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import requests
import difflib
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, List, Optional
import requests
from difflib import SequenceMatcher
from IPython.display import Image, display
from openai import OpenAI
client = OpenAI(api_key="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")


app = FastAPI()

def get_all_fund_info():
    """Fetch all mutual fund schemes"""
    url = "https://api.mfapi.in/mf"
    response = requests.get(url).json()
    dict1 = {}
    for i in response:
        dict1[i['schemeName']] = i['schemeCode']
    return dict1   

dict1 = get_all_fund_info()
dict1_inverse = {j:i for i,j in dict1.items()}

def get_scheme_code(mf_name):
    closest_mf = difflib.get_close_matches(mf_name,list(dict1.keys()),cutoff=0)[0]
    print(f"Closest mf for {mf_name} is {closest_mf}")
    return dict1[closest_mf]

@app.get("/funds/{scheme_code}")
def extract_mf_info(scheme_code):
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    response = requests.get(url).json()
    return response

class Schema_Codes(BaseModel):
    numbers: List[int]
        
class Queryinfo(BaseModel):
    query:str

@app.post("/funds/compare")
def compare_mfs(mf_list:Schema_Codes):
    response_list = []
    print(mf_list.numbers)
    for i in mf_list.numbers:
        response_1 = extract_mf_info(i)
        response_list.append([{'fund_name':dict1_inverse[i]},response_1['meta'],response_1['data'][0]])
    return response_list
   
@app.post("/ai/query")
def answer_query(query:Queryinfo):
    query1 = query.query
    prompt1 = f'''Extract the name of the mutual fund from query : {query1}.Only return the name and not the entire answer sentence.'''
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
                {"role": "system", "content": "You are an AI that answers question related to Queries about Mutual Funds."},
                {"role": "user", "content":prompt1}
        ]
    )

    mf_name = completion.choices[0].message.content
    mf_scheme_code = get_scheme_code(mf_name)
    mf_info = extract_mf_info(mf_scheme_code)
    prompt2 = f'''Using the following information about {mf_name} : {mf_info['meta'], mf_info['data'][0]}, answer the following query : {query1}'''
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
                {"role": "system", "content": "You are an AI that answers question related to Queries about Mutual Funds."},
                {"role": "user", "content":prompt2}
        ]
    )
    print(completion.choices[0].message.content)