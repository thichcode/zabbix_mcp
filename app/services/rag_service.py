from typing import List, Dict, Any
from datetime import datetime, timedelta
from .database import DatabaseService
import json

class RAGService:
    def __init__(self, db: DatabaseService):
        self.db = db

    async def get_relevant_context(self, event: Dict[str, Any], max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for related events and analyses from history
        """
        # Find similar events based on multiple criteria
        similar_events = await self._find_similar_events(event, max_results)
        
        # Find related analyses
        related_analyses = await self._find_related_analyses(similar_events)
        
        # Combine and sort results
        context = self._combine_and_rank_context(similar_events, related_analyses)
        
        return context

    async def _find_similar_events(self, event: Dict[str, Any], max_results: int) -> List[Dict[str, Any]]:
        """
        Find similar events based on multiple criteria
        """
        # Find by host and trigger
        host_trigger_events = await self.db.find_similar_events(event, max_results)
        
        # Find by severity
        severity_events = await self.db.get_events_by_severity(event["severity"], max_results)
        
        # Find by recent time (7 days)
        recent_events = await self.db.get_recent_events(max_results)
        
        # Combine and remove duplicates
        all_events = host_trigger_events + severity_events + recent_events
        unique_events = {e["event_id"]: e for e in all_events}.values()
        
        return list(unique_events)[:max_results]

    async def _find_related_analyses(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Find analyses related to events
        """
        analyses = []
        for event in events:
            analysis = await self.db.get_analysis(event["event_id"])
            if analysis:
                analyses.append(analysis)
        return analyses

    def _combine_and_rank_context(self, events: List[Dict[str, Any]], analyses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Combine and sort results by relevance
        """
        context = []
        
        # Add corresponding events and analyses
        for event in events:
            event_context = {
                "type": "event",
                "data": event,
                "relevance_score": self._calculate_relevance_score(event)
            }
            context.append(event_context)
            
            # Find corresponding analysis
            for analysis in analyses:
                if analysis["event_id"] == event["event_id"]:
                    analysis_context = {
                        "type": "analysis",
                        "data": analysis,
                        "relevance_score": self._calculate_relevance_score(analysis)
                    }
                    context.append(analysis_context)
        
        # Sort by relevance score
        context.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return context

    def _calculate_relevance_score(self, item: Dict[str, Any]) -> float:
        """
        Calculate relevance score based on factors
        """
        score = 0.0
        
        # Time factor (more recent events are more relevant)
        if "timestamp" in item:
            time_diff = datetime.utcnow() - item["timestamp"]
            time_score = 1.0 / (1.0 + time_diff.days)
            score += time_score * 0.3
        
        # Analysis reliability factor
        if "confidence" in item:
            score += item["confidence"] * 0.4
        
        # Severity factor
        if "severity" in item:
            severity_score = item["severity"] / 5.0  # Assume severity is from 0-5
            score += severity_score * 0.3
        
        return min(score, 1.0)

    def format_context_for_prompt(self, context: List[Dict[str, Any]]) -> str:
        """
        Format context for prompt
        """
        formatted_context = "Historical Context:\n"
        
        for item in context:
            if item["type"] == "event":
                event = item["data"]
                formatted_context += f"\nEvent ID: {event['event_id']}\n"
                formatted_context += f"Host: {event['host']}\n"
                formatted_context += f"Trigger: {event['trigger']}\n"
                formatted_context += f"Severity: {event['severity']}\n"
                formatted_context += f"Value: {event['value']}\n"
                formatted_context += f"Timestamp: {event['timestamp']}\n"
                
                # Add corresponding analysis if available
                for analysis_item in context:
                    if (analysis_item["type"] == "analysis" and 
                        analysis_item["data"]["event_id"] == event["event_id"]):
                        analysis = analysis_item["data"]
                        formatted_context += f"\nAnalysis:\n"
                        formatted_context += f"RCA: {analysis['rca']}\n"
                        formatted_context += f"Confidence: {analysis['confidence']}\n"
                        formatted_context += f"Recommendations: {', '.join(analysis['recommendations'])}\n"
                        break
                
                formatted_context += "\n" + "-"*50 + "\n"
        
        return formatted_context 