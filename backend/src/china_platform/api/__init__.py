"""Stage 1 / S1.10 — FastAPI readonly query layer.

Per docs/24-stage1-s10-fastapi-readonly-plan-20260825.md.
"""
from china_platform.api.config import ApiSettings
from china_platform.api.main import app, create_app

__all__ = ["app", "create_app", "ApiSettings"]