"""placeholder_001

Stage 1 / S1.2 — alembic placeholder for schema/01-core.sql
Canonical DDL lives in schema/01-core.sql; this alembic revision is an empty
history marker only (per docs/17-stage1-kickoff-plan-20260824.md §2).

Revision ID: cegr001
Revises:
Create Date: 2026-08-24
"""

# revision identifiers, used by Alembic.
revision = "cegr001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Empty by design — schema/01-core.sql owns the canonical DDL.
    # tests/conftest.py autouse session fixture applies schema/* via psql
    # before pytest collection; see docs/17 §2.
    pass


def downgrade() -> None:
    pass