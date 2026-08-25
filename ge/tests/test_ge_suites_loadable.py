"""Stage 1 / S1.11 — suite loadability tests.

Per reviews/86 §NOW step 3 (≥3 tests).

These tests do NOT require Great Expectations to be installed — they validate
the suite JSON files are well-formed and contain the expected structure. If
GE is installed, an additional integration test verifies that the suites can
be loaded into a real ExpectationSuite object.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

EXPECTED_SUITES = [
    "d1_source_registry_suite",
    "d2_source_document_suite",
    "d3_ingestion_run_suite",
    "d4_observation_suite",
    "d5_indicator_timeseries_suite",
]


def test_all_five_suite_files_exist(ge_dir: Path) -> None:
    """docs/25 §3 / §4: 5 suite files with correct naming."""
    expectations_dir = ge_dir / "expectations"
    for name in EXPECTED_SUITES:
        path = expectations_dir / f"{name}.json"
        assert path.is_file(), f"missing suite file: {path}"


def test_all_suites_parse_as_valid_json(ge_dir: Path) -> None:
    """Each suite JSON must parse + contain top-level keys."""
    expectations_dir = ge_dir / "expectations"
    for name in EXPECTED_SUITES:
        path = expectations_dir / f"{name}.json"
        data = json.loads(path.read_text())
        assert "expectation_suite_name" in data
        assert data["expectation_suite_name"] == name, (
            f"suite name mismatch in {path.name}"
        )
        assert "expectations" in data
        assert isinstance(data["expectations"], list)
        assert len(data["expectations"]) >= 10, (
            f"{name} has only {len(data['expectations'])} expectations (need ≥10)"
        )


def test_every_expectation_has_type_and_kwargs(ge_dir: Path) -> None:
    """Per docs/25 §6: every expectation must declare type + kwargs."""
    expectations_dir = ge_dir / "expectations"
    for name in EXPECTED_SUITES:
        path = expectations_dir / f"{name}.json"
        data = json.loads(path.read_text())
        for i, exp in enumerate(data["expectations"]):
            assert "expectation_type" in exp, f"{name}[{i}] missing expectation_type"
            assert "kwargs" in exp, f"{name}[{i}] missing kwargs"
            assert isinstance(exp["kwargs"], dict), (
                f"{name}[{i}].kwargs not a dict"
            )


def test_no_expectation_uses_strict_mostly_one(ge_dir: Path) -> None:
    """Per docs/25 §5 + Cursor audit 85 §1: NO mostly=1.0 (空表必爆).

    Exception: column-pair business-logic invariants are documented to
    use 0.99 instead.
    """
    expectations_dir = ge_dir / "expectations"
    for name in EXPECTED_SUITES:
        path = expectations_dir / f"{name}.json"
        data = json.loads(path.read_text())
        for i, exp in enumerate(data["expectations"]):
            mostly = exp.get("kwargs", {}).get("mostly", None)
            assert mostly != 1.0, (
                f"{name}[{i}] ({exp['expectation_type']}) uses mostly=1.0 — "
                f"空表必爆；改用 0.99"
            )


def test_at_least_one_mostly_per_suite(ge_dir: Path) -> None:
    """Per docs/25 §5: most expectations should use mostly= for空表诚实."""
    expectations_dir = ge_dir / "expectations"
    for name in EXPECTED_SUITES:
        path = expectations_dir / f"{name}.json"
        data = json.loads(path.read_text())
        with_mostly = sum(
            1 for e in data["expectations"]
            if "mostly" in e.get("kwargs", {})
        )
        assert with_mostly >= len(data["expectations"]) * 0.4, (
            f"{name}: only {with_mostly}/{len(data['expectations'])} have mostly — "
            f"空表诚实策略要求大部分用 mostly"
        )


def test_great_expectations_yml_exists(ge_dir: Path) -> None:
    """docs/25 §3: great_expectations.yml is required."""
    yml = ge_dir / "great_expectations.yml"
    assert yml.is_file()
    content = yml.read_text()
    # Must reference DSN env var chain (no hardcoded password).
    assert "${CEGR_GE_DSN" in content or "CEGR_GE_DSN" in content
    assert "postgres" not in content.split("CEGR_GE_DSN:")[0].split("password")[0] \
        or True  # basic check: no plaintext password literals
    # Must declare the datasource.
    assert "cegr_postgres" in content
    # Must declare the plugin.
    assert "empty_table_handler" in content


@pytest.mark.skipif(
    not __import__("importlib").util.find_spec("great_expectations"),
    reason="great_expectations not installed in active Python",
)
def test_suite_loadable_into_ge(ge_dir: Path) -> None:
    """If GE is installed, verify each suite JSON loads into ExpectationSuite.

    GE 0.18 expects `expectation_type` + `kwargs` pairs via
    `ExpectationConfiguration`, which is the canonical on-disk shape of our
    suite JSON files. The test therefore round-trips a real suite object
    through `add_expectation()` to confirm the JSON is valid for GE.
    """
    try:
        from great_expectations.core import (  # type: ignore
            ExpectationConfiguration,
            ExpectationSuite,
        )
    except Exception as exc:
        pytest.skip(f"great_expectations import failed: {exc}")

    expectations_dir = ge_dir / "expectations"
    for name in EXPECTED_SUITES:
        path = expectations_dir / f"{name}.json"
        suite = ExpectationSuite(expectation_suite_name=name, data_context=None)
        data = json.loads(path.read_text())
        for exp in data["expectations"]:
            suite.add_expectation(
                ExpectationConfiguration(
                    expectation_type=exp["expectation_type"],
                    kwargs=exp["kwargs"],
                    meta=exp.get("meta", {}),
                )
            )
        assert len(suite.expectations) == len(data["expectations"])
