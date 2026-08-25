"""Stage 1 / S1.10 — FastAPI dependencies.

Per docs/24 §6.3 (Depends(get_db)).
"""
from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Request

from china_platform.api.db import Database


def get_db(request: Request) -> Database:
    """FastAPI dependency: retrieve Database from app.state."""
    return request.app.state.db


DatabaseDep = Annotated[Database, Depends(get_db)]