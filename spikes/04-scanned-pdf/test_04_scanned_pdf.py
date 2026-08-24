#!/usr/bin/env python3
"""Tests for spike 04: scanned-PDF extraction, truth table, evaluator.

Per directive 二-5: tests must CALL the extractor (not just read pre-generated
JSON), rebuild outputs from the real PDF, and FAIL (not skip) when the PDF,
tesseract, or extracted.json are missing. Per B-07: no tautologies.
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
EXTRACTOR = HERE / "extract_04_scanned_pdf.py"
EVALUATOR = HERE / "evaluate_04.py"
PROVENANCE = HERE / "provenance.json"
TRUTH_BUILDER = HERE / "build_truth_p24.py"
TRUTH = HERE / "truth_p24.json"
PDF = HERE / "statistical_abstract_foreign_countries_1909.pdf"
EXTRACTED = REPO / "data" / "extracts" / "04-scanned-pdf" / "extracted.json"
EVAL_REPORT = EXTRACTED.parent / "eval_report.json"


def _run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *cmd], cwd=str(REPO),
                          capture_output=True, text=True, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                          **kw)


# ---------------------------------------------------------- truth builder

class TestTruthTable:
    def test_builder_exists(self):
        assert TRUTH_BUILDER.exists()

    def test_truth_exists_and_validates(self):
        if not TRUTH.exists():
            subprocess.run([sys.executable, str(TRUTH_BUILDER)], cwd=str(REPO), check=True,
                           env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        d = json.loads(TRUTH.read_text(encoding="utf-8"))
        assert d["rows"] == 30
        assert d["page_pdf_1indexed"] == 24
        assert len(d["rows_data"]) == 30
        for r in d["rows_data"]:
            for k in ("gt_imports", "gt_exports", "gt_excess", "st_imports",
                     "st_exports", "st_excess", "gold_imports", "gold_exports",
                     "gold_excess", "silver_imports", "silver_exports",
                     "silver_excess", "gs_imports", "gs_exports", "gs_excess"):
                assert k in r, f"truth row missing key {k}"

    def test_rebuilds_without_truth_present(self, tmp_path):
        """Truth table is deterministically rebuildable from builder script."""
        tmp_truth = tmp_path / "t.json"
        builder_copy = tmp_path / "b.py"
        builder_copy.write_text(TRUTH_BUILDER.read_text(encoding="utf-8")
                                .replace('HERE / "truth_p24.json"', f'Path("{tmp_truth}")'))
        rc = subprocess.run([sys.executable, str(builder_copy)], capture_output=True, text=True)
        assert rc.returncode == 0, rc.stderr
        assert tmp_truth.exists()
        d = json.loads(tmp_truth.read_text(encoding="utf-8"))
        assert d["rows"] == 30 and len(d["rows_data"]) == 30

    def test_identity_violations_fail_build(self, tmp_path):
        """Builder refuses to write if an arithmetic identity is broken."""
        bad = tmp_path / "b.py"
        bad.write_text(TRUTH_BUILDER.read_text(encoding="utf-8").replace(
            '(1843, [229100, 191500, -37600,', '(1843, [229100, 191500, -99999,', 1)
        )
        rc = subprocess.run([sys.executable, str(bad)], capture_output=True, text=True)
        assert rc.returncode != 0, "builder should fail on broken identity"
        assert "identity violations" in rc.stdout


# ----------------------------------------------------- extractor end-to-end

class TestExtractor:
    # --- 一次抽取，多测试共享（写入 tmp_path，绝不动仓库真实 extracted.json）---
    @pytest.fixture(scope="class")
    def extracted_bytes(self, tmp_path_factory):
        """CLI --out 写入临时目录并返回原始字节。第 1 运行（determinism 基准）。"""
        out = tmp_path_factory.mktemp("ext04") / "extracted.json"
        rc = _run([str(EXTRACTOR), "--out", str(out)])
        assert rc.returncode == 0, f"extractor failed: {rc.stderr}\n{rc.stdout}"
        return out.read_bytes()

    @pytest.fixture(scope="class")
    def extracted(self, extracted_bytes):
        return json.loads(extracted_bytes)

    def test_extractor_exists(self):
        assert EXTRACTOR.exists()

    def test_extractor_runs_and_writes_output(self, tmp_path):
        """CLI --out 写入指定文件（tmp_path），而非仓库默认路径 DEFAULT_OUT。"""
        out = tmp_path / "out.json"
        rc = _run([str(EXTRACTOR), "--out", str(out)])
        assert rc.returncode == 0, f"extractor failed: {rc.stderr}\n{rc.stdout}"
        assert out.exists(), f"extractor did not write {out}"
        d = json.loads(out.read_text(encoding="utf-8"))
        assert d["sample"]["pdf_pages_total"] >= 24
        assert d["sample"]["target_page_pdf"] == 24
        assert len(d["rows"]) == 30 * 15

    def test_two_runs_produce_same_hash(self, extracted_bytes, tmp_path):
        """deterministic rebuild：另跑一次与 fixture 字节一致（跨运行稳定）。

        直接对比两次独立子进程的字节输出，证明算法在相同环境下可复现
        （B-07 / I-01 stable hash）。这比对比 committed artifact 更稳，
        不把测试绑死在特定 tesseract 版本上。
        """
        b = tmp_path / "b.json"
        rc = _run([str(EXTRACTOR), "--out", str(b)])
        assert rc.returncode == 0, rc.stderr
        assert b.read_bytes() == extracted_bytes, "两次抽取字节不一致 — 非 deterministic"

    def test_sample_key_contract(self, extracted):
        d = extracted
        for k in ("sample_id", "source_url", "source_file", "file_hash_sha256",
                  "pdf_pages_total", "target_page_pdf", "rows_detected",
                  "columns_detected", "observations", "extraction_method"):
            assert k in d["sample"], f"sample missing {k}"

    def test_obs_key_contract(self, extracted):
        d = extracted
        for obs in d["rows"]:
            for k in ("row_index", "year", "indicator", "column_key",
                     "group_l1", "group_l2", "leaf", "period", "value",
                     "raw_ocr", "unit", "source_url", "file_hash_sha256",
                     "table_locator", "page_pdf_1indexed", "needs_review",
                     "needs_review_reasons", "extraction_method"):
                assert k in obs, f"observation missing {k}"

    def test_extracted_sha_matches_provenance(self, extracted):
        d = extracted
        prov = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        assert d["sample"]["file_hash_sha256"] == prov["file_hash_sha256"]

    def test_geometry_detected_correctly(self, extracted):
        d = extracted
        assert d["sample"]["rows_detected"] == 30
        assert d["sample"]["columns_detected"] == 15
        # 15 column keys in printed order
        expected_keys = ["gt_imports", "gt_exports", "gt_excess",
                         "st_imports", "st_exports", "st_excess",
                         "gold_imports", "gold_exports", "gold_excess",
                         "silver_imports", "silver_exports", "silver_excess",
                         "gs_imports", "gs_exports", "gs_excess"]
        seen = [obs["column_key"] for obs in d["rows"][:15]]
        assert seen == expected_keys

    def test_needs_review_records_reasons(self, extracted):
        d = extracted
        for obs in d["rows"]:
            assert "needs_review" in obs
            assert isinstance(obs["needs_review_reasons"], list)
            if obs["needs_review"]:
                assert obs["needs_review_reasons"], "flagged obs must have a reason"

    def test_extracted_at_utc_is_locked(self, extracted):
        """extracted_at_utc 必须锁定，不存在 datetime.now() 漂移（B-07）。"""
        v = extracted["sample"]["extracted_at_utc"]
        assert v == "2026-08-23T06:00:00Z"
        assert v.endswith("Z") or "+00:00" in v

    def test_extractor_fails_when_pdf_missing(self, tmp_path):
        fake = tmp_path / "missing.pdf"
        rc = _run([str(EXTRACTOR), "--pdf", str(fake)])
        assert rc.returncode != 0
        assert "not found" in rc.stderr or "FATAL" in rc.stderr

    def test_extractor_fails_when_tesseract_missing(self, tmp_path):
        """Extractor aborts when tesseract is not on PATH (per directive 二-5 +
        R4-1: 不得 skip 后仍宣称 Gate 通过；缺工具必须 failed 非 0）。"""
        empty_path = tmp_path / "empty_bin"
        empty_path.mkdir()
        env = {k: v for k, v in os.environ.items()
               if k not in ("PATH", "Path")}
        env["PATH"] = str(empty_path)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        rc = subprocess.run(
            [sys.executable, str(EXTRACTOR),
             "--out", str(REPO / "data" / "should_not_exist.json")],
            cwd=str(REPO), capture_output=True, text=True, env=env,
        )
        assert rc.returncode != 0, "extractor should fail when tesseract is missing"
        assert "tesseract" in rc.stderr


# ----------------------------------------------------------- evaluator

class TestEvaluator:
    def test_evaluator_runs_and_writes_report(self, tmp_path):
        # 抽取写入 tmp，evaluator 把 eval_report 写到 --extracted 的父目录，
        # 因此都落在 tmp_path，绝不触碰仓库真实 extracted.json / eval_report.json。
        ext = tmp_path / "extracted.json"
        rc_ext = _run([str(EXTRACTOR), "--out", str(ext)])
        assert rc_ext.returncode == 0, rc_ext.stderr
        rc = _run([str(EVALUATOR), "--extracted", str(ext), "--truth", str(TRUTH)])
        assert rc.returncode == 0, rc.stderr
        report = ext.parent / "eval_report.json"
        assert report.exists(), f"evaluator did not write {report}"
        d = json.loads(report.read_text(encoding="utf-8"))
        for k in ("char_accuracy_pct", "numeric_cell_accuracy_pct",
                 "indicator_name_accuracy_pct", "unit_accuracy_pct",
                 "page_locator_accuracy_pct", "bbox_locator_accuracy_pct",
                 "needs_review_total", "needs_review_breakdown"):
            assert k in d
        assert d["matched_to_truth"] == 450
        assert d["observations_total"] == 450

    def test_evaluator_fails_when_truth_missing(self, tmp_path):
        rc = _run([str(EVALUATOR), "--truth", str(tmp_path / "nope.json")])
        assert rc.returncode != 0
        assert "FATAL" in rc.stderr

    def test_evaluator_fails_when_extracted_missing(self, tmp_path):
        rc = _run([str(EVALUATOR), "--extracted", str(tmp_path / "nope.json")])
        assert rc.returncode != 0
        assert "FATAL" in rc.stderr