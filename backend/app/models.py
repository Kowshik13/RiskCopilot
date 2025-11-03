"""
Pydantic models for Risk Copilot API
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
from enum import Enum

class RiskLevel(str, Enum):
    """Risk level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class GuardrailViolation(BaseModel):
    """Model for guardrail violations"""
    type: Literal["pii", "toxic", "banned_topic", "hallucination"]
    severity: RiskLevel
    description: str
    detected_content: Optional[str] = None
    
class Citation(BaseModel):
    """Model for document citations"""
    source_id: str
    document_name: str
    page_number: Optional[int] = None
    section: Optional[str] = None
    relevance_score: float = Field(ge=0.0, le=1.0)
    excerpt: str

class AgentTrace(BaseModel):
    """Model for agent execution traces"""
    agent_name: str
    timestamp: datetime
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    duration_ms: int
    status: Literal["success", "failure", "skipped"]
    error: Optional[str] = None

class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str = Field(..., min_length=1, max_length=4000)
    session_id: Optional[str] = Field(default=None, max_length=100)
    context: Optional[Dict[str, Any]] = None
    enable_guardrails: bool = True
    return_traces: bool = False
    
    @validator('message')
    def validate_message(cls, v):
        # Basic input validation
        if not v or v.isspace():
            raise ValueError("Message cannot be empty")
        return v.strip()

class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    message_id: str
    session_id: str
    question: str
    answer: str
    risk_level: RiskLevel
    confidence: float = Field(ge=0.0, le=1.0)
    citations: List[Citation] = []
    guardrail_violations: List[GuardrailViolation] = []
    traces: Optional[List[AgentTrace]] = None
    processing_time_ms: int
    timestamp: datetime

class HealthStatus(BaseModel):
    """Model for health check response"""
    status: Literal["healthy", "degraded", "unhealthy"]
    version: str
    uptime_seconds: int
    components: Dict[str, str]
    
class TraceQuery(BaseModel):
    """Query parameters for trace endpoint"""
    session_id: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    agent_name: Optional[str] = None
    limit: int = Field(default=100, le=1000)

class AuditLog(BaseModel):
    """Model for audit log entries"""
    id: str
    timestamp: datetime
    session_id: str
    user_id: Optional[str] = None
    action: str
    risk_level: RiskLevel
    request: Dict[str, Any]
    response: Dict[str, Any]
    guardrail_violations: List[GuardrailViolation] = []
    metadata: Dict[str, Any] = {}

class PolicyDocument(BaseModel):
    """Model for policy documents"""
    id: str
    name: str
    category: str
    version: str
    last_updated: datetime
    content_hash: str
    chunk_count: int
    metadata: Dict[str, Any] = {}

class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    error_type: str
    details: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
