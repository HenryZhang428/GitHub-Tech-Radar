import time
import logging
import os
from datetime import datetime
from cache_manager import TrendingCache
from generator import generate_markdown, generate_html, save_report
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("service.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def update_hourly(cache_manager):
    """Fetch latest data and update TODAY.md and index.html"""
    logger.info("Running hourly update...")
    
    # 1. Fetch Trending (Global)
    trending_data = cache_manager.get_data(since='daily', force_refresh=True)
    
    # 2. Fetch VIP (Watchlist)
    vip_data = cache_manager.get_vip_activities(force_refresh=True)
    
    date_str = datetime.now().strftime('%Y-%m-%d')
    time_str = datetime.now().strftime('%H:%M')
    
    # 3. Generate Markdown Report
    content = f"# GitHub Daily Insight - {date_str}\n\n"
    content += f"> 🔄 Last Updated: {time_str}\n\n"
    
    content += "## 🔥 Global Trending\n\n"
    content += generate_markdown(trending_data, date_str, 'daily').split('\n', 4)[-1] # Reuse generator logic but skip header
    
    content += "\n\n## 👀 VIP Watchlist Activity\n\n"
    if vip_data:
        for act in vip_data:
            icon = "⭐️" if act['type'] == 'star' else "🆕"
            content += f"- {icon} **{act['user']}** {act['description']} [{act['repo_name']}]({act['repo_url']}) - *{act['time']}*\n"
    else:
        content += "*No recent activity from VIPs.*\n"
        
    save_report(content, "TODAY.md")
    logger.info("Updated TODAY.md")
    
    # 4. Generate HTML Dashboard
    html_content = generate_html(trending_data, vip_data, date_str)
    save_report(html_content, "dashboard.html")
    logger.info("Updated dashboard.html")

def archive_daily():
    """Copy TODAY.md to archives/YYYY-MM-DD.md"""
    date_str = datetime.now().strftime('%Y-%m-%d')
    archive_path = f"archives/{date_str}.md"
    
    if os.path.exists("TODAY.md"):
        with open("TODAY.md", 'r') as f:
            content = f.read()
        
        save_report(content, archive_path)
        logger.info(f"Archived report to {archive_path}")
    else:
        logger.warning("No TODAY.md found to archive.")

def main():
    load_dotenv()
    cache_manager = TrendingCache(ttl_seconds=3600)
    
    logger.info("Service started. Press Ctrl+C to stop.")
    
    last_archive_date = None
    
    try:
        while True:
            current_date = datetime.now().strftime('%Y-%m-%d')
            
            # 1. Hourly Update
            update_hourly(cache_manager)
            
            # 2. Daily Archive (Check if it's a new day or near end of day)
            # Simple logic: If current date != last archive date, and it's 23:xx, archive it.
            # Or simpler: Archive every time we update, overwriting the file. 
            # This ensures the archive is always up to date with the latest fetch of that day.
            archive_daily()
            
            # Sleep for 1 hour
            logger.info("Sleeping for 1 hour...")
            time.sleep(3600)
            
    except KeyboardInterrupt:
        logger.info("Service stopped by user.")
    except Exception as e:
        logger.error(f"Service crashed: {e}")

if __name__ == "__main__":
    main()
