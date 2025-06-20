from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .api import webhook, health
from .core.logging import api_logger
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Zabbix MCP Server",
    description="Middleware service for Zabbix event analysis using AI",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(webhook.router, prefix="/api/v1", tags=["webhook"])
app.include_router(health.router, prefix="/api/v1", tags=["health"])

@app.on_event("startup")
async def startup_event():
    """Handle server startup event"""
    api_logger.info("Server starting up...")
    try:
        # Check service connections
        from .api.health import health_check
        health_status = await health_check()
        if health_status["status"] == "unhealthy":
            api_logger.error("Some services are unhealthy on startup")
            for service, status in health_status["services"].items():
                if status["status"] == "unhealthy":
                    api_logger.error(f"{service}: {status['message']}")
    except Exception as e:
        api_logger.error(f"Error during startup: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Handle server shutdown event"""
    api_logger.info("Server shutting down...")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Zabbix MCP Server",
        "version": "1.0.0",
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    # Get configuration from environment variables
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    # Start server
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=debug
    ) 