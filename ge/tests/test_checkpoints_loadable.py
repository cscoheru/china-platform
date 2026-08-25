"""Stage 1 / S1.11 — checkpoint YAML loadability tests.

Per reviews/86 §NOW step 3 (≥2 tests).
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml


def test_ci_checkpoint_exists(ge_dir: Path) -> None:
    path = ge_dir / "checkpoints" / "ci_checkpoint.yml"
    assert path.is_file(), f"missing checkpoint: {path}"


def test_dev_checkpoint_exists(ge_dir: Path) -> None:
    path = ge_dir / "checkpoints" / "dev_checkpoint.yml"
    assert path.is_file(), f"missing checkpoint: {path}"


def test_ci_checkpoint_parses_and_has_5_validations(ge_dir: Path) -> None:
    path = ge_dir / "checkpoints" / "ci_checkpoint.yml"
    data = yaml.safe_load(path.read_text())
    assert data["name"] == "ci_checkpoint"
    assert isinstance(data["validations"], list)
    assert len(data["validations"]) == 5, (
        f"ci_checkpoint must validate 5 suites, got {len(data['validations'])}"
    )
    suite_names = {v["expectation_suite_name"] for v in data["validations"]}
    assert suite_names == {
        "d1_source_registry_suite",
        "d2_source_document_suite",
        "d3_ingestion_run_suite",
        "d4_observation_suite",
        "d5_indicator_timeseries_suite",
    }


def test_dev_checkpoint_parses_and_targets_d4(ge_dir: Path) -> None:
    path = ge_dir / "checkpoints" / "dev_checkpoint.yml"
    data = yaml.safe_load(path.read_text())
    assert data["name"] == "dev_checkpoint"
    assert len(data["validations"]) >= 1
    suites = {v["expectation_suite_name"] for v in data["validations"]}
    assert "d4_observation_suite" in suites


def test_checkpoints_reference_correct_data_assets(ge_dir: Path) -> None:
    """Each validation must target a cegr_staging.* asset (per docs/25 §2)."""
    ci = yaml.safe_load((ge_dir / "checkpoints" / "ci_checkpoint.yml").read_text())
    expected_assets = {
        "d1_source_registry_suite": "cegr_staging.stg_source_registry",
        "d2_source_document_suite": "cegr_staging.stg_source_document",
        "d3_ingestion_run_suite": "cegr_staging.stg_ingestion_run",
        "d4_observation_suite": "cegr_staging.stg_observation",
        "d5_indicator_timeseries_suite": "cegr_staging.int_indicator_timeseries",
    }
    for v in ci["validations"]:
        suite = v["expectation_suite_name"]
        asset = v["batch_request"]["data_asset_name"]
        assert asset == expected_assets[suite], (
            f"{suite}: expected {expected_assets[suite]}, got {asset}"
        )


def test_ge_run_script_is_executable(ge_dir: Path) -> None:
    script = ge_dir / "scripts" / "ge_run.sh"
    assert script.is_file()
    import os
    import stat

    mode = script.stat().st_mode
    assert mode & stat.S_IXUSR, "ge_run.sh must be executable for the user"
