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
        # Find similar events based on host and trigger
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

    async def get_events_by_host(self, host: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get events for a specific host"""
        cursor = self.events_collection.find({"host": host}).sort("timestamp", -1).limit(limit)
        return await cursor.to_list(length=limit)

    async def get_events_by_host_and_trigger(self, host: str, trigger: str, 
                                           start_time: datetime = None, 
                                           end_time: datetime = None) -> List[Dict[str, Any]]:
        """Get events for a host and trigger within a time range"""
        query = {
            "host": host,
            "trigger": trigger
        }
        
        if start_time and end_time:
            query["timestamp"] = {
                "$gte": start_time,
                "$lte": end_time
            }
        
        cursor = self.events_collection.find(query).sort("timestamp", -1)
        return await cursor.to_list(length=None)

    async def find_similar_triggers(self, trigger: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Find similar triggers"""
        # Find triggers with similar patterns
        cursor = self.events_collection.find({
            "trigger": {"$regex": trigger, "$options": "i"}
        }).sort("timestamp", -1).limit(limit)
        return await cursor.to_list(length=limit)

    async def get_events_by_time_range(self, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Get events within a time range"""
        cursor = self.events_collection.find({
            "timestamp": {
                "$gte": start_time,
                "$lte": end_time
            }
        }).sort("timestamp", -1)
        return await cursor.to_list(length=None)

    async def get_events_by_severity(self, severity: int, limit: int = 100) -> List[Dict[str, Any]]:
        """Get events by severity"""
        cursor = self.events_collection.find({"severity": severity}).sort("timestamp", -1).limit(limit)
        return await cursor.to_list(length=limit)

    async def get_events_by_status(self, status: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get events by status"""
        cursor = self.events_collection.find({"status": status}).sort("timestamp", -1).limit(limit)
        return await cursor.to_list(length=limit)

    async def get_events_by_tag(self, tag_key: str, tag_value: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get events by tag"""
        cursor = self.events_collection.find({
            "tags": {"$elemMatch": {"key": tag_key, "value": tag_value}}
        }).sort("timestamp", -1).limit(limit)
        return await cursor.to_list(length=limit)

    async def get_events_statistics(self) -> Dict[str, Any]:
        """Get event statistics"""
        total_events = await self.events_collection.count_documents({})
        problem_events = await self.events_collection.count_documents({"status": "PROBLEM"})
        ok_events = await self.events_collection.count_documents({"status": "OK"})
        
        # Calculate statistics by severity
        severity_stats = {}
        for severity in range(1, 6):
            count = await self.events_collection.count_documents({"severity": severity})
            severity_stats[f"severity_{severity}"] = count
        
        return {
            "total_events": total_events,
            "problem_events": problem_events,
            "ok_events": ok_events,
            "severity_distribution": severity_stats
        }

    async def close(self):
        """Close database connection"""
        self.client.close() 