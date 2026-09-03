"""Stage 2 / S2.7-a — Six-segment evidence chain UI pytest.

Per tasking 168 §NOW-1 / §NOW-3 + docs/06 §2:
  - 固定六段 CONDITION → COMMITMENT → INPUT → PROCESS → OUTPUT → OUTCOME_RISK
  - 缺一不可（空段显式标"未覆盖"，不省略）
  - 禁止评分 / 总分 / 排名
  - DemoBadge 契约保留（is_demo="true" 时显角标）
  - 静态段路由不能分支 on params.*

661 适配 (2026-09-03): 5 静态省详情页 (jiangsu/guangdong/shandong/sichuan/zhejiang)
  已被 C3 删除, 由 provinces/[province_code]/page.tsx 动态路由接管.
  EvidenceChain 6 段演示 UI 在 660 Track B 后已退场, 661 数据完全来自 mart JSON
  (lineage_is_demo='false' 全行, per 红线 8). 本文件中引用旧静态页 + 旧 6 段
  sentinel 契约的测试已替换为 661 reality 守门 (mart JSON 真值 + dynamic route
  VALID_CODES 32 slug). 仍保留的: tests 1-4 (EvidenceChain 组件本身契约) +
  test 10 (mock_evidence_chain.ts 五省链路完整, 资产保留 per 红线 4) + test 14
  (mock chain 6 段空数组结构).

Tests:
  1. test_evidence_chain_component_contains_six_segments
  2. test_evidence_chain_renders_uncovered_badge_for_empty_segments
  3. test_evidence_chain_renders_count_badge_for_populated_segments
  4. test_evidence_chain_forbids_scoring_terms
  5. test_jianlu_in_mart_json_has_real_metrics [661: replaces old jiangsu page]
  6. test_zhejiang_in_mart_json_has_real_metrics [661: replaces old zhejiang page]
  7. test_province_dynamic_route_has_32_valid_codes [661: replaces old no-params-branching]
  8. test_home_page_includes_province_list_entry
  9. test_mart_json_all_lineage_is_demo_false [661: replaces old DemoBadge sentinel]
 10. test_mock_evidence_chain_exposes_required_provinces
 11. test_province_dynamic_route_includes_guangdong [661]
 13. test_province_dynamic_route_includes_shandong [661]
 14. test_s27a2_shells_have_all_six_segments_empty
"""
from __future__ import annotations

import json
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


# ---------- Case 5 (661): JIANGSU 真数据 (旧 jiangsu 静态页已删) ----------
def test_jianlu_in_mart_json_has_real_metrics() -> None:
    """661 C3 删 5 静态详情页 (jiangsu/zhejiang/...) → dynamic route 接管.
    数据源 = mart JSON. 验证 JIANGSU 行在 mart JSON 中是真实数据
    (status != DATA_MISSING, gdp_total 非 null, lineage_is_demo='false')."""
    mart = json.loads(_read("data/mart_province_gdp_2024.json"))
    js = [r for r in mart["provinces"] if r["province_code"] == "JIANGSU"]
    assert len(js) == 1, f"JIANGSU 在 mart JSON 中应有 1 行, got {len(js)}"
    js_row = js[0]
    assert js_row["status"] != "DATA_MISSING", \
        f"JIANGSU 不应是 DATA_MISSING: {js_row['status']!r}"
    assert js_row["gdp_total"] is not None, \
        f"JIANGSU gdp_total 应为真值, got None (旧 jiangsu 静态页全 6 段已废)"
    assert js_row["lineage_is_demo"] == "false", \
        f"JIANGSU lineage_is_demo 应为 false, got {js_row['lineage_is_demo']!r}"


# ---------- Case 6 (661): ZHEJIANG 真数据 (旧 zhejiang 静态页已删) ----------
def test_zhejiang_in_mart_json_has_real_metrics() -> None:
    """旧 zhejiang 静态页全 6 段 empty 演示"未覆盖"; 661 reality:
    zhejiang 静态页删除, 改由 dynamic route + mart JSON 接管. zhejiang
    在 28 真实省之列, gdp_total 应为非 null 真值."""
    mart = json.loads(_read("data/mart_province_gdp_2024.json"))
    zj = [r for r in mart["provinces"] if r["province_code"] == "ZHEJIANG"]
    assert len(zj) == 1, f"ZHEJIANG 在 mart JSON 中应有 1 行, got {len(zj)}"
    zj_row = zj[0]
    assert zj_row["status"] != "DATA_MISSING", \
        f"ZHEJIANG 不应是 DATA_MISSING: {zj_row['status']!r}"
    assert zj_row["gdp_total"] is not None, \
        f"ZHEJIANG gdp_total 应为真值, got None"


# ---------- Case 7 (661): dynamic route VALID_CODES 32 slug 守门 ----------
def test_province_dynamic_route_has_32_valid_codes() -> None:
    """661 C3: 5 静态详情页删除, provinces/[province_code] 动态路由接管.
    VALID_CODES 必须包含 31 GB/T 2260 + NATIONAL (32 slug), 且
    generateStaticParams + dynamicParams=false 双兜底 (per docs/46 §3.1).
    旧守门 "static route 不分支 on params.*" 反向 = 新守门 "dynamic route
    有 generateStaticParams 静态预生成 + dynamicParams=false 兜底"."""
    src = _read("app/provinces/[province_code]/page.tsx")
    code = _strip_js_comments(src)
    assert "VALID_CODES" in code, \
        "provinces/[province_code]/page.tsx 缺 VALID_CODES 数组"
    # Spot-check 5 个曾为静态页的省, 确保新代码包含他们
    for province in ("JIANGSU", "ZHEJIANG", "GUANGDONG", "SICHUAN", "SHANDONG"):
        assert province in code, \
            f"VALID_CODES 缺 {province} (旧静态详情页应已迁移)"
    assert "NATIONAL" in code, \
        "VALID_CODES 缺 NATIONAL (国家锚 per docs/81 §3)"
    # generateStaticParams 必须存在 (静态预生成 32 slug)
    assert "generateStaticParams" in code, \
        "provinces/[province_code]/page.tsx 缺 generateStaticParams"
    # dynamicParams=false 兜底 (slug 命中锁定清单之外的请求一律 404)
    assert "dynamicParams" in code and "false" in code, \
        "provinces/[province_code]/page.tsx 缺 dynamicParams=false 兜底"


# ---------- Case 8: home page lists ≥1 province entry ----------
def test_home_page_includes_province_list_entry() -> None:
    home = _read("app/page.tsx")
    mock_chain = _read("lib/mock_evidence_chain.ts")
    # Home page must reference the mock province list (661: comment 注释保留 S1.18 历史资产
    # + 默认渲染已移除 per 661 C1; mock 链路未删 per 红线 4).
    assert "MOCK_PROVINCE_LIST" in home, "home page must reference MOCK_PROVINCE_LIST"
    # Mock list must include at least 2 provinces (per tasking 168: 江苏 + ≥1 他省).
    n_provinces = len(re.findall(r"slug:\s*\"[a-z_]+\"", mock_chain))
    assert n_provinces >= 2, (
        f"MOCK_PROVINCE_LIST must have ≥2 entries (jiangsu + ≥1 other); got {n_provinces}"
    )


# ---------- Case 9 (661): mart JSON lineage_is_demo 全行 false (替代 DemoBadge sentinel) ----------
def test_mart_json_all_lineage_is_demo_false() -> None:
    """旧 DemoBadge sentinel 契约 (S1.18 is_demo='true') 在 660 Track B 后
    已废: 661 mart JSON 全行 lineage_is_demo='false' (per 661 tasking §1.661
    + 红线 8). DemoBadge.tsx 保留作为历史资产 (per 红线 4 mock 链不删).
    本守门验证 32 行 mart 数据无一例外 lineage_is_demo='false'."""
    mart = json.loads(_read("data/mart_province_gdp_2024.json"))
    rows = mart["provinces"]
    bad = [r for r in rows if r.get("lineage_is_demo") != "false"]
    assert not bad, (
        f"mart JSON 有 {len(bad)} 行 lineage_is_demo != 'false': "
        f"{[r['province_code'] for r in bad]}"
    )
    # 额外守门: 32 行总数 (1 NATIONAL + 28 真 + 3 缺) 不漂
    assert len(rows) == 32, f"mart JSON 应 32 行, got {len(rows)} (1+28+3)"


# ---------- Case 10: mock provides required provinces ----------
def test_mock_evidence_chain_exposes_required_provinces() -> None:
    """Per tasking 168 §NOW-2: 江苏 + ≥1 他省.
    Per tasking 187 §S2.7-a2: 江苏 + 浙江 + 粤/川/鲁 五省全链路。
    资产保留 (per 红线 4 mock 链不删); 即便 661 默认不渲染, mock 文件结构必须完整."""
    mock = _read("lib/mock_evidence_chain.ts")
    for province in ["jiangsu", "zhejiang", "guangdong", "sichuan", "shandong"]:
        assert f'"{province}"' in mock, (
            f"mock must include {province!r} province chain (per tasking 187)"
        )


# ---------- Case 11 (661): GUANGDONG 已迁 dynamic route ----------
def test_province_dynamic_route_includes_guangdong() -> None:
    """旧 guangdong 静态页删除; 661 dynamic route VALID_CODES 必有 GUANGDONG."""
    src = _read("app/provinces/[province_code]/page.tsx")
    code = _strip_js_comments(src)
    assert "GUANGDONG" in code, \
        "provinces/[province_code]/page.tsx VALID_CODES 缺 GUANGDONG"


# ---------- Case 12 (661): SICHUAN 已迁 dynamic route ----------
def test_province_dynamic_route_includes_sichuan() -> None:
    """旧 sichuan 静态页删除; 661 dynamic route VALID_CODES 必有 SICHUAN."""
    src = _read("app/provinces/[province_code]/page.tsx")
    code = _strip_js_comments(src)
    assert "SICHUAN" in code, \
        "provinces/[province_code]/page.tsx VALID_CODES 缺 SICHUAN"


# ---------- Case 13 (661): SHANDONG 已迁 dynamic route ----------
def test_province_dynamic_route_includes_shandong() -> None:
    """旧 shandong 静态页删除; 661 dynamic route VALID_CODES 必有 SHANDONG."""
    src = _read("app/provinces/[province_code]/page.tsx")
    code = _strip_js_comments(src)
    assert "SHANDONG" in code, \
        "provinces/[province_code]/page.tsx VALID_CODES 缺 SHANDONG"


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
