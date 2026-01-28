from datetime import datetime
import os
import json
from jinja2 import Environment, FileSystemLoader

def generate_markdown(repos, date_str, period='daily'):
    """
    Generate a markdown report for the repositories.
    """
    title = f"GitHub {period.capitalize()} Trending - {date_str}"
    
    content = f"# {title}\n\n"
    content += f"> 📅 Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    content += "Here are the trending repositories based on creation date and stars.\n\n"
    
    content += "| Project | Stars | Language | AI Analysis |\n"
    content += "|---------|-------|----------|-------------|\n"
    
    for repo in repos:
        name = repo.get('name')
        url = repo.get('html_url')
        stars = repo.get('stargazers_count')
        language = repo.get('language') or 'Unknown'
        analysis = repo.get('ai_analysis', '').replace('\n', ' ')
        
        # Escape pipes in analysis to avoid breaking table
        analysis = analysis.replace('|', '\\|')
        
        content += f"| [{name}]({url}) | {stars} | {language} | {analysis} |\n"
        
    return content

def generate_html(repos, vip_activities, date_str):
    """
    Generate an HTML dashboard using Jinja2 template.
    """
    env = Environment(loader=FileSystemLoader('src/templates'))
    template = env.get_template('index.html')
    
    return template.render(
        trending_repos=repos,
        vip_activities=vip_activities,
        date=date_str,
        last_updated=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )

def save_report(content, filename):
    """Save content to file"""
    dirname = os.path.dirname(filename)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
        
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

def update_readme(latest_report_link, date_str):
    """
    Update the main README with the latest link.
    This is a placeholder. In a real scenario, we might append to a list.
    """
    pass
