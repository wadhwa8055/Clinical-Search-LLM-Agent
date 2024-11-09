from fastapi import FastAPI, HTTPException
from pubmed_utils import search_pubmed_bioc
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START
from schemas import UserQuery
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
import os 
import datetime
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("The OPENAI_API_KEY environment variable is not set.")

app = FastAPI()

def search_pubmed_tool(disease: str, max_results: int = 10) -> str:
    """
    search tool node TODO add doc comments
    """
    articles = search_pubmed_bioc(disease, max_results)
    if not articles:
        return "No articles found for the specified disease."
    
        # Create a directory to store files, if it doesn't exist
    os.makedirs("articles", exist_ok=True)
    
    # Loop through each article and save it to a file
    for i, article in enumerate(articles, start=1):
        file_name = f"articles/{disease.replace(' ', '_').lower()}-{i}.txt"
        with open(file_name, "w") as file:
            file.write(f"Title: {article['title']}\n")
            file.write(f"Abstract: {article['abstract']}\n")
    return "\n".join([f"Title: {article['title']}\nAbstract: {article['abstract']}\n" for article in articles])


tools = [search_pubmed_tool]
model = ChatOpenAI(model="gpt-4-turbo", api_key=OPENAI_API_KEY)

system_prompt = """
You are a medical research assistant who helps users find comprehensive information on rare diseases.
Depending on the complexity and detail required, you may use specialized tools to retrieve relevant PubMed articles.
If you use the tool, integrate up to 10 titles and abstracts into your response. Do not display them directly; 
use them only as context to generate a structured and informative summary, including these sections:

1. **Overview**: Define the disease and provide background, affected populations, and prevalence.
2. **Causes**: Describe causes in both lay and technical terms with citations if available.
3. **Clinical Presentation**: Outline symptoms and suggest visual aids if necessary.
4. **Complications**: Explain potential complications for both general and professional audiences.
5. **Diagnosis**: Summarize diagnostic methods and suggest visual aids.
6. **Treatment Options**: Outline treatments with clarity for patients and depth for professionals.
7. **Prognosis**: Describe the expected disease course, including data on outcomes.
8. **Research and Clinical Trials**: Include recent research or trials.
9. **Support and Advocacy Resources**: List resources and support networks with citations.

If the tool is used, state "I am using a tool to gather relevant PubMed information."
When generating your response, insert numbered references within the text as needed to indicate the source used, like this: [1].
At the end of the response, list the full citation details under "References," with each reference number matching the in-text citations.
You will provide References as:
[1] "Title" of paper used from PubMed

At the end of the summary, ask the user if they have questions or need more details.
"""


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
        
        final_response = ""

        for s in graph.stream(inputs, config=config, stream_mode="values"):
            message = s["messages"][-1]
            print("Message from stream:", message)
            
            if message.content and "tool_calls" not in message.additional_kwargs:
                final_response = message.content
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        disease_name = user_query.query.replace(" ", "_").lower()
        file_name = f"chat_responses/{disease_name}_{timestamp}.txt"
        
        # Ensure the directory exists
        os.makedirs("chat_responses", exist_ok=True)
        with open(file_name, "w") as file:
            file.write(f"Query: {user_query.query}\n")
            file.write(f"Response:\n{final_response}\n")

        return {"response": final_response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")