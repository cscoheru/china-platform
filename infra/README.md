# infra/README.md

> Stage 1 / S1.1 — Local PostgreSQL 16 + PostGIS 3.x stack for CEGR data底座
>  任务书：`reviews/26-stage1-s11-postgresql-tasking-20260824.md` §1
>  规划：`docs/17-stage1-kickoff-plan-20260824.md` §1 (S1.1)

---

## §0. Why this file

Per Cursor 26 §1, Stage 1 needs a **reproducible** local PG16 + PostGIS stack so
that connectionor code (S1.4-S1.7) and Alembic migration chain (S1.2) run
against a known instance, not the Stage 0 test rig.

## §1. Up

```bash
# 1. copy env template (do NOT commit .env)
cp .env.example .env
# edit .env: set POSTGRES_PASSWORD to something dev-only

# 2. bring stack up
docker compose -f infra/docker-compose.yml --env-file .env.example up -d

# 3. healthcheck
docker compose -f infra/docker-compose.yml ps
# expect cegr_pg16_postgis (healthy)

# 4. probe PostGIS
PGPASSWORD=$POSTGRES_PASSWORD psql \
  -h 127.0.0.1 -p ${POSTGRES_PORT:-55440} \
  -U ${POSTGRES_USER:-postgres} \
  -d ${POSTGRES_DB:-cegr_test} \
  -c "SELECT PostGIS_Version();"
# expect: 3.4.x | ...
```

## §2. Schema apply chain (Stage 0 contract preserved)

The Stage 0 chain is **unchanged** — `tests/conftest.py` autouse session fixture
+ `scripts/build_evidence_pack.py::run_db_apply()` still
`DROP SCHEMA cegr CASCADE` + chain-apply `schema/01-core.sql` + `schema/migrations/*.sql`
directly with `psql`. Alembic (S1.2) lives alongside, not replacing, this chain
(per `docs/17` §2).

```bash
PGPASSWORD=$POSTGRES_PASSWORD psql -h 127.0.0.1 -p 55440 -U postgres -d cegr_test \
  -v ON_ERROR_STOP=1 -f schema/01-core.sql

PGPASSWORD=$POSTGRES_PASSWORD psql -h 127.0.0.1 -p 55440 -U postgres -d cegr_test \
  -v ON_ERROR_STOP=1 -f schema/migrations/002_source_governance.sql
```

Both must `exit 0`. The 39 `tests/test_schema_negative.py` + 21
`tests/test_source_governance.py` cases then run green.

## §3. Teardown

```bash
# Stop (data preserved in named volume cegr_pg16_data)
docker compose -f infra/docker-compose.yml down

# Nuke data
docker compose -f infra/docker-compose.yml down -v
docker volume rm cegr_pg16_data
```

## §4. Current local dev workaround

The CC dev box in 2026-08 does **not** have `docker` installed. To keep Stage 1
moving, we use the Stage 0 homebrew `postgresql@17` already running on
`127.0.0.1:55440` (per `docs/12` §9 clean-clone instructions). The
`infra/docker-compose.yml` here is still the canonical reproducibility contract;
it will be exercised by a teammate with Docker (per Cursor 27-wakeup §3
BLOCKED_BY_ENV).

## §5. Red lines

- ❌ Do NOT bind-mount production data into this container
- ❌ Do NOT publish port 55440 to anything but host loopback
- ❌ Do NOT commit `.env` (`.gitignore` already excludes)
- ❌ Do NOT change schema/01-core.sql content via this compose — chain lives
  in conftest.py + scripts/build_evidence_pack.py