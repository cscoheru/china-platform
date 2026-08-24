"""
Spike 01 tests: validate extracted JSON structure AND that extractor is callable.

Per directive 五 (R2-6): tests must CALL the implementation, not just read
pre-baked extracted.json. Also no tautologies — every assertion is meaningful
about real extractor behavior.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).parent
REPO = HERE.parent.parent
SAMPLE_HTML = HERE / "sample.html"
EXTRACTOR = HERE / "extract_01_national_yearbook.py"
EXTRACTED = REPO / "data" / "extracts" / "01-national-yearbook" / "extracted.json"

REQUIRED_ROW_FIELDS = {
    "indicator", "period", "value", "unit", "source_url",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, *cmd], cwd=str(REPO),
        capture_output=True, text=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        **kw,
    )


# ------------------------------------------------- Extractor must exist

class TestExtractorExists:
    def test_extractor_script_exists(self):
        assert EXTRACTOR.exists(), f"Extractor missing: {EXTRACTOR}"

    def test_sample_html_exists(self):
        assert SAMPLE_HTML.exists()
        assert SAMPLE_HTML.stat().st_size > 0


# ------------------------------------------------- Real invocation (per 指令五)

class TestExtractorRuns:
    """Tests must CALL the extractor and verify it produces the artifact."""

    def test_extractor_runs_and_writes_output(self, tmp_path):
        out = tmp_path / "extracted.json"
        rc = _run([str(EXTRACTOR), "--out", str(out)])
        assert rc.returncode == 0, f"extractor failed: stderr={rc.stderr}\nstdout={rc.stdout}"
        assert out.exists()
        data = json.loads(out.read_text(encoding="utf-8"))
        assert "sample" in data and "rows" in data

    def test_extractor_runs_default_output(self):
        rc = _run([str(EXTRACTOR)])
        assert rc.returncode == 0, rc.stderr
        assert EXTRACTED.exists()

    def test_extractor_fails_when_sample_missing(self, tmp_path):
        rc = _run([str(EXTRACTOR), "--input", str(tmp_path / "nope.html"),
                   "--out", str(tmp_path / "should_not_exist.json")])
        assert rc.returncode != 0
        assert not (tmp_path / "should_not_exist.json").exists()


# ------------------------------------------------- artifact check (after fresh run)

@pytest.fixture(scope="module")
def fresh_extracted(tmp_path_factory):
    """Run extractor fresh into tmp dir, return parsed JSON + sha."""
    tmp = tmp_path_factory.mktemp("spike01")
    out = tmp / "extracted.json"
    rc = _run([str(EXTRACTOR), "--out", str(out)])
    assert rc.returncode == 0
    return json.loads(out.read_text(encoding="utf-8")), sha256_file(out)


class TestExtractedArtifact:
    def test_artifact_has_sample(self, fresh_extracted):
        data, _ = fresh_extracted
        assert "sample" in data
        assert "rows" in data

    def test_hash_matches_sample_html(self, fresh_extracted):
        data, _ = fresh_extracted
        stored_hash = data["sample"]["file_hash_sha256"]
        actual_hash = sha256_file(SAMPLE_HTML)
        assert stored_hash == actual_hash

    def test_source_url_is_nbs(self, fresh_extracted):
        data, _ = fresh_extracted
        assert data["sample"]["source_url"].startswith("https://www.stats.gov.cn")

    def test_source_type_html(self, fresh_extracted):
        data, _ = fresh_extracted
        assert data["sample"]["source_type"] == "html"

    def test_fetched_at_iso(self, fresh_extracted):
        data, _ = fresh_extracted
        ts = data["sample"]["fetched_at"]
        assert "T" in ts and ("+" in ts or "Z" in ts)

    def test_at_least_3_rows(self, fresh_extracted):
        data, _ = fresh_extracted
        assert len(data["rows"]) >= 3

    def test_all_rows_have_required_fields(self, fresh_extracted):
        data, _ = fresh_extracted
        for i, row in enumerate(data["rows"]):
            missing = REQUIRED_ROW_FIELDS - set(row.keys())
            assert not missing, f"Row {i} missing {missing}"

    def test_unit_non_empty(self, fresh_extracted):
        data, _ = fresh_extracted
        for i, row in enumerate(data["rows"]):
            assert row.get("unit", ""), f"Row {i} unit empty"

    def test_values_numeric_or_null(self, fresh_extracted):
        data, _ = fresh_extracted
        for i, row in enumerate(data["rows"]):
            v = row.get("value")
            assert v is None or isinstance(v, (int, float)), f"Row {i} value={v!r}"

    def test_indicator_non_empty_string(self, fresh_extracted):
        data, _ = fresh_extracted
        for i, row in enumerate(data["rows"]):
            ind = row.get("indicator", "")
            assert isinstance(ind, str) and ind, f"Row {i} indicator={ind!r}"

    def test_period_iso_like(self, fresh_extracted):
        data, _ = fresh_extracted
        for i, row in enumerate(data["rows"]):
            p = row.get("period", "")
            assert p and len(p) >= 7, f"Row {i} period too short: {p}"

    def test_confidence_in_range(self, fresh_extracted):
        data, _ = fresh_extracted
        for i, row in enumerate(data["rows"]):
            c = row.get("confidence", -1)
            assert 0.0 <= c <= 1.0, f"Row {i} confidence={c}"


# ------------------------------------------------- determinism + no path hardcoding

class TestDeterminism:
    def test_two_runs_byte_identical(self, tmp_path):
        """Same input → byte-identical output (no datetime.now() drift)."""
        a = tmp_path / "a.json"
        b = tmp_path / "b.json"
        rc1 = _run([str(EXTRACTOR), "--out", str(a)])
        rc2 = _run([str(EXTRACTOR), "--out", str(b)])
        assert rc1.returncode == 0 and rc2.returncode == 0
        assert a.read_bytes() == b.read_bytes()


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


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))