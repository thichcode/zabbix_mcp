from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from ..models.event import WebhookPayload, ZabbixEvent
from ..services.analysis import EventAnalysisService
import os

router = APIRouter()

def get_analysis_service() -> EventAnalysisService:
    use_ollama = os.getenv("USE_OLLAMA", "false").lower() == "true"
    if use_ollama:
        return EventAnalysisService(use_ollama=True)
    else:
        return EventAnalysisService(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model=os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
        )

@router.post("/webhook/zabbix")
async def zabbix_webhook(
    payload: WebhookPayload,
    analysis_service: EventAnalysisService = Depends(get_analysis_service)
) -> Dict[str, Any]:
    try:
        # Phân tích sự kiện
        analysis = await analysis_service.analyze_event(payload.event)
        
        # TODO: Lưu kết quả phân tích vào MongoDB
        
        # TODO: Gửi thông báo qua n8n nếu cần
        
        return {
            "status": "success",
            "event_id": payload.event.event_id,
            "analysis": analysis.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 