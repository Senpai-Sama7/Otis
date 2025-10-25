"""Core configuration management for Otis."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="Otis Cybersecurity AI Agent")
    app_version: str = Field(default="0.1.0")
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")

    # API
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    api_prefix: str = Field(default="/api/v1")

    # Security
    secret_key: str = Field(default="change-this-to-a-secure-random-key-in-production")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)

    # Database
    database_url: str = Field(default="sqlite:///./otis.db")

    # Ollama
    ollama_base_url: str = Field(default="http://localhost:11434")
    ollama_model: str = Field(default="deepseek-r1:7b")
    ollama_timeout: int = Field(default=300)

    # Chroma
    chroma_persist_directory: str = Field(default="./chroma_data")
    chroma_collection_name: str = Field(default="cybersecurity_knowledge")

    # Telegram
    telegram_bot_token: str | None = Field(default=None)
    telegram_admin_chat_id: str | None = Field(default=None)
    telegram_approval_timeout: int = Field(default=300)

    # Docker Sandbox
    docker_sandbox_image: str = Field(default="python:3.11-slim")
    docker_sandbox_timeout: int = Field(default=60)
    docker_sandbox_memory_limit: str = Field(default="512m")
    docker_sandbox_cpu_limit: float = Field(default=1.0)

    # RAG Data Sources
    mitre_attack_url: str = Field(
        default="https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json"
    )
    nist_csf_url: str = Field(default="https://www.nist.gov/cyberframework")
    owasp_top10_url: str = Field(default="https://owasp.org/www-project-top-ten/")

    # Feature Flags
    enable_approval_gate: bool = Field(default=True)
    enable_code_execution: bool = Field(default=True)
    enable_threat_intel: bool = Field(default=True)


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
