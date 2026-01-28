import rumps
import rumps.rumps
import os
import webbrowser
import threading
import logging
from cache_manager import TrendingCache
from dotenv import load_dotenv

# Monkeypatch application_support to use a local directory
# This prevents the app from trying to write to ~/Library/Application Support/
# which is restricted in the sandbox environment.
def local_application_support(name):
    local_path = os.path.join(os.getcwd(), ".app_support", name)
    if not os.path.exists(local_path):
        os.makedirs(local_path, exist_ok=True)
    return local_path

rumps.rumps.application_support = local_application_support

# Setup logging
logging.basicConfig(level=logging.INFO)

class GitHubTrendingApp(rumps.App):
    def __init__(self):
        super(GitHubTrendingApp, self).__init__("GH Trend", icon=None)
        
        load_dotenv()
        
        # Initialize Cache Manager (1 hour TTL)
        self.cache_manager = TrendingCache(ttl_seconds=3600, cache_file="data/cache.json")
        
        # State
        self.current_language = ""  # "" means all
        self.current_view = "trending" # "trending" or "vip"
        self.available_languages = ["All", "Python", "JavaScript", "Rust", "Go", "Java", "C++"]
        
        # Initial Menu Setup
        self.menu = ["Loading..."]
        
        # Start initial load
        self.update_lock = threading.Lock()
        threading.Thread(target=self.bg_fetch_data, daemon=True).start()

    @rumps.timer(1)
    def check_updates(self, _):
        # This runs on the main thread every 1 second
        # We can use a queue or just check a flag to update UI
        pass

    @rumps.timer(3600)
    def auto_refresh(self, _):
        threading.Thread(target=self.bg_fetch_data, daemon=True).start()

    def bg_fetch_data(self, sender=None):
        # Background thread for fetching data
        print(f"Fetching data for view='{self.current_view}' lang='{self.current_language}'...")
        
        # Update title safely? No, can't update title from thread easily in rumps without risk.
        # But we can try to rely on rumps internal safety or just update main UI in a callback.
        # Since rumps wraps Cocoa, we must update UI on main thread.
        
        # Workaround: Use a timer to poll for data, or simply trigger a callback via a shared state.
        try:
            if self.current_view == "trending":
                data = self.cache_manager.get_data(
                    since='daily', 
                    language=self.current_language if self.current_language != "All" else ""
                )
            else: # vip
                data = self.cache_manager.get_vip_activities()
            
            # Pass data to main thread function
            rumps.timer(0.1)(lambda _: self.update_ui_main_thread(data))
        except Exception as e:
            print(f"Error fetching data: {e}")

    def update_ui_main_thread(self, data):
        # This should be called from the main thread (via timer callback hack)
        print("Updating UI on main thread...")
        self.title = "GH Trend"
        self.update_menu(data)

    def refresh_data(self, _=None):
        # Manually triggered refresh
        self.title = "GH Trend ⏳"
        threading.Thread(target=self.bg_fetch_data, daemon=True).start()

    def update_menu(self, data):
        # 1. Static Controls
        menu_items = []
        
        # View Switcher
        view_menu = rumps.MenuItem("👁️ View Mode")
        item_trending = rumps.MenuItem("🔥 Trending Repos", callback=self.set_view)
        item_trending.state = 1 if self.current_view == "trending" else 0
        view_menu.add(item_trending)
        
        item_vip = rumps.MenuItem("👀 VIP Watchlist", callback=self.set_view)
        item_vip.state = 1 if self.current_view == "vip" else 0
        view_menu.add(item_vip)
        
        menu_items.append(view_menu)
        
        # Language Filter (Only for Trending view)
        if self.current_view == "trending":
            lang_menu = rumps.MenuItem("🔍 Filter Language")
            for lang in self.available_languages:
                item = rumps.MenuItem(lang, callback=self.set_language)
                item.state = 1 if (lang == self.current_language or (lang == "All" and self.current_language == "")) else 0
                lang_menu.add(item)
            menu_items.append(lang_menu)
        else:
            # VIP Management
            menu_items.append(rumps.MenuItem("⚙️ Edit Watchlist", callback=self.edit_watchlist))
        
        menu_items.append(rumps.MenuItem("🔄 Refresh Now", callback=self.refresh_data))
        menu_items.append(rumps.separator)
        
        # 2. Content List
        if not data:
             menu_items.append(rumps.MenuItem("No data found"))
        
        if self.current_view == "trending":
            self._render_trending_items(data, menu_items)
        else:
            self._render_vip_items(data, menu_items)
            
        menu_items.append(rumps.separator)
        menu_items.append(rumps.MenuItem("Quit", callback=rumps.quit_application))
        
        # Update menu
        self.menu.clear()
        self.menu.update(menu_items)

    def _render_trending_items(self, repos, menu_items):
        for repo in repos:
            icon = "🔥" if repo['stargazers_count'] > 1000 else "⭐"
            lang_icon = self._get_lang_icon(repo['language'])
            
            title = f"{icon} {repo['name']} ({lang_icon} {repo['stargazers_count']})"
            item = rumps.MenuItem(title, callback=self.open_repo)
            
            item.repo_url = repo['html_url']
            item.ai_analysis = repo.get('ai_analysis', '暂无分析')
            
            analysis_btn = rumps.MenuItem("🧠 View AI Analysis", callback=self.show_analysis)
            analysis_btn.analysis_text = item.ai_analysis
            analysis_btn.repo_name = repo['name']
            item.add(analysis_btn)
            
            menu_items.append(item)

    def _render_vip_items(self, activities, menu_items):
        # Group by user for better display? Or just flat list sorted by time?
        # Let's do flat list for now but with clear prefixes
        
        for act in activities:
            # Format: [User] starred [Repo]
            icon = "⭐️" if act['type'] == 'star' else "🆕"
            title = f"{icon} {act['user']} {act['description']}"
            
            # Truncate if too long
            if len(title) > 50:
                title = title[:47] + "..."
                
            item = rumps.MenuItem(title, callback=self.open_repo)
            item.repo_url = act['repo_url']
            
            # Submenu details
            item.add(rumps.MenuItem(f"User: {act['user']}"))
            item.add(rumps.MenuItem(f"Time: {act['time']}"))
            item.add(rumps.MenuItem("Open Repo", callback=self.open_repo))
            
            menu_items.append(item)

    def set_view(self, sender):
        self.current_view = "trending" if "Trending" in sender.title else "vip"
        self.refresh_data(None)

    def set_language(self, sender):
        # sender.title is usually just "Python", but we need to handle "All"
        # And importantly, we need to update the tick mark state visually
        
        # Reset all states
        # Accessing the menu object directly to find the language submenu
        # rumps structure is a bit flat, but we can iterate our constructed menu
        # This is tricky in rumps. Easier to just rebuild the whole menu in update_menu
        
        self.current_language = "" if sender.title == "All" else sender.title
        self.refresh_data(None)

    def edit_watchlist(self, _):
        # Simple alert to tell user to edit the file
        # In a real app we'd open a window
        config_path = self.cache_manager.config_file
        rumps.alert("Edit Watchlist", f"Please edit the file '{config_path}' to add/remove users.\n\nCurrent users: {', '.join(self.cache_manager.watchlist)}")
        # Optionally open the file in default editor
        import subprocess
        subprocess.call(['open', config_path])

    def show_analysis(self, sender):
        msg = f"{sender.analysis_text}\n\n(Click 'OK' to close)"
        rumps.alert(title=f"🧠 AI Analysis: {sender.repo_name}", message=msg)

    def open_repo(self, sender):
        if hasattr(sender, 'repo_url'):
            webbrowser.open(sender.repo_url)

    def _get_lang_icon(self, lang):
        icons = {
            "Python": "🐍", "JavaScript": "🟨", "TypeScript": "📘", 
            "Rust": "🦀", "Go": "🐹", "Java": "☕", "C++": "⚡️"
        }
        return icons.get(lang, "📝")

if __name__ == "__main__":
    GitHubTrendingApp().run()
