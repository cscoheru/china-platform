"""Stage 2 / S2.7-a2 — 补齐三省省级路由壳 pytest.

Per tasking 187 §SCHEMA + docs/06 §2:
  - 范围：frontend/app/provinces/{guangdong,sichuan,shandong}/page.tsx 路由壳
  - 每页挂 <EvidenceChain />；六段可全空（显式「未覆盖」）；复用 mock_evidence_chain
  - 禁：评分 / 排名 / 总分；不接 S2.1 person 真数据（留给 S2.7-b）
  - 首页 5 省列表链接须全部可点进真实路由（非死链）

既有 S2.7-a 套件（tests/test_evidence_chain_s27a.py）不改，仍须全绿。
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
FRONTEND = REPO_ROOT / "frontend"

NEW_SHELL_SLUGS = ["guangdong", "sichuan", "shandong"]
ALL_SLUGS = ["jiangsu", "zhejiang", *NEW_SHELL_SLUGS]

EXPECTED_SEGMENTS = [
    "CONDITION", "COMMITMENT", "INPUT", "PROCESS", "OUTPUT", "OUTCOME_RISK",
]


def _read(rel: str) -> str:
    return (FRONTEND / rel).read_text(encoding="utf-8")


def _strip_js_comments(src: str) -> str:
    src = re.sub(r"//[^\n]*", "", src)
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.DOTALL)
    return src


def _chain_block(mock_chain: str, slug: str) -> str:
    """Source slice for one province's chain literal, up to the next decl."""
    anchor = f"const {slug}Chain"
    start = mock_chain.index(anchor)
    rest = mock_chain[start + len(anchor):]
    nxt = re.search(r"\n(?:const|export)\s", rest)
    end = start + len(anchor) + (nxt.start() if nxt else len(rest))
    return mock_chain[start:end]


# ---------- Case 1: three new route shells exist ----------
@pytest.mark.parametrize("slug", NEW_SHELL_SLUGS)
def test_province_shell_page_exists(slug: str) -> None:
    page = FRONTEND / f"app/provinces/{slug}/page.tsx"
    assert page.is_file(), f"missing route shell: app/provinces/{slug}/page.tsx"


# ---------- Case 2: each shell mounts EvidenceChain on its own mock ----------
@pytest.mark.parametrize("slug", NEW_SHELL_SLUGS)
def test_province_shell_mounts_evidence_chain(slug: str) -> None:
    src = _read(f"app/provinces/{slug}/page.tsx")
    code = _strip_js_comments(src)
    assert "<EvidenceChain" in src, f"{slug} page must render <EvidenceChain />"
    assert f'getMockEvidenceChain("{slug}")' in code, (
        f"{slug} page must resolve its own chain via getMockEvidenceChain({slug!r})"
    )


# ---------- Case 3: static segment — no params.* branching ----------
@pytest.mark.parametrize("slug", NEW_SHELL_SLUGS)
def test_province_shell_no_params_branching(slug: str) -> None:
    """Per tasking 150 fix: static segments never receive params."""
    code = _strip_js_comments(_read(f"app/provinces/{slug}/page.tsx"))
    assert not re.search(r"params\.province\s*[!=]==", code), (
        f"{slug}/page.tsx must not gate on params.province (static route)"
    )
    assert not re.search(r"if\s*\(\s*params\.", code), (
        f"{slug}/page.tsx must not branch on params.* at all"
    )
    assert not re.search(r"interface\s+\w*PageProps\b", code), (
        f"{slug}/page.tsx must not declare PageProps (stale params typing)"
    )


# ---------- Case 4: each new chain has all six segments, all empty ----------
@pytest.mark.parametrize("slug", NEW_SHELL_SLUGS)
def test_province_shell_chain_has_six_empty_segments(slug: str) -> None:
    block = _chain_block(_read("lib/mock_evidence_chain.ts"), slug)
    for seg in EXPECTED_SEGMENTS:
        assert f'key: "{seg}"' in block, f"{slug} mock chain missing segment {seg}"
    n_empty = len(re.findall(r'key:\s*"[A-Z_]+",\s*items:\s*\[\]', block))
    assert n_empty == 6, (
        f"{slug} chain must have all 6 segments empty (演示未覆盖); got {n_empty}"
    )


# ---------- Case 5: registry wires every slug ----------
@pytest.mark.parametrize("slug", ALL_SLUGS)
def test_chain_registry_exposes_slug(slug: str) -> None:
    mock_chain = _read("lib/mock_evidence_chain.ts")
    registry = mock_chain[
        mock_chain.index("MOCK_EVIDENCE_CHAIN_BY_PROVINCE"):
        mock_chain.index("MOCK_PROVINCE_LIST")
    ]
    assert f"{slug}:" in registry, (
        f"MOCK_EVIDENCE_CHAIN_BY_PROVINCE missing {slug!r}; "
        "getMockEvidenceChain would return null and the page would throw"
    )


# ---------- Case 6: home page 5-province list has no dead links ----------
def test_home_province_list_has_no_dead_links() -> None:
    """Per tasking 187 §SCHEMA: 首页 5 省列表链接须全部可点进真实路由."""
    mock_chain = _read("lib/mock_evidence_chain.ts")
    list_block = mock_chain[mock_chain.index("MOCK_PROVINCE_LIST"):]
    slugs = re.findall(r'slug:\s*"([a-z_]+)"', list_block)
    assert len(slugs) >= 5, f"province list must advertise ≥5 provinces; got {len(slugs)}"
    missing = [
        s for s in slugs
        if not (FRONTEND / f"app/provinces/{s}/page.tsx").is_file()
    ]
    assert not missing, f"home page links to provinces with no route: {missing}"


# ---------- Case 7: shells stay data-free (no S2.1 person wiring) ----------
@pytest.mark.parametrize("slug", NEW_SHELL_SLUGS)
def test_province_shell_does_not_wire_person_data(slug: str) -> None:
    """Per tasking 187 §禁: 不接 S2.1 person 真数据（留给 S2.7-b）."""
    code = _strip_js_comments(_read(f"app/provinces/{slug}/page.tsx"))
    for forbidden in ("mart_person_tenure", "person_tenure", "appointment_event"):
        assert forbidden not in code, (
            f"{slug}/page.tsx references {forbidden!r} — S2.1 person data is S2.7-b scope"
        )


# ---------- Case 8: no scoring / ranking anywhere in the shells ----------
@pytest.mark.parametrize("slug", NEW_SHELL_SLUGS)
@pytest.mark.parametrize("forbidden", [
    r"\bscore\b",
    r"\brating\b",
    r"\brank(?:ing)?\b",
    r"\btotal[_-]?score\b",
])
def test_province_shell_forbids_scoring_terms(slug: str, forbidden: str) -> None:
    """Per tasking 187 §红线: 不做官员评分 / 总分 / 排名."""
    code = _strip_js_comments(_read(f"app/provinces/{slug}/page.tsx"))
    assert not re.search(forbidden, code, re.IGNORECASE), (
        f"{slug}/page.tsx contains forbidden term matching {forbidden!r}"
    )


# ---------- Case 9: mock chain slices used by S2.7-a stay unpolluted ----------
def test_s27a_slice_anchors_still_isolate_jiangsu_and_zhejiang() -> None:
    """Guards the ordering constraint that keeps tests/test_evidence_chain_s27a.py
    case 5/6 exact: new province literals must not sit between the
    `const jiangsuChain` / `const zhejiangChain` anchors or after zhejiang.
    """
    mock_chain = _read("lib/mock_evidence_chain.ts")
    jiangsu_block = mock_chain[
        mock_chain.index("const jiangsuChain"):
        mock_chain.index("const zhejiangChain")
    ]
    zhejiang_block = mock_chain[mock_chain.index("const zhejiangChain"):]
    for slug in NEW_SHELL_SLUGS:
        assert f"const {slug}Chain" not in jiangsu_block
        assert f"const {slug}Chain" not in zhejiang_block
    assert len(re.findall(r'key:\s*"[A-Z_]+",\s*items:\s*\[\]', zhejiang_block)) == 6
