"""Stage 1 / S1.11 — pytest config for GE tests.

Adds `ge/` to sys.path so `import plugins.custom_data_docs.empty_table_handler`
resolves without packaging. Also resolves GE's `great_expectations.yml` from
the ge/ directory.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

GE_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = GE_DIR.parent

if str(GE_DIR) not in sys.path:
    sys.path.insert(0, str(GE_DIR))


@pytest.fixture(scope="session")
def ge_dir() -> Path:
    return GE_DIR


@pytest.fixture(scope="session")
def dsn() -> str:
    import os

    return os.environ.get(
        "CEGR_GE_DSN",
        "postgresql://postgres:postgres@127.0.0.1:55440/cegr_test",
    )
