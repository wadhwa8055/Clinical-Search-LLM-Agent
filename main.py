from fastapi import FastAPI, HTTPException
from pubmed_utils import search_pubmed_bioc

# Initialize FastAPI app
app = FastAPI()

@app.get("/")
def root():
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
    # Search for articles using the utility function
    articles = search_pubmed_bioc(disease, max_results)
    
    if not articles:
        raise HTTPException(status_code=404, detail="No articles found for the given query.")
    
    if format == "plain":
        # Return plain text articles (title and abstract)
        return articles
    elif format == "bioc":
        # Return the full BioC format data
        return {
            "format": "BioC",
            "data": articles
        }
    else:
        raise HTTPException(status_code=400, detail="Invalid format. Use 'plain' or 'bioc'.")
