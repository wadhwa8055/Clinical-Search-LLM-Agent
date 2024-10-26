from fastapi import FastAPI, HTTPException
from pubmed_utils import search_pubmed_bioc
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph, MessagesState
from schemas import UserQuery
import uuid
from langgraph.prebuilt import ToolNode
import openai
from fastapi import FastAPI, HTTPException
from pubmed_utils import search_pubmed_bioc
from schemas import UserQuery
import openai
from langgraph.prebuilt import create_react_agent, ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from datetime import datetime
import os

app = FastAPI()

# openai.api_key = os.getenv("OPENAI_API_KEY")

# if not openai.api_key:
#     raise ValueError("The OPENAI_API_KEY environment variable is not set.")

def search_pubmed_tool(disease: str, max_results: int = 5) -> str:
    """
    search tool node TODO add doc comments
    """
    articles = search_pubmed_bioc(disease, max_results)
    if not articles:
        return "No articles found for the specified disease."
    return "\n".join([f"Title: {article['title']}\nAbstract: {article['abstract']}\n" for article in articles])


tools = [search_pubmed_tool]
model = ChatOpenAI(model="gpt-4-turbo", api_key="sk-proj-xBBcHihlwiv5lt85SN0aT3BlbkFJKP5Jmjg2mg3FPpdLyXhw")

system_prompt = "You are a medical research assistant that helps users find information on diseases."

graph = create_react_agent(model, tools=tools, state_modifier=system_prompt, checkpointer=MemorySaver())

@app.get("/")
def root():
    """
    root node TODO add doc comments
    """
    return {"message": "Welcome to PubMed Article Search API"}

@app.get("/search/")
def search_articles(disease: str, format: str = "plain", max_results: int = 10):
    """
    Search PubMed articles by disease name. Returns results in either plain text or BioC format.
    
    :param disease: Name of the disease or search term
    :param format: 'plain' for plain text (title, abstract) or 'bioc' for BioC format
    :param max_results: Number of articles to retrieve
    :return: List of articles (title, abstract) or BioC format articles
    """
    articles = search_pubmed_bioc(disease, max_results)
    
    if not articles:
        raise HTTPException(status_code=404, detail="No articles found for the given query.")
    
    if format == "plain":
        return articles
    elif format == "bioc":
        return {
            "format": "BioC",
            "data": articles
        }
    else:
        raise HTTPException(status_code=400, detail="Invalid format. Use 'plain' or 'bioc'.")
    
@app.post("/chat/")
def chat_with_agent(user_query: UserQuery):
    """
    Chatbot endpoint that interacts with PubMed using a LangGraph ReAct agent.
    
    :param user_query: User's input message.
    :return: Response from the chatbot, either article summaries or relevant suggestions.
    """
    try:
        inputs = {"messages": [("user", user_query.query)]}
        config = {"configurable": {"thread_id": str(user_query.thread_id)}}
        
        response_messages = []
        for s in graph.stream(inputs, config=config, stream_mode="values"):
            message = s["messages"][-1]
            if isinstance(message, tuple):
                response_messages.append(message[1])
            else:
                response_messages.append(message.content)
        
        return {"response": "\n".join(response_messages)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")