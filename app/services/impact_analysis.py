from typing import Dict, Any, List
from datetime import datetime, timedelta
from ..services.database import DatabaseService
from ..models.event import ZabbixEvent

class ImpactAnalysisService:
    def __init__(self, db: DatabaseService):
        self.db = db

    async def analyze_impact(self, event: ZabbixEvent) -> Dict[str, Any]:
        """
        Analyze the impact of a trigger
        """
        # Find related events
        related_events = await self._find_related_events(event)
        
        # Analyze direct impact
        direct_impact = await self._analyze_direct_impact(event)
        
        # Analyze indirect impact
        indirect_impact = await self._analyze_indirect_impact(event, related_events)
        
        # Analyze temporal impact
        temporal_impact = await self._analyze_temporal_impact(event, related_events)

        return {
            "direct_impact": direct_impact,
            "indirect_impact": indirect_impact,
            "temporal_impact": temporal_impact,
            "related_events_count": len(related_events),
            "impact_score": self._calculate_impact_score(direct_impact, indirect_impact, temporal_impact)
        }

    async def _find_related_events(self, event: ZabbixEvent) -> List[Dict[str, Any]]:
        """Find related events"""
        # Find events on the same host
        host_events = await self.db.get_events_by_host(event.host)
        
        # Find events with the same trigger pattern
        similar_triggers = await self.db.find_similar_triggers(event.trigger)
        
        # Combine and remove duplicates
        all_events = host_events + similar_triggers
        unique_events = {e["event_id"]: e for e in all_events}.values()
        
        return list(unique_events)

    async def _analyze_direct_impact(self, event: ZabbixEvent) -> Dict[str, Any]:
        """Analyze direct impact"""
        return {
            "severity_level": event.severity,
            "affected_host": event.host,
            "affected_item": event.item,
            "impact_type": self._determine_impact_type(event),
            "immediate_actions_required": self._get_required_actions(event)
        }

    async def _analyze_indirect_impact(self, event: ZabbixEvent, related_events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze indirect impact"""
        affected_services = set()
        affected_users = set()
        
        for related_event in related_events:
            # Analyze affected services
            if "service" in related_event.get("tags", []):
                affected_services.add(related_event["tags"]["service"])
            
            # Analyze affected users
            if "user_impact" in related_event.get("tags", []):
                affected_users.add(related_event["tags"]["user_impact"])

        return {
            "affected_services": list(affected_services),
            "affected_users": list(affected_users),
            "cascade_effect": self._analyze_cascade_effect(event, related_events),
            "business_impact": self._assess_business_impact(event, affected_services)
        }

    async def _analyze_temporal_impact(self, event: ZabbixEvent, related_events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze temporal impact"""
        # Analyze event occurrence time
        event_time = event.timestamp
        hour = event_time.hour
        day = event_time.weekday()
        
        # Determine impact time
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
        """Determine impact type"""
        if event.severity >= 4:
            return "CRITICAL"
        elif event.severity >= 3:
            return "HIGH"
        elif event.severity >= 2:
            return "MEDIUM"
        return "LOW"

    def _get_required_actions(self, event: ZabbixEvent) -> List[str]:
        """Determine necessary actions"""
        actions = []
        if event.severity >= 4:
            actions.extend(["IMMEDIATE_INVESTIGATION", "NOTIFY_TEAM"])
        if event.severity >= 3:
            actions.append("SCHEDULE_MAINTENANCE")
        return actions

    def _analyze_cascade_effect(self, event: ZabbixEvent, related_events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze cascade effect"""
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
        """Assess business impact"""
        return {
            "affected_services_count": len(affected_services),
            "business_critical": any(service in ["core", "payment", "auth"] for service in affected_services),
            "estimated_cost": self._estimate_business_cost(event, affected_services)
        }

    def _is_peak_hours(self, hour: int, day: int) -> bool:
        """Check if it's peak hours"""
        if day < 5:  # Weekday
            return (10 <= hour <= 12) or (14 <= hour <= 16)
        return False

    def _estimate_impact_duration(self, event: ZabbixEvent, related_events: List[Dict[str, Any]]) -> float:
        """Estimate impact duration"""
        if not related_events:
            return 0.0
        
        # Find the next OK event
        ok_events = [e for e in related_events if e["status"] == "OK" and e["timestamp"] > event.timestamp]
        if ok_events:
            return (ok_events[0]["timestamp"] - event.timestamp).total_seconds() / 60
        return 0.0

    def _estimate_recovery_time(self, event: ZabbixEvent, related_events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Estimate recovery time"""
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
            "confidence": min(1.0, len(recovery_times) / 10)  # More data means more reliability
        }

    def _analyze_historical_pattern(self, event: ZabbixEvent, related_events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze historical pattern"""
        if not related_events:
            return {
                "has_pattern": False,
                "message": "# Not enough historical data"
            }
        
        # Analyze frequency
        frequency = len(related_events) / 30  # Number of events per month
        
        return {
            "has_pattern": True,
            "frequency": frequency,
            "is_recurring": frequency > 1,
            "pattern_type": "recurring" if frequency > 1 else "sporadic"
        }

    def _estimate_business_cost(self, event: ZabbixEvent, affected_services: List[str]) -> float:
        """Estimate business cost"""
        base_cost = 1000  # Basic cost for each hour of downtime
        severity_multiplier = event.severity / 2
        service_multiplier = len(affected_services) * 0.5
        
        return base_cost * severity_multiplier * (1 + service_multiplier)

    def _calculate_impact_score(self, direct_impact: Dict[str, Any], 
                              indirect_impact: Dict[str, Any], 
                              temporal_impact: Dict[str, Any]) -> float:
        """Calculate overall impact score"""
        # Weights for components
        weights = {
            "direct": 0.4,
            "indirect": 0.3,
            "temporal": 0.3
        }
        
        # Calculate score for each component
        direct_score = direct_impact["severity_level"] / 5
        indirect_score = len(indirect_impact["affected_services"]) / 10
        temporal_score = 1 if temporal_impact["timing"]["is_business_hours"] else 0.5
        
        # Calculate composite score
        return (direct_score * weights["direct"] +
                indirect_score * weights["indirect"] +
                temporal_score * weights["temporal"]) 