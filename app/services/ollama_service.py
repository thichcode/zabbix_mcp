import requests
from typing import Dict, Any, List
import json
from datetime import datetime

class OllamaService:
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        self.base_url = base_url
        self.model = model
        self.api_url = f"{base_url}/api/generate"

    async def analyze_event(self, event: Dict[str, Any], context: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        # Create prompt for Ollama
        prompt = self._create_analysis_prompt(event, context)
        
        # Call Ollama API
        response = requests.post(
            self.api_url,
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"Ollama API error: {response.text}")
            
        result = response.json()
        
        # Parse analysis result
        return self._parse_analysis_response(result["response"])

    def _create_analysis_prompt(self, event: Dict[str, Any], context: List[Dict[str, Any]] = None) -> str:
        context_text = ""
        if context:
            context_text = "\nHistorical Context:\n"
            for item in context:
                if item["type"] == "event":
                    event_data = item["data"]
                    context_text += f"\nEvent ID: {event_data['event_id']}\n"
                    context_text += f"Host: {event_data['host']}\n"
                    context_text += f"Trigger: {event_data['trigger']}\n"
                    context_text += f"Severity: {event_data['severity']}\n"
                    context_text += f"Value: {event_data['value']}\n"
                    context_text += f"Timestamp: {event_data['timestamp']}\n"
                    
                    # Add corresponding analysis if available
                    for analysis_item in context:
                        if (analysis_item["type"] == "analysis" and 
                            analysis_item["data"]["event_id"] == event_data["event_id"]):
                            analysis = analysis_item["data"]
                            context_text += f"\nAnalysis:\n"
                            context_text += f"RCA: {analysis['rca']}\n"
                            context_text += f"Confidence: {analysis['confidence']}\n"
                            context_text += f"Recommendations: {', '.join(analysis['recommendations'])}\n"
                            break
                    
                    context_text += "\n" + "-"*50 + "\n"

        return f"""You are an expert system administrator analyzing Zabbix events. Please analyze the following event and provide:
1. Root Cause Analysis (RCA) - explain what might have caused this issue
2. Confidence level (0-1) - how confident you are in your analysis
3. Recommendations for resolution - specific steps to fix the issue
4. Similar events to check - related issues that might be connected

Current Event Details:
- Host: {event['host']}
- Item: {event['item']}
- Trigger: {event['trigger']}
- Severity: {event['severity']}
- Status: {event['status']}
- Value: {event['value']}
- Description: {event.get('description', 'N/A')}
- Tags: {event.get('tags', [])}

{context_text}

Please use the historical context above to provide a more accurate analysis.
If you find similar events, explain how they relate to the current event.
If you find successful resolutions in the history, include them in your recommendations.

Please format your response as JSON with the following structure:
{{
    "rca": "detailed root cause analysis",
    "confidence": 0.85,
    "recommendations": ["recommendation 1", "recommendation 2"],
    "metadata": {{
        "analysis_timestamp": "ISO timestamp",
        "model_used": "{self.model}"
    }}
}}"""

    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        try:
            # Find JSON in response
            start_idx = response.find("{")
            end_idx = response.rfind("}") + 1
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON found in response")
                
            json_str = response[start_idx:end_idx]
            analysis = json.loads(json_str)
            
            # Ensure required fields
            required_fields = ["rca", "confidence", "recommendations"]
            for field in required_fields:
                if field not in analysis:
                    raise ValueError(f"Missing required field: {field}")
                    
            # Add timestamp if not present
            if "metadata" not in analysis:
                analysis["metadata"] = {}
            if "analysis_timestamp" not in analysis["metadata"]:
                analysis["metadata"]["analysis_timestamp"] = datetime.utcnow().isoformat()
                
            return analysis
            
        except Exception as e:
            # Fallback if JSON cannot be parsed
            return {
                "rca": response,
                "confidence": 0.5,
                "recommendations": ["Please review the raw analysis"],
                "metadata": {
                    "analysis_timestamp": datetime.utcnow().isoformat(),
                    "model_used": self.model,
                    "parse_error": str(e)
                }
            } 