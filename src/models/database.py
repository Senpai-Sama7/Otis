"""Database models for Otis."""

from datetime import UTC, datetime
from enum import Enum

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class UserRole(str, Enum):
    """User roles for RBAC."""

    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"


class ActionStatus(str, Enum):
    """Status of agent actions."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"
    FAILED = "failed"


def utcnow():
    """Return timezone-aware UTC datetime."""
    return datetime.now(UTC)


class User(Base):
    """User model for authentication and authorization."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.VIEWER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)


class AgentAction(Base):
    """Agent action model for tracking proposed and executed actions."""

    __tablename__ = "agent_actions"

    id = Column(Integer, primary_key=True, index=True)
    action_type = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=False)
    proposed_code = Column(Text, nullable=True)
    reasoning = Column(Text, nullable=False)
    risk_level = Column(String(20), nullable=False)
    status = Column(SQLEnum(ActionStatus), default=ActionStatus.PENDING, nullable=False, index=True)
    approved_by = Column(Integer, nullable=True)
    execution_result = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)


class ThreatIntelligence(Base):
    """Threat intelligence entries for knowledge base."""

    __tablename__ = "threat_intelligence"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(100), nullable=False, index=True)  # MITRE, NIST, OWASP
    category = Column(String(100), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(20), nullable=True)
    mitigation = Column(Text, nullable=True)
    external_id = Column(String(100), nullable=True, index=True)
    embedding_id = Column(String(255), nullable=True)  # Reference to Chroma vector
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)


class EnvironmentScan(Base):
    """Environment scan results."""

    __tablename__ = "environment_scans"

    id = Column(Integer, primary_key=True, index=True)
    scan_type = Column(String(100), nullable=False, index=True)
    target = Column(String(255), nullable=False)
    findings = Column(Text, nullable=False)
    vulnerabilities_count = Column(Integer, default=0)
    risk_score = Column(Float, nullable=True)
    scan_duration = Column(Float, nullable=True)  # seconds
    created_at = Column(DateTime, default=utcnow, nullable=False, index=True)
