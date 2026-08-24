#!/usr/bin/env python3
"""End-to-end tests for the non-gating Shaanxi Chinese OCR research track."""
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
PDF = HERE / "data" / "shaanxi_fiscal_regulation_flk.pdf"
PROVENANCE = HERE / "provenance.json"
TRUTH_BUILDER = HERE / "build_truth_shaanxi_flk.py"
EXTRACTOR = HERE / "extract_04_shaanxi_text.py"
EVALUATOR = HERE / "evaluate_04_shaanxi_text.py"
TRUTH = HERE / "truth_shaanxi_flk.json"
EXTRACTED = REPO / "data" / "extracts" / "04-scanned-pdf" / "shaanxi_text_ocr.json"
EVAL_REPORT = EXTRACTED.parent / "shaanxi_text_eval_report.json"
SAMPLE_KEY = "shaanxi_fiscal_regulation_flk"


def run_script(arguments: list[str], *, env: dict[str, str] | None = None):
    command_env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    if env is not None:
        command_env = env
    return subprocess.run(
        [sys.executable, *arguments],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        env=command_env,
    )


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture(scope="module")
def rebuilt_truth(tmp_path_factory) -> Path:
    output = tmp_path_factory.mktemp("shaanxi_truth") / "truth.json"
    result = run_script([str(TRUTH_BUILDER), "--out", str(output)])
    assert result.returncode == 0, result.stderr
    return output


@pytest.fixture(scope="module")
def fresh_extracted(tmp_path_factory) -> Path:
    output = tmp_path_factory.mktemp("shaanxi_ocr") / "extracted.json"
    result = run_script([str(EXTRACTOR), "--out", str(output)])
    assert result.returncode == 0, result.stderr
    return output


@pytest.fixture(scope="module")
def fresh_report(tmp_path_factory, rebuilt_truth, fresh_extracted) -> Path:
    output = tmp_path_factory.mktemp("shaanxi_eval") / "report.json"
    result = run_script(
        [
            str(EVALUATOR),
            "--truth",
            str(rebuilt_truth),
            "--extracted",
            str(fresh_extracted),
            "--out",
            str(output),
        ]
    )
    assert result.returncode == 0, result.stderr
    return output


class TestShaanxiSource:
    def test_pdf_and_origin_are_pinned(self):
        provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        sample = provenance["research_samples"][SAMPLE_KEY]
        assert PDF.read_bytes().startswith(b"%PDF-1.4")
        assert PDF.stat().st_size == 1007943
        assert sha256_file(PDF) == sample["file_hash_sha256"]
        assert sample["source_url"].startswith("https://wb.flk.npc.gov.cn/")
        assert sample["acquisition"]["http_status_observed_by_cc"] is None

    def test_license_scope_is_not_overclaimed(self):
        sample = json.loads(PROVENANCE.read_text(encoding="utf-8"))[
            "research_samples"
        ][SAMPLE_KEY]
        assert "Article-5-Legal-Text" in sample["license"]["classification"]
        assert "No blanket public-domain" in sample["license"]["scope_limit"]
        assert sample["metrics_policy"]["stage0_effect"] == "none_per_U3"


class TestShaanxiTruth:
    def test_truth_rebuild_is_byte_deterministic(self, rebuilt_truth, tmp_path):
        second = tmp_path / "truth-second.json"
        result = run_script([str(TRUTH_BUILDER), "--out", str(second)])
        assert result.returncode == 0, result.stderr
        assert rebuilt_truth.read_bytes() == second.read_bytes()
        assert rebuilt_truth.read_bytes() == TRUTH.read_bytes()

    def test_truth_uses_accepted_embedded_layer(self, rebuilt_truth):
        truth = json.loads(rebuilt_truth.read_text(encoding="utf-8"))
        assert truth["reference"]["type"] == "embedded_pdf_text_layer_accepted_by_U2"
        assert truth["reference"]["text_sha256"] == (
            "cec93b67f8da16ecdd97b7e08ab2baf23995f2e61530afff3f1d6295dfdfc0bf"
        )
        assert truth["reference"]["han_characters"] == 3230
        assert truth["pages_total"] == 4
        assert truth["layout_canonicalization"]["method"].startswith(
            "robust_content_bounds_midpoint"
        )
        assert truth["pages"][0]["layout"]["divider_x_points"] == 200.67
        assert truth["pages"][0]["layout"]["physical_midpoint_x_points"] == 226.62
        assert all(
            page["layout"]["crossing_word_policy"]
            == "assign_by_bbox_center_and_report"
            for page in truth["pages"]
        )

    def test_reference_noise_is_preserved_not_silently_corrected(self, rebuilt_truth):
        truth = json.loads(rebuilt_truth.read_text(encoding="utf-8"))
        text = "".join(
            line
            for page in truth["pages"]
            for region in page["regions"]
            for line in region["canonical_lines"]
        )
        assert "预箅" in text
        assert "本行畋区域" in text
        assert "税产业发展项" not in text
        assert "时候,由本级人民政府向人会作预箅草案决定" not in text


class TestShaanxiExtractor:
    def test_extractor_reads_images_only(self, fresh_extracted):
        extracted = json.loads(fresh_extracted.read_text(encoding="utf-8"))
        assert extracted["extraction"]["input"] == "rendered_scanned_page_images_only"
        assert extracted["extraction"]["embedded_text_layer_used"] is False
        assert extracted["extraction"]["tesseract_language"] == "chi_sim"
        assert extracted["extraction"]["page_segmentation_mode"] == 6
        assert extracted["toolchain"]["tesseract_language_data"] == {
            "filename": "chi_sim.traineddata",
            "sha256": "a5fcb6f0db1e1d6d8522f39db4e848f05984669172e584e8d76b6b3141e1f730",
            "size_bytes": 2469156,
        }
        assert len(extracted["pages"]) == 4
        assert all("layout" in page for page in extracted["pages"])

    def test_two_ocr_runs_are_byte_deterministic(self, fresh_extracted, tmp_path):
        second = tmp_path / "ocr-second.json"
        result = run_script([str(EXTRACTOR), "--out", str(second)])
        assert result.returncode == 0, result.stderr
        assert fresh_extracted.read_bytes() == second.read_bytes()
        assert fresh_extracted.read_bytes() == EXTRACTED.read_bytes()

    def test_ocr_does_not_copy_known_reference_errors(self, fresh_extracted):
        extracted = json.loads(fresh_extracted.read_text(encoding="utf-8"))
        text = "".join(
            line
            for page in extracted["pages"]
            for region in page["regions"]
            for line in region["canonical_lines"]
        )
        assert "预算" in text
        assert "本行政区域" in text

    def test_missing_pdf_fails(self, tmp_path):
        result = run_script(
            [str(EXTRACTOR), "--pdf", str(tmp_path / "missing.pdf"), "--out", str(tmp_path / "x.json")]
        )
        assert result.returncode != 0
        assert "PDF not found" in result.stderr

    def test_missing_tesseract_fails_not_skips(self, tmp_path):
        binary_dir = tmp_path / "bin"
        binary_dir.mkdir()
        for executable in ("pdfinfo", "pdftoppm"):
            os.symlink(shutil.which(executable), binary_dir / executable)
        env = {**os.environ, "PATH": str(binary_dir), "PYTHONDONTWRITEBYTECODE": "1"}
        result = run_script(
            [str(EXTRACTOR), "--out", str(tmp_path / "x.json")], env=env
        )
        assert result.returncode != 0
        assert "tesseract" in result.stderr


class TestShaanxiEvaluator:
    def test_metrics_and_non_gating_contract(self, fresh_report, tmp_path):
        report = json.loads(fresh_report.read_text(encoding="utf-8"))
        assert report["char_accuracy_pct"] == 93.93
        assert report["all_non_whitespace_char_accuracy_pct"] == 90.05
        assert report["numeric_cell_accuracy_pct"] is None
        assert report["numeric_metric_status"] == "not_applicable_non_tabular_source"
        assert report["needs_review_pages"] == [1]
        assert report["needs_review_pct"] == 25.0
        assessment = report["threshold_assessment"]
        assert assessment["threshold_values_unchanged"] is True
        assert assessment["needs_review_definition"] == (
            "page_han_accuracy_below_char_accuracy_min_pct"
        )
        assert assessment["needs_review_scope"].startswith("shaanxi_research_page_triage")
        assert assessment["applicable_thresholds_all_met"] is True
        assert assessment["research_track_result"] == (
            "MEETS_UNCHANGED_APPLICABLE_THRESHOLDS"
        )
        assert report["stage0_effect"] == "none_per_U3_non_gating_research_sample"
        assert report["stage0_verdict"] == "not_determined_by_this_report_user_U4_required"
        rebuilt_committed_inputs = tmp_path / "report-from-committed-inputs.json"
        result = run_script([str(EVALUATOR), "--out", str(rebuilt_committed_inputs)])
        assert result.returncode == 0, result.stderr
        assert rebuilt_committed_inputs.read_bytes() == EVAL_REPORT.read_bytes()

    def test_reference_limitation_is_machine_readable(self, fresh_report):
        report = json.loads(fresh_report.read_text(encoding="utf-8"))
        assert "not human-corrected ground truth" in report["reference"]["known_limitation"]
        assert report["reference"]["accepted_policy"] == "U2"

    def test_commands_with_temp_outputs_do_not_rewrite_repository_artifacts(self, tmp_path):
        tracked_outputs = (TRUTH, EXTRACTED, EVAL_REPORT)
        before = {path: sha256_file(path) for path in tracked_outputs}
        truth = tmp_path / "truth.json"
        extracted = tmp_path / "extracted.json"
        report = tmp_path / "report.json"
        assert run_script([str(TRUTH_BUILDER), "--out", str(truth)]).returncode == 0
        assert run_script([str(EXTRACTOR), "--out", str(extracted)]).returncode == 0
        assert run_script(
            [str(EVALUATOR), "--truth", str(truth), "--extracted", str(extracted), "--out", str(report)]
        ).returncode == 0
        assert {path: sha256_file(path) for path in tracked_outputs} == before

    def test_missing_inputs_fail(self, tmp_path):
        missing = tmp_path / "missing.json"
        result = run_script(
            [str(EVALUATOR), "--truth", str(missing), "--out", str(tmp_path / "report.json")]
        )
        assert result.returncode != 0
        assert "FATAL" in result.stderr
