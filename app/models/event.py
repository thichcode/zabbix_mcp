from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

class TriggerType(str, Enum):
    PROBLEM = "PROBLEM"
    OK = "OK"
    ACKNOWLEDGE = "ACKNOWLEDGE"

class TriggerPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class ZabbixEvent(BaseModel):
    event_id: str
    host: str
    item: str
    trigger: str
    severity: int
    status: TriggerType
    timestamp: datetime
    value: str
    description: Optional[str] = None
    tags: List[Dict[str, str]] = Field(default_factory=list)
    priority: TriggerPriority = Field(default=TriggerPriority.MEDIUM)
    related_events: List[str] = Field(default_factory=list)
    impact_scope: List[str] = Field(default_factory=list)

class EventAnalysis(BaseModel):
    event_id: str
    rca: str
    confidence: float
    recommendations: List[str]
    similar_events: List[str]
    metadata: Dict[str, Any]
    trend_analysis: Optional[Dict[str, Any]] = None
    impact_analysis: Optional[Dict[str, Any]] = None
    resolution_time: Optional[float] = None

class WebhookPayload(BaseModel):
    event: ZabbixEvent
    action: str
    additional_data: Optional[Dict[str, Any]] = None 