import json
import os
from flask import Flask, render_template, jsonify, request
from cache_manager import TrendingCache
from user_tracker import get_user_activities
from datetime import datetime

app = Flask(__name__)
cache_manager = TrendingCache(ttl_seconds=3600, cache_file="data/cache.json")

# Load recommended gurus
def load_gurus():
    gurus_path = os.path.join(os.path.dirname(__file__), 'data', 'gurus.json')
    if os.path.exists(gurus_path):
        with open(gurus_path, 'r') as f:
            return json.load(f)
    return {}

@app.route('/')
def dashboard():
    # Fetch data from cache (assuming service.py has populated it)
    # Default to daily
    trending_data = cache_manager.get_data(since='daily')
    vip_data = cache_manager.get_vip_activities()
    
    # Get current watchlist to mark gurus as followed
    watchlist = cache_manager.watchlist
    gurus = load_gurus()
    
    date_str = datetime.now().strftime('%Y-%m-%d')
    last_updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    return render_template('index.html', 
                           trending_repos=trending_data, 
                           vip_activities=vip_data,
                           date=date_str,
                           last_updated=last_updated,
                           gurus=gurus,
                           watchlist=watchlist,
                           current_period='daily')

@app.route('/api/trending')
def get_trending():
    since = request.args.get('since', 'daily')
    if since not in ['daily', 'weekly', 'monthly']:
        since = 'daily'
        
    # Force refresh if user explicitly asks? Maybe not for now to be fast.
    # But if data is missing, get_data will fetch it.
    trending_data = cache_manager.get_data(since=since)
    return jsonify(trending_data)

@app.route('/api/follow', methods=['POST'])
def follow_user():
    data = request.json
    username = data.get('username')
    
    if not username:
        return jsonify({"error": "Username required"}), 400
        
    watchlist = cache_manager.watchlist
    if username not in watchlist:
        # 1. Update Watchlist
        watchlist.append(username)
        cache_manager.save_watchlist(watchlist)
        
        # 2. Immediately fetch data for this new user
        try:
            new_activities = get_user_activities([username])
            
            # 3. Merge with existing cache
            current_activities = cache_manager.get_vip_activities() or []
            # Filter out any existing activities for this user (just in case) to avoid dupes
            current_activities = [act for act in current_activities if act['user'] != username]
            
            updated_activities = current_activities + new_activities
            # Sort by time descending
            updated_activities.sort(key=lambda x: x['time'], reverse=True)
            
            # 4. Update Cache directly
            cache_manager._cache['vip_activities'] = updated_activities
            cache_manager._save_cache()
            
        except Exception as e:
            print(f"Error fetching new user data: {e}")
            
        return jsonify({"status": "success", "message": f"Followed {username}", "watchlist": watchlist})
    
    return jsonify({"status": "info", "message": f"Already following {username}"})

@app.route('/api/unfollow', methods=['POST'])
def unfollow_user():
    data = request.json
    username = data.get('username')
    
    if not username:
        return jsonify({"error": "Username required"}), 400
        
    watchlist = cache_manager.watchlist
    if username in watchlist:
        # 1. Remove from watchlist
        watchlist.remove(username)
        cache_manager.save_watchlist(watchlist)
        
        # 2. Remove their activities from cache
        current_activities = cache_manager.get_vip_activities() or []
        updated_activities = [act for act in current_activities if act['user'] != username]
        
        cache_manager._cache['vip_activities'] = updated_activities
        cache_manager._save_cache()
        
        return jsonify({"status": "success", "message": f"Unfollowed {username}", "watchlist": watchlist})
    
    return jsonify({"status": "info", "message": f"Not following {username}"})

from scraper import search_repos, search_hidden_gems

@app.route('/api/hidden-gems')
def get_hidden_gems():
    # 1. Fetch raw gems
    gems = search_hidden_gems(limit=6) # 6 is a good number for grid
    
    # 2. Analyze with LLM to find "Why it is a gem"
    for gem in gems:
        # Simple analysis
        gem['gem_analysis'] = cache_manager.llm_analyzer.analyze_potential(
            gem['name'], 
            gem['description'] or '', 
            gem['language'] or 'Unknown'
        )
        
    return jsonify(gems)

@app.route('/api/search', methods=['POST'])
def search():
    data = request.json
    query = data.get('query')
    
    if not query:
        return jsonify({"error": "Query required"}), 400
        
    # 1. Expand query using LLM (Cross-language support)
    expanded_query = cache_manager.llm_analyzer.expand_search_query(query)
    
    # 2. Search GitHub
    repos = search_repos(expanded_query)
    
    # 3. Analyze repos with LLM (Optional, maybe for top 3 to be fast?)
    # For now, let's just return raw results to be fast, 
    # and maybe frontend can trigger analysis or we show descriptions.
    # To be consistent with UI, let's just use description as ai_analysis fallback
    for repo in repos:
        repo['ai_analysis'] = f"{repo['description']} (Click to analyze)"
        
    return jsonify({"results": repos, "expanded_query": expanded_query})

@app.route('/api/translate', methods=['POST'])
def translate_text():
    data = request.json
    text = data.get('text')
    target_language = data.get('target_language', 'zh-CN')
    
    if not text:
        return jsonify({"error": "Text required"}), 400
        
    # Map common language codes to full names for LLM
    lang_map = {
        'zh-CN': 'Chinese',
        'en': 'English',
        'ja': 'Japanese',
        'es': 'Spanish',
        'ko': 'Korean',
        'fr': 'French',
        'de': 'German'
    }
    
    target_lang_name = lang_map.get(target_language, target_language)
    
    translated_text = cache_manager.llm_analyzer.translate(text, target_lang_name)
    return jsonify({"translated_text": translated_text})

@app.route('/api/settings/token', methods=['POST'])
def save_token():
    data = request.json
    token = data.get('token')
    
    if not token:
        # Clear token if empty string provided
        token = ""
        
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    
    try:
        # Read existing lines
        lines = []
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                lines = f.readlines()
        
        # Remove existing GITHUB_TOKEN line
        lines = [line for line in lines if not line.startswith('GITHUB_TOKEN=')]
        
        # Append new token
        if token:
            if lines and not lines[-1].endswith('\n'):
                lines.append('\n')
            lines.append(f'GITHUB_TOKEN={token}\n')
            
        with open(env_path, 'w') as f:
            f.writelines(lines)
            
        # Update current process env
        if token:
            os.environ['GITHUB_TOKEN'] = token
        elif 'GITHUB_TOKEN' in os.environ:
            del os.environ['GITHUB_TOKEN']
            
        return jsonify({"status": "success", "message": "Token saved successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/settings/token', methods=['GET'])
def get_token_status():
    token = os.getenv("GITHUB_TOKEN")
    return jsonify({
        "has_token": bool(token),
        "masked_token": f"{token[:4]}...{token[-4:]}" if token and len(token) > 8 else None
    })

if __name__ == '__main__':
    print("Starting Web Server on http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)
