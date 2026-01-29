from mcp.server.fastmcp import FastMCP
from scraper import get_trending_repos, search_repos, search_hidden_gems
from llm import LLMAnalyzer
import json

# Initialize the MCP Server
mcp = FastMCP("GitHub Tech Radar")
analyzer = LLMAnalyzer()

@mcp.tool()
def get_trending(since: str = "daily", language: str = "", limit: int = 10) -> str:
    """
    Get trending repositories from GitHub.
    
    Args:
        since: 'daily', 'weekly', or 'monthly'. Defaults to 'daily'.
        language: Programming language to filter by (e.g., 'python', 'javascript').
        limit: Number of repositories to return. Defaults to 10.
    """
    repos = get_trending_repos(since=since, language=language, limit=limit)
    return json.dumps(repos, indent=2)

@mcp.tool()
def search_github(query: str, limit: int = 10) -> str:
    """
    Search for repositories on GitHub.
    
    Args:
        query: Search keywords (e.g., 'machine learning', 'react components').
        limit: Number of results to return. Defaults to 10.
    """
    # Use the existing smart search logic
    repos = search_repos(query, limit=limit)
    return json.dumps(repos, indent=2)

@mcp.tool()
def find_hidden_gems(limit: int = 5) -> str:
    """
    Find 'Hidden Gems': high-potential but low-star repositories.
    Useful for discovering new, innovative tools that aren't famous yet.
    
    Args:
        limit: Number of gems to find. Defaults to 5.
    """
    gems = search_hidden_gems(limit=limit)
    
    # Optional: Enrich with lightweight AI analysis if possible
    # For speed in MCP, we might skip the full LLM analysis loop here
    # or just return the raw data which is often enough for the calling Agent to analyze.
    
    return json.dumps(gems, indent=2)

@mcp.tool()
def analyze_repo_potential(name: str, description: str, language: str) -> str:
    """
    Use local AI to analyze the potential of a specific repository.
    
    Args:
        name: Repository name.
        description: Repository description.
        language: Primary programming language.
    """
    analysis = analyzer.analyze_potential(name, description, language)
    return analysis

if __name__ == "__main__":
    mcp.run()
