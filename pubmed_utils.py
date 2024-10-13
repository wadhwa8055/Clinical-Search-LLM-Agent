import requests
import xml.etree.ElementTree as ET
import bioc
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def search_pubmed_bioc(disease, max_results=10):
    """
    Search PubMed and retrieve articles in BioC format using the BioC library.
    
    :param query: Disease or search term (e.g., Alzheimer's disease)
    :param max_results: Maximum number of articles to retrieve
    :return: List of article titles and abstracts in BioC format
    """
    query = f"What is {disease}"
    # Step 1: Use PubMed's E-utilities to search for articles
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    search_params = {
        'db': 'pubmed',
        'term': query,
        'retmax': max_results,
        'retmode': 'xml',
        'sort': 'relevance'
    }
    
    # Log the search URL and parameters
    search_url = f"{base_url}?db=pubmed&term={query}&retmax={max_results}&retmode=xml&sort=relevance"
    logger.info(f"Searching PubMed with URL: {search_url}")
    
    search_response = requests.get(base_url, params=search_params)
    
    # Log the response status and content
    logger.info(f"Search Response Status Code: {search_response.status_code}")
    if search_response.status_code != 200:
        logger.error(f"Error fetching search results: {search_response.text}")
        return []
    
    # Parse the XML response to extract PubMed IDs
    root = ET.fromstring(search_response.content)
    article_ids = [id_elem.text for id_elem in root.findall("./IdList/Id")]

    if not article_ids:
        logger.info("No articles found for the given query.")
        return []

    logger.info(f"Article IDs found: {article_ids}")
    
    # Step 2: Use efetch to retrieve the articles in BioC format
    fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    fetch_params = {
        'db': 'pubmed',
        'id': ','.join(article_ids),
        'retmode': 'xml',
        'rettype': 'abstract'  # Ensures that we fetch the abstract in XML format
    }
    
    # Log the full fetch URL with the parameters
    full_url = f"{fetch_url}?db=pubmed&id={','.join(article_ids)}&retmode=xml&rettype=abstract"
    logger.info(f"Full Fetch URL: {full_url}")
    
    try:
        # Adding a timeout of 10 seconds
        fetch_response = requests.get(fetch_url, params=fetch_params, timeout=10)
    except requests.Timeout:
        logger.error("The request to PubMed timed out.")
        return []
    
    # Log the response status and content
    logger.info(f"Fetch Response Status Code: {fetch_response.status_code}")
    if fetch_response.status_code != 200:
        logger.error(f"Error fetching article details: {fetch_response.text}")
        return []
    
    # Parse the XML response manually
    articles = []
    try:
        root = ET.fromstring(fetch_response.content)
        for pubmed_article in root.findall("./PubmedArticle"):
            title = pubmed_article.find(".//ArticleTitle").text if pubmed_article.find(".//ArticleTitle") is not None else "No title available"
            abstract = "No abstract available"
            abstract_element = pubmed_article.find(".//Abstract")
            if abstract_element is not None:
                abstract_texts = [elem.text for elem in abstract_element.findall(".//AbstractText")]
                abstract = ' '.join(abstract_texts) if abstract_texts else "No abstract available"
            
            articles.append({
                'title': title,
                'abstract': abstract
            })
            logger.info(f"Title: {title}, Abstract: {abstract}")
    except ET.ParseError as e:
        logger.error(f"Error parsing the XML response: {e}")
        return []
    
    logger.info(f"Total articles parsed: {len(articles)}")
    return articles