from typing import List, Dict, Any
from datetime import datetime
import openai
import os
from ..models.event import ZabbixEvent, EventAnalysis
from .database import DatabaseService
from .ollama_service import OllamaService
from .rag_service import RAGService
from .deep_research import DeepResearchService
from .trend_analysis import TrendAnalysisService
from .impact_analysis import ImpactAnalysisService

class EventAnalysisService:
    def __init__(self, openai_api_key: str = None, model: str = "gpt-4-turbo-preview", use_ollama: bool = False):
        self.use_ollama = use_ollama
        self.db = DatabaseService()
        self.rag = RAGService(self.db)
        self.deep_research = DeepResearchService(self.db)
        self.trend_analysis = TrendAnalysisService(self.db)
        self.impact_analysis = ImpactAnalysisService(self.db)
        
        if use_ollama:
            self.ollama = OllamaService(
                base_url=os.getenv("OLLAMA_API_URL", "http://localhost:11434"),
                model=os.getenv("OLLAMA_MODEL", "llama2")
            )
        else:
            self.model = model
            openai.api_key = openai_api_key

    async def analyze_event(self, event: ZabbixEvent) -> EventAnalysis:
        # Save event to database
        event_dict = event.dict()
        await self.db.save_event(event_dict)
        
        # Get relevant context from RAG
        context = await self.rag.get_relevant_context(event_dict)
        context_text = self.rag.format_context_for_prompt(context)
        
        # Perform deep analysis
        deep_research_results = await self.deep_research.research_event(event_dict, context)
        
        # Analyze trends
        trend_results = await self.trend_analysis.analyze_trends(
            host=event.host,
            trigger=event.trigger,
            time_range=24  # Analyze last 24 hours
        )
        
        # Analyze impact
        impact_results = await self.impact_analysis.analyze_impact(event)
        
        # Analyze event
        if self.use_ollama:
            analysis = await self.ollama.analyze_event(event_dict, context)
        else:
            # Create prompt for OpenAI with context from RAG and deep analysis results
            prompt = self._create_analysis_prompt(
                event, 
                context_text, 
                deep_research_results,
                trend_results,
                impact_results
            )
            
            # Call OpenAI API
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert system administrator analyzing Zabbix events."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Parse analysis result
            analysis = self._parse_analysis_response(response.choices[0].message.content)
        
        # Create EventAnalysis object
        event_analysis = EventAnalysis(
            event_id=event.event_id,
            rca=analysis["rca"],
            confidence=analysis["confidence"],
            recommendations=analysis["recommendations"],
            similar_events=[e["event_id"] for e in context if e["type"] == "event"],
            metadata={
                **analysis["metadata"],
                "context_used": len(context),
                "context_relevance_scores": [item["relevance_score"] for item in context],
                "deep_research": deep_research_results
            },
            trend_analysis=trend_results,
            impact_analysis=impact_results,
            resolution_time=impact_results["temporal_impact"]["recovery_estimate"]["estimated_minutes"]
        )
        
        # Save analysis result to database
        await self.db.save_analysis(event_analysis.dict())
        
        return event_analysis

    def _create_analysis_prompt(self, event: ZabbixEvent, context_text: str, 
                              deep_research: Dict[str, Any], trend_results: Dict[str, Any],
                              impact_results: Dict[str, Any]) -> str:
        # Format deep analysis results
        deep_research_text = "\nDeep Research Results:\n"
        
        # Add information about event patterns
        if deep_research["event_patterns"]["recurring_issues"]:
            deep_research_text += "\nRecurring Issues:\n"
            for issue in deep_research["event_patterns"]["recurring_issues"]:
                deep_research_text += f"- {issue['pattern']}: {issue['count']} occurrences\n"
        
        # Add information about system health
        health = deep_research["system_health"]
        deep_research_text += f"\nSystem Health:\n"
        deep_research_text += f"- Stability: {health['system_stability']:.2f}\n"
        if health["recovery_time"]:
            deep_research_text += f"- Average Recovery Time: {health['recovery_time']}\n"
        
        # Add information about dependency chain
        deps = deep_research["dependency_chain"]
        if deps["upstream_events"] or deps["downstream_events"]:
            deep_research_text += "\nDependencies:\n"
            if deps["upstream_events"]:
                deep_research_text += f"- Upstream Events: {len(deps['upstream_events'])}\n"
            if deps["downstream_events"]:
                deep_research_text += f"- Downstream Events: {len(deps['downstream_events'])}\n"
        
        # Add recommendations
        if deep_research["recommendations"]:
            deep_research_text += "\nRecommendations:\n"
            for rec in deep_research["recommendations"]:
                deep_research_text += f"- [{rec['priority']}] {rec['description']}\n"
                deep_research_text += f"  Action: {rec['action']}\n"

        # Format trend analysis results
        trend_text = "\nTrend Analysis:\n"
        if trend_results["has_trend"]:
            trend_text += f"- Frequency: {trend_results['frequency_analysis']['trend']}\n"
            trend_text += f"- Severity Trend: {trend_results['severity_analysis']['trend']}\n"
            if trend_results['recovery_analysis']['has_recovery_data']:
                trend_text += f"- Average Recovery Time: {trend_results['recovery_analysis']['average_recovery_time']:.2f} minutes\n"

        # Format impact analysis results
        impact_text = "\nImpact Analysis:\n"
        impact_text += f"- Direct Impact: {impact_results['direct_impact']['impact_type']}\n"
        impact_text += f"- Affected Services: {len(impact_results['indirect_impact']['affected_services'])}\n"
        impact_text += f"- Business Hours Impact: {impact_results['temporal_impact']['timing']['is_business_hours']}\n"
        impact_text += f"- Estimated Cost: ${impact_results['indirect_impact']['business_impact']['estimated_cost']:.2f}\n"

        return f"""
        Analyze the following Zabbix event and provide:
        1. Root Cause Analysis (RCA)
        2. Confidence level (0-1)
        3. Recommendations for resolution
        4. Similar events to check

        Current Event Details:
        - Host: {event.host}
        - Item: {event.item}
        - Trigger: {event.trigger}
        - Severity: {event.severity}
        - Status: {event.status}
        - Value: {event.value}
        - Description: {event.description}
        - Tags: {event.tags}

        {context_text}

        {deep_research_text}

        {trend_text}

        {impact_text}

        Please use all the analysis results above to provide a comprehensive analysis.
        Consider:
        1. Any recurring patterns or issues
        2. System health and stability metrics
        3. Dependencies and impact chains
        4. Specific recommendations based on the analysis
        5. Business impact and cost implications
        6. Recovery time estimates

        If you find similar events, explain how they relate to the current event.
        If you find successful resolutions in the history, include them in your recommendations.
        """

    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        # TODO: Implement proper parsing of OpenAI response
        # This is a simplified version
        return {
            "rca": "Sample RCA analysis",
            "confidence": 0.85,
            "recommendations": ["Sample recommendation 1", "Sample recommendation 2"],
            "metadata": {"parsed_at": datetime.utcnow().isoformat()}
        }

    async def close(self):
        await self.db.close() 