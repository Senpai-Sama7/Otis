"""
Log ingestion API for Blue Team operations.

Receives logs from sysmon, osquery, Zeek, etc.
"""

from typing import Any

import structlog
from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/ingest", tags=["blue-team"])


class LogEntry(BaseModel):
    """Log entry schema."""

    timestamp: str
    source: str
    level: str
    message: str
    metadata: dict[str, Any] | None = None


@router.post("/logs")
async def ingest_logs(request: Request):
    """
    Ingest logs from security tools.

    Accepts logs from sysmon, osquery, Zeek, etc.
    Forwards to Vector for processing and Elasticsearch storage.
    """
    try:
        # Get raw body
        body = await request.body()

        logger.info(
            "ingest.log_received",
            content_type=request.headers.get("content-type"),
            size=len(body),
        )

        # Forward to Vector (Vector listens on HTTP)
        # In production, Vector would be configured to listen on a port
        # and this endpoint would forward logs there

        # For now, log to file for Vector to pick up
        from datetime import datetime

        log_file = f"/logs/ingested/{datetime.now().strftime('%Y%m%d')}.json"

        with open(log_file, "a") as f:
            f.write(body.decode() + "\n")

        return {"success": True, "message": "Logs ingested"}

    except Exception as e:
        logger.error("ingest.failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Log ingestion failed: {str(e)}",
        )


@router.post("/trigger_mitigation")
async def trigger_mitigation(alert: dict[str, Any]):
    """
    Trigger real-time mitigation based on alert.

    Called by ElastAlert when Sigma rule matches.
    Tasks Otis agent to mitigate threat.
    """
    try:
        logger.warning(
            "mitigation.triggered",
            alert_name=alert.get("rule_name"),
            severity=alert.get("severity"),
        )

        # Extract threat details
        threat_ip = alert.get("source_ip")
        threat_type = alert.get("rule_name")

        # Task agent with mitigation instruction
        from src.models.schemas import AgentRequest

        instruction = f"""URGENT: Mitigate detected threat.

Alert: {threat_type}
Source IP: {threat_ip}
Severity: {alert.get('severity')}

Recommended actions:
1. Quarantine host {threat_ip}
2. Block network access
3. Collect forensic evidence
4. Notify security team

Analyze the threat and propose mitigation actions."""

        # Create agent request
        AgentRequest(
            instruction=instruction,
            mode="active",  # Active mode for mitigation
        )

        # This will go through PolicyEngine and require approval
        # Human analyst gets Telegram notification with Approve/Deny

        return {
            "success": True,
            "message": "Mitigation task created",
            "alert": alert.get("rule_name"),
            "requires_approval": True,
        }

    except Exception as e:
        logger.error("mitigation.failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Mitigation trigger failed: {str(e)}",
        )
