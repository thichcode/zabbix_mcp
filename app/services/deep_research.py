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
        Thực hiện nghiên cứu sâu về sự kiện
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
        Phân tích các mẫu sự kiện
        """
        patterns = {
            "recurring_issues": [],
            "correlated_events": [],
            "time_patterns": [],
            "severity_patterns": []
        }
        
        if context:
            # Phân tích sự kiện lặp lại
            event_counts = {}
            for item in context:
                if item["type"] == "event":
                    event_data = item["data"]
                    key = f"{event_data['host']}_{event_data['trigger']}"
                    event_counts[key] = event_counts.get(key, 0) + 1
                    
                    # Kiểm tra mẫu thời gian
                    if "timestamp" in event_data:
                        event_time = event_data["timestamp"]
                        if isinstance(event_time, str):
                            event_time = datetime.fromisoformat(event_time)
                        patterns["time_patterns"].append(event_time)
            
            # Xác định sự kiện lặp lại
            for key, count in event_counts.items():
                if count > 1:
                    patterns["recurring_issues"].append({
                        "pattern": key,
                        "count": count
                    })
            
            # Phân tích mẫu severity
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
        Phân tích sức khỏe hệ thống
        """
        # Lấy các sự kiện gần đây của host
        recent_events = await self.db.get_events_by_host(event["host"], limit=10)
        
        health_metrics = {
            "event_frequency": len(recent_events),
            "severity_distribution": {},
            "recovery_time": None,
            "system_stability": 0.0
        }
        
        # Phân tích thời gian phục hồi
        if recent_events:
            recovery_times = []
            for i in range(len(recent_events) - 1):
                if recent_events[i]["status"] == "PROBLEM" and recent_events[i + 1]["status"] == "OK":
                    time_diff = recent_events[i + 1]["timestamp"] - recent_events[i]["timestamp"]
                    recovery_times.append(time_diff)
            
            if recovery_times:
                health_metrics["recovery_time"] = sum(recovery_times, timedelta()) / len(recovery_times)
        
        # Tính toán độ ổn định hệ thống
        total_events = len(recent_events)
        if total_events > 0:
            problem_events = sum(1 for e in recent_events if e["status"] == "PROBLEM")
            health_metrics["system_stability"] = 1 - (problem_events / total_events)
        
        return health_metrics

    async def _analyze_dependency_chain(self, event: Dict[str, Any], context: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Phân tích chuỗi phụ thuộc
        """
        dependencies = {
            "upstream_events": [],
            "downstream_events": [],
            "related_services": [],
            "impact_chain": []
        }
        
        if context:
            # Tìm các sự kiện liên quan theo thời gian
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
                            
                            # Xác định sự kiện upstream/downstream
                            if other_time < event_time:
                                dependencies["upstream_events"].append(event_data)
                            elif other_time > event_time:
                                dependencies["downstream_events"].append(event_data)
        
        return dependencies

    async def _analyze_trends(self, event: Dict[str, Any], context: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Phân tích xu hướng
        """
        trends = {
            "frequency_trend": [],
            "severity_trend": [],
            "recovery_trend": [],
            "pattern_changes": []
        }
        
        if context:
            # Sắp xếp sự kiện theo thời gian
            events = [
                item["data"] for item in context 
                if item["type"] == "event" and "timestamp" in item["data"]
            ]
            events.sort(key=lambda x: x["timestamp"])
            
            # Phân tích xu hướng tần suất
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
        Tạo các khuyến nghị dựa trên phân tích sâu
        """
        recommendations = []
        
        # Phân tích mẫu sự kiện
        patterns = await self._analyze_event_patterns(event, context)
        if patterns["recurring_issues"]:
            recommendations.append({
                "type": "pattern_based",
                "priority": "high",
                "description": f"Phát hiện {len(patterns['recurring_issues'])} vấn đề lặp lại",
                "action": "Xem xét cấu hình lại hệ thống để tránh lặp lại"
            })
        
        # Phân tích sức khỏe hệ thống
        health = await self._analyze_system_health(event)
        if health["system_stability"] < 0.7:
            recommendations.append({
                "type": "system_health",
                "priority": "high",
                "description": "Độ ổn định hệ thống thấp",
                "action": "Kiểm tra và tối ưu hóa cấu hình hệ thống"
            })
        
        # Phân tích chuỗi phụ thuộc
        dependencies = await self._analyze_dependency_chain(event, context)
        if dependencies["upstream_events"]:
            recommendations.append({
                "type": "dependency",
                "priority": "medium",
                "description": f"Phát hiện {len(dependencies['upstream_events'])} sự kiện upstream",
                "action": "Kiểm tra các dịch vụ phụ thuộc"
            })
        
        return recommendations 