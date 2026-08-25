"""Stage 1 / S1.10 — custom exceptions + handlers.

Per docs/24 §7.
"""
from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

log = logging.getLogger(__name__)


class ApiError(Exception):
    """Base API error with HTTP status + error code."""

    def __init__(
        self,
        status_code: int,
        error_code: str,
        message: str,
        detail: dict | None = None,
    ) -> None:
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
        self.detail = detail
        super().__init__(message)


class ResourceNotFound(ApiError):
    """404 — resource with given id not found."""

    def __init__(self, resource: str, id: str) -> None:
        super().__init__(
            status_code=404,
            error_code=f"{resource.upper()}_NOT_FOUND",
            message=f"{resource} with id={id} not found",
            detail={"resource": resource, "id": str(id)},
        )


class DatabaseUnavailable(ApiError):
    """503 — DB connection failed or pool exhausted."""

    def __init__(self, reason: str) -> None:
        super().__init__(
            status_code=503,
            error_code="DB_UNAVAILABLE",
            message="Database connection failed",
            detail={"reason": reason},
        )


def api_error_handler(_request: Request, exc: ApiError) -> JSONResponse:
    """FastAPI exception handler for ApiError."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": exc.error_code,
            "message": exc.message,
            "detail": exc.detail,
        },
    )


def install_error_handlers(app: FastAPI) -> None:
    """Register exception handlers on FastAPI app."""
    app.add_exception_handler(ApiError, api_error_handler)