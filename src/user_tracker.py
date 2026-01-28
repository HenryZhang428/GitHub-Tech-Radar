import os
import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def get_user_activities(usernames, limit=5):
    """
    Fetch recent relevant activities (Stars, Create) for a list of users.
    
    Args:
        usernames (list): List of GitHub usernames.
        limit (int): Max events per user.
        
    Returns:
        list: A consolidated list of interesting activities.
    """
    activities = []
    
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"

    for user in usernames:
        try:
            url = f"https://api.github.com/users/{user}/events/public"
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                logger.warning(f"Could not fetch events for {user}: {response.status_code}")
                continue
                
            events = response.json()
            
            # Filter for interesting events: WatchEvent (Star), CreateEvent (New Repo)
            user_events = []
            for event in events[:limit*2]: # Fetch a bit more to filter
                event_type = event.get('type')
                repo_name = event.get('repo', {}).get('name')
                created_at = event.get('created_at')
                
                if event_type == 'WatchEvent':
                    user_events.append({
                        'user': user,
                        'type': 'star',
                        'repo_name': repo_name,
                        'repo_url': f"https://github.com/{repo_name}",
                        'time': created_at,
                        'description': f"starred {repo_name}"
                    })
                elif event_type == 'CreateEvent' and event.get('payload', {}).get('ref_type') == 'repository':
                    user_events.append({
                        'user': user,
                        'type': 'create',
                        'repo_name': repo_name,
                        'repo_url': f"https://github.com/{repo_name}",
                        'time': created_at,
                        'description': f"created new repo {repo_name}"
                    })
                
                if len(user_events) >= limit:
                    break
            
            activities.extend(user_events)
            
        except Exception as e:
            logger.error(f"Error processing user {user}: {e}")

    # Sort by time descending
    activities.sort(key=lambda x: x['time'], reverse=True)
    return activities
