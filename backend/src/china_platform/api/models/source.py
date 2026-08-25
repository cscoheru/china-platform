"""Stage 1 / S1.10 — Source-related Pydantic models.

Per docs/24 §5.3.
"""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from china_platform.api.models.common import Pagination


class SourceListItem(BaseModel):
    """Summary of a source registry entry."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "source_id": "00000000-0000-0000-0000-000000000000",
                "domain": "stats.gov.cn",
                "organization": "国家统计局",
                "category": "NATIONAL_BULLETIN",
                "source_level": "S1",
                "enabled": True,
            }
        }
    )

    source_id: UUID
    domain: str
    organization: str
    category: str
    source_level: str
    enabled: bool


class SourceListResponse(BaseModel):
    """List of sources."""

    sources: list[SourceListItem]
    pagination: Pagination


class SourceCoverage(BaseModel):
    """Per-source coverage + quality stats (from int_source_coverage)."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "source_id": "00000000-0000-0000-0000-000000000000",
                "domain": "stats.gov.cn",
                "category": "NATIONAL_BULLETIN",
                "source_level": "S1",
                "enabled": True,
                "total_runs": 12,
                "success_runs": 11,
                "failure_runs": 1,
                "failure_rate": 0.083,
                "total_extracted": 1200,
                "total_inserted": 1180,
                "overall_insertion_pct": 98.3,
                "avg_quality_score": 0.85,
                "low_confidence_count": 5,
                "missing_with_reason_count": 2,
                "total_observations": 1180,
                "last_run_at": "2026-08-25T08:00:00Z",
            }
        }
    )

    source_id: UUID
    domain: str
    category: str
    source_level: str
    enabled: bool
    total_runs: int = Field(ge=0)
    success_runs: int = Field(ge=0)
    failure_runs: int = Field(ge=0)
    failure_rate: float = Field(ge=0.0, le=1.0)
    total_extracted: int = Field(ge=0)
    total_inserted: int = Field(ge=0)
    overall_insertion_pct: float | None = None
    avg_quality_score: float | None = None
    low_confidence_count: int = Field(ge=0)
    missing_with_reason_count: int = Field(ge=0)
    total_observations: int = Field(ge=0)
    last_run_at: datetime | None = None


class SourceRun(BaseModel):
    """One ingestion run summary (for /source/{id}/runs)."""

    run_id: UUID
    status: str
    started_at: datetime
    finished_at: datetime | None = None
    duration_seconds: float | None = None
    records_extracted: int | None = None
    records_inserted: int | None = None
    is_stale: bool = False


class SourceRunsResponse(BaseModel):
    """Recent ingestion runs for a source."""

    source_id: UUID
    runs: list[SourceRun] = Field(default_factory=list)
    pagination: Pagination