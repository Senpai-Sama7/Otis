"""Unit tests for core configuration."""
from src.core.config import Settings, get_settings


def test_settings_defaults():
    """Test default settings values."""
    settings = Settings()
    assert settings.app_name == "Otis Cybersecurity AI Agent"
    assert settings.app_version == "0.1.0"
    assert settings.api_prefix == "/api/v1"
    assert settings.ollama_model == "deepseek-r1:7b"


def test_get_settings_cached():
    """Test that get_settings returns cached instance."""
    settings1 = get_settings()
    settings2 = get_settings()
    assert settings1 is settings2
