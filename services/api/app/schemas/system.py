from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SystemMetadataBase(BaseModel):
    key: str = Field(..., max_length=128, description="Unique metadata key")
    value: str = Field(..., description="Configuration or state value")
    description: str | None = Field(default=None, max_length=255)


class SystemMetadataCreate(SystemMetadataBase):
    pass


class SystemMetadataRead(SystemMetadataBase):
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
