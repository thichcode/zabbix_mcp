from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class ZabbixEvent(BaseModel):
    event_id: str
    host: str
    item: str
    trigger: str
    severity: int
    status: str
    timestamp: datetime
    value: str
    description: Optional[str] = None
    tags: List[Dict[str, str]] = Field(default_factory=list)

class EventAnalysis(BaseModel):
    event_id: str
    rca: str
    confidence: float
    similar_events: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class WebhookPayload(BaseModel):
    event: ZabbixEvent
    action: str
    additional_data: Optional[Dict[str, Any]] = None 