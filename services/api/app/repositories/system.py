from sqlalchemy.orm import Session

from app.models.system import SystemMetadata
from app.repositories.base import BaseRepository


class SystemMetadataRepository(BaseRepository[SystemMetadata]):
    """Repository managing system-level metadata and configuration flags."""

    def __init__(self, db: Session) -> None:
        super().__init__(SystemMetadata, db)

    def get_by_key(self, key: str) -> SystemMetadata | None:
        """Retrieves a metadata entry by its unique key."""
        return self.get_by_id(key)

    def set_value(self, key: str, value: str, description: str | None = None) -> SystemMetadata:
        """Sets or updates a metadata entry."""
        entry = self.get_by_key(key)
        if entry:
            entry.value = value
            if description is not None:
                entry.description = description
            self.db.commit()
            self.db.refresh(entry)
            return entry

        new_entry = SystemMetadata(key=key, value=value, description=description)
        return self.create(new_entry)
