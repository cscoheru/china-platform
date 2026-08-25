"""Stage 1 / S1.10 — Indicator endpoints.

Per docs/24 §6.2:
  GET /api/indicator                         — list
  GET /api/indicator/{id}/series            — core series
  GET /api/indicator/{id}/series/{geo_id}   — filtered by geo
"""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Path, Query

from china_platform.api.deps import DatabaseDep
from china_platform.api.errors import ResourceNotFound
from china_platform.api.models.common import Pagination
from china_platform.api.models.indicator import (
    IndicatorListItem,
    IndicatorListResponse,
    IndicatorSeriesPoint,
    IndicatorSeriesResponse,
)

router = APIRouter(prefix="/api/indicator", tags=["indicator"])


@router.get("", response_model=IndicatorListResponse)
def list_indicators(
    db: DatabaseDep,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=500),
) -> IndicatorListResponse:
    """Aggregated indicator inventory from stg_observation."""
    with db.session() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(DISTINCT indicator_id) FROM cegr_staging.stg_observation")
            total_count = cur.fetchone()[0]
            cur.execute(
                """
                SELECT
                    indicator_id,
                    COUNT(DISTINCT geo_entity_id)   AS geo_count,
                    COUNT(*)                        AS obs_count,
                    MAX(period_start)               AS latest
                FROM cegr_staging.stg_observation
                GROUP BY indicator_id
                ORDER BY obs_count DESC, indicator_id
                LIMIT %s OFFSET %s
                """,
                (page_size, (page - 1) * page_size),
            )
            rows = cur.fetchall()
    items = [
        IndicatorListItem(
            indicator_id=r[0],
            geo_entity_count=r[1],
            observation_count=r[2],
            latest_period_start=r[3],
        )
        for r in rows
    ]
    return IndicatorListResponse(
        indicators=items,
        pagination=Pagination(
            page=page,
            page_size=page_size,
            total_count=total_count,
            has_next=(page * page_size) < total_count,
        ),
    )


@router.get("/{indicator_id}/series", response_model=IndicatorSeriesResponse)
def indicator_series(
    db: DatabaseDep,
    indicator_id: UUID = Path(...),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=500, ge=1, le=5000),
) -> IndicatorSeriesResponse:
    """Core series endpoint — joins int_indicator_timeseries.

    Returns 200 + (possibly empty) series even when indicator_id has no data,
    per docs/24 §6.2 acceptance. Does NOT raise INDICATOR_NOT_FOUND.
    """
    with db.session() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    indicator_id, geo_entity_id, period_start, period_end,
                    period_type, value, unit, status, comparison_basis,
                    source_domain, source_category, source_level,
                    verification_status, extraction_method, confidence,
                    extracted_at
                FROM cegr_staging.int_indicator_timeseries
                WHERE indicator_id = %s
                ORDER BY period_start DESC, geo_entity_id
                LIMIT %s OFFSET %s
                """,
                (str(indicator_id), page_size, (page - 1) * page_size),
            )
            rows = cur.fetchall()
    points = [_row_to_series_point(r) for r in rows]
    return IndicatorSeriesResponse(
        indicator_id=indicator_id,
        series=points,
        pagination=Pagination(
            page=page,
            page_size=page_size,
            total_count=len(points),
            has_next=len(points) == page_size,
        ),
    )


@router.get(
    "/{indicator_id}/series/{geo_entity_id}",
    response_model=IndicatorSeriesResponse,
)
def indicator_series_for_geo(
    db: DatabaseDep,
    indicator_id: UUID = Path(...),
    geo_entity_id: UUID = Path(...),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=500, ge=1, le=5000),
) -> IndicatorSeriesResponse:
    """Series filtered by (indicator, geo)."""
    with db.session() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    indicator_id, geo_entity_id, period_start, period_end,
                    period_type, value, unit, status, comparison_basis,
                    source_domain, source_category, source_level,
                    verification_status, extraction_method, confidence,
                    extracted_at
                FROM cegr_staging.int_indicator_timeseries
                WHERE indicator_id = %s AND geo_entity_id = %s
                ORDER BY period_start DESC
                LIMIT %s OFFSET %s
                """,
                (str(indicator_id), str(geo_entity_id), page_size, (page - 1) * page_size),
            )
            rows = cur.fetchall()
    points = [_row_to_series_point(r) for r in rows]
    return IndicatorSeriesResponse(
        indicator_id=indicator_id,
        series=points,
        pagination=Pagination(
            page=page,
            page_size=page_size,
            total_count=len(points),
            has_next=len(points) == page_size,
        ),
    )


def _row_to_series_point(row: tuple) -> IndicatorSeriesPoint:
    """Map raw row tuple (in SELECT order) to IndicatorSeriesPoint."""
    return IndicatorSeriesPoint(
        indicator_id=row[0],
        geo_entity_id=row[1],
        period_start=row[2],
        period_end=row[3],
        period_type=row[4],
        value=float(row[5]),
        unit=row[6],
        status=row[7],
        comparison_basis=row[8],
        source_domain=row[9],
        source_category=row[10],
        source_level=row[11],
        verification_status=row[12],
        extraction_method=row[13],
        confidence=(float(row[14]) if row[14] is not None else None),
        extracted_at=row[15],
    )