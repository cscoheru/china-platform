"""Stage 1 / S1.10 — /health endpoint."""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter

from china_platform.api.deps import DatabaseDep
from china_platform.api.models.common import HealthCheck

router = APIRouter(prefix="", tags=["health"])


@router.get("/health", response_model=HealthCheck)
def health(db: DatabaseDep) -> HealthCheck:
    """Liveness + DB reachability check.

    Always returns 200 with status payload; callers can branch on db_reachable.
    """
    return HealthCheck(
        status="ok",
        db_reachable=db.is_alive,
        timestamp_utc=datetime.now(timezone.utc),
    )