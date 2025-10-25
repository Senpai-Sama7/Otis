"""Unit tests for database models."""

from src.models.database import ActionStatus, User, UserRole


def test_user_model_creation(db_session):
    """Test creating a user model."""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password",
        role=UserRole.ANALYST,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.id is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.role == UserRole.ANALYST
    assert user.is_active is True


def test_user_roles():
    """Test user role enum."""
    assert UserRole.ADMIN.value == "admin"
    assert UserRole.ANALYST.value == "analyst"
    assert UserRole.VIEWER.value == "viewer"


def test_action_status():
    """Test action status enum."""
    assert ActionStatus.PENDING.value == "pending"
    assert ActionStatus.APPROVED.value == "approved"
    assert ActionStatus.REJECTED.value == "rejected"
    assert ActionStatus.EXECUTED.value == "executed"
    assert ActionStatus.FAILED.value == "failed"
