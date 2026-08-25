"""Stage 1 / S1.10 — API route definitions."""
from china_platform.api.routes.health import router as health_router
from china_platform.api.routes.indicators import router as indicators_router
from china_platform.api.routes.observations import router as observations_router
from china_platform.api.routes.sources import router as sources_router

__all__ = [
    "health_router",
    "indicators_router",
    "observations_router",
    "sources_router",
]