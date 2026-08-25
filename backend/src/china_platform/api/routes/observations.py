"""Stage 1 / S1.10 — Observation endpoints.

Per docs/24 §6.4:
  GET /api/observation             — paginated list (filterable)
  GET /api/observation/{id}        — single observation (404 if missing)
"""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Path, Query

from china_platform.api.deps import DatabaseDep
from china_platform.api.errors import ResourceNotFound
from china_platform.api.models.common import Pagination
from china_platform.api.models.observation import (
    ObservationItem,
    ObservationListResponse,
)

router = APIRouter(prefix="/api/observation", tags=["observation"])


@router.get("", response_model=ObservationListResponse)
def list_observations(
    db: DatabaseDep,
    indicator_id: UUID | None = Query(default=None),
    geo_entity_id: UUID | None = Query(default=None),
    source_id: UUID | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=500),
) -> ObservationListResponse:
    """Paginated observation list (FACT only).

    Optional filters: indicator_id, geo_entity_id, source_id.
    """
    wheres: list[str] = []
    params: list = []
    if indicator_id is not None:
        wheres.append("indicator_id = %s")
        params.append(str(indicator_id))
    if geo_entity_id is not None:
        wheres.append("geo_entity_id = %s")
        params.append(str(geo_entity_id))
    if source_id is not None:
        wheres.append("source_id = %s")
        params.append(str(source_id))
    where_clause = ("WHERE " + " AND ".join(wheres)) if wheres else ""

    with db.session() as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) FROM cegr_staging.stg_observation {where_clause}", params)
            total_count = cur.fetchone()[0]
            cur.execute(
                f"""
                SELECT
                    observation_id, indicator_id, geo_entity_id,
                    calendar_period_id, value, unit, confidence,
                    source_id, period_start, period_type, extracted_at
                FROM cegr_staging.stg_observation
                {where_clause}
                ORDER BY period_start DESC NULLS LAST, observation_id
                LIMIT %s OFFSET %s
                """,
                params + [page_size, (page - 1) * page_size],
            )
            rows = cur.fetchall()

    items = [
        ObservationItem(
            observation_id=r[0],
            indicator_id=r[1],
            geo_entity_id=r[2],
            calendar_period_id=r[3],
            value=(float(r[4]) if r[4] is not None else None),
            unit=r[5],
            confidence=(float(r[6]) if r[6] is not None else None),
            source_id=r[7],
            period_start=r[8],
            period_type=r[9],
            extracted_at=r[10],
        )
        for r in rows
    ]
    return ObservationListResponse(
        observations=items,
        pagination=Pagination(
            page=page,
            page_size=page_size,
            total_count=total_count,
            has_next=(page * page_size) < total_count,
        ),
    )


@router.get("/{observation_id}", response_model=ObservationItem)
def get_observation(
    db: DatabaseDep,
    observation_id: UUID = Path(...),
) -> ObservationItem:
    """Get one observation by id. 404 if not found."""
    with db.session() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    observation_id, indicator_id, geo_entity_id,
                    calendar_period_id, value, unit, confidence,
                    source_id, period_start, period_type, extracted_at
                FROM cegr_staging.stg_observation
                WHERE observation_id = %s
                """,
                (str(observation_id),),
            )
            row = cur.fetchone()
    if row is None:
        raise ResourceNotFound(resource="observation", id=str(observation_id))
    return ObservationItem(
        observation_id=row[0],
        indicator_id=row[1],
        geo_entity_id=row[2],
        calendar_period_id=row[3],
        value=(float(row[4]) if row[4] is not None else None),
        unit=row[5],
        confidence=(float(row[6]) if row[6] is not None else None),
        source_id=row[7],
        period_start=row[8],
        period_type=row[9],
        extracted_at=row[10],
    )