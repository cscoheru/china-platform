"""P2 / knife 664 — Province time-series endpoints.

Per docs/87 §3.2 P2 数据扩展 + knife 664 plan.
Source of truth: cegr_mart.mart_province_timeseries (dbt mart, knife 663).

Routes:
  GET /api/province-timeseries                    — list all 31 provinces
  GET /api/province-timeseries/{province_code}    — single province full series (year range filtered)

Year range validation (FastAPI Pydantic Query):
  - year_start: 2001-2026, default 2020
  - year_end:   2001-2026, default 2025
  - year_start <= year_end enforced by Pydantic ge/le
  - requested year range must include 2020-2025 (mart coverage) or be explicitly bounded

Province code format: ^[A-Z][A-Z0-9_]*$ (e.g., BEIJING / SHANGHAI / NEI_MENGGU).
NATIONAL row available post-665 (knife 665 harvest).

Per-session READ ONLY enforced by Database.session() (knife 660 inherited).
"""
from __future__ import annotations

import re

from fastapi import APIRouter, Path, Query
from psycopg2 import errors as pg_errors

from china_platform.api.config import get_settings
from china_platform.api.deps import DatabaseDep
from china_platform.api.errors import ApiError, ResourceNotFound
from china_platform.api.models.common import Pagination
from china_platform.api.models.province_timeseries import (
    ProvinceTimeSeriesPoint,
    ProvinceTimeSeriesResponse,
)

router = APIRouter(prefix="/api/province-timeseries", tags=["province-timeseries"])

# Province code regex: uppercase letters / digits / underscore, must start with letter.
# Examples: BEIJING / SHANGHAI / NEI_MENGGU / XINJIANG. NATIONAL accepted (post-665).
_PROVINCE_CODE_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")

# Mart coverage: 663 ships 2020-2025 (per knife 660 batch + 665 harvest target).
# 2001-2019 + 2026 explicitly DATA_MISSING (新增红线-1/2).
DEFAULT_YEAR_START = 2020
DEFAULT_YEAR_END = 2025
MIN_YEAR = 2001
MAX_YEAR = 2026


@router.get("", response_model=list[ProvinceTimeSeriesResponse])
def list_province_timeseries(
    db: DatabaseDep,
    year_start: int = Query(
        default=DEFAULT_YEAR_START, ge=MIN_YEAR, le=MAX_YEAR,
        description="Inclusive lower bound year (2001-2026).",
    ),
    year_end: int = Query(
        default=DEFAULT_YEAR_END, ge=MIN_YEAR, le=MAX_YEAR,
        description="Inclusive upper bound year (2001-2026).",
    ),
) -> list[ProvinceTimeSeriesResponse]:
    """Return per-province summary (one row per province_code) for the requested year range.

    Lightweight summary — does NOT return full point list (use the per-province route).
    Useful for navigation/listing UIs (e.g., /timeseries page province selector).
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
            province_code,
            MAX(province_name) AS province_name,
            COUNT(DISTINCT indicator_key) AS indicator_count,
            COUNT(*)                    AS points_count
        FROM {schema}.mart_province_timeseries
        WHERE year BETWEEN %s AND %s
        GROUP BY province_code
        ORDER BY province_code
    """
    with db.session() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (year_start, year_end))
            rows = cur.fetchall()

    return [
        ProvinceTimeSeriesResponse(
            province_code=r[0],
            province_name=r[1],
            indicator_count=int(r[2]),
            year_range=(year_start, year_end),
            points_count=int(r[3]),
            points=[],
            pagination=Pagination(
                page=1,
                page_size=1,  # dummy: list endpoint returns summary only, not full points
                total_count=int(r[3]),
                has_next=False,
            ),
        )
        for r in rows
    ]


@router.get("/{province_code}", response_model=ProvinceTimeSeriesResponse)
def get_province_timeseries(
    db: DatabaseDep,
    province_code: str = Path(
        ...,
        pattern=r"^[A-Z][A-Z0-9_]*$",
        description="Province code (uppercase ASCII). E.g., BEIJING / SHANGHAI / NATIONAL.",
    ),
    year_start: int = Query(
        default=DEFAULT_YEAR_START, ge=MIN_YEAR, le=MAX_YEAR,
        description="Inclusive lower bound year (2001-2026).",
    ),
    year_end: int = Query(
        default=DEFAULT_YEAR_END, ge=MIN_YEAR, le=MAX_YEAR,
        description="Inclusive upper bound year (2001-2026).",
    ),
) -> ProvinceTimeSeriesResponse:
    """Return full time-series for one province in the requested year range.

    Returns 200 + (possibly empty) points when province_code has no rows in mart
    (e.g., LIAONING / HAINAN / GUIZHOU have all-DATA_MISSING cells per knife 660 红线).
    Returns 404 ONLY when province_code passes regex but has zero rows across
    ALL 26 years × 10 indicators (i.e., truly unknown province code).

    Note: mart contains ALL 32 rows (31 provinces × 26 years × 10 indicators = 8060),
    so a missing province_code means it's NOT a recognized 31-province code.

    Per-session READ ONLY enforced by Database.session().
    """
    if year_start > year_end:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=422,
            detail=f"year_start ({year_start}) must be <= year_end ({year_end})",
        )

    if not _PROVINCE_CODE_RE.match(province_code):
        # Path-level pattern already filters; double-check for safety.
        raise ApiError(
            status_code=422,
            error_code="INVALID_PROVINCE_CODE",
            message=f"Invalid province code format: {province_code}",
            detail={"resource": "province", "id": province_code},
        )

    settings = get_settings()
    schema = settings.mart_schema

    sql = f"""
        SELECT
            province_code,
            province_name,
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
        FROM {schema}.mart_province_timeseries
        WHERE province_code = %s
          AND year BETWEEN %s AND %s
        ORDER BY indicator_key, year
    """
    with db.session() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute(sql, (province_code, year_start, year_end))
                rows = cur.fetchall()
        except pg_errors.UndefinedTable as exc:
            # Mart not yet built (664 startup race condition); return 503 not 500.
            from fastapi import HTTPException
            raise HTTPException(
                status_code=503,
                detail=f"Mart table {schema}.mart_province_timeseries not built. Run dbt first.",
            ) from exc

    if not rows:
        # Province code passed regex but has zero rows in mart. Either truly unknown,
        # or mart is missing this row. Distinguish by querying mart for ANY row for this code.
        with db.session() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"SELECT COUNT(*) FROM {schema}.mart_province_timeseries WHERE province_code = %s",
                    (province_code,),
                )
                total = cur.fetchone()[0]
        if total == 0:
            raise ResourceNotFound(
                resource="province",
                id=province_code,
            )

    points = [_row_to_point(r) for r in rows]
    province_name = points[0].province_name if points else None
    return ProvinceTimeSeriesResponse(
        province_code=province_code,
        province_name=province_name,
        indicator_count=10,
        year_range=(year_start, year_end),
        points_count=len(points),
        points=points,
        pagination=Pagination(
            page=1, page_size=len(points), total_count=len(points), has_next=False,
        ),
    )


def _row_to_point(row: tuple) -> ProvinceTimeSeriesPoint:
    """Map raw row tuple (in SELECT order) to ProvinceTimeSeriesPoint."""
    return ProvinceTimeSeriesPoint(
        province_code=row[0],
        province_name=row[1],
        indicator_key=row[2],
        indicator_label=row[3],
        unit=row[4],
        year=int(row[5]),
        value=(float(row[6]) if row[6] is not None else None),
        status=row[7],
        missing_reason=row[8],
        lineage_source_type=row[9],
        lineage_origin=row[10],
        lineage_ruling=row[11],
        lineage_is_demo=row[12],
    )