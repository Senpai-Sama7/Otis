"""Security utilities for authentication and authorization."""

from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

# Use argon2 for password hashing (more modern and secure than bcrypt)
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    result: bool = pwd_context.verify(plain_password, hashed_password)
    return result


def get_password_hash(password: str) -> str:
    """Hash a password."""
    hashed: str = pwd_context.hash(password)
    return hashed


def create_access_token(
    data: dict[str, Any], secret_key: str, algorithm: str, expires_delta: timedelta | None = None
) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt: str = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt


def decode_access_token(token: str, secret_key: str, algorithm: str) -> dict[str, Any] | None:
    """Decode and verify a JWT access token."""
    try:
        payload: dict[str, Any] = jwt.decode(token, secret_key, algorithms=[algorithm])
        return payload
    except JWTError:
        return None
