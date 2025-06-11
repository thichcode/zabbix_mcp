from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import webhook

app = FastAPI(
    title="Zabbix MCP Server",
    description="Model Context Protocol Server for Zabbix Event Analysis",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(webhook.router, prefix="/api/v1", tags=["webhook"])

@app.get("/")
async def root():
    return {"message": "Welcome to Zabbix MCP Server"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 