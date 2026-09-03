# backend/Dockerfile — China Platform FastAPI (knife 664h)
#
# Per docs/24 §11 + knife 664 plan.
# python:3.12-slim: Pydantic 2.10 + FastAPI 0.115 stable; psycopg2-binary 2.9 wheels
# built for cp312-cp312-manylinux_2_17_x86_64. Avoid 3.14 (dbt parser incompatibility).
#
# Build:   docker build --no-cache -t china-platform-backend:0.2.0 -f backend/Dockerfile backend
# Push:     docker push <registry>/china-platform-backend:0.2.0  (架构师端不主动 push)
# Run:     docker run --rm --network puer-net -p 8001:8000 \
#            -e CEGR_API_DSN=postgresql://... china-platform-backend:0.2.0
#
# Multi-stage: deps layer cached separately from source — fast incremental builds.

FROM python:3.12-slim AS deps

# System deps for psycopg2 wheels + uvicorn [standard] (uvloop, httptools, websockets).
# libpq5: psycopg2-binary runtime (avoids needing postgresql-dev).
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
        ca-certificates \
        curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Pin to specific versions; cache layer independently of source.
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt


FROM deps AS runtime

# Copy source. pyc files excluded via .dockerignore.
COPY src /app/src

# Run as non-root user (UID 10001 matches china-platform-pg postgres user).
RUN useradd --create-home --uid 10001 --shell /usr/sbin/nologin app \
    && chown -R app:app /app
USER app

# CEGR_API_* env vars drive config (see china_platform.api.config.ApiSettings).
# Required in production:
#   CEGR_API_DSN        postgresql://user:pass@host:5432/cegr_test
#   CEGR_API_MART_SCHEMA  cegr_mart  (default)
# Optional:
#   CEGR_API_POOL_MIN    2 (default)
#   CEGR_API_POOL_MAX    10 (default)
#   CEGR_API_LOG_LEVEL   INFO (default)
#   CEGR_API_CORS_ORIGINS  http://localhost:3000 (default)

ENV PYTHONPATH=/app/src \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

EXPOSE 8000

# uvicorn entrypoint; --proxy-headers enables X-Forwarded-* from nginx.
# --workers 2: dev single-cpu; prod scale via docker compose --scale api=N.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -fsS http://127.0.0.1:8000/health || exit 1

CMD ["uvicorn", "china_platform.api.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--proxy-headers"]