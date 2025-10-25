"""Integration tests for authentication API."""


def test_register_user(client):
    """Test user registration."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "securepass123",
            "role": "viewer",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert data["role"] == "viewer"


def test_register_duplicate_username(client, mock_user):
    """Test registration with duplicate username."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "email": "different@example.com",
            "password": "securepass123",
        },
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_login_success(client, mock_user):
    """Test successful login."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "testpass123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, mock_user):
    """Test login with wrong password."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "wrongpassword"},
    )
    assert response.status_code == 401


def test_login_nonexistent_user(client):
    """Test login with non-existent user."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "nonexistent", "password": "password123"},
    )
    assert response.status_code == 401
