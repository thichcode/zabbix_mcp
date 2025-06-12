from typing import Dict, Any, List
from datetime import datetime, timedelta
from ..services.database import DatabaseService
from ..models.event import ZabbixEvent

class ImpactAnalysisService:
    def __init__(self, db: DatabaseService):
        self.db = db

    async def analyze_impact(self, event: ZabbixEvent) -> Dict[str, Any]:
        """
        Phân tích tác động của một trigger
        """
        # Tìm các sự kiện liên quan
        related_events = await self._find_related_events(event)
        
        # Phân tích tác động trực tiếp
        direct_impact = await self._analyze_direct_impact(event)
        
        # Phân tích tác động gián tiếp
        indirect_impact = await self._analyze_indirect_impact(event, related_events)
        
        # Phân tích tác động theo thời gian
        temporal_impact = await self._analyze_temporal_impact(event, related_events)

        return {
            "direct_impact": direct_impact,
            "indirect_impact": indirect_impact,
            "temporal_impact": temporal_impact,
            "related_events_count": len(related_events),
            "impact_score": self._calculate_impact_score(direct_impact, indirect_impact, temporal_impact)
        }

    async def _find_related_events(self, event: ZabbixEvent) -> List[Dict[str, Any]]:
        """Tìm các sự kiện liên quan"""
        # Tìm các sự kiện trên cùng host
        host_events = await self.db.get_events_by_host(event.host)
        
        # Tìm các sự kiện có cùng trigger pattern
        similar_triggers = await self.db.find_similar_triggers(event.trigger)
        
        # Kết hợp và loại bỏ trùng lặp
        all_events = host_events + similar_triggers
        unique_events = {e["event_id"]: e for e in all_events}.values()
        
        return list(unique_events)

    async def _analyze_direct_impact(self, event: ZabbixEvent) -> Dict[str, Any]:
        """Phân tích tác động trực tiếp"""
        return {
            "severity_level": event.severity,
            "affected_host": event.host,
            "affected_item": event.item,
            "impact_type": self._determine_impact_type(event),
            "immediate_actions_required": self._get_required_actions(event)
        }

    async def _analyze_indirect_impact(self, event: ZabbixEvent, related_events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Phân tích tác động gián tiếp"""
        affected_services = set()
        affected_users = set()
        
        for related_event in related_events:
            # Phân tích các service bị ảnh hưởng
            if "service" in related_event.get("tags", []):
                affected_services.add(related_event["tags"]["service"])
            
            # Phân tích các user bị ảnh hưởng
            if "user_impact" in related_event.get("tags", []):
                affected_users.add(related_event["tags"]["user_impact"])

        return {
            "affected_services": list(affected_services),
            "affected_users": list(affected_users),
            "cascade_effect": self._analyze_cascade_effect(event, related_events),
            "business_impact": self._assess_business_impact(event, affected_services)
        }

    async def _analyze_temporal_impact(self, event: ZabbixEvent, related_events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Phân tích tác động theo thời gian"""
        # Phân tích thời gian xảy ra sự kiện
        event_time = event.timestamp
        hour = event_time.hour
        day = event_time.weekday()
        
        # Xác định thời điểm tác động
        impact_timing = {
            "is_business_hours": 9 <= hour <= 17 and day < 5,
            "is_peak_hours": self._is_peak_hours(hour, day),
            "duration": self._estimate_impact_duration(event, related_events)
        }

        return {
            "timing": impact_timing,
            "recovery_estimate": self._estimate_recovery_time(event, related_events),
            "historical_pattern": self._analyze_historical_pattern(event, related_events)
        }

    def _determine_impact_type(self, event: ZabbixEvent) -> str:
        """Xác định loại tác động"""
        if event.severity >= 4:
            return "CRITICAL"
        elif event.severity >= 3:
            return "HIGH"
        elif event.severity >= 2:
            return "MEDIUM"
        return "LOW"

    def _get_required_actions(self, event: ZabbixEvent) -> List[str]:
        """Xác định các hành động cần thiết"""
        actions = []
        if event.severity >= 4:
            actions.extend(["IMMEDIATE_INVESTIGATION", "NOTIFY_TEAM"])
        if event.severity >= 3:
            actions.append("SCHEDULE_MAINTENANCE")
        return actions

    def _analyze_cascade_effect(self, event: ZabbixEvent, related_events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Phân tích hiệu ứng dây chuyền"""
        cascade_chain = []
        for related in related_events:
            if related["timestamp"] > event.timestamp:
                cascade_chain.append({
                    "event_id": related["event_id"],
                    "delay": (related["timestamp"] - event.timestamp).total_seconds() / 60,
                    "severity": related["severity"]
                })
        
        return {
            "has_cascade": len(cascade_chain) > 0,
            "cascade_chain": cascade_chain,
            "max_cascade_delay": max([c["delay"] for c in cascade_chain]) if cascade_chain else 0
        }

    def _assess_business_impact(self, event: ZabbixEvent, affected_services: List[str]) -> Dict[str, Any]:
        """Đánh giá tác động kinh doanh"""
        return {
            "affected_services_count": len(affected_services),
            "business_critical": any(service in ["core", "payment", "auth"] for service in affected_services),
            "estimated_cost": self._estimate_business_cost(event, affected_services)
        }

    def _is_peak_hours(self, hour: int, day: int) -> bool:
        """Kiểm tra có phải giờ cao điểm không"""
        if day < 5:  # Weekday
            return (10 <= hour <= 12) or (14 <= hour <= 16)
        return False

    def _estimate_impact_duration(self, event: ZabbixEvent, related_events: List[Dict[str, Any]]) -> float:
        """Ước tính thời gian tác động"""
        if not related_events:
            return 0.0
        
        # Tìm sự kiện OK tiếp theo
        ok_events = [e for e in related_events if e["status"] == "OK" and e["timestamp"] > event.timestamp]
        if ok_events:
            return (ok_events[0]["timestamp"] - event.timestamp).total_seconds() / 60
        return 0.0

    def _estimate_recovery_time(self, event: ZabbixEvent, related_events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Ước tính thời gian phục hồi"""
        recovery_times = []
        for related in related_events:
            if related["status"] == "OK" and related["timestamp"] > event.timestamp:
                recovery_times.append((related["timestamp"] - event.timestamp).total_seconds() / 60)
        
        if not recovery_times:
            return {
                "estimated_minutes": 0,
                "confidence": 0
            }
        
        return {
            "estimated_minutes": sum(recovery_times) / len(recovery_times),
            "confidence": min(1.0, len(recovery_times) / 10)  # Càng nhiều dữ liệu càng tin cậy
        }

    def _analyze_historical_pattern(self, event: ZabbixEvent, related_events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Phân tích mẫu lịch sử"""
        if not related_events:
            return {
                "has_pattern": False,
                "message": "Không đủ dữ liệu lịch sử"
            }
        
        # Phân tích tần suất
        frequency = len(related_events) / 30  # Số sự kiện mỗi tháng
        
        return {
            "has_pattern": True,
            "frequency": frequency,
            "is_recurring": frequency > 1,
            "pattern_type": "recurring" if frequency > 1 else "sporadic"
        }

    def _estimate_business_cost(self, event: ZabbixEvent, affected_services: List[str]) -> float:
        """Ước tính chi phí kinh doanh"""
        base_cost = 1000  # Chi phí cơ bản cho mỗi giờ downtime
        severity_multiplier = event.severity / 2
        service_multiplier = len(affected_services) * 0.5
        
        return base_cost * severity_multiplier * (1 + service_multiplier)

    def _calculate_impact_score(self, direct_impact: Dict[str, Any], 
                              indirect_impact: Dict[str, Any], 
                              temporal_impact: Dict[str, Any]) -> float:
        """Tính toán điểm tác động tổng thể"""
        # Trọng số cho các thành phần
        weights = {
            "direct": 0.4,
            "indirect": 0.3,
            "temporal": 0.3
        }
        
        # Tính điểm cho từng thành phần
        direct_score = direct_impact["severity_level"] / 5
        indirect_score = len(indirect_impact["affected_services"]) / 10
        temporal_score = 1 if temporal_impact["timing"]["is_business_hours"] else 0.5
        
        # Tính điểm tổng hợp
        return (direct_score * weights["direct"] +
                indirect_score * weights["indirect"] +
                temporal_score * weights["temporal"]) 