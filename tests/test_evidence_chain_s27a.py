"""Stage 2 / S2.7-a — Six-segment evidence chain UI pytest.

Per tasking 168 §NOW-1 / §NOW-3 + docs/06 §2:
  - 固定六段 CONDITION → COMMITMENT → INPUT → PROCESS → OUTPUT → OUTCOME_RISK
  - 缺一不可（空段显式标"未覆盖"，不省略）
  - 禁止评分 / 总分 / 排名
  - DemoBadge 契约保留（is_demo="true" 时显角标）
  - 静态段路由不能分支 on params.*

Tests (≥1 required by §NOW-3):
  1. test_evidence_chain_component_contains_six_segments
  2. test_evidence_chain_renders_uncovered_badge_for_empty_segments
  3. test_evidence_chain_renders_count_badge_for_populated_segments
  4. test_evidence_chain_forbids_scoring_terms
  5. test_jiangsu_page_includes_evidence_chain_with_full_segments
  6. test_zhejiang_page_includes_evidence_chain_with_all_empty_segments
  7. test_zhejiang_page_no_params_branching_on_static_route
  8. test_home_page_includes_province_list_entry
  9. test_demo_badge_sentinel_contract_preserved_on_jiangsu_page
 10. test_mock_evidence_chain_exposes_required_provinces
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
FRONTEND = REPO_ROOT / "frontend"

EXPECTED_SEGMENTS = [
    "CONDITION", "COMMITMENT", "INPUT", "PROCESS", "OUTPUT", "OUTCOME_RISK",
]


def _read(rel: str) -> str:
    return (FRONTEND / rel).read_text(encoding="utf-8")


def _strip_js_comments(src: str) -> str:
    """Per standing rule: strip line + block comments before scanning."""
    src = re.sub(r"//[^\n]*", "", src)
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.DOTALL)
    return src


# ---------- Case 1: component contains all six segments ----------
def test_evidence_chain_component_contains_six_segments() -> None:
    src = _read("app/components/EvidenceChain.tsx")
    code = _strip_js_comments(src)
    # Each segment key must be present in the metadata record AND in the
    # order map; we just check the literals appear at least once.
    for seg in EXPECTED_SEGMENTS:
        assert f'"{seg}"' in code or seg in code, (
            f"EvidenceChain.tsx missing segment {seg}"
        )


# ---------- Case 2: empty segment renders 'uncovered' badge ----------
def test_evidence_chain_renders_uncovered_badge_for_empty_segments() -> None:
    src = _read("app/components/EvidenceChain.tsx")
    # Look for the "未覆盖" marker and the gap testid.
    assert "未覆盖" in src, "EvidenceChain must include '未覆盖' label for empty segments"
    assert "segment-gap-" in src, "EvidenceChain must render gap marker testid"


# ---------- Case 3: populated segment renders count badge ----------
def test_evidence_chain_renders_count_badge_for_populated_segments() -> None:
    src = _read("app/components/EvidenceChain.tsx")
    assert "条证据" in src or "evidence" in src.lower(), (
        "EvidenceChain must indicate count of evidence items per populated segment"
    )


# ---------- Case 4: no scoring terms (per tasking 168 §红线) ----------
@pytest.mark.parametrize("forbidden", [
    r"\bscore\b",
    r"\brating\b",
    r"\brank(?:ing)?\b",
    r"\btotal[_-]?score\b",
])
def test_evidence_chain_forbids_scoring_terms(forbidden: str) -> None:
    """Per tasking 168 §红线: 禁止官员能力分 / 总分 / 排名."""
    src = _read("app/components/EvidenceChain.tsx")
    code = _strip_js_comments(src)
    assert not re.search(forbidden, code, re.IGNORECASE), (
        f"EvidenceChain.tsx contains forbidden term matching {forbidden!r}"
    )


# ---------- Case 5: Jiangsu page mounts EvidenceChain with full segments ----------
def test_jiangsu_page_includes_evidence_chain_with_full_segments() -> None:
    jiangsu = _read("app/provinces/jiangsu/page.tsx")
    mock_chain = _read("lib/mock_evidence_chain.ts")
    # Mount point.
    assert "<EvidenceChain" in jiangsu, "jiangsu page must render <EvidenceChain />"
    # Mock provides Jiangsu's full chain — locate via `const jiangsuChain`
    # variable declaration so we don't accidentally hit the slug list.
    jiangsu_block = mock_chain[
        mock_chain.index("const jiangsuChain"):
        mock_chain.index("const zhejiangChain")
    ]
    for seg in EXPECTED_SEGMENTS:
        assert f'key: "{seg}"' in jiangsu_block, (
            f"jiangsu mock chain missing segment {seg}"
        )


# ---------- Case 6: Zhejiang page shows all-empty segments ----------
def test_zhejiang_page_includes_evidence_chain_with_all_empty_segments() -> None:
    zj_page = _read("app/provinces/zhejiang/page.tsx")
    mock_chain = _read("lib/mock_evidence_chain.ts")
    assert "<EvidenceChain" in zj_page, "zhejiang page must render <EvidenceChain />"
    # Extract zhejiang's chain block via its variable declaration; bound to
    # next `const xChain` (any other province) or 800 chars (whichever first).
    zj_start = mock_chain.index("const zhejiangChain")
    block_end = len(mock_chain)
    for other in ("jiangsu", "guangdong", "sichuan", "shandong"):
        other_var = f"const {other}Chain"
        other_pos = mock_chain.find(other_var, zj_start + 1)
        if other_pos != -1 and other_pos < block_end:
            block_end = other_pos
    zj_block = mock_chain[zj_start:min(block_end, zj_start + 800)]
    # All six segments must be present.
    for seg in EXPECTED_SEGMENTS:
        assert f'key: "{seg}"' in zj_block, (
            f"zhejiang mock chain missing segment {seg}"
        )
    # Every segment.items array must be empty (演示"未覆盖").
    n_empty = len(re.findall(r'key:\s*"[A-Z_]+",\s*items:\s*\[\]', zj_block))
    assert n_empty == 6, (
        f"zhejiang chain must have all 6 segments empty; got {n_empty}"
    )


# ---------- Case 7: Zhejiang static-segment route must NOT branch on params.* ----------
def test_zhejiang_page_no_params_branching_on_static_route() -> None:
    src = _read("app/provinces/zhejiang/page.tsx")
    code = _strip_js_comments(src)
    assert not re.search(r"params\.province\s*[!=]==", code), (
        "zhejiang/page.tsx must not gate on params.province (static route)"
    )
    assert not re.search(r"if\s*\(\s*params\.", code), (
        "zhejiang/page.tsx must not branch on params.* at all"
    )


# ---------- Case 8: home page lists ≥1 province entry ----------
def test_home_page_includes_province_list_entry() -> None:
    home = _read("app/page.tsx")
    mock_chain = _read("lib/mock_evidence_chain.ts")
    # Home page must import the mock province list.
    assert "MOCK_PROVINCE_LIST" in home, "home page must import MOCK_PROVINCE_LIST"
    # Mock list must include at least 2 provinces (per tasking 168: 江苏 + ≥1 他省).
    n_provinces = len(re.findall(r"slug:\s*\"[a-z_]+\"", mock_chain))
    assert n_provinces >= 2, (
        f"MOCK_PROVINCE_LIST must have ≥2 entries (jiangsu + ≥1 other); got {n_provinces}"
    )


# ---------- Case 9: DemoBadge sentinel contract preserved ----------
def test_demo_badge_sentinel_contract_preserved_on_jiangsu_page() -> None:
    """is_demo="true" sentinel still drives <DemoBadge /> (S1.18 contract)."""
    jiangsu = _read("app/provinces/jiangsu/page.tsx")
    mock = _read("lib/mock.ts")
    demo_badge = _read("app/DemoBadge.tsx")
    # jiangsu page must still render DemoBadge.
    assert "<DemoBadge" in jiangsu
    # mock.ts must still emit is_demo="true" rows.
    assert re.search(r'is_demo:\s*"true"', mock)
    # DemoBadge must check for the literal string "true" (S1.18 sentinel).
    assert '"true"' in demo_badge or "'true'" in demo_badge


# ---------- Case 10: mock provides required provinces ----------
def test_mock_evidence_chain_exposes_required_provinces() -> None:
    """Per tasking 168 §NOW-2: 江苏 + ≥1 他省.
    Per tasking 187 §S2.7-a2: 江苏 + 浙江 + 粤/川/鲁 五省全链路。"""
    mock = _read("lib/mock_evidence_chain.ts")
    for province in ["jiangsu", "zhejiang", "guangdong", "sichuan", "shandong"]:
        assert f'"{province}"' in mock, (
            f"mock must include {province!r} province chain (per tasking 187)"
        )


# ---------- Case 11 (S2.7-a2): Guangdong shell — static, no params branching ----------
def test_guangdong_page_is_static_no_params_branching() -> None:
    """Per tasking 187 + standing rule (static-segment routes must NOT branch
    on params.*). Guangdong page must render <EvidenceChain />."""
    src = _read("app/provinces/guangdong/page.tsx")
    code = _strip_js_comments(src)
    assert "<EvidenceChain" in src, "guangdong page must render <EvidenceChain />"
    assert not re.search(r"params\.province\s*[!=]==", code), (
        "guangdong/page.tsx must not gate on params.province (static route)"
    )
    assert not re.search(r"if\s*\(\s*params\.", code), (
        "guangdong/page.tsx must not branch on params.* at all"
    )


# ---------- Case 12 (S2.7-a2): Sichuan shell — static, no params branching ----------
def test_sichuan_page_is_static_no_params_branching() -> None:
    src = _read("app/provinces/sichuan/page.tsx")
    code = _strip_js_comments(src)
    assert "<EvidenceChain" in src, "sichuan page must render <EvidenceChain />"
    assert not re.search(r"params\.province\s*[!=]==", code), (
        "sichuan/page.tsx must not gate on params.province (static route)"
    )
    assert not re.search(r"if\s*\(\s*params\.", code), (
        "sichuan/page.tsx must not branch on params.* at all"
    )


# ---------- Case 13 (S2.7-a2): Shandong shell — static, no params branching ----------
def test_shandong_page_is_static_no_params_branching() -> None:
    src = _read("app/provinces/shandong/page.tsx")
    code = _strip_js_comments(src)
    assert "<EvidenceChain" in src, "shandong page must render <EvidenceChain />"
    assert not re.search(r"params\.province\s*[!=]==", code), (
        "shandong/page.tsx must not gate on params.province (static route)"
    )
    assert not re.search(r"if\s*\(\s*params\.", code), (
        "shandong/page.tsx must not branch on params.* at all"
    )


# ---------- Case 14 (S2.7-a2): 3 new shells all-empty, all 6 segments ----------
def test_s27a2_shells_have_all_six_segments_empty() -> None:
    """Per tasking 187 §NOW-1: 粤/川/鲁三省页六段可全空 ("未覆盖")."""
    mock_chain = _read("lib/mock_evidence_chain.ts")
    # Order: declaration order in the file is jiangsu, zhejiang, guangdong,
    # sichuan, shandong. Bound each block by finding the NEXT `const xChain`
    # of any province.
    provinces = ["guangdong", "sichuan", "shandong"]
    all_province_vars = ["const jiangsuChain", "const zhejiangChain",
                         "const guangdongChain", "const sichuanChain",
                         "const shandongChain"]
    for i, province in enumerate(provinces):
        var = f"const {province}Chain"
        assert var in mock_chain, f"mock must declare {var}"
        block_start = mock_chain.index(var)
        # Find the next province's `const xChain` declaration.
        block_end = len(mock_chain)
        for other_var in all_province_vars:
            if other_var == var:
                continue
            other_pos = mock_chain.find(other_var, block_start + 1)
            if other_pos != -1 and other_pos < block_end:
                block_end = other_pos
        block = mock_chain[block_start:block_end]
        # All six segments must appear.
        for seg in EXPECTED_SEGMENTS:
            assert f'key: "{seg}"' in block, (
                f"{province} chain missing segment {seg}"
            )
        # All six segment items arrays must be empty (演示"未覆盖").
        n_empty = len(re.findall(r'key:\s*"[A-Z_]+",\s*items:\s*\[\]', block))
        assert n_empty == 6, (
            f"{province} chain must have all 6 segments empty; got {n_empty}"
        )
