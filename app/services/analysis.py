from typing import List, Dict, Any
from datetime import datetime
import openai
import os
from ..models.event import ZabbixEvent, EventAnalysis
from .database import DatabaseService
from .ollama_service import OllamaService
from .rag_service import RAGService
from .deep_research import DeepResearchService

class EventAnalysisService:
    def __init__(self, openai_api_key: str = None, model: str = "gpt-4-turbo-preview", use_ollama: bool = False):
        self.use_ollama = use_ollama
        self.db = DatabaseService()
        self.rag = RAGService(self.db)
        self.deep_research = DeepResearchService(self.db)
        
        if use_ollama:
            self.ollama = OllamaService(
                base_url=os.getenv("OLLAMA_API_URL", "http://localhost:11434"),
                model=os.getenv("OLLAMA_MODEL", "llama2")
            )
        else:
            self.model = model
            openai.api_key = openai_api_key

    async def analyze_event(self, event: ZabbixEvent) -> EventAnalysis:
        # Lưu sự kiện vào database
        event_dict = event.dict()
        await self.db.save_event(event_dict)
        
        # Lấy context liên quan từ RAG
        context = await self.rag.get_relevant_context(event_dict)
        context_text = self.rag.format_context_for_prompt(context)
        
        # Thực hiện phân tích sâu
        deep_research_results = await self.deep_research.research_event(event_dict, context)
        
        # Phân tích sự kiện
        if self.use_ollama:
            analysis = await self.ollama.analyze_event(event_dict, context)
        else:
            # Tạo prompt cho OpenAI với context từ RAG và kết quả phân tích sâu
            prompt = self._create_analysis_prompt(event, context_text, deep_research_results)
            
            # Gọi OpenAI API
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert system administrator analyzing Zabbix events."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Phân tích kết quả
            analysis = self._parse_analysis_response(response.choices[0].message.content)
        
        # Tạo đối tượng EventAnalysis
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
            }
        )
        
        # Lưu kết quả phân tích vào database
        await self.db.save_analysis(event_analysis.dict())
        
        return event_analysis

    def _create_analysis_prompt(self, event: ZabbixEvent, context_text: str, deep_research: Dict[str, Any]) -> str:
        # Định dạng kết quả phân tích sâu
        deep_research_text = "\nDeep Research Results:\n"
        
        # Thêm thông tin về mẫu sự kiện
        if deep_research["event_patterns"]["recurring_issues"]:
            deep_research_text += "\nRecurring Issues:\n"
            for issue in deep_research["event_patterns"]["recurring_issues"]:
                deep_research_text += f"- {issue['pattern']}: {issue['count']} occurrences\n"
        
        # Thêm thông tin về sức khỏe hệ thống
        health = deep_research["system_health"]
        deep_research_text += f"\nSystem Health:\n"
        deep_research_text += f"- Stability: {health['system_stability']:.2f}\n"
        if health["recovery_time"]:
            deep_research_text += f"- Average Recovery Time: {health['recovery_time']}\n"
        
        # Thêm thông tin về chuỗi phụ thuộc
        deps = deep_research["dependency_chain"]
        if deps["upstream_events"] or deps["downstream_events"]:
            deep_research_text += "\nDependencies:\n"
            if deps["upstream_events"]:
                deep_research_text += f"- Upstream Events: {len(deps['upstream_events'])}\n"
            if deps["downstream_events"]:
                deep_research_text += f"- Downstream Events: {len(deps['downstream_events'])}\n"
        
        # Thêm các khuyến nghị
        if deep_research["recommendations"]:
            deep_research_text += "\nRecommendations:\n"
            for rec in deep_research["recommendations"]:
                deep_research_text += f"- [{rec['priority']}] {rec['description']}\n"
                deep_research_text += f"  Action: {rec['action']}\n"

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

        Please use both the historical context and deep research results above to provide a comprehensive analysis.
        Consider:
        1. Any recurring patterns or issues
        2. System health and stability metrics
        3. Dependencies and impact chains
        4. Specific recommendations based on the analysis

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