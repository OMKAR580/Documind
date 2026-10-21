from collections.abc import Sequence
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.base import Base


class BaseRepository[ModelType: Base]:
    """Generic base repository encapsulating common database queries."""

    def __init__(self, model: type[ModelType], db: Session) -> None:
        self.model = model
        self.db = db

    def get_by_id(self, id_: Any) -> ModelType | None:
        """Retrieves a single record by its primary key."""
        return self.db.get(self.model, id_)

    def list_all(self, skip: int = 0, limit: int = 100) -> Sequence[ModelType]:
        """Retrieves paginated records."""
        statement = select(self.model).offset(skip).limit(limit)
        return self.db.scalars(statement).all()

    def create(self, instance: ModelType) -> ModelType:
        """Adds and persists a new instance."""
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def delete(self, instance: ModelType) -> None:
        """Removes an instance from the database."""
        self.db.delete(instance)
        self.db.commit()
