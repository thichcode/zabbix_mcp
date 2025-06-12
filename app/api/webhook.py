from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import APIKeyHeader
from typing import Dict, Any
from ..models.event import WebhookPayload, ZabbixEvent
from ..services.analysis import EventAnalysisService
from ..services.cache_service import CacheService
import os
import time
from ..core.logging import api_logger

router = APIRouter()
api_key_header = APIKeyHeader(name="X-API-Key")
cache = CacheService()

async def verify_api_key(api_key: str = Depends(api_key_header)) -> bool:
    """Xác thực API key"""
    expected_key = os.getenv("ZABBIX_WEBHOOK_API_KEY")
    if not expected_key:
        api_logger.warning("ZABBIX_WEBHOOK_API_KEY not set in environment")
        return False
    return api_key == expected_key

async def check_rate_limit(request: Request) -> None:
    """Kiểm tra rate limit"""
    client_ip = request.client.host
    current_time = time.time()
    
    # Lấy số request trong 1 phút gần nhất
    key = f"rate_limit:{client_ip}"
    requests = await cache.get(key) or []
    
    # Lọc các request trong 1 phút gần nhất
    requests = [req_time for req_time in requests if current_time - req_time < 60]
    
    # Kiểm tra số lượng request
    if len(requests) >= 60:  # Giới hạn 60 request/phút
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please try again later."
        )
    
    # Thêm request mới
    requests.append(current_time)
    await cache.set(key, requests, expire=60)

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
    request: Request,
    payload: WebhookPayload,
    analysis_service: EventAnalysisService = Depends(get_analysis_service)
) -> Dict[str, Any]:
    try:
        # Kiểm tra xác thực
        if not await verify_api_key():
            raise HTTPException(
                status_code=401,
                detail="Invalid API key"
            )
        
        # Kiểm tra rate limit
        await check_rate_limit(request)
        
        # Log request
        api_logger.info(f"Received webhook from {request.client.host}")
        api_logger.debug(f"Webhook payload: {payload.dict()}")
        
        # Phân tích sự kiện
        analysis = await analysis_service.analyze_event(payload.event)
        
        # Log kết quả phân tích
        api_logger.info(f"Analysis completed for event {payload.event.event_id}")
        api_logger.debug(f"Analysis result: {analysis.dict()}")
        
        return {
            "status": "success",
            "event_id": payload.event.event_id,
            "analysis": analysis.dict()
        }
    except Exception as e:
        api_logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 