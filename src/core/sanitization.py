"""
Input sanitization and validation layers.

Provides defense-in-depth input validation beyond Pydantic schemas.
"""

import re
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class InputSanitizer:
    """Multi-layer input sanitization."""

    # Dangerous patterns to block
    DANGEROUS_PATTERNS = [
        r"(?i)(rm\s+-rf|del\s+/|format\s+c:)",  # Destructive commands
        r"(?i)(eval|exec|__import__|compile)\s*\(",  # Code execution
        r"(?i)(DROP|DELETE|TRUNCATE)\s+TABLE",  # SQL injection
        r"<script[^>]*>.*?</script>",  # XSS
        r"(?i)(wget|curl).*\|.*sh",  # Remote code execution
        r"\$\(.*\)",  # Command substitution
        r"`.*`",  # Backtick execution
        r"(?i)(/etc/passwd|/etc/shadow)",  # Sensitive files
    ]

    # Maximum lengths
    MAX_QUERY_LENGTH = 10000
    MAX_CODE_LENGTH = 50000
    MAX_TARGET_LENGTH = 255

    @classmethod
    def sanitize_query(cls, query: str) -> str:
        """
        Sanitize user query input.
        
        Args:
            query: User query string
            
        Returns:
            Sanitized query
            
        Raises:
            ValueError: If input contains dangerous patterns
        """
        if not query or not isinstance(query, str):
            raise ValueError("Query must be a non-empty string")

        # Length check
        if len(query) > cls.MAX_QUERY_LENGTH:
            raise ValueError(f"Query exceeds maximum length of {cls.MAX_QUERY_LENGTH}")

        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, query):
                logger.warning("sanitizer.dangerous_pattern_detected", pattern=pattern)
                raise ValueError("Query contains potentially dangerous content")

        # Strip control characters
        sanitized = "".join(char for char in query if ord(char) >= 32 or char in "\n\t")

        return sanitized.strip()

    @classmethod
    def sanitize_code(cls, code: str, language: str = "python") -> str:
        """
        Sanitize code input for sandbox execution.
        
        Args:
            code: Code to execute
            language: Programming language
            
        Returns:
            Sanitized code
            
        Raises:
            ValueError: If code contains dangerous patterns
        """
        if not code or not isinstance(code, str):
            raise ValueError("Code must be a non-empty string")

        # Length check
        if len(code) > cls.MAX_CODE_LENGTH:
            raise ValueError(f"Code exceeds maximum length of {cls.MAX_CODE_LENGTH}")

        # Language-specific checks
        if language == "python":
            dangerous_imports = [
                r"import\s+os",
                r"import\s+subprocess",
                r"import\s+sys",
                r"from\s+os\s+import",
                r"__import__",
            ]
            for pattern in dangerous_imports:
                if re.search(pattern, code):
                    logger.warning("sanitizer.dangerous_import", pattern=pattern)
                    raise ValueError("Code contains restricted imports")

        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, code):
                logger.warning("sanitizer.dangerous_code_pattern", pattern=pattern)
                raise ValueError("Code contains potentially dangerous content")

        return code

    @classmethod
    def sanitize_target(cls, target: str) -> str:
        """
        Sanitize network target input.
        
        Args:
            target: Target hostname or IP
            
        Returns:
            Sanitized target
            
        Raises:
            ValueError: If target is invalid
        """
        if not target or not isinstance(target, str):
            raise ValueError("Target must be a non-empty string")

        # Length check
        if len(target) > cls.MAX_TARGET_LENGTH:
            raise ValueError(f"Target exceeds maximum length of {cls.MAX_TARGET_LENGTH}")

        # Allow only alphanumeric, dots, hyphens, underscores
        if not re.match(r"^[a-zA-Z0-9\.\-_]+$", target):
            raise ValueError("Target contains invalid characters")

        # Block localhost variations (unless explicitly allowed)
        localhost_patterns = [r"^127\.", r"^::1$", r"^0\.0\.0\.0$"]
        for pattern in localhost_patterns:
            if re.match(pattern, target):
                # Localhost is allowed, but log it
                logger.info("sanitizer.localhost_target", target=target)

        return target.strip()

    @classmethod
    def sanitize_dict(cls, data: dict[str, Any], max_depth: int = 5) -> dict[str, Any]:
        """
        Recursively sanitize dictionary values.
        
        Args:
            data: Dictionary to sanitize
            max_depth: Maximum recursion depth
            
        Returns:
            Sanitized dictionary
        """
        if max_depth <= 0:
            raise ValueError("Maximum recursion depth exceeded")

        sanitized = {}
        for key, value in data.items():
            # Sanitize key
            if not isinstance(key, str) or len(key) > 100:
                continue

            # Sanitize value based on type
            if isinstance(value, str):
                try:
                    sanitized[key] = cls.sanitize_query(value)
                except ValueError:
                    logger.warning("sanitizer.invalid_value", key=key)
                    continue
            elif isinstance(value, dict):
                sanitized[key] = cls.sanitize_dict(value, max_depth - 1)
            elif isinstance(value, (int, float, bool)):
                sanitized[key] = value
            elif isinstance(value, list):
                sanitized[key] = [
                    cls.sanitize_query(item) if isinstance(item, str) else item
                    for item in value[:100]  # Limit list size
                ]

        return sanitized
