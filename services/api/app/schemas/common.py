from typing import Any

from pydantic import BaseModel, Field


class APIResponse[DataT](BaseModel):
    """Standard success envelope for API payloads."""

    success: bool = True
    data: DataT
    message: str | None = None


class ErrorDetail(BaseModel):
    """Detailed error object returned within ErrorResponse."""

    code: str = Field(description="Machine-readable error identifier")
    message: str = Field(description="Human-readable error description")
    details: Any | None = Field(
        default=None, description="Optional diagnostic details or validation errors"
    )


class ErrorResponse(BaseModel):
    """Standard error envelope for all client and server error responses."""

    error: ErrorDetail


class ComponentHealth(BaseModel):
    """Health status representation of a single subsystem dependency."""

    status: str = Field(description="'healthy' or 'unhealthy'")
    details: str = Field(description="Sanitized status summary")


class LivenessResponse(BaseModel):
    """Process liveness probe response schema."""

    status: str
    service: str
    version: str
    environment: str
    timestamp: str


class ReadinessResponse(BaseModel):
    """Service readiness probe response schema."""

    status: str
    service: str
    version: str
    timestamp: str
    components: dict[str, ComponentHealth]
