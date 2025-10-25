#!/usr/bin/env python3
"""Create initial admin user."""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.logging import configure_logging, get_logger
from src.core.security import get_password_hash
from src.database import get_db_context
from src.models.database import User, UserRole

configure_logging()
logger = get_logger(__name__)


def create_admin_user(username: str = "admin", email: str = "admin@otis.local", password: str = "admin123"):
    """Create initial admin user."""
    logger.info("Creating admin user", username=username)
    
    with get_db_context() as db:
        # Check if user exists
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            logger.warning("Admin user already exists", username=username)
            return
        
        # Create admin user
        admin_user = User(
            username=username,
            email=email,
            hashed_password=get_password_hash(password),
            role=UserRole.ADMIN,
            is_active=True,
        )
        db.add(admin_user)
        db.commit()
        
        logger.info("Admin user created successfully", username=username)
        print(f"\nAdmin user created:")
        print(f"  Username: {username}")
        print(f"  Email: {email}")
        print(f"  Password: {password}")
        print(f"\n⚠️  Change the password after first login!")


if __name__ == "__main__":
    create_admin_user()
