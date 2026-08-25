"""Stage 1 / S1.10 — FastAPI app factory + lifespan.

Per docs/24 §2 + §6.
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from china_platform.api.config import get_settings
from china_platform.api.db import Database
from china_platform.api.errors import install_error_handlers
from china_platform.api.routes.health import router as health_router
from china_platform.api.routes.indicators import router as indicators_router
from china_platform.api.routes.observations import router as observations_router
from china_platform.api.routes.sources import router as sources_router

log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Manage DB pool lifecycle (startup/shutdown)."""
    settings = get_settings()
    db = Database(
        dsn=settings.resolved_dsn(),
        min_conn=settings.pool_min,
        max_conn=settings.pool_max,
    )
    _app.state.db = db
    log.info("API startup complete (dsn=%s...)", settings.resolved_dsn()[:30])
    try:
        yield
    finally:
        db.close()
        log.info("API shutdown complete")


def create_app() -> FastAPI:
    """Build FastAPI app with routers + error handlers."""
    settings = get_settings()
    app = FastAPI(
        title="CEGR Read-only API",
        description=(
            "Stage 1 / S1.10 — Read-only query layer over cegr_staging dbt views. "
            "All endpoints enforce read-only at the database session level."
        ),
        version="0.1.0",
        lifespan=lifespan,
    )
    install_error_handlers(app)
    app.include_router(health_router)
    app.include_router(indicators_router)
    app.include_router(sources_router)
    app.include_router(observations_router)
    return app


# Module-level instance for `uvicorn china_platform.api.main:app`
app = create_app()