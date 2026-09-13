"""P2 / knife H-series — City time-series endpoints.

Per knife H1 plan (2026-09-13) — city mart 数据接驳公网.
Source of truth: cegr_mart.mart_city_timeseries (dbt mart, knife 934 部署).

Routes:
  GET /api/city-timeseries                    — list all 43 cities in mart dimension
  GET /api/city-timeseries/{city_code}        — single city full series (year range filtered)

Year range validation (FastAPI Pydantic Query):
  - year_start: 2001-2026, default 2020
  - year_end:   2001-2026, default 2025
  - year_start <= year_end enforced by Pydantic ge/le

City code format: ^[A-Z][A-Z0-9_]+$ (e.g., GUANGDONG_SHENZHEN).
4 直辖市 excluded from city mart per 红线-7 (返回 404).

Per-session READ ONLY enforced by Database.session() (knife 660 inherited).
"""
from __future__ import annotations

import re

from fastapi import APIRouter, Path, Query
from psycopg2 import errors as pg_errors

from china_platform.api.config import get_settings
from china_platform.api.deps import DatabaseDep
from china_platform.api.errors import ApiError, ResourceNotFound
from china_platform.api.models.city_timeseries import (
    CityTimeSeriesPoint,
    CityTimeSeriesResponse,
)
from china_platform.api.models.common import Pagination

router = APIRouter(prefix="/api/city-timeseries", tags=["city-timeseries"])

# City code regex: uppercase letters / digits / underscore, must start with letter,
# MUST contain at least one underscore (format is {PROVINCE}_{CITY}).
# Examples: GUANGDONG_SHENZHEN / JIANGSU_NANJING / ZHEJIANG_HANGZHOU.
_CITY_CODE_RE = re.compile(r"^[A-Z][A-Z0-9_]+$")

# Mart coverage: city mart covers 2020-2026 (per knife 663 + 669b-i umbrella).
# 2020 and 2026 are all DATA_MISSING per red lines 1+2 (historical/future).
DEFAULT_YEAR_START = 2020
DEFAULT_YEAR_END = 2025
MIN_YEAR = 2001
MAX_YEAR = 2026


@router.get("", response_model=list[CityTimeSeriesResponse])
def list_city_timeseries(
    db: DatabaseDep,
    year_start: int = Query(
        default=DEFAULT_YEAR_START, ge=MIN_YEAR, le=MAX_YEAR,
        description="Inclusive lower bound year (2001-2026).",
    ),
    year_end: int = Query(
        default=DEFAULT_YEAR_END, ge=MIN_YEAR, le=MAX_YEAR,
        description="Inclusive upper bound year (2001-2026).",
    ),
) -> list[CityTimeSeriesResponse]:
    """Return per-city summary (one row per city_code) for the requested year range.

    Lightweight summary — does NOT return full point list (use the per-city route).
    Useful for navigation/listing UIs (e.g., homepage city column per H3 plan).
    """
    if year_start > year_end:
        # Pydantic Query doesn't enforce cross-field constraints; do it here.
        from fastapi import HTTPException
        raise HTTPException(
            status_code=422,
            detail=f"year_start ({year_start}) must be <= year_end ({year_end})",
        )

    settings = get_settings()
    schema = settings.mart_schema

    sql = f"""
        SELECT
            city_code,
            MAX(city_name) AS city_name,
            MAX(province_code) AS province_code,
            COUNT(DISTINCT indicator_key) AS indicator_count,
            COUNT(*)                    AS points_count
        FROM {schema}.mart_city_timeseries
        WHERE year BETWEEN %s AND %s
        GROUP BY city_code
        ORDER BY city_code
    """
    with db.session() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (year_start, year_end))
            rows = cur.fetchall()

    return [
        CityTimeSeriesResponse(
            city_code=r[0],
            city_name=r[1],
            province_code=r[2],
            indicator_count=int(r[3]),
            year_range=(year_start, year_end),
            points_count=int(r[4]),
            points=[],
            pagination=Pagination(
                page=1,
                page_size=1,  # dummy: list endpoint returns summary only, not full points
                total_count=int(r[4]),
                has_next=False,
            ),
        )
        for r in rows
    ]


@router.get("/{city_code}", response_model=CityTimeSeriesResponse)
def get_city_timeseries(
    db: DatabaseDep,
    city_code: str = Path(
        ...,
        pattern=r"^[A-Z][A-Z0-9_]+$",
        description="City code (uppercase ASCII, must contain underscore). "
                    "E.g., GUANGDONG_SHENZHEN / JIANGSU_NANJING.",
    ),
    year_start: int = Query(
        default=DEFAULT_YEAR_START, ge=MIN_YEAR, le=MAX_YEAR,
        description="Inclusive lower bound year (2001-2026).",
    ),
    year_end: int = Query(
        default=DEFAULT_YEAR_END, ge=MIN_YEAR, le=MAX_YEAR,
        description="Inclusive upper bound year (2001-2026).",
    ),
) -> CityTimeSeriesResponse:
    """Return full time-series for one city in the requested year range.

    Returns 200 + (possibly empty) points when city_code has no rows in mart
    (e.g., NANTONG/WENZHOU have all-DATA_MISSING cells per 红线-3 禁补零).
    Returns 404 ONLY when city_code passes regex but has zero rows across
    ALL 7 years × 10 indicators (i.e., truly unknown city code, OR
    4 直辖市 excluded per 红线-7).

    Per-session READ ONLY enforced by Database.session().
    """
    if year_start > year_end:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=422,
            detail=f"year_start ({year_start}) must be <= year_end ({year_end})",
        )

    if not _CITY_CODE_RE.match(city_code):
        # Path-level pattern already filters; double-check for safety.
        raise ApiError(
            status_code=422,
            error_code="INVALID_CITY_CODE",
            message=f"Invalid city code format: {city_code}",
            detail={"resource": "city", "id": city_code},
        )

    settings = get_settings()
    schema = settings.mart_schema

    sql = f"""
        SELECT
            city_code,
            city_name,
            province_code,
            indicator_key,
            indicator_label,
            unit,
            year,
            value,
            status,
            missing_reason,
            lineage_source_type,
            lineage_origin,
            lineage_ruling,
            lineage_is_demo
        FROM {schema}.mart_city_timeseries
        WHERE city_code = %s
          AND year BETWEEN %s AND %s
        ORDER BY indicator_key, year
    """
    with db.session() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute(sql, (city_code, year_start, year_end))
                rows = cur.fetchall()
        except pg_errors.UndefinedTable as exc:
            # Mart not yet built (664 startup race condition); return 503 not 500.
            from fastapi import HTTPException
            raise HTTPException(
                status_code=503,
                detail=f"Mart table {schema}.mart_city_timeseries not built. Run dbt first.",
            ) from exc

    if not rows:
        # city_code passed regex but has zero rows in mart. Either truly unknown,
        # or excluded (4 直辖市 per 红线-7). Distinguish by querying mart for ANY row.
        with db.session() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"SELECT COUNT(*) FROM {schema}.mart_city_timeseries WHERE city_code = %s",
                    (city_code,),
                )
                total = cur.fetchone()[0]
        if total == 0:
            raise ResourceNotFound(
                resource="city",
                id=city_code,
            )

    points = [_row_to_point(r) for r in rows]
    city_name = points[0].city_name if points else None
    province_code = points[0].province_code if points else None
    return CityTimeSeriesResponse(
        city_code=city_code,
        city_name=city_name,
        province_code=province_code,
        indicator_count=10,
        year_range=(year_start, year_end),
        points_count=len(points),
        points=points,
        pagination=Pagination(
            page=1, page_size=len(points), total_count=len(points), has_next=False,
        ),
    )


def _row_to_point(row: tuple) -> CityTimeSeriesPoint:
    """Map raw row tuple (in SELECT order) to CityTimeSeriesPoint."""
    return CityTimeSeriesPoint(
        city_code=row[0],
        city_name=row[1],
        province_code=row[2],
        indicator_key=row[3],
        indicator_label=row[4],
        unit=row[5],
        year=int(row[6]),
        value=(float(row[7]) if row[7] is not None else None),
        status=row[8],
        missing_reason=row[9],
        lineage_source_type=row[10],
        lineage_origin=row[11],
        lineage_ruling=row[12],
        lineage_is_demo=row[13],
    )