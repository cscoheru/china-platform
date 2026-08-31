"""Stage 1 / S1.10 — Indicator-related Pydantic models.

Per docs/24 §5.2.
"""
from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from china_platform.api.models.common import Pagination


class IndicatorSeriesPoint(BaseModel):
    """One data point in an indicator time series."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "indicator_id": "00000000-0000-0000-0000-000000000000",
                "geo_entity_id": "00000000-0000-0000-0000-000000000000",
                "period_start": "2024-01-01",
                "period_end": "2024-12-31",
                "period_type": "ANNUAL",
                "value": 12345.67,
                "unit": "亿元",
                "status": "FINAL",
                "source_domain": "stats.gov.cn",
                "source_category": "NATIONAL_BULLETIN",
                "source_level": "S1",
                "verification_status": "VERIFIED",
                "extraction_method": "HTML_PARSE",
                "confidence": 0.95,
                "extracted_at": "2026-08-25T12:00:00Z",
            }
        }
    )

    indicator_id: UUID
    geo_entity_id: UUID
    period_start: date
    period_end: date | None = None
    period_type: str
    value: float
    unit: str | None = None
    status: str
    comparison_basis: str | None = None
    source_domain: str
    source_category: str
    source_level: str
    verification_status: str
    extraction_method: str
    confidence: float | None = None
    caveat_text: str | None = None
    source_hash_prefix: str | None = None
    extracted_at: datetime


class IndicatorSeriesResponse(BaseModel):
    """Indicator time series response (core endpoint).

    Always returns 200 + (possibly empty) series, even when indicator
    doesn't exist (per docs/24 §6.2 acceptance).
    """

    indicator_id: UUID
    series: list[IndicatorSeriesPoint] = Field(default_factory=list)
    pagination: Pagination


class IndicatorListItem(BaseModel):
    """Summary of an indicator (for list endpoints)."""

    indicator_id: UUID
    geo_entity_count: int = Field(ge=0)
    observation_count: int = Field(ge=0)
    latest_period_start: date | None = None


class IndicatorListResponse(BaseModel):
    """List of indicators (aggregated from stg_observation)."""

    indicators: list[IndicatorListItem]
    pagination: Pagination