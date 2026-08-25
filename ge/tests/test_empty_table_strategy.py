"""Stage 1 / S1.11 — empty-table strategy tests.

Per docs/25 §5 + reviews/86 §NOW step 3 (≥3 tests).

Validates the EmptyTableHandler reclassification logic in isolation (no GE
runtime required).
"""
from __future__ import annotations

import pytest

from plugins.custom_data_docs.empty_table_handler import (
    EMPTY_TABLE_ROW_COUNT,
    EmptyTableHandler,
)


def _make_result(success: bool, *, row_count: int | None = None) -> dict:
    return {
        "success": success,
        "metrics": {} if row_count is None else {"table_row_count": row_count},
        "results": [],
    }


def _make_failing_result(
    mostly: float, *, row_count: int = 0
) -> dict:
    return {
        "success": False,
        "metrics": {"table_row_count": row_count},
        "results": [
            {
                "success": False,
                "expectation_config": {
                    "kwargs": {"mostly": mostly},
                },
            }
        ],
    }


def test_passing_result_unchanged() -> None:
    handler = EmptyTableHandler()
    result = _make_result(success=True, row_count=5)
    out = handler.handle(result)
    assert out["success"] is True
    assert "empty_table_reclassified" not in out.get("meta", {})


def test_empty_table_with_mostly_failures_reclassified_to_pass() -> None:
    handler = EmptyTableHandler()
    result = _make_failing_result(mostly=0.99, row_count=0)
    out = handler.handle(result)
    assert out["success"] is True
    assert out.get("meta", {}).get("empty_table_reclassified") is True


def test_nonempty_table_failures_not_reclassified() -> None:
    """Per docs/25 §5: FAIL only for non-empty tables (legitimate data issue)."""
    handler = EmptyTableHandler()
    result = _make_failing_result(mostly=0.99, row_count=100)
    out = handler.handle(result)
    assert out["success"] is False
    assert "empty_table_reclassified" not in out.get("meta", {})


def test_empty_table_with_strict_mostly_one_not_reclassified() -> None:
    """Strict mostly=1.0 is a 红色 (per docs/25 §5.1); even empty table fails."""
    handler = EmptyTableHandler()
    result = _make_failing_result(mostly=1.0, row_count=0)
    out = handler.handle(result)
    assert out["success"] is False


def test_empty_table_threshold_constant() -> None:
    """Constant is documented at EMPTY_TABLE_ROW_COUNT=1.

    Per docs/25 §5.1: row_count <= 1 triggers empty-table reclassification.
    """
    assert EMPTY_TABLE_ROW_COUNT == 1


def test_handler_ignores_extra_constructor_args() -> None:
    """GE constructs plugins without args; we accept kwargs gracefully."""
    handler = EmptyTableHandler(extra_arg="ignored", another=42)
    assert handler is not None
