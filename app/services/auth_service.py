from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from typing import Optional
import os
from dotenv import load_dotenv
import hashlib
import time

load_dotenv()

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

class AuthService:
    def __init__(self):
        self.api_keys = {}
        self._load_api_keys()

    def _load_api_keys(self):
        """Load API keys from environment variables"""
        api_key = os.getenv("API_KEY")
        if api_key:
            self.api_keys[api_key] = {
                "name": "default",
                "created_at": time.time()
            }

    async def validate_api_key(self, api_key: str = Security(api_key_header)) -> bool:
        """Authenticate API key"""
        if api_key not in self.api_keys:
            raise HTTPException(
                status_code=403,
                detail="Invalid API key"
            )
        return True

    def generate_api_key(self, name: str) -> str:
        """Generate new API key"""
        timestamp = str(time.time())
        api_key = hashlib.sha256(f"{name}:{timestamp}".encode()).hexdigest()
        self.api_keys[api_key] = {
            "name": name,
            "created_at": time.time()
        }
        return api_key

    def revoke_api_key(self, api_key: str) -> bool:
        """Revoke API key"""
        if api_key in self.api_keys:
            del self.api_keys[api_key]
            return True
        return False

    def get_api_key_info(self, api_key: str) -> Optional[dict]:
        """Get API key information"""
        return self.api_keys.get(api_key) 