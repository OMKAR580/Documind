from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class SystemMetadata(Base, TimestampMixin):
    """
    Stores platform-level metadata, runtime status flags, and schema version records.
    Minimal infrastructure model required for Phase 1 backend and database integration.
    """

    __tablename__ = "system_metadata"

    key: Mapped[str] = mapped_column(String(128), primary_key=True, index=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    def __repr__(self) -> str:
        return f"<SystemMetadata(key='{self.key}', value='{self.value}')>"
