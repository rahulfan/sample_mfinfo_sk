import requests
import difflib

def get_all_fund_info():
    """Fetch all mutual fund schemes"""
    url = "https://api.mfapi.in/mf"
    response = requests.get(url).json()
    dict1 = {}
    for i in response:
        dict1[i['schemeName']] = i['schemeCode']
    return dict1   
    
dict1 = get_all_fund_info()

def extract_mf_info(mf_scheme_code):
    url = f"https://api.mfapi.in/mf/{mf_scheme_code}"
    response = requests.get(url).json()
    return response

def compare_mfs(mf_list):
    response_list = []
    for i in mf_list:
        response_1 = extract_mf_info(i)
        response_list.append([response_1['meta'],response_1['data'][0]])
    return response_list
            
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, List, Optional
import requests
from difflib import SequenceMatcher
from IPython.display import Image, display

# ------------- 1. State Schema --------------
class FundSearchState(TypedDict):
    mf_scheme_code: Optional[int]
    mf_scheme_codes_for_comparison: Optional[List[int]]

# ------------- 2. Tools -------------------
def Summarizer(state: FundSearchState) -> FundSearchState:
    print(extract_mf_info(state["mf_scheme_code"]))
    return {}

def Comparator(state: FundSearchState) -> FundSearchState:
    if state.get('mf_scheme_codes_for_comparison') and len(state['mf_scheme_codes_for_comparison']) >= 2:
        print(compare_mfs(state['mf_scheme_codes_for_comparison']))
        return {}

def QuestionRouter(state: FundSearchState) -> str:
    if "mf_scheme_code" in state:
        return 'Summarizer'
    elif "mf_scheme_codes_for_comparison" in state:
        return "Comparator"
    else:
        return "Followup"
    
def Followup(state: FundSearchState) -> FundSearchState:
    print("Your Question is not clear! Please resend with valid fields!")
    return {}


graph = StateGraph(FundSearchState)
graph.add_node("Summarizer", Summarizer)
graph.add_node("Comparator", Comparator)
graph.add_node("QuestionRouter", QuestionRouter)
graph.add_node("Followup", Followup)


# Define edges
graph.add_conditional_edges(START, QuestionRouter)
graph.add_edge("Followup", END)
graph.add_edge("Summarizer", END)
graph.add_edge("Comparator", END)

compiled_graph = graph.compile()
# print(compiled_graph.invoke({"mf_scheme_code" : 100027}))
# print(compiled_graph.invoke({"mf_scheme_codes_for_comparison" : [100027,100028]}))
# print(compiled_graph.invoke({}))