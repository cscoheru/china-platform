"""placeholder_003

Stage 1 / S1.3 — alembic placeholder for schema/migrations/003_source_registry_declared_level.sql
Canonical DDL lives in schema/migrations/003_source_registry_declared_level.sql; this
alembic revision is an empty history marker only (per docs/17 §2).

Adds columns:
  source_registry.source_level, source_registry.declared_source_level,
  source_registry.local_sample_path, source_registry.file_hash_sha256,
  source_registry.file_size_bytes, source_registry.purpose_note

Revision ID: cegr003
Revises: cegr002
Create Date: 2026-08-24
"""

# revision identifiers, used by Alembic.
revision = "cegr003"
down_revision = "cegr002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Empty by design — schema/migrations/003_source_registry_declared_level.sql
    # owns the canonical DDL; see docs/17-stage1-kickoff-plan-20260824.md §2.
    pass


def downgrade() -> None:
    pass