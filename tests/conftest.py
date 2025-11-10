"""Pytest configuration and fixtures for Otis tests."""


import pytest


class MockNotificationSystem:
    """Mock notification system for testing."""

    def __init__(self):
        self.alerts_sent = []
        self.notifications_sent = []

    def send_alert(self, level, title, details, event_id):
        """Mock method to send alerts."""
        self.alerts_sent.append({
            "level": level,
            "title": title,
            "details": details,
            "event_id": event_id
        })
        return {"status": "sent", "event_id": event_id}

    def send_notification(self, level, title, details, event_id):
        """Mock method to send notifications."""
        self.notifications_sent.append({
            "level": level,
            "title": title,
            "details": details,
            "event_id": event_id
        })
        return {"status": "sent", "event_id": event_id}


class MockAuditLogger:
    """Mock audit logger for testing."""

    def __init__(self):
        self.logs = []

    def log_remediation(self, remediation_data):
        """Mock method to log remediation actions."""
        self.logs.append(remediation_data)


@pytest.fixture
def mock_notification_system():
    """Provide a mock notification system."""
    return MockNotificationSystem()


@pytest.fixture
def mock_audit_logger():
    """Provide a mock audit logger."""
    return MockAuditLogger()


def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
