"""placeholder_002

Stage 1 / S1.2 — alembic placeholder for schema/migrations/002_source_governance.sql
Canonical DDL lives in schema/migrations/002_source_governance.sql; this
alembic revision is an empty history marker only (per docs/17 §2).

`alembic_version.version_num` is stamped to this revision (HEAD); `alembic
upgrade head` is therefore a no-op against an already-applied stack.

Revision ID: cegr002
Revises: cegr001
Create Date: 2026-08-24
"""

# revision identifiers, used by Alembic.
revision = "cegr002"
down_revision = "cegr001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Empty by design — schema/migrations/002_source_governance.sql owns the
    # canonical DDL; see docs/17-stage1-kickoff-plan-20260824.md §2.
    pass


def downgrade() -> None:
    pass