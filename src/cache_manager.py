import time
import logging
import json
import os
from datetime import datetime, timedelta
from scraper import get_trending_repos
from user_tracker import get_user_activities
from llm import LLMAnalyzer

logger = logging.getLogger(__name__)

class TrendingCache:
    def __init__(self, ttl_seconds=3600, cache_file="data/cache.json"):
        """
        Initialize the cache.
        :param ttl_seconds: Time to live in seconds (default 1 hour)
        """
        self._cache = {}
        self._last_update = {}
        self._ttl = ttl_seconds
        self.llm_analyzer = LLMAnalyzer()
        self.config_file = "watchlist.json"
        self.cache_file = cache_file
        
        # Create data dir
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
        
        # Load watchlist config
        self.watchlist = self._load_watchlist()
        
        # Load persistent cache
        self._load_cache()

    def _load_watchlist(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return []
        return ["torvalds", "antirez", "karpathy"] # Default famous devs

    def save_watchlist(self, new_list):
        self.watchlist = new_list
        with open(self.config_file, 'w') as f:
            json.dump(new_list, f)

    def _load_cache(self):
        """Load cache from disk"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    self._cache = data.get('cache', {})
                    self._last_update = data.get('last_update', {})
                    logger.info("Cache loaded from disk.")
            except Exception as e:
                logger.error(f"Failed to load cache: {e}")

    def _save_cache(self):
        """Save cache to disk"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump({
                    'cache': self._cache,
                    'last_update': self._last_update
                }, f)
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")

    def get_data(self, since='daily', language='', force_refresh=False):
        """
        Get trending data from cache or fetch new data if expired.
        """
        cache_key = f"{since}_{language}"
        return self._get_cached_or_fetch(cache_key, lambda: self._fetch_trending(since, language), force_refresh)

    def get_vip_activities(self, force_refresh=False):
        """
        Get VIP activities from cache or fetch.
        """
        cache_key = "vip_activities"
        return self._get_cached_or_fetch(cache_key, lambda: get_user_activities(self.watchlist), force_refresh)

    def _get_cached_or_fetch(self, key, fetch_func, force_refresh):
        now = time.time()
        last_update = self._last_update.get(key, 0)
        
        if not force_refresh and (now - last_update < self._ttl) and (key in self._cache):
            logger.info(f"Returning cached data for {key}")
            return self._cache[key]
        
        logger.info(f"Cache expired or missing for {key}. Fetching...")
        try:
            data = fetch_func()
            self._cache[key] = data
            self._last_update[key] = time.time()
            self._save_cache() # Persist immediately
            return data
        except Exception as e:
            logger.error(f"Failed to refresh {key}: {e}")
            return self._cache.get(key, [])

    def _fetch_trending(self, since, language):
        repos = get_trending_repos(since=since, language=language, limit=10)
        for repo in repos:
            repo['ai_analysis'] = self.llm_analyzer.analyze_repo(
                repo['name'], 
                repo['description'], 
                repo['language']
            )
        return repos
