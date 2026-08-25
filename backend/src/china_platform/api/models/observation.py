"""Stage 1 / S1.10 — Observation-related Pydantic models.

Per docs/24 §5.4.
"""
from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from china_platform.api.models.common import Pagination


class ObservationItem(BaseModel):
    """One observation (FACT only; stg_observation)."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "observation_id": "00000000-0000-0000-0000-000000000000",
                "indicator_id": "00000000-0000-0000-0000-000000000000",
                "geo_entity_id": "00000000-0000-0000-0000-000000000000",
                "calendar_period_id": "00000000-0000-0000-0000-000000000000",
                "value": 12345.67,
                "unit": "亿元",
                "confidence": 0.95,
                "source_id": "00000000-0000-0000-0000-000000000000",
                "period_start": "2024-01-01",
                "period_type": "ANNUAL",
                "extracted_at": "2026-08-25T12:00:00Z",
            }
        }
    )

    observation_id: UUID
    indicator_id: UUID
    geo_entity_id: UUID
    calendar_period_id: UUID
    value: float | None = None
    unit: str | None = None
    confidence: float | None = None
    source_id: UUID
    period_start: date | None = None
    period_type: str | None = None
    extracted_at: datetime | None = None


class ObservationListResponse(BaseModel):
    """Paginated list of observations."""

    observations: list[ObservationItem] = Field(default_factory=list)
    pagination: Pagination