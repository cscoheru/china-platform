"""placeholder_004

Stage 1 / S1.6 — alembic placeholder for schema/migrations/004_observation_period_lineage.sql
Canonical DDL lives in schema/migrations/004_observation_period_lineage.sql; this
alembic revision is an empty history marker only (per docs/17 §2 pattern).

Adds columns to cegr.observation:
  observation.period_start   DATE  NULL
  observation.period_end     DATE  NULL
  observation.period_label   TEXT  NULL
  observation.period_type    TEXT  NULL
  observation.lineage        JSONB NULL
  observation.caveat_text    TEXT  NULL

Plus:
  CHECK observation_period_range (date ordering sanity, NOT VALID then VALIDATED)
  INDEX idx_observation_period_range  (period_start, period_end)
  INDEX idx_observation_period_type   (period_type)
  INDEX idx_observation_lineage_gin   (GIN on lineage)

Per Cursor 50 §SCHEMA (Stage 1 / S1.6 省级年鉴连接器实现任务书):
  * B-06 per-indicator period metadata
  * R3-E per-row lineage chain
  * Red line: period_type is TEXT (not ENUM) so future period_type values
    can be added without migration churn; no DEFAULT forcing single value.

Revision ID: cegr004
Revises: cegr003
Create Date: 2026-08-25
"""

# revision identifiers, used by Alembic.
revision = "cegr004"
down_revision = "cegr003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Empty by design — schema/migrations/004_observation_period_lineage.sql
    # owns the canonical DDL; see docs/20-stage1-s16-provincial-yearbook-plan-20260824.md
    # §3 + Cursor 50 §SCHEMA.
    pass


def downgrade() -> None:
    pass