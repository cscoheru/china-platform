"""Stage 1 / S1.10 — Pydantic models for the API."""
from china_platform.api.models.common import ErrorResponse, HealthCheck, Pagination
from china_platform.api.models.indicator import (
    IndicatorListItem,
    IndicatorListResponse,
    IndicatorSeriesPoint,
    IndicatorSeriesResponse,
)
from china_platform.api.models.observation import (
    ObservationItem,
    ObservationListResponse,
)
from china_platform.api.models.source import (
    SourceCoverage,
    SourceListItem,
    SourceListResponse,
    SourceRun,
    SourceRunsResponse,
)

__all__ = [
    "ErrorResponse",
    "HealthCheck",
    "Pagination",
    "IndicatorListItem",
    "IndicatorListResponse",
    "IndicatorSeriesPoint",
    "IndicatorSeriesResponse",
    "ObservationItem",
    "ObservationListResponse",
    "SourceCoverage",
    "SourceListItem",
    "SourceListResponse",
    "SourceRun",
    "SourceRunsResponse",
]