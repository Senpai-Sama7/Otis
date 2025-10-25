"""Pydantic schemas for API requests and responses."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema."""

    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr


class UserCreate(UserBase):
    """User creation schema."""

    password: str = Field(..., min_length=8)
    role: str = Field(default="viewer")


class UserResponse(UserBase):
    """User response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str
    is_active: bool
    created_at: datetime


class Token(BaseModel):
    """Token response schema."""

    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    """Login request schema."""

    username: str
    password: str


class AgentRequest(BaseModel):
    """Agent request schema for ReAct execution."""

    instruction: str = Field(..., description="Task instruction for the agent")
    scan_duration: int = Field(default=10, ge=1, le=300, description="Scan duration in seconds")
    mode: str = Field(
        default="passive",
        pattern="^(passive|active)$",
        description="Operation mode: passive (read-only) or active (may include changes)",
    )


class AgentResponse(BaseModel):
    """Agent response schema with execution results."""

    summary: str = Field(..., description="Summary of agent execution")
    steps: List[Dict[str, Any]] = Field(..., description="List of reasoning steps")
    proposals: Optional[List[Dict[str, Any]]] = Field(
        None, description="Action proposals requiring approval"
    )
    evidence: Optional[List[Dict[str, Any]]] = Field(None, description="Evidence collected")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")


class ActionProposal(BaseModel):
    """Action proposal schema."""

    action_id: str = Field(..., description="Unique action identifier")
    action_type: str = Field(..., description="Type of action")
    description: str = Field(..., description="Action description")
    code: Optional[str] = Field(None, description="Code to execute")
    rationale: str = Field(..., description="Reasoning for the action")
    risk_level: str = Field(..., pattern="^(low|medium|high|critical)$")
    status: str = Field(..., description="Approval status")


class AgentActionRequest(BaseModel):
    """Agent action request schema."""

    action_type: str = Field(..., description="Type of action to perform")
    description: str = Field(..., description="Action description")
    proposed_code: str | None = Field(None, description="Code to execute")
    reasoning: str = Field(..., description="Reasoning for the action")
    risk_level: str = Field(..., pattern="^(low|medium|high|critical)$")


class AgentActionResponse(BaseModel):
    """Agent action response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    action_type: str
    description: str
    reasoning: str
    risk_level: str
    status: str
    created_at: datetime
    execution_result: str | None = None


class ScanRequest(BaseModel):
    """Environment scan request schema."""

    scan_type: str = Field(..., description="Type of scan: ports, vulnerabilities, config")
    target: str = Field(..., description="Target to scan")
    options: dict | None = Field(default_factory=dict)


class ScanResponse(BaseModel):
    """Environment scan response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    scan_type: str
    target: str
    findings: str
    vulnerabilities_count: int
    risk_score: float | None
    created_at: datetime


class ThreatQueryRequest(BaseModel):
    """Threat intelligence query request."""

    query: str = Field(..., description="Natural language query")
    sources: list[str] | None = Field(default=None, description="Filter by sources")
    limit: int = Field(default=5, ge=1, le=20)


class ThreatQueryResponse(BaseModel):
    """Threat intelligence query response."""

    query: str
    results: list[dict]
    sources_searched: list[str]


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    timestamp: datetime
    services: dict[str, str]

