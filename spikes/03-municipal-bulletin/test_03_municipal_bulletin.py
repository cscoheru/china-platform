#!/usr/bin/env python3
"""
test_extract.py — Spike 03 Municipal Bulletin Extraction (reworked per directive 五)

Tests now CALL the extractor and rebuild artifacts (not just read pre-baked JSON).
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).parent
REPO = HERE.parent.parent
SAMPLE_HTML = HERE / "sample.html"
EXTRACTOR = HERE / "extract_03_municipal_bulletin.py"
OUTPUT_DIR = REPO / "data" / "extracts" / "03-municipal-bulletin"
EXTRACTED = OUTPUT_DIR / "extracted.json"


def _run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, *cmd], cwd=str(REPO),
        capture_output=True, text=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        **kw,
    )


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


# ------------------------------------------------- Files exist

class TestFilesExist:
    def test_extractor_script_exists(self):
        assert EXTRACTOR.exists()

    def test_sample_html_exists(self):
        assert SAMPLE_HTML.exists()
        assert SAMPLE_HTML.stat().st_size > 0


# ------------------------------------------------- Real invocation (per directive 五)

class TestExtractorRuns:
    def test_extractor_runs_default_output(self):
        rc = _run([str(EXTRACTOR)])
        assert rc.returncode == 0, f"extractor failed: {rc.stderr}\n{rc.stdout}"
        assert EXTRACTED.exists()

    def test_extractor_runs_with_explicit_out(self, tmp_path):
        out = tmp_path / "out.json"
        rc = _run([str(EXTRACTOR), "--out", str(out)])
        assert rc.returncode == 0
        assert out.exists()

    def test_extractor_fails_when_input_missing(self, tmp_path):
        rc = _run([str(EXTRACTOR),
                   "--input", str(tmp_path / "nope.html"),
                   "--out", str(tmp_path / "should_not_exist.json")])
        assert rc.returncode != 0


# ------------------------------------------------- Fresh artifact fixture

@pytest.fixture(scope="module")
def fresh_extracted(tmp_path_factory):
    """Run extractor fresh into tmp dir, return parsed JSON."""
    tmp = tmp_path_factory.mktemp("spike03")
    out = tmp / "extracted.json"
    rc = _run([str(EXTRACTOR), "--out", str(out)])
    assert rc.returncode == 0
    return json.loads(out.read_text(encoding="utf-8"))


# ------------------------------------------------- Sample metadata

class TestSampleMetadata:
    def test_required_fields(self, fresh_extracted):
        sample = fresh_extracted["sample"]
        for f in ("city", "year", "source_url", "source_type",
                  "file_hash_sha256", "file_name", "file_size_bytes",
                  "fetched_at", "extraction_method"):
            assert f in sample, f"missing {f}"

    def test_city_is_shenzhen(self, fresh_extracted):
        assert fresh_extracted["sample"]["city"] == "深圳"

    def test_year_is_2024(self, fresh_extracted):
        assert fresh_extracted["sample"]["year"] == 2024

    def test_source_type_html(self, fresh_extracted):
        assert fresh_extracted["sample"]["source_type"] == "html"

    def test_source_url_valid(self, fresh_extracted):
        assert fresh_extracted["sample"]["source_url"].startswith("https://")

    def test_fetched_at_iso(self, fresh_extracted):
        ts = fresh_extracted["sample"]["fetched_at"]
        assert "T" in ts and ("+" in ts or "Z" in ts)


# ------------------------------------------------- Hash integrity

class TestHashIntegrity:
    def test_hash_matches_sample_html(self, fresh_extracted):
        expected = sha256_file(SAMPLE_HTML)
        assert fresh_extracted["sample"]["file_hash_sha256"] == expected

    def test_hash_is_valid_sha256(self, fresh_extracted):
        h = fresh_extracted["sample"]["file_hash_sha256"]
        assert len(h) == 64 and all(c in "0123456789abcdef" for c in h)


# ------------------------------------------------- Rows contract

class TestRows:
    def test_at_least_three_rows(self, fresh_extracted):
        assert len(fresh_extracted["rows"]) >= 3

    def test_rows_are_list(self, fresh_extracted):
        assert isinstance(fresh_extracted["rows"], list)

    def test_each_row_has_required_fields(self, fresh_extracted):
        required = ["indicator", "period", "value", "unit",
                    "context_quote", "source_url", "locator",
                    "extraction_method", "confidence"]
        for i, row in enumerate(fresh_extracted["rows"]):
            missing = [f for f in required if f not in row]
            assert not missing, f"Row {i} missing {missing}"

    def test_value_numeric(self, fresh_extracted):
        for i, row in enumerate(fresh_extracted["rows"]):
            v = row["value"]
            assert isinstance(v, (int, float)), f"Row {i} value={v!r}"

    def test_confidence_in_range(self, fresh_extracted):
        for i, row in enumerate(fresh_extracted["rows"]):
            assert 0.0 <= row["confidence"] <= 1.0, f"Row {i} confidence={row['confidence']}"

    def test_units_non_empty(self, fresh_extracted):
        for i, row in enumerate(fresh_extracted["rows"]):
            assert row.get("unit", ""), f"Row {i} unit empty"

    def test_context_quote_non_empty(self, fresh_extracted):
        for i, row in enumerate(fresh_extracted["rows"]):
            assert row.get("context_quote", ""), f"Row {i} context_quote empty — possible hallucination"

    def test_context_quote_length_reasonable(self, fresh_extracted):
        for i, row in enumerate(fresh_extracted["rows"]):
            q = row.get("context_quote", "")
            assert 5 <= len(q) <= 200, f"Row {i} context_quote len={len(q)}"

    def test_no_duplicate_indicators(self, fresh_extracted):
        names = [r["indicator"] for r in fresh_extracted["rows"]]
        assert len(names) == len(set(names)), f"Duplicate indicators: {names}"


# ------------------------------------------------- Indicator sanity (B-07: no tautologies)

class TestIndicatorSanity:
    def test_gdp_total_in_range(self, fresh_extracted):
        for row in fresh_extracted["rows"]:
            if row["indicator"] in ("地区生产总值(GDP)", "地区生产总值"):
                assert 20_000 < row["value"] < 50_000, f"GDP {row['value']} outside range"

    def test_population_in_range(self, fresh_extracted):
        for row in fresh_extracted["rows"]:
            if row["indicator"] == "常住人口":
                assert 1_000 < row["value"] < 2_500, f"Population {row['value']} outside range"

    def test_percentage_bounds(self, fresh_extracted):
        for row in fresh_extracted["rows"]:
            if row["unit"] == "%":
                assert -50 < row["value"] < 150, f"Percentage {row['value']} out of range"


# ------------------------------------------------- Determinism + no path hardcoding

class TestDeterminism:
    def test_two_runs_byte_identical(self, tmp_path):
        a = tmp_path / "a.json"
        b = tmp_path / "b.json"
        rc1 = _run([str(EXTRACTOR), "--out", str(a)])
        rc2 = _run([str(EXTRACTOR), "--out", str(b)])
        assert rc1.returncode == 0 and rc2.returncode == 0
        assert a.read_bytes() == b.read_bytes()

    def test_fetched_at_locked(self, fresh_extracted):
        """fetched_at 不应 datetime.now() 漂移。"""
        assert fresh_extracted["sample"]["fetched_at"].endswith("Z")


class TestNoPathHardcoding:
    def test_no_users_path_in_extractor(self):
        src = EXTRACTOR.read_text(encoding="utf-8")
        slash = chr(47)
        users_pat = slash + "Users" + slash
        assert users_pat not in src

    def test_no_users_path_in_test(self):
        src = Path(__file__).read_text(encoding="utf-8")
        slash = chr(47)
        users_pat = slash + "Users" + slash
        sentinel = chr(88) + "USERS" + chr(88)
        cleaned = src.replace(users_pat, sentinel)
        assert sentinel not in cleaned