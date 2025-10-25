"""Unit tests for security utilities."""
from src.core.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)


def test_password_hashing():
    """Test password hashing and verification."""
    password = "testpassword123"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False


def test_create_and_decode_token():
    """Test JWT token creation and decoding."""
    data = {"sub": "testuser", "role": "admin"}
    secret = "test-secret-key"
    algorithm = "HS256"
    
    token = create_access_token(data, secret, algorithm)
    assert token is not None
    assert isinstance(token, str)
    
    decoded = decode_access_token(token, secret, algorithm)
    assert decoded is not None
    assert decoded["sub"] == "testuser"
    assert decoded["role"] == "admin"


def test_decode_invalid_token():
    """Test decoding invalid token."""
    secret = "test-secret-key"
    algorithm = "HS256"
    
    result = decode_access_token("invalid.token.here", secret, algorithm)
    assert result is None
