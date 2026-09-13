"""Stage 1 / S1.10 — Indicator endpoints.

Per docs/24 §6.2:
  GET /api/indicator                         — list
  GET /api/indicator/{id}/series            — core series
  GET /api/indicator/{id}/series/{geo_id}   — filtered by geo

P2 / knife H-series B1+B2 (2026-09-13): list_indicators rewritten to read from
cegr_mart.mart_province_timeseries UNION mart_city_timeseries (mart indicator_key
instead of stg_observation). Series endpoints keep their UUID contract but
return 503 (not 500) when cegr_staging.int_indicator_timeseries is missing —
defensive hygiene so the public site can never 500 on infra problems.
"""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, Path, Query
from psycopg2 import errors as pg_errors

from china_platform.api.config import get_settings
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

# P2 / knife 664 — year range filter (Pydantic validated, ge/le=2001-2026)
DEFAULT_YEAR_START = 2001
DEFAULT_YEAR_END = 2026


@router.get("", response_model=IndicatorListResponse)
def list_indicators(
    db: DatabaseDep,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=500),
) -> IndicatorListResponse:
    """Aggregated indicator inventory from mart (province + city UNION).

    P2 / knife H-series B1 (2026-09-13): source-of-truth migration from
    cegr_staging.stg_observation (does not exist in knife 663+ mart-only world)
    to cegr_mart.mart_province_timeseries UNION mart_city_timeseries. The 10
    indicator_keys (gdp_total / gdp_growth / gdp_percapita / primary_gdp /
    secondary_gdp / tertiary_gdp / fiscal_rev / retail / fixed_asset / trade)
    are derived from mart distinct values.

    Returns 503 (not 500) if mart tables are missing — public site treats 503
    as a deployment / dbt-rerun signal, not a data error.
    """
    settings = get_settings()
    schema = settings.mart_schema

    # 1. List distinct indicator_keys with per-key aggregate (geo_count, obs_count, latest_year).
    list_sql = f"""
        WITH mart_union AS (
            SELECT indicator_key, province_code AS geo_code, year
              FROM {schema}.mart_province_timeseries
            UNION ALL
            SELECT indicator_key, city_code AS geo_code, year
              FROM {schema}.mart_city_timeseries
        ),
        per_key_geo AS (
            SELECT indicator_key,
                   geo_code,
                   MAX(year) AS latest_year,
                   COUNT(*)  AS obs_count
              FROM mart_union
             GROUP BY indicator_key, geo_code
        )
        SELECT indicator_key,
               COUNT(DISTINCT geo_code)              AS geo_count,
               SUM(obs_count)                        AS total_obs,
               MAX(latest_year)                      AS latest_year
          FROM per_key_geo
         GROUP BY indicator_key
         ORDER BY total_obs DESC, indicator_key
         LIMIT %s OFFSET %s
    """

    # 2. total_count = distinct indicator_key across both marts (for pagination).
    total_sql = f"""
        SELECT COUNT(DISTINCT indicator_key)
          FROM (
            SELECT indicator_key FROM {schema}.mart_province_timeseries
            UNION
            SELECT indicator_key FROM {schema}.mart_city_timeseries
          ) all_keys
    """

    with db.session() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute(list_sql, (page_size, (page - 1) * page_size))
                rows = cur.fetchall()
                cur.execute(total_sql)
                total_count = cur.fetchone()[0]
        except pg_errors.UndefinedTable as exc:
            raise HTTPException(
                status_code=503,
                detail=(
                    f"Mart tables in schema '{schema}' not built. "
                    "Run dbt to materialize mart_province_timeseries + mart_city_timeseries."
                ),
            ) from exc

    items = [
        IndicatorListItem(
            indicator_id=r[0],
            geo_entity_count=int(r[1]),
            observation_count=int(r[2]),
            # Mart year is integer (e.g., 2025). Format as Dec-31 ISO date to keep
            # date type (front-end expects date | None per docs/24 §5.2).
            latest_period_start=(f"{int(r[3])}-12-31" if r[3] is not None else None),
        )
        for r in rows
    ]
    return IndicatorListResponse(
        indicators=items,
        pagination=Pagination(
            page=page,
            page_size=page_size,
            total_count=int(total_count),
            has_next=(page * page_size) < total_count,
        ),
    )


@router.get("/{indicator_id}/series", response_model=IndicatorSeriesResponse)
def indicator_series(
    db: DatabaseDep,
    indicator_id: UUID = Path(...),
    year_start: int = Query(
        default=DEFAULT_YEAR_START, ge=DEFAULT_YEAR_START, le=DEFAULT_YEAR_END,
        description="Lower bound year (inclusive). Filters by period_start year.",
    ),
    year_end: int = Query(
        default=DEFAULT_YEAR_END, ge=DEFAULT_YEAR_START, le=DEFAULT_YEAR_END,
        description="Upper bound year (inclusive). Filters by period_start year.",
    ),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=500, ge=1, le=5000),
) -> IndicatorSeriesResponse:
    """Core series endpoint — joins int_indicator_timeseries.

    Returns 200 + (possibly empty) series even when indicator_id has no data,
    per docs/24 §6.2 acceptance. Does NOT raise INDICATOR_NOT_FOUND.
    """
    if year_start > year_end:
        raise HTTPException(
            status_code=422,
            detail=f"year_start ({year_start}) must be <= year_end ({year_end})",
        )

    with db.session() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        indicator_id, geo_entity_id, period_start, period_end,
                        period_type, value, unit, status, comparison_basis,
                        source_domain, source_category, source_level,
                        verification_status, extraction_method, confidence,
                        caveat_text, source_hash_prefix, extracted_at
                    FROM cegr_staging.int_indicator_timeseries
                    WHERE indicator_id = %s
                      AND EXTRACT(YEAR FROM period_start) BETWEEN %s AND %s
                    ORDER BY period_start DESC, geo_entity_id
                    LIMIT %s OFFSET %s
                    """,
                    (str(indicator_id), year_start, year_end, page_size, (page - 1) * page_size),
                )
                rows = cur.fetchall()
        except pg_errors.UndefinedTable as exc:
            # P2 / knife H-series B2 (2026-09-13): cegr_staging.int_indicator_timeseries
            # does not exist in the knife 663+ mart-only world. Return 503 (not 500)
            # so the frontend treats this as a deployment / dbt-rerun signal, not a
            # data error. /research/m1-series already wraps in try/catch + renders
            # 'FastAPI 暂不可达' banner when this happens.
            raise HTTPException(
                status_code=503,
                detail=(
                    "Series table cegr_staging.int_indicator_timeseries not built. "
                    "Series endpoint unavailable in mart-only mode (knife 663+)."
                ),
            ) from exc
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
    year_start: int = Query(
        default=DEFAULT_YEAR_START, ge=DEFAULT_YEAR_START, le=DEFAULT_YEAR_END,
        description="Lower bound year (inclusive). Filters by period_start year.",
    ),
    year_end: int = Query(
        default=DEFAULT_YEAR_END, ge=DEFAULT_YEAR_START, le=DEFAULT_YEAR_END,
        description="Upper bound year (inclusive). Filters by period_start year.",
    ),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=500, ge=1, le=5000),
) -> IndicatorSeriesResponse:
    """Series filtered by (indicator, geo) and year range."""
    if year_start > year_end:
        raise HTTPException(
            status_code=422,
            detail=f"year_start ({year_start}) must be <= year_end ({year_end})",
        )

    with db.session() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        indicator_id, geo_entity_id, period_start, period_end,
                        period_type, value, unit, status, comparison_basis,
                        source_domain, source_category, source_level,
                        verification_status, extraction_method, confidence,
                        caveat_text, source_hash_prefix, extracted_at
                    FROM cegr_staging.int_indicator_timeseries
                    WHERE indicator_id = %s AND geo_entity_id = %s
                      AND EXTRACT(YEAR FROM period_start) BETWEEN %s AND %s
                    ORDER BY period_start DESC
                    LIMIT %s OFFSET %s
                    """,
                    (str(indicator_id), str(geo_entity_id), year_start, year_end,
                     page_size, (page - 1) * page_size),
                )
                rows = cur.fetchall()
        except pg_errors.UndefinedTable as exc:
            # P2 / knife H-series B2: same 503 fallback as indicator_series.
            raise HTTPException(
                status_code=503,
                detail=(
                    "Series table cegr_staging.int_indicator_timeseries not built. "
                    "Series endpoint unavailable in mart-only mode (knife 663+)."
                ),
            ) from exc
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
        caveat_text=row[15],
        source_hash_prefix=row[16],
        extracted_at=row[17],
    )