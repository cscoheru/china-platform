"""Stage 1 / S1.10 — API settings (env var driven).

Per docs/24 §11.
"""
from __future__ import annotations

import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class ApiSettings(BaseSettings):
    """API server settings; all fields overridable via env vars."""

    dsn: str | None = None
    pool_min: int = 2
    pool_max: int = 10
    cors_origins: list[str] = ["http://localhost:3000"]
    log_level: str = "INFO"

    # S1.13.1 — /admin/upload 人工上传配置
    admin_upload_token: str | None = None  # Bearer token; 缺 → /admin/upload 返 503
    uploads_dir: str = "/tmp/cegr_uploads"  # 文件落盘目录
    max_upload_size_bytes: int = 100 * 1024 * 1024  # 默认 100 MB (per docs/28 §1.1)

    # P2 / knife 664 — mart schema name (env: CEGR_API_MART_SCHEMA)
    # Default 'cegr_mart' per docs/87 §3.2 + knife 663 mart schema.
    # Override for prod (e.g., 'cegr_prod_mart') without code changes.
    mart_schema: str = "cegr_mart"

    model_config = SettingsConfigDict(
        env_prefix="CEGR_API_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def resolved_dsn(self) -> str:
        """Resolve DSN with env var fallback chain.

        Priority: CEGR_API_DSN → CEGR_DSN → DATABASE_URL → dev default.
        Per docs/24 §4.1 + §11.
        """
        return (
            self.dsn
            or os.environ.get("CEGR_DSN")
            or os.environ.get("DATABASE_URL")
            or "postgresql://postgres:postgres@127.0.0.1:55440/cegr_test"
        )


_settings: ApiSettings | None = None


def get_settings() -> ApiSettings:
    """Singleton accessor; cached after first call."""
    global _settings
    if _settings is None:
        _settings = ApiSettings()
    return _settings