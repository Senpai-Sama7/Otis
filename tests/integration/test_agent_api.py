"""Integration tests for agent API."""

import pytest


@pytest.mark.asyncio
async def test_threat_intel_query_requires_auth(client):
    """Test that threat intel query requires authentication."""
    response = client.post(
        "/api/v1/agent/threat-intel",
        json={"query": "SQL injection", "limit": 5},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_scan_environment_requires_analyst(client, auth_headers):
    """Test environment scan with analyst role."""
    response = client.post(
        "/api/v1/agent/scan",
        json={
            "scan_type": "ports",
            "target": "localhost",
            "options": {},
        },
        headers=auth_headers,
    )
    # May fail if Docker not available, but should not be auth error
    assert response.status_code != 403


@pytest.mark.asyncio
async def test_propose_action_requires_analyst(client, auth_headers):
    """Test action proposal with analyst role."""
    response = client.post(
        "/api/v1/agent/propose-action",
        json={
            "action_type": "patch",
            "description": "Apply security patch",
            "reasoning": "Critical vulnerability detected",
            "risk_level": "high",
        },
        headers=auth_headers,
    )
    # Should not be auth error
    assert response.status_code != 403
