from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import aiohttp
import os
from datetime import datetime
from ..services.database import DatabaseService
from ..services.cache_service import CacheService
from ..core.logging import api_logger

router = APIRouter()
db = DatabaseService()
cache = CacheService()

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Kiểm tra trạng thái tổng thể của hệ thống"""
    try:
        # Kiểm tra MongoDB
        mongo_status = await check_mongodb()
        
        # Kiểm tra Redis
        redis_status = await check_redis()
        
        # Kiểm tra Zabbix
        zabbix_status = await check_zabbix()
        
        # Kiểm tra Ollama/OpenAI
        ai_status = await check_ai_service()
        
        # Tổng hợp kết quả
        status = {
            "status": "healthy" if all([
                mongo_status["status"] == "healthy",
                redis_status["status"] == "healthy",
                zabbix_status["status"] == "healthy",
                ai_status["status"] == "healthy"
            ]) else "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "mongodb": mongo_status,
                "redis": redis_status,
                "zabbix": zabbix_status,
                "ai": ai_status
            }
        }
        
        api_logger.info(f"Health check completed: {status['status']}")
        return status
        
    except Exception as e:
        api_logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def check_mongodb() -> Dict[str, Any]:
    """Kiểm tra kết nối MongoDB"""
    try:
        await db.ping()
        return {
            "status": "healthy",
            "message": "MongoDB connection successful"
        }
    except Exception as e:
        database_logger.error(f"MongoDB health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "message": str(e)
        }

async def check_redis() -> Dict[str, Any]:
    """Kiểm tra kết nối Redis"""
    try:
        await cache.redis_client.ping()
        return {
            "status": "healthy",
            "message": "Redis connection successful"
        }
    except Exception as e:
        cache_logger.error(f"Redis health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "message": str(e)
        }

async def check_zabbix() -> Dict[str, Any]:
    """Kiểm tra kết nối Zabbix API"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(os.getenv("ZABBIX_API_URL")) as response:
                if response.status == 200:
                    return {
                        "status": "healthy",
                        "message": "Zabbix API connection successful"
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "message": f"Zabbix API returned status {response.status}"
                    }
    except Exception as e:
        api_logger.error(f"Zabbix health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "message": str(e)
        }

async def check_ai_service() -> Dict[str, Any]:
    """Kiểm tra kết nối AI service (Ollama/OpenAI)"""
    try:
        if os.getenv("USE_OLLAMA") == "true":
            # Kiểm tra Ollama
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{os.getenv('OLLAMA_API_URL')}/api/tags") as response:
                    if response.status == 200:
                        return {
                            "status": "healthy",
                            "message": "Ollama connection successful"
                        }
                    else:
                        return {
                            "status": "unhealthy",
                            "message": f"Ollama API returned status {response.status}"
                        }
        else:
            # Kiểm tra OpenAI
            from openai import OpenAI
            client = OpenAI()
            client.models.list()
            return {
                "status": "healthy",
                "message": "OpenAI connection successful"
            }
    except Exception as e:
        api_logger.error(f"AI service health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "message": str(e)
        } 