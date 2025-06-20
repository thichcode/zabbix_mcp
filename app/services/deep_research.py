from typing import Dict, Any, List
import requests
import json
from datetime import datetime, timedelta
from .database import DatabaseService

class DeepResearchService:
    def __init__(self, db: DatabaseService):
        self.db = db

    async def research_event(self, event: Dict[str, Any], context: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Perform deep research on the event
        """
        research_results = {
            "event_patterns": await self._analyze_event_patterns(event, context),
            "system_health": await self._analyze_system_health(event),
            "dependency_chain": await self._analyze_dependency_chain(event, context),
            "trend_analysis": await self._analyze_trends(event, context),
            "recommendations": await self._generate_recommendations(event, context)
        }
        
        return research_results

    async def _analyze_event_patterns(self, event: Dict[str, Any], context: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze event patterns
        """
        patterns = {
            "recurring_issues": [],
            "correlated_events": [],
            "time_patterns": [],
            "severity_patterns": []
        }
        
        if context:
            # Analyze recurring events
            event_counts = {}
            for item in context:
                if item["type"] == "event":
                    event_data = item["data"]
                    key = f"{event_data['host']}_{event_data['trigger']}"
                    event_counts[key] = event_counts.get(key, 0) + 1
                    
                    # Check time patterns
                    if "timestamp" in event_data:
                        event_time = event_data["timestamp"]
                        if isinstance(event_time, str):
                            event_time = datetime.fromisoformat(event_time)
                        patterns["time_patterns"].append(event_time)
            
            # Identify recurring events
            for key, count in event_counts.items():
                if count > 1:
                    patterns["recurring_issues"].append({
                        "pattern": key,
                        "count": count
                    })
            
            # Analyze severity patterns
            severity_counts = {}
            for item in context:
                if item["type"] == "event":
                    severity = item["data"].get("severity", 0)
                    severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            patterns["severity_patterns"] = [
                {"severity": k, "count": v}
                for k, v in severity_counts.items()
            ]
        
        return patterns

    async def _analyze_system_health(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze system health
        """
        # Get recent events for the host
        recent_events = await self.db.get_events_by_host(event["host"], limit=10)
        
        health_metrics = {
            "event_frequency": len(recent_events),
            "severity_distribution": {},
            "recovery_time": None,
            "system_stability": 0.0
        }
        
        # Analyze recovery time
        if recent_events:
            recovery_times = []
            for i in range(len(recent_events) - 1):
                if recent_events[i]["status"] == "PROBLEM" and recent_events[i + 1]["status"] == "OK":
                    time_diff = recent_events[i + 1]["timestamp"] - recent_events[i]["timestamp"]
                    recovery_times.append(time_diff)
            
            if recovery_times:
                health_metrics["recovery_time"] = sum(recovery_times, timedelta()) / len(recovery_times)
        
        # Calculate system stability
        total_events = len(recent_events)
        if total_events > 0:
            problem_events = sum(1 for e in recent_events if e["status"] == "PROBLEM")
            health_metrics["system_stability"] = 1 - (problem_events / total_events)
        
        return health_metrics

    async def _analyze_dependency_chain(self, event: Dict[str, Any], context: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze dependency chain
        """
        dependencies = {
            "upstream_events": [],
            "downstream_events": [],
            "related_services": [],
            "impact_chain": []
        }
        
        if context:
            # Find related events by time
            event_time = event.get("timestamp")
            if event_time:
                if isinstance(event_time, str):
                    event_time = datetime.fromisoformat(event_time)
                
                for item in context:
                    if item["type"] == "event":
                        event_data = item["data"]
                        if "timestamp" in event_data:
                            other_time = event_data["timestamp"]
                            if isinstance(other_time, str):
                                other_time = datetime.fromisoformat(other_time)
                            
                            # Identify upstream/downstream events
                            if other_time < event_time:
                                dependencies["upstream_events"].append(event_data)
                            elif other_time > event_time:
                                dependencies["downstream_events"].append(event_data)
        
        return dependencies

    async def _analyze_trends(self, event: Dict[str, Any], context: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze trends
        """
        trends = {
            "frequency_trend": [],
            "severity_trend": [],
            "recovery_trend": [],
            "pattern_changes": []
        }
        
        if context:
            # Sort events by time
            events = [
                item["data"] for item in context 
                if item["type"] == "event" and "timestamp" in item["data"]
            ]
            events.sort(key=lambda x: x["timestamp"])
            
            # Analyze frequency trend
            time_windows = []
            current_window = []
            window_size = timedelta(hours=24)
            
            for event_data in events:
                event_time = event_data["timestamp"]
                if isinstance(event_time, str):
                    event_time = datetime.fromisoformat(event_time)
                
                if not current_window or event_time - current_window[0]["timestamp"] <= window_size:
                    current_window.append(event_data)
                else:
                    time_windows.append(len(current_window))
                    current_window = [event_data]
            
            if current_window:
                time_windows.append(len(current_window))
            
            trends["frequency_trend"] = time_windows
        
        return trends

    async def _generate_recommendations(self, event: Dict[str, Any], context: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Generate recommendations based on deep analysis
        """
        recommendations = []
        
        # Analyze event patterns
        patterns = await self._analyze_event_patterns(event, context)
        if patterns["recurring_issues"]:
            recommendations.append({
                "type": "pattern_based",
                "priority": "high",
                "description": f"# Found {len(patterns['recurring_issues'])} recurring issues",
                "action": "# Consider reconfiguring the system to avoid recurrence"
            })
        
        # Analyze system health
        health = await self._analyze_system_health(event)
        if health["system_stability"] < 0.7:
            recommendations.append({
                "type": "system_health",
                "priority": "high",
                "description": "# Low system stability",
                "action": "# Check and optimize system configuration"
            })
        
        # Analyze dependency chain
        dependencies = await self._analyze_dependency_chain(event, context)
        if dependencies["upstream_events"]:
            recommendations.append({
                "type": "dependency",
                "priority": "medium",
                "description": f"# Found {len(dependencies['upstream_events'])} upstream events",
                "action": "# Check dependent services"
            })
        
        return recommendations 