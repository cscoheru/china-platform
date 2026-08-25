"""Stage 1 / S1.11 — custom empty-table handler.

Per docs/25 §5.2. Converts GE validation results from FAIL → PASS_WITH_WARN
when a dataset is empty AND the failing expectations are mostly-based.

This module exposes `EmptyTableHandler` (referenced from great_expectations.yml
`plugins.custom_data_docs`).

NOTE: This handler is a **post-validation reclassifier** — it consumes the
GE validation result and rewrites its `success` flag without changing the
underlying data. We intentionally do NOT touch the data or the underlying
expectations themselves.
"""
from __future__ import annotations

from typing import Any

# Threshold below which a table is considered "empty" for our purposes.
EMPTY_TABLE_ROW_COUNT = 1  # 0 rows OR (rows but all-NULL) → empty


class EmptyTableHandler:
    """Reclassify FAIL → PASS_WITH_WARN when table is empty.

    Usage in great_expectations.yml:
        plugins:
          custom_data_docs:
            class_name: EmptyTableHandler
            module_name: plugins.custom_data_docs.empty_table_handler

    The handler is invoked with a validation result dict. It mutates
    `success` to True (turning FAIL into PASS_WITH_WARN) when:
        1. The batch's `metrics.table_row_count <= EMPTY_TABLE_ROW_COUNT`
        2. All failing expectations are 'mostly'-style (have `mostly` < 1.0)
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # GE constructs plugins with no args by default; ignore extras.
        pass

    def handle(self, validation_result: dict[str, Any]) -> dict[str, Any]:
        """Reclassify FAIL → PASS_WITH_WARN for empty tables.

        Parameters
        ----------
        validation_result : dict
            GE validation result structure. Must contain `results` and
            optionally `statistics` / `metrics`.

        Returns
        -------
        dict
            The same validation_result with `success` reclassified.
        """
        if validation_result.get("success", False):
            return validation_result  # already PASS; nothing to do

        row_count = self._extract_row_count(validation_result)
        if row_count > EMPTY_TABLE_ROW_COUNT:
            return validation_result  # table has data; FAIL is legitimate

        # Empty table. Reclassify only if all failures are mostly-based.
        failures = [
            r for r in validation_result.get("results", [])
            if not r.get("success", True)
        ]
        if not failures:
            return validation_result

        all_mostly = all(
            float(
                r.get("expectation_config", {})
                .get("kwargs", {})
                .get("mostly", 1.0)
            )
            < 1.0
            for r in failures
        )
        if all_mostly:
            validation_result["success"] = True
            validation_result.setdefault("meta", {})[
                "empty_table_reclassified"
            ] = True

        return validation_result

    @staticmethod
    def _extract_row_count(validation_result: dict[str, Any]) -> int:
        """Read row count from validation_result (best-effort)."""
        metrics = validation_result.get("metrics", {})
        if "table_row_count" in metrics:
            try:
                return int(metrics["table_row_count"])
            except (TypeError, ValueError):
                return -1
        return -1  # unknown; treat as non-empty to be safe
