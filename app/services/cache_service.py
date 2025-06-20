from fastapi import HTTPException
from datetime import datetime, timedelta
import redis
from typing import Any, Dict, Optional
import json
import os
from dotenv import load_dotenv

load_dotenv()

class CacheService:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=0,
            decode_responses=True
        )
        self.rate_limit_window = int(os.getenv("RATE_LIMIT_WINDOW", 60))  # seconds
        self.rate_limit_max_requests = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", 100))

    async def get_cached_analysis(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get analysis results from cache"""
        cached_data = self.redis_client.get(f"analysis:{event_id}")
        if cached_data:
            return json.loads(cached_data)
        return None

    async def cache_analysis(self, event_id: str, analysis: Dict[str, Any], ttl: int = 3600):
        """Save analysis results to cache"""
        self.redis_client.setex(
            f"analysis:{event_id}",
            ttl,
            json.dumps(analysis)
        )

    async def check_rate_limit(self, client_id: str) -> bool:
        """Check rate limit for client"""
        key = f"rate_limit:{client_id}"
        current = self.redis_client.get(key)
        
        if current is None:
            self.redis_client.setex(key, self.rate_limit_window, 1)
            return True
            
        current = int(current)
        if current >= self.rate_limit_max_requests:
            return False
            
        self.redis_client.incr(key)
        return True

    async def get_rate_limit_info(self, client_id: str) -> Dict[str, Any]:
        """Get client rate limit information"""
        key = f"rate_limit:{client_id}"
        current = int(self.redis_client.get(key) or 0)
        ttl = self.redis_client.ttl(key)
        
        return {
            "current_requests": current,
            "max_requests": self.rate_limit_max_requests,
            "window_seconds": self.rate_limit_window,
            "remaining_seconds": ttl,
            "remaining_requests": max(0, self.rate_limit_max_requests - current)
        } 