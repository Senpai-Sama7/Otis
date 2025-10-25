"""Pydantic schemas for API requests and responses."""

from datetime import datetime

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
