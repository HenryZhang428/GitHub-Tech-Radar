import os
import logging
from datetime import datetime
from dotenv import load_dotenv

from scraper import get_trending_repos
from llm import LLMAnalyzer
from generator import generate_markdown, save_report

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    # Load env vars
    load_dotenv()
    
    # Config
    since = os.getenv("TRENDING_SINCE", "daily")
    limit = int(os.getenv("TRENDING_LIMIT", "10"))
    
    date_str = datetime.now().strftime('%Y-%m-%d')
    logger.info(f"Starting GitHub Trending job for {date_str} ({since})")
    
    # 1. Fetch
    repos = get_trending_repos(since=since, limit=limit)
    if not repos:
        logger.warning("No repositories found.")
        return

    # 2. Analyze
    analyzer = LLMAnalyzer()
    for repo in repos:
        logger.info(f"Analyzing {repo['name']}...")
        analysis = analyzer.analyze_repo(repo['name'], repo['description'], repo['language'])
        repo['ai_analysis'] = analysis

    # 3. Generate Report
    markdown_content = generate_markdown(repos, date_str, since)
    
    # 4. Save
    filename = f"archives/{date_str}.md"
    save_report(markdown_content, filename)
    logger.info(f"Report saved to {filename}")
    
    # Update README (Simple append for now, or just leave it)
    # In a real "high star" repo, we would update a summary index in README.
    
    logger.info("Job finished successfully.")

if __name__ == "__main__":
    main()
