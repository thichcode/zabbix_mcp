from motor.motor_asyncio import AsyncIOMotorClient
from typing import Dict, Any, List
import os
from datetime import datetime

class DatabaseService:
    def __init__(self):
        self.client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
        self.db = self.client[os.getenv("MONGODB_DB")]
        self.events_collection = self.db.events
        self.analysis_collection = self.db.analysis

    async def save_event(self, event: Dict[str, Any]) -> str:
        result = await self.events_collection.insert_one(event)
        return str(result.inserted_id)

    async def save_analysis(self, analysis: Dict[str, Any]) -> str:
        result = await self.analysis_collection.insert_one(analysis)
        return str(result.inserted_id)

    async def get_event(self, event_id: str) -> Dict[str, Any]:
        return await self.events_collection.find_one({"event_id": event_id})

    async def get_analysis(self, event_id: str) -> Dict[str, Any]:
        return await self.analysis_collection.find_one({"event_id": event_id})

    async def find_similar_events(self, event: Dict[str, Any], limit: int = 5) -> List[Dict[str, Any]]:
        # Tìm các sự kiện tương tự dựa trên host và trigger
        query = {
            "host": event["host"],
            "trigger": event["trigger"],
            "event_id": {"$ne": event["event_id"]}
        }
        
        cursor = self.events_collection.find(query).sort("timestamp", -1).limit(limit)
        return await cursor.to_list(length=limit)

    async def get_recent_events(self, limit: int = 10) -> List[Dict[str, Any]]:
        cursor = self.events_collection.find().sort("timestamp", -1).limit(limit)
        return await cursor.to_list(length=limit)

    async def get_events_by_severity(self, severity: int, limit: int = 10) -> List[Dict[str, Any]]:
        cursor = self.events_collection.find({"severity": severity}).sort("timestamp", -1).limit(limit)
        return await cursor.to_list(length=limit)

    async def get_events_by_host(self, host: str, limit: int = 10) -> List[Dict[str, Any]]:
        cursor = self.events_collection.find({"host": host}).sort("timestamp", -1).limit(limit)
        return await cursor.to_list(length=limit)

    async def close(self):
        self.client.close() 