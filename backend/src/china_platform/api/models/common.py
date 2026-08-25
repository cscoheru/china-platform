"""Stage 1 / S1.10 — shared Pydantic models (Health, Error, Pagination)."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class HealthCheck(BaseModel):
    """Health check response."""

    model_config = ConfigDict(
        json_schema_extra={"example": {"status": "ok", "db_reachable": True}}
    )

    status: str = "ok"
    db_reachable: bool
    timestamp_utc: datetime


class ErrorResponse(BaseModel):
    """Standard error envelope per docs/24 §7.2."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error_code": "INDICATOR_NOT_FOUND",
                "message": "Indicator with id=... not found",
                "detail": {"resource": "indicator", "id": "..."},
            }
        }
    )

    error_code: str
    message: str
    detail: dict | None = None


class Pagination(BaseModel):
    """Pagination metadata for list endpoints."""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=500)
    total_count: int = Field(default=0, ge=0)
    has_next: bool = False