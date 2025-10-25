"""JSON structured logging with rotating file handler."""

import json
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Dict, Optional

import structlog

from src.core.config import get_settings

settings = get_settings()


def configure_json_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
) -> None:
    """
    Configure JSON structured logging with rotating file handler.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path (creates rotating handler if provided)
        max_bytes: Maximum log file size before rotation (default: 10MB)
        backup_count: Number of backup files to keep (default: 5)
    """
    # Configure structlog for JSON output
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )

    # Add rotating file handler if log file specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
        )
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(logging.Formatter("%(message)s"))

        # Add handler to root logger
        logging.getLogger().addHandler(file_handler)


def get_json_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a JSON logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Structured logger instance
    """
    return structlog.get_logger(name)


class JSONLogger:
    """
    JSON logger wrapper with additional utility methods.
    """

    def __init__(self, name: str, log_file: Optional[str] = None):
        self.name = name
        self.logger = get_json_logger(name)
        self.log_file = log_file

    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message with additional context."""
        self.logger.info(message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message with additional context."""
        self.logger.warning(message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """Log error message with additional context."""
        self.logger.error(message, **kwargs)

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message with additional context."""
        self.logger.debug(message, **kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        """Log critical message with additional context."""
        self.logger.critical(message, **kwargs)

    def log_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Log a structured event.

        Args:
            event_type: Type of event
            data: Event data
        """
        self.logger.info(event_type, event_data=data)

    def log_to_file(self, message: str, data: Optional[Dict[str, Any]] = None) -> None:
        """
        Log directly to a file (bypassing standard logging).

        Args:
            message: Log message
            data: Optional additional data
        """
        if not self.log_file:
            return

        log_entry = {
            "timestamp": structlog.processors.TimeStamper(fmt="iso")(None, None, None),
            "logger": self.name,
            "message": message,
        }
        if data:
            log_entry.update(data)

        log_path = Path(self.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")


def setup_audit_logging(audit_file: str = "data/audit.log") -> JSONLogger:
    """
    Setup audit logging to a dedicated file.

    Args:
        audit_file: Path to audit log file

    Returns:
        JSONLogger instance configured for audit logging
    """
    logger = JSONLogger("audit", audit_file)
    logger.info("Audit logging initialized", audit_file=audit_file)
    return logger


# Singleton audit logger
_audit_logger: Optional[JSONLogger] = None


def get_audit_logger() -> JSONLogger:
    """
    Get the global audit logger instance.

    Returns:
        Audit logger
    """
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = setup_audit_logging()
    return _audit_logger


def audit_log(
    action: str,
    user: Optional[str] = None,
    risk_level: Optional[str] = None,
    status: Optional[str] = None,
    **kwargs: Any,
) -> None:
    """
    Log an audit event.

    Args:
        action: Action being performed
        user: User performing the action
        risk_level: Risk level of the action
        status: Status of the action
        **kwargs: Additional context
    """
    logger = get_audit_logger()
    log_data = {
        "action": action,
        "user": user,
        "risk_level": risk_level,
        "status": status,
        **kwargs,
    }
    logger.log_to_file("audit_event", log_data)
