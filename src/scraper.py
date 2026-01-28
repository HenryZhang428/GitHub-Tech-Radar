import os
import requests
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def get_trending_repos(since='daily', language='', limit=10):
    """
    Fetch trending repositories from GitHub Search API.
    
    Args:
        since (str): 'daily', 'weekly', 'monthly'
        language (str): Programming language filter
        limit (int): Number of repos to fetch
    """
    if since == 'daily':
        since_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    elif since == 'weekly':
        since_date = (datetime.now() - timedelta(weeks=1)).strftime('%Y-%m-%d')
    elif since == 'monthly':
        since_date = (datetime.now() - timedelta(weeks=4)).strftime('%Y-%m-%d')
    else:
        since_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    query = f'created:>{since_date}'
    if language:
        query += f' language:{language}'

    url = "https://api.github.com/search/repositories"
    params = {
        "q": query,
        "sort": "stars",
        "order": "desc",
        "per_page": limit
    }
    
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Add token if available to increase rate limit
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"

    try:
        logger.info(f"Fetching trending repos with query: {query}")
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get("items", [])
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data from GitHub: {e}")
        return []

def search_repos(query, limit=10):
    """
    Search repositories by keyword with smart filtering.
    """
    url = "https://api.github.com/search/repositories"
    
    # Improved Search Strategy:
    # 1. Don't force stars>100 if query is very specific (might be a new/niche project)
    # 2. But for generic queries, we want quality.
    
    is_specific = " " not in query and len(query) > 5 # Simple heuristic for single word proper noun
    
    if is_specific:
        # For specific names like "xiaozhi", search broadly but sort by match
        final_query = query
        sort_mode = "best_match" # Default behavior when sort param is omitted or specified
    else:
        # For generic terms like "ai assistant", filter by stars to reduce noise
        final_query = f"{query} stars:>50" # Lower threshold to catch rising stars
        sort_mode = "stars"
    
    params = {
        "q": final_query,
        "per_page": limit
    }
    
    if not is_specific:
        params["sort"] = sort_mode
        params["order"] = "desc"
    
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }
    
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"

    try:
        logger.info(f"Searching repos with query: {final_query}, sort: {sort_mode}")
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get("items", [])
    except requests.exceptions.RequestException as e:
        logger.error(f"Error searching GitHub: {e}")
        return []
