"""Repository pattern for database operations."""

from typing import Generic, TypeVar

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.core.logging import get_logger
from src.models.database import Base

logger = get_logger(__name__)

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository with common CRUD operations."""

    def __init__(self, model: type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get(self, id: int) -> ModelType | None:
        """
        Get a single record by ID.

        Args:
            id: Record ID

        Returns:
            Model instance or None if not found
        """
        try:
            return self.db.query(self.model).filter(self.model.id == id).first()
        except SQLAlchemyError as e:
            logger.error("repository.get_failed", model=self.model.__name__, id=id, error=str(e))
            raise

    def get_all(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        """
        Get all records with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of model instances
        """
        try:
            return self.db.query(self.model).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error("repository.get_all_failed", model=self.model.__name__, error=str(e))
            raise

    def create(self, **kwargs) -> ModelType:
        """
        Create a new record.

        Args:
            **kwargs: Model field values

        Returns:
            Created model instance
        """
        try:
            db_obj = self.model(**kwargs)
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
            logger.info("repository.created", model=self.model.__name__, id=db_obj.id)
            return db_obj
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error("repository.create_failed", model=self.model.__name__, error=str(e))
            raise

    def update(self, id: int, **kwargs) -> ModelType | None:
        """
        Update a record.

        Args:
            id: Record ID
            **kwargs: Fields to update

        Returns:
            Updated model instance or None if not found
        """
        try:
            db_obj = self.get(id)
            if db_obj:
                for key, value in kwargs.items():
                    setattr(db_obj, key, value)
                self.db.commit()
                self.db.refresh(db_obj)
                logger.info("repository.updated", model=self.model.__name__, id=id)
            return db_obj
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error("repository.update_failed", model=self.model.__name__, id=id, error=str(e))
            raise

    def delete(self, id: int) -> bool:
        """
        Delete a record.

        Args:
            id: Record ID

        Returns:
            True if deleted, False if not found
        """
        try:
            db_obj = self.get(id)
            if db_obj:
                self.db.delete(db_obj)
                self.db.commit()
                logger.info("repository.deleted", model=self.model.__name__, id=id)
                return True
            return False
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error("repository.delete_failed", model=self.model.__name__, id=id, error=str(e))
            raise
