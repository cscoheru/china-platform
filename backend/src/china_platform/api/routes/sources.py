"""Stage 1 / S1.10 — Source endpoints.

Per docs/24 §6.3:
  GET /api/source                      — list
  GET /api/source/{id}                 — single (404 if missing)
  GET /api/source/{id}/coverage        — coverage stats
  GET /api/source/{id}/runs            — recent ingestion runs
"""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Path, Query

from china_platform.api.deps import DatabaseDep
from china_platform.api.errors import ResourceNotFound
from china_platform.api.models.common import Pagination
from china_platform.api.models.source import (
    SourceCoverage,
    SourceListItem,
    SourceListResponse,
    SourceRun,
    SourceRunsResponse,
)

router = APIRouter(prefix="/api/source", tags=["source"])


@router.get("", response_model=SourceListResponse)
def list_sources(
    db: DatabaseDep,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=500),
    enabled_only: bool = Query(default=False),
) -> SourceListResponse:
    """List sources from stg_source_registry."""
    where = "WHERE enabled = TRUE" if enabled_only else ""
    with db.session() as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) FROM cegr_staging.stg_source_registry {where}")
            total_count = cur.fetchone()[0]
            cur.execute(
                f"""
                SELECT source_id, domain, organization, category, source_level, enabled
                FROM cegr_staging.stg_source_registry
                {where}
                ORDER BY domain, organization
                LIMIT %s OFFSET %s
                """,
                (page_size, (page - 1) * page_size),
            )
            rows = cur.fetchall()
    items = [
        SourceListItem(
            source_id=r[0],
            domain=r[1],
            organization=r[2],
            category=r[3],
            source_level=r[4],
            enabled=r[5],
        )
        for r in rows
    ]
    return SourceListResponse(
        sources=items,
        pagination=Pagination(
            page=page,
            page_size=page_size,
            total_count=total_count,
            has_next=(page * page_size) < total_count,
        ),
    )


@router.get("/{source_id}", response_model=SourceListItem)
def get_source(
    db: DatabaseDep,
    source_id: UUID = Path(...),
) -> SourceListItem:
    """Get one source by id. 404 if not found."""
    with db.session() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT source_id, domain, organization, category, source_level, enabled
                FROM cegr_staging.stg_source_registry
                WHERE source_id = %s
                """,
                (str(source_id),),
            )
            row = cur.fetchone()
    if row is None:
        raise ResourceNotFound(resource="source", id=str(source_id))
    return SourceListItem(
        source_id=row[0],
        domain=row[1],
        organization=row[2],
        category=row[3],
        source_level=row[4],
        enabled=row[5],
    )


@router.get("/{source_id}/coverage", response_model=SourceCoverage)
def get_source_coverage(
    db: DatabaseDep,
    source_id: UUID = Path(...),
) -> SourceCoverage:
    """Coverage + quality stats from int_source_coverage."""
    with db.session() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    source_id, domain, category, source_level, enabled,
                    total_runs, success_runs, failure_runs, failure_rate,
                    total_extracted, total_inserted, overall_insertion_pct,
                    avg_quality_score, low_confidence_count,
                    missing_with_reason_count, total_observations, last_run_at
                FROM cegr_staging.int_source_coverage
                WHERE source_id = %s
                """,
                (str(source_id),),
            )
            row = cur.fetchone()
            if row is None:
                cur.execute(
                    "SELECT 1 FROM cegr_staging.stg_source_registry WHERE source_id = %s",
                    (str(source_id),),
                )
                if cur.fetchone() is None:
                    raise ResourceNotFound(resource="source", id=str(source_id))
                row = (str(source_id), None, None, None, None, 0, 0, 0, 0.0, 0, 0, None, None, 0, 0, 0, None)
    return SourceCoverage(
        source_id=row[0],
        domain=row[1] or "",
        category=row[2] or "",
        source_level=row[3] or "",
        enabled=bool(row[4]) if row[4] is not None else False,
        total_runs=row[5],
        success_runs=row[6],
        failure_runs=row[7],
        failure_rate=float(row[8]) if row[8] is not None else 0.0,
        total_extracted=row[9] or 0,
        total_inserted=row[10] or 0,
        overall_insertion_pct=(float(row[11]) if row[11] is not None else None),
        avg_quality_score=(float(row[12]) if row[12] is not None else None),
        low_confidence_count=row[13] or 0,
        missing_with_reason_count=row[14] or 0,
        total_observations=row[15] or 0,
        last_run_at=row[16],
    )


@router.get("/{source_id}/runs", response_model=SourceRunsResponse)
def get_source_runs(
    db: DatabaseDep,
    source_id: UUID = Path(...),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=200),
) -> SourceRunsResponse:
    """Recent ingestion runs for a source (from stg_ingestion_run)."""
    with db.session() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM cegr_staging.stg_source_registry WHERE source_id = %s",
                (str(source_id),),
            )
            if cur.fetchone() is None:
                raise ResourceNotFound(resource="source", id=str(source_id))
            cur.execute(
                """
                SELECT
                    run_id, status, started_at, finished_at, duration_seconds,
                    records_extracted, records_inserted, is_stale
                FROM cegr_staging.stg_ingestion_run
                WHERE source_id = %s
                ORDER BY started_at DESC
                LIMIT %s OFFSET %s
                """,
                (str(source_id), page_size, (page - 1) * page_size),
            )
            rows = cur.fetchall()
            cur.execute(
                "SELECT COUNT(*) FROM cegr_staging.stg_ingestion_run WHERE source_id = %s",
                (str(source_id),),
            )
            total = cur.fetchone()[0]
    runs = [
        SourceRun(
            run_id=r[0],
            status=r[1],
            started_at=r[2],
            finished_at=r[3],
            duration_seconds=(float(r[4]) if r[4] is not None else None),
            records_extracted=r[5],
            records_inserted=r[6],
            is_stale=bool(r[7]) if r[7] is not None else False,
        )
        for r in rows
    ]
    return SourceRunsResponse(
        source_id=source_id,
        runs=runs,
        pagination=Pagination(
            page=page,
            page_size=page_size,
            total_count=total,
            has_next=(page * page_size) < total,
        ),
    )