#!/usr/bin/env python3
"""Stage 2 / S2.0.1 — Frontend skeleton smoke check.

Pure file inspection; does NOT require node_modules or `next build`.
Invoked via `npm run smoke` (package.json script) or `python3 smoke-check.py`.

Validates:
  1. All required skeleton files exist (package.json, tsconfig.json,
     next.config.js, .gitignore, README.md, app/layout.tsx, app/page.tsx,
     app/DemoBadge.tsx, app/provinces/jiangsu/page.tsx,
     lib/api.ts, lib/types.ts, lib/mock.ts).
  2. package.json declares next + react.
  3. tsconfig.json enables App Router conventions ("jsx": "preserve").
  4. app/layout.tsx renders a top banner keyed off IS_MOCK_MODE
     and reads NEXT_PUBLIC_USE_MOCK / NEXT_PUBLIC_API_BASE env vars.
  5. app/provinces/jiangsu/page.tsx imports DemoBadge from "../../DemoBadge".
  6. lib/mock.ts includes at least one observation row with
     lineage.is_demo === "true" (S1.18 sentinel pattern).
  7. lib/api.ts honours NEXT_PUBLIC_USE_MOCK switch (default true).

Exits 0 on full pass; non-zero on any missing/wrong file.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def _strip_forbidden_field_lists(src: str) -> str:
    """Strip contents of FORBIDDEN_*_FIELDS / FORBIDDEN_TOKENS array declarations.

    mart_city_types.ts 的 FORBIDDEN_MART_FIELDS 数组声明是为了禁词守门 —
    列出禁词不等于使用禁词。须剥离此声明体后再做禁词扫描。
    """
    pat = re.compile(
        r"(?:export\s+)?const\s+FORBIDDEN[A-Z_]*\s*=\s*\[[^\]]*\]\s*(?:as\s+const)?",
        re.DOTALL,
    )
    return pat.sub("", src)


REQUIRED_FILES = [
    "package.json",
    "tsconfig.json",
    "next.config.js",
    ".gitignore",
    "README.md",
    "app/layout.tsx",
    "app/page.tsx",
    "app/DemoBadge.tsx",
    "app/components/EvidenceChain.tsx",        # S2.7-a
    "app/provinces/jiangsu/page.tsx",
    "app/provinces/zhejiang/page.tsx",          # S2.7-a 路由壳
    "app/provinces/guangdong/page.tsx",         # S2.7-a2 路由壳
    "app/provinces/sichuan/page.tsx",           # S2.7-a2 路由壳
    "app/provinces/shandong/page.tsx",          # S2.7-a2 路由壳
    "app/cities/[slug]/page.tsx",               # S2.7-b-lite dynamic route
    "app/components/CityPage.tsx",              # S2.7-b-lite 组件
    "lib/api.ts",
    "lib/types.ts",
    "lib/mock.ts",
    "lib/mock_evidence_chain.ts",               # S2.7-a mock
    "lib/city_slug_map.ts",                     # S2.7-b-lite slug 映射
    "lib/mock_cities.ts",                       # S2.7-b-lite 10 城 mock
    "lib/types_cities.ts",                      # S2.7-b-lite 类型契约
]


def fail(msg: str) -> None:
    print(f"❌ {msg}", file=sys.stderr)


def ok(msg: str) -> None:
    print(f"✅ {msg}")


def main() -> int:
    errors: list[str] = []

    # 1. Required files exist
    for rel in REQUIRED_FILES:
        path = ROOT / rel
        if not path.is_file():
            errors.append(f"missing required file: {rel}")
        else:
            ok(f"present: {rel}")

    if errors:
        for e in errors:
            fail(e)
        return 1

    # 2. package.json declares next + react
    pkg = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    deps = pkg.get("dependencies", {})
    for dep in ("next", "react", "react-dom"):
        if dep not in deps:
            errors.append(f"package.json missing dependency: {dep}")
        else:
            ok(f"package.json declares {dep}={deps[dep]}")

    # 3. tsconfig.json enables App Router conventions
    ts = json.loads((ROOT / "tsconfig.json").read_text(encoding="utf-8"))
    compiler = ts.get("compilerOptions", {})
    if compiler.get("jsx") != "preserve":
        errors.append('tsconfig.json compilerOptions.jsx must be "preserve"')
    else:
        ok('tsconfig.json compilerOptions.jsx == "preserve"')

    # 4. app/layout.tsx renders top banner keyed off IS_MOCK_MODE
    layout = (ROOT / "app/layout.tsx").read_text(encoding="utf-8")
    if "IS_MOCK_MODE" not in layout:
        errors.append("app/layout.tsx does not reference IS_MOCK_MODE")
    elif "data-testid=\"mode-banner\"" not in layout:
        errors.append("app/layout.tsx banner is missing data-testid=\"mode-banner\"")
    else:
        ok("app/layout.tsx renders IS_MOCK_MODE banner")

    # 5. jiangsu page imports DemoBadge
    jiangsu = (ROOT / "app/provinces/jiangsu/page.tsx").read_text(encoding="utf-8")
    if 'from "../../DemoBadge"' not in jiangsu:
        errors.append("jiangsu/page.tsx does not import DemoBadge from '../../DemoBadge'")
    else:
        ok("jiangsu/page.tsx imports DemoBadge from '../../DemoBadge'")
    if "DemoBadge" not in jiangsu or "<DemoBadge" not in jiangsu:
        errors.append("jiangsu/page.tsx does not render <DemoBadge />")
    else:
        ok("jiangsu/page.tsx renders <DemoBadge />")

    # 5b. FIX per tasking 150 (Cursor 149 FAIL): reject any source-level
    # constant-failure gate that prevents the series table from rendering.
    # Specifically: static-segment pages must NOT compare `params.province`
    # (always undefined on a static route → always-false gate).
    #
    # Strip JS comments first — explanatory comments may legitimately mention
    # the bad pattern name. We only want to scan executable code.
    code = re.sub(r"//[^\n]*", "", jiangsu)
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
    if re.search(r"params\.province\s*[!=]==", code):
        errors.append(
            "jiangsu/page.tsx references params.province in executable code — "
            "static-segment route does not receive params; this gate is "
            "always false. Per tasking 150, drop it or move to [province]/ "
            "dynamic route."
        )
    else:
        ok("jiangsu/page.tsx has no params.province gate (FIX per 149/150)")
    if re.search(r"if\s*\(\s*params\.", code):
        errors.append(
            "jiangsu/page.tsx still branches on params.* in executable code — "
            "static-segment params are always undefined."
        )
    # 5c. Static-segment page must not declare PageProps with `params`.
    if re.search(r"interface\s+\w*PageProps\b", code):
        errors.append(
            "jiangsu/page.tsx declares a PageProps interface in executable "
            "code — remove if it still types params (static segment)."
        )
    else:
        ok("jiangsu/page.tsx has no PageProps interface (no stale params typing)")

    # 6. lib/mock.ts has at least one row with lineage.is_demo === "true"
    mock = (ROOT / "lib/mock.ts").read_text(encoding="utf-8")
    if not re.search(r'is_demo:\s*"true"', mock):
        errors.append("lib/mock.ts has no row with lineage.is_demo === 'true'")
    else:
        n = len(re.findall(r'is_demo:\s*"true"', mock))
        ok(f"lib/mock.ts has {n} is_demo=true sentinel rows")

    # 7. lib/api.ts honours NEXT_PUBLIC_USE_MOCK
    api = (ROOT / "lib/api.ts").read_text(encoding="utf-8")
    if "NEXT_PUBLIC_USE_MOCK" not in api:
        errors.append("lib/api.ts does not reference NEXT_PUBLIC_USE_MOCK")
    elif "USE_MOCK" not in api or "if (USE_MOCK)" not in api:
        errors.append("lib/api.ts does not branch on USE_MOCK")
    else:
        ok("lib/api.ts branches on NEXT_PUBLIC_USE_MOCK")

    # 8. S2.7-a — Six-segment evidence chain contract.
    #    Per docs/06 §2: 固定六段 CONDITION → COMMITMENT → INPUT → PROCESS
    #    → OUTPUT → OUTCOME_RISK；缺一不可。
    chain_src = (ROOT / "app/components/EvidenceChain.tsx").read_text(encoding="utf-8")
    expected_segments = [
        "CONDITION", "COMMITMENT", "INPUT", "PROCESS", "OUTPUT", "OUTCOME_RISK",
    ]
    for seg in expected_segments:
        if seg not in chain_src:
            errors.append(f"EvidenceChain.tsx missing segment key: {seg}")
    if not errors or all("EvidenceChain.tsx missing" not in e for e in errors):
        ok(f"EvidenceChain.tsx references all 6 fixed segments ({len(expected_segments)})")

    # 8b. Per tasking 168 §红线: 禁止评分 / 总分 / 排名。静态扫描
    # EvidenceChain.tsx 源码以确保没有数值化或排名化逻辑。
    chain_code = re.sub(r"//[^\n]*", "", chain_src)
    chain_code = re.sub(r"/\*.*?\*/", "", chain_code, flags=re.DOTALL)
    forbidden_patterns = [
        (r"\bscore\b", "score"),
        (r"\brating\b", "rating"),
        (r"\brank(?:ing)?\b", "rank"),
        (r"\btotal[_-]?score\b", "total_score"),
    ]
    for pat, label in forbidden_patterns:
        if re.search(pat, chain_code, re.IGNORECASE):
            errors.append(
                f"EvidenceChain.tsx contains forbidden term {label!r} "
                f"(per tasking 168 §红线: 禁止评分/总分/排名)"
            )
        else:
            ok(f"EvidenceChain.tsx has no forbidden {label!r} term")

    # 8c. Zhejiang route shell — verify it's a static-segment route with no
    # params.* branching (mirror of jiangsu check 5b).
    zhejiang = (ROOT / "app/provinces/zhejiang/page.tsx").read_text(encoding="utf-8")
    zj_code = re.sub(r"//[^\n]*", "", zhejiang)
    zj_code = re.sub(r"/\*.*?\*/", "", zj_code, flags=re.DOTALL)
    if re.search(r"params\.province\s*[!=]==", zj_code):
        errors.append(
            "zhejiang/page.tsx references params.province in executable code — "
            "static-segment route does not receive params."
        )
    else:
        ok("zhejiang/page.tsx has no params.province gate")
    if "EvidenceChain" not in zhejiang:
        errors.append("zhejiang/page.tsx does not render <EvidenceChain />")
    else:
        ok("zhejiang/page.tsx renders <EvidenceChain />")

    # 8d. Mock chain — all 5 provinces (jiangsu + zhejiang + guangdong +
    # sichuan + shandong per tasking 187 §S2.7-a2) must each provide all 6
    # segments; this guards against future "we only show N segments" regressions.
    mock_chain = (ROOT / "lib/mock_evidence_chain.ts").read_text(encoding="utf-8")
    expected_provinces = ["jiangsu", "zhejiang", "guangdong", "sichuan", "shandong"]
    for province in expected_provinces:
        # Locate the chain block via the `const <slug>Chain` declaration.
        var = f"const {province}Chain"
        if var not in mock_chain:
            errors.append(f"mock_evidence_chain.ts missing chain for {province!r}")
            continue
        # Compute end of this block: next `const <slug>Chain` or `};` closing
        block_start = mock_chain.index(var)
        block_end = len(mock_chain)
        for other in expected_provinces:
            if other == province:
                continue
            other_var = f"const {other}Chain"
            other_pos = mock_chain.find(other_var, block_start + 1)
            if other_pos != -1 and other_pos < block_end:
                block_end = other_pos
        block = mock_chain[block_start:block_end]
        for seg in expected_segments:
            if f'key: "{seg}"' not in block:
                errors.append(
                    f"mock_evidence_chain.ts: {province} chain missing segment {seg}"
                )
    # Also require at least N=5 occurrences of each segment key (one per
    # province). Belt-and-suspenders with the per-province loop above.
    seg_key_count = {seg: len(re.findall(rf'key:\s*"{seg}"', mock_chain)) for seg in expected_segments}
    min_per_seg = len(expected_provinces)
    for seg, n in seg_key_count.items():
        if n < min_per_seg:
            errors.append(
                f"mock_evidence_chain.ts: segment {seg} appears {n}x; "
                f"expected ≥{min_per_seg} (one per province)"
            )
    if all(seg_key_count[s] >= min_per_seg for s in expected_segments):
        ok(f"mock_evidence_chain.ts has ≥{min_per_seg} of each of 6 segment keys")

    # 8e. S2.7-a2 — Guangdong / Sichuan / Shandong route shells must:
    #   (a) exist as static-segment pages with no params.* branching
    #   (b) render <EvidenceChain />
    # Per tasking 187 §NOW-1 + standing rule (static-segment routes must
    # NOT branch on params.*).
    for slug in ("guangdong", "sichuan", "shandong"):
        path = ROOT / "app" / "provinces" / slug / "page.tsx"
        if not path.is_file():
            errors.append(f"{slug}/page.tsx missing (S2.7-a2 route shell)")
            continue
        src = path.read_text(encoding="utf-8")
        code = re.sub(r"//[^\n]*", "", src)
        code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
        if re.search(r"params\.province\s*[!=]==", code):
            errors.append(
                f"{slug}/page.tsx references params.province in executable code — "
                f"static-segment route does not receive params."
            )
        else:
            ok(f"{slug}/page.tsx has no params.province gate")
        if re.search(r"if\s*\(\s*params\.", code):
            errors.append(
                f"{slug}/page.tsx still branches on params.* in executable code"
            )
        if "EvidenceChain" not in src:
            errors.append(f"{slug}/page.tsx does not render <EvidenceChain />")
        else:
            ok(f"{slug}/page.tsx renders <EvidenceChain />")

    if errors:
        for e in errors:
            fail(e)
        return 1

    # 9. S2.7-b-lite — 10 地市 dynamic route + slug map 守门.
    #    Per docs/46 §3.2 (路由) + §3.1 (slug 字符集 [a-z0-9-]+) +
    #    `256` §SCHEMA "10 城锁定"; per Cursor 锁定清单 = 南京/苏州/无锡/南通 +
    #    杭州/宁波/温州 + 广州/深圳/东莞.
    slug_map_src = (ROOT / "lib/city_slug_map.ts").read_text(encoding="utf-8")
    locked_slugs = [
        "nanjing", "suzhou", "wuxi", "nantong",
        "hangzhou", "ningbo", "wenzhou",
        "guangzhou", "shenzhen", "dongguan",
    ]
    for s in locked_slugs:
        if f'slug: "{s}"' not in slug_map_src:
            errors.append(f"city_slug_map.ts missing locked slug: {s}")
    if all(f'slug: "{s}"' in slug_map_src for s in locked_slugs):
        ok(f"city_slug_map.ts contains all 10 locked slugs")

    # 9b. CITY_SLUG_LIST 顺序 + 长度 (per Cursor 裁定; 不擅自增减).
    m = re.search(
        r"export const CITY_SLUG_LIST:\s*readonly string\[\]\s*=\s*\[([^\]]+)\]",
        slug_map_src,
    )
    if not m:
        errors.append("city_slug_map.ts: CITY_SLUG_LIST not found")
    else:
        items = [s.strip().strip('"') for s in m.group(1).split(",") if s.strip()]
        if items != locked_slugs:
            errors.append(
                f"city_slug_map.ts: CITY_SLUG_LIST order/length mismatch: "
                f"got {items}, expected {locked_slugs}"
            )
        else:
            ok("city_slug_map.ts: CITY_SLUG_LIST ordered == 10 locked slugs")

    # 9c. Dynamic segment route must use generateStaticParams + dynamicParams=false.
    city_route = (ROOT / "app/cities/[slug]/page.tsx").read_text(encoding="utf-8")
    city_route_code = re.sub(r"//[^\n]*", "", city_route)
    city_route_code = re.sub(r"/\*.*?\*/", "", city_route_code, flags=re.DOTALL)
    if "generateStaticParams" not in city_route_code:
        errors.append(
            "cities/[slug]/page.tsx missing generateStaticParams "
            "(per docs/46 §3.2 dynamic segment + 256 §SCHEMA)"
        )
    else:
        ok("cities/[slug]/page.tsx declares generateStaticParams")
    if "dynamicParams" not in city_route_code:
        errors.append(
            "cities/[slug]/page.tsx missing dynamicParams=false "
            "(per docs/46 §3.1 slug 守门)"
        )
    if "params.slug" not in city_route_code:
        errors.append(
            "cities/[slug]/page.tsx must read params.slug in executable code"
        )

    # 9d. CityPage component 必须复用三件套 (EvidenceChain + SevenDimGrid + PeerCompareCard).
    city_page_src = (ROOT / "app/components/CityPage.tsx").read_text(encoding="utf-8")
    for needle, label in [
        ("EvidenceChain", "EvidenceChain"),
        ("SevenDimGrid", "SevenDimGrid"),
        ("PeerCompareCard", "PeerCompareCard"),
    ]:
        if needle not in city_page_src:
            errors.append(f"components/CityPage.tsx missing {label} reuse")
    if all(n in city_page_src for n in ("EvidenceChain", "SevenDimGrid", "PeerCompareCard")):
        ok("components/CityPage.tsx reuses EvidenceChain + SevenDimGrid + PeerCompareCard")

    # 9e. mock_cities.ts 必须覆盖 10 城 (per Cursor 锁定).
    # 覆盖证据：(a) CITY_SLUG_LIST 已从 city_slug_map.ts 导入并参与迭代
    # (Object.fromEntries 沿 CITY_SLUG_LIST map); (b) 单条 slug 字面量出现.
    mock_cities_src = (ROOT / "lib/mock_cities.ts").read_text(encoding="utf-8")
    coverage_via_import = (
        "CITY_SLUG_LIST" in mock_cities_src
        and "city_slug_map" in mock_cities_src
        and (
            "Object.fromEntries" in mock_cities_src
            or ".map(" in mock_cities_src
        )
    )
    literal_hits = sum(
        1 for s in locked_slugs
        if (
            f'"{s}"' in mock_cities_src
            or f"'{s}'" in mock_cities_src
            or f'slug: "{s}"' in mock_cities_src
            or f"[{s}]" in mock_cities_src
        )
    )
    if not coverage_via_import and literal_hits < len(locked_slugs):
        errors.append(
            f"mock_cities.ts missing coverage for 10 cities: "
            f"literal_hits={literal_hits}/10, via_import={coverage_via_import}"
        )
    else:
        ok(
            f"mock_cities.ts covers 10 cities (via_import={coverage_via_import}, "
            f"literal_hits={literal_hits}/10)"
        )

    # 9f. 禁词守门 (per docs/46 §1.2 + 256 §红线): mock_cities.ts 不出现
    # score / rating / rank / total_score / confidence_score 字段 (应用层).
    mock_cities_code = re.sub(r"//[^\n]*", "", mock_cities_src)
    mock_cities_code = re.sub(r"/\*.*?\*/", "", mock_cities_code, flags=re.DOTALL)
    forbidden_terms = [
        (r"\bscore\b", "score"),
        (r"\brating\b", "rating"),
        (r"\brank(?:ing)?\b", "rank"),
        (r"\btotal[_-]?score\b", "total_score"),
        (r"\bconfidence[_-]?score\b", "confidence_score"),
    ]
    for pat, label in forbidden_terms:
        if re.search(pat, mock_cities_code, re.IGNORECASE):
            errors.append(
                f"mock_cities.ts contains forbidden term {label!r} "
                f"(per docs/46 §1.2 + 256 §红线)"
            )
        else:
            ok(f"mock_cities.ts has no forbidden {label!r} term")

    # 10. S2.7-b-full-lite — mart-shape types + demo fixture + CityPage 接驳.
    #     Per docs/47 §3.1 + §3.2 + §3.3 + §4.1 + §4.2 +
    #     `265` §SCHEMA "mart 形状 TS 类型 + is_demo fixture + CityPage 接驳".
    mart_types_path = ROOT / "lib/mart_city_types.ts"
    mart_demo_path = ROOT / "lib/mart_city_demo.ts"
    city_page_mart_path = ROOT / "app/components/CityPageMart.tsx"
    slug_page_path = ROOT / "app/cities/[slug]/page.tsx"

    # 10a. mart_city_types.ts 必含 4 个导出 + SHA256 占位
    if not mart_types_path.exists():
        errors.append("lib/mart_city_types.ts missing (per docs/47 §3.1 + 265 §SCHEMA)")
    else:
        msrc = mart_types_path.read_text(encoding="utf-8")
        mcode = re.sub(r"//[^\n]*", "", msrc)
        mcode = re.sub(r"/\*.*?\*/", "", mcode, flags=re.DOTALL)
        for sym, label in [
            ("export interface MartLineageProps", "MartLineageProps"),
            ("export interface MartCityViewProps", "MartCityViewProps"),
            ("export const MART_LINEAGE_PLACEHOLDER_SHA", "MART_LINEAGE_PLACEHOLDER_SHA"),
            ("export function isValidMartLineage", "isValidMartLineage"),
            ("export function assertMartRowHasNoForbiddenFields",
             "assertMartRowHasNoForbiddenFields"),
        ]:
            if sym not in mcode:
                errors.append(f"mart_city_types.ts missing {label}")
        if all(s in mcode for s in [
            "export interface MartLineageProps",
            "export interface MartCityViewProps",
            "export const MART_LINEAGE_PLACEHOLDER_SHA",
            "export function isValidMartLineage",
            "export function assertMartRowHasNoForbiddenFields",
        ]):
            ok("mart_city_types.ts exports MartLineageProps + MartCityViewProps + sha256 placeholder")
        if '"0".repeat(64)' not in mcode:
            errors.append(
                "mart_city_types.ts: SHA256 placeholder must be '0'.repeat(64) "
                "(per docs/47 §3.1 ⚠️ OPEN)"
            )
        else:
            ok("mart_city_types.ts: SHA256 placeholder = '0'.repeat(64)")

    # 10b. mart_city_demo.ts 必含 CITY_SLUG_LIST + 10 城引用 + SHA256 占位
    if not mart_demo_path.exists():
        errors.append("lib/mart_city_demo.ts missing (per docs/47 §3.1 + 265 §SCHEMA)")
    else:
        dsrc = mart_demo_path.read_text(encoding="utf-8")
        dcode = re.sub(r"//[^\n]*", "", dsrc)
        dcode = re.sub(r"/\*.*?\*/", "", dcode, flags=re.DOTALL)
        if "CITY_SLUG_LIST" not in dcode:
            errors.append("mart_city_demo.ts missing CITY_SLUG_LIST reference")
        else:
            ok("mart_city_demo.ts references CITY_SLUG_LIST")
        if "MART_LINEAGE_PLACEHOLDER_SHA" not in dcode:
            errors.append(
                "mart_city_demo.ts missing MART_LINEAGE_PLACEHOLDER_SHA reuse "
                "(O1 收口前恒占位)"
            )
        else:
            ok("mart_city_demo.ts reuses MART_LINEAGE_PLACEHOLDER_SHA (= '0'*64)")
        # Coverage via import (mirrors §9e mock_cities.ts pattern):
        # demo iterates over CITY_SLUG_LIST via Object.fromEntries(...map(...))
        coverage_via_import = (
            "CITY_SLUG_LIST" in dcode
            and "city_slug_map" in dcode
            and ("Object.fromEntries" in dcode or ".map(" in dcode)
        )
        literal_hits = sum(
            1 for s in locked_slugs
            if (
                f'"{s}"' in dcode
                or f"'{s}'" in dcode
                or f'slug: "{s}"' in dcode
                or f"[{s}]" in dcode
            )
        )
        if not coverage_via_import and literal_hits < len(locked_slugs):
            errors.append(
                f"mart_city_demo.ts missing coverage for 10 cities: "
                f"literal_hits={literal_hits}/10, via_import={coverage_via_import}"
            )
        else:
            ok(
                f"mart_city_demo.ts covers 10 cities "
                f"(via_import={coverage_via_import}, literal_hits={literal_hits}/10)"
            )

    # 10c. mart-shape 禁词守门 (per docs/47 §1.2 + 265 §红线)
    for fp, label in [
        (mart_types_path, "mart_city_types.ts"),
        (mart_demo_path, "mart_city_demo.ts"),
        (city_page_mart_path, "CityPageMart.tsx"),
        (slug_page_path, "[slug]/page.tsx"),
    ]:
        if not fp.exists():
            continue
        c = fp.read_text(encoding="utf-8")
        cc = re.sub(r"//[^\n]*", "", c)
        cc = re.sub(r"/\*.*?\*/", "", cc, flags=re.DOTALL)
        cc = _strip_forbidden_field_lists(cc)  # FORBIDDEN_* 声明体不计入禁词
        for pat, tlabel in forbidden_terms:
            if re.search(pat, cc, re.IGNORECASE):
                errors.append(
                    f"{label} contains forbidden term {tlabel!r} "
                    f"(per docs/47 §1.2 + 265 §红线)"
                )

    # 10d. CityPageMart 复用三件套 (EvidenceChain + SevenDimGrid + PeerCompareCard)
    if not city_page_mart_path.exists():
        errors.append("app/components/CityPageMart.tsx missing")
    else:
        msrc = city_page_mart_path.read_text(encoding="utf-8")
        mcode = re.sub(r"//[^\n]*", "", msrc)
        mcode = re.sub(r"/\*.*?\*/", "", mcode, flags=re.DOTALL)
        for needle, label in [
            ("EvidenceChain", "EvidenceChain"),
            ("SevenDimGrid", "SevenDimGrid"),
            ("PeerCompareCard", "PeerCompareCard"),
        ]:
            if needle not in mcode:
                errors.append(f"CityPageMart.tsx missing {label} reuse")
        if all(n in mcode for n in ("EvidenceChain", "SevenDimGrid", "PeerCompareCard")):
            ok("CityPageMart.tsx reuses EvidenceChain + SevenDimGrid + PeerCompareCard")

    # 10e. /cities/[slug]/page.tsx feature-flag 守门
    if not slug_page_path.exists():
        errors.append("app/cities/[slug]/page.tsx missing")
    else:
        sp = slug_page_path.read_text(encoding="utf-8")
        spc = re.sub(r"//[^\n]*", "", sp)
        spc = re.sub(r"/\*.*?\*/", "", spc, flags=re.DOTALL)
        if "NEXT_PUBLIC_USE_MART_FIXTURE" not in spc:
            errors.append("[slug]/page.tsx missing NEXT_PUBLIC_USE_MART_FIXTURE feature-flag")
        else:
            ok("[slug]/page.tsx declares NEXT_PUBLIC_USE_MART_FIXTURE feature-flag")
        if "shouldUseMartFixture" not in spc:
            errors.append("[slug]/page.tsx missing shouldUseMartFixture() helper")
        if "getMockCity" not in spc:
            errors.append("[slug]/page.tsx missing default mock path (getMockCity)")
        else:
            ok("[slug]/page.tsx defaults to getMockCity (mock path 保留)")
        if "getMartCityDemo" not in spc:
            errors.append("[slug]/page.tsx missing mart-shape path (getMartCityDemo)")
        else:
            ok("[slug]/page.tsx opt-in mart-shape path (getMartCityDemo)")
        if "CityPageMart" not in spc:
            errors.append("[slug]/page.tsx missing CityPageMart import")
        else:
            ok("[slug]/page.tsx imports CityPageMart")

    # 11. Home navigation — knife 30 (tasking 280). Per `280` §SCHEMA "本刀做":
    #     smoke-check.py 增加首页守门：含 10 城 /cities/{slug} 链接 + /seven-dim +
    #     /peer-compare. Per `280` §NOW-1. Per docs/46 §2 (10 城列表入口) +
    #     docs/42 §3.1 (七维度入口) + docs/43 §3.5 (同类对比入口).
    #
    # 11a. app/page.tsx 必须存在 + 含 4 个 section (indicator inventory +
    #      省级 + 地市 + 横向视角入口).
    home_src = (ROOT / "app/page.tsx").read_text(encoding="utf-8")
    home_code = re.sub(r"//[^\n]*", "", home_src)
    home_code = re.sub(r"/\*.*?\*/", "", home_code, flags=re.DOTALL)

    required_home_anchors = [
        ("Indicator inventory", "Indicator inventory"),
        ("/provinces/", "/provinces/"),
        ("/cities/", "/cities/"),
        ("/seven-dim", "/seven-dim"),
        ("/peer-compare", "/peer-compare"),
        ("CITY_SLUG_LIST", "CITY_SLUG_LIST import"),
        ("MOCK_PROVINCE_LIST", "MOCK_PROVINCE_LIST import"),
    ]
    for needle, label in required_home_anchors:
        if needle not in home_code:
            errors.append(f"app/page.tsx missing {label} (per tasking 280 §NOW-1)")
    if all(n in home_code for n, _ in required_home_anchors):
        ok("app/page.tsx contains all 4 home sections (indicator + 省级 + 地市 + 横向)")

    # 11b. 10 城首页链接守门：home page 必须为每个锁定 slug 含 /cities/{slug} 链接.
    #      Accept both literal `/cities/<slug>` and template-literal
    #      `/cities/${...slug...}` variants (per knife 28 home page).
    def _has_city_link(code: str, slug: str) -> bool:
        if f"/cities/{slug}" in code:
            return True
        # template literal form: `/cities/${...slug...}` where ...slug... is
        # `entry.slug` or `slug` (any expression). We accept either.
        if re.search(rf"/cities/\$\{{\s*(?:entry\.slug|slug)\s*\}}", code):
            # generic template covers all slugs iterated from CITY_SLUG_LIST
            return True
        return False

    home_city_link_hits = sum(
        1 for s in locked_slugs if _has_city_link(home_code, s)
    )
    if home_city_link_hits < len(locked_slugs):
        errors.append(
            f"app/page.tsx missing /cities/{{slug}} links for locked cities: "
            f"got {home_city_link_hits}/10"
        )
    else:
        ok(f"app/page.tsx links all 10 locked cities via /cities/{{slug}} (template or literal)")

    # 11c. 横向视角入口守门：/seven-dim + /peer-compare (各 1 个)
    for url, label in [("/seven-dim", "/seven-dim"), ("/peer-compare", "/peer-compare")]:
        if url not in home_code:
            errors.append(f"app/page.tsx missing {label} nav anchor")

    # 11d. 首页禁词守门 (per docs/06 §6.6 + docs/42 §8 + docs/43 §8):
    #      home page 不出现 score/rating/rank 数值化逻辑.
    for pat, label in [
        (r"\bscore\b", "score"),
        (r"\brating\b", "rating"),
        (r"\brank(?:ing)?\b", "rank"),
        (r"\btotal[_-]?score\b", "total_score"),
        (r"\bconfidence[_-]?score\b", "confidence_score"),
        (r"\bpeer_rank\b", "peer_rank"),
    ]:
        if re.search(pat, home_code, re.IGNORECASE):
            errors.append(
                f"app/page.tsx contains forbidden term {label!r} "
                f"(per docs/06 §6.6 + 280 §红线)"
            )
        else:
            ok(f"app/page.tsx has no forbidden {label!r} term")

    # 11e. 7 维度枚举守门 (per docs/42 §3.1 — 仅展示枚举名称, 不派生 score).
    seven_dim_card_path = ROOT / "lib/types_seven_dim.ts"
    if seven_dim_card_path.exists():
        tsrc = seven_dim_card_path.read_text(encoding="utf-8")
        expected_dims = [
            "POLICY_DELIVERY", "FISCAL_EXECUTION", "PROJECT_DELIVERY",
            "ECONOMIC_ADAPTATION", "PUBLIC_SERVICES", "RISK_MANAGEMENT",
            "GOAL_CONSISTENCY",
        ]
        for dim in expected_dims:
            if dim not in tsrc:
                errors.append(f"types_seven_dim.ts missing enum: {dim}")
        if all(d in tsrc for d in expected_dims):
            ok(f"types_seven_dim.ts declares all 7 dimension enums")

    # 12. 公开提取呈现 — knife 52 (tasking 349). Per `349` §SCHEMA:
    #     (1) 前端可读 public_extracts (build-time fixture);
    #     (2) 专用区块 ≥1 行可见 + 显式 REGISTRY_SAMPLE / demo 标注;
    #     (3) 保留 mart demo 旗标逻辑;
    #     (4) build/测证据由 pytest test_public_extract_frontend_fixture.py 提供.
    fixture_path = ROOT / "lib/public_extract_nbs.json"
    pe_page_path = ROOT / "app/public-extracts/page.tsx"
    if not fixture_path.is_file():
        errors.append("lib/public_extract_nbs.json missing (per tasking 349 §NOW-1)")
    else:
        try:
            fx = json.loads(fixture_path.read_text(encoding="utf-8"))
            if fx.get("domain") != "stats.gov.cn":
                errors.append("public_extract_nbs.json: domain != stats.gov.cn")
            if fx.get("category") != "NATIONAL_BULLETIN":
                errors.append("public_extract_nbs.json: category != NATIONAL_BULLETIN")
            if fx.get("row_count") != 63:
                errors.append(
                    f"public_extract_nbs.json: row_count={fx.get('row_count')} != 63"
                )
            if not isinstance(fx.get("rows"), list) or len(fx["rows"]) < 1:
                errors.append("public_extract_nbs.json: rows empty (≥1 行可见 per 349)")
            else:
                ok("public_extract_nbs.json: 63 行 NBS 提取 fixture 在位")
        except json.JSONDecodeError as e:
            errors.append(f"public_extract_nbs.json is not valid JSON: {e}")

    if not pe_page_path.is_file():
        errors.append("app/public-extracts/page.tsx missing (per tasking 349 §NOW-1)")
    else:
        pe_src = pe_page_path.read_text(encoding="utf-8")
        pe_code = re.sub(r"//[^\n]*", "", pe_src)
        pe_code = re.sub(r"/\*.*?\*/", "", pe_code, flags=re.DOTALL)
        for needle, label in [
            ("REGISTRY_SAMPLE", "REGISTRY_SAMPLE 标注"),
            ("DemoBadge", "DemoBadge 复用"),
            ("public_extract_nbs.json", "fixture import"),
            ("source_sha256", "provenance SHA 展示"),
        ]:
            if needle not in pe_code:
                errors.append(f"public-extracts/page.tsx missing {label}")
        if all(
            n in pe_code
            for n in ("REGISTRY_SAMPLE", "DemoBadge", "public_extract_nbs.json", "source_sha256")
        ):
            ok("public-extracts/page.tsx: fixture import + REGISTRY_SAMPLE 标注 + provenance")
        # 禁词守门 (per 349 §红线 + docs/06 §6.6): 不评分 / 不排名.
        for pat, label in [
            (r"\bscore\b", "score"),
            (r"\brating\b", "rating"),
            (r"\brank(?:ing)?\b", "rank"),
            (r"\btotal[_-]?score\b", "total_score"),
        ]:
            if re.search(pat, pe_code, re.IGNORECASE):
                errors.append(
                    f"public-extracts/page.tsx contains forbidden term {label!r} "
                    f"(per tasking 349 §红线)"
                )

    # 12b. 首页导航入口: /public-extracts (per 349 §SCHEMA '首页或专用区块').
    if "/public-extracts" not in home_code:
        errors.append("app/page.tsx missing /public-extracts nav anchor (per tasking 349)")
    else:
        ok("app/page.tsx links /public-extracts nav anchor")

    # 12b'. 首页 NBS sample 轨显式 deeplink (per tasking 420 §SCHEMA "本刀做")
    # 镜像 湖北 `#track-hb` 行; 文案标明 REGISTRY_SAMPLE / demo / 非 O1;
    # 含 data-testid 供 pytest 守门; 不动 4 fixture 字节 / SHA.
    if 'href="/public-extracts#track-nbs-sample"' not in home_code:
        errors.append(
            "app/page.tsx missing /public-extracts#track-nbs-sample NBS sample "
            "deeplink anchor (per tasking 420)"
        )
    else:
        ok("app/page.tsx links /public-extracts#track-nbs-sample deeplink")
    if 'data-testid="home-public-extracts-nbs-sample"' not in home_code:
        errors.append(
            "app/page.tsx missing data-testid='home-public-extracts-nbs-sample' "
            "(per tasking 420 §NOW)"
        )
    else:
        ok("app/page.tsx testId=home-public-extracts-nbs-sample")
    for label in ("REGISTRY_SAMPLE", "demo", "非 live O1"):
        if label not in home_code:
            errors.append(
                f"app/page.tsx NBS sample deeplink row missing {label!r} marker "
                f"(per tasking 420)"
            )
    if all(
        s in home_code
        for s in (
            "REGISTRY_SAMPLE",
            "demo",
            "非 live O1",
            "/public-extracts#track-nbs-sample",
            "home-public-extracts-nbs-sample",
        )
    ):
        ok("app/page.tsx NBS sample deeplink row: REGISTRY_SAMPLE / demo / 非 O1")

    # 12b''. 首页 NBS live 候选轨显式 deeplink (per tasking 424 §SCHEMA "本刀做")
    # 镜像 NBS sample `#track-nbs-sample` 行 + 湖北 `#track-hb` 行;
    # 文案标明 LIVE_CANDIDATE / drift 候选 / 非 O1 收口;
    # 含 data-testid 供 pytest 守门; 不动 4 fixture 字节 / SHA;
    # 不引入 next/link; 不分支 params.*.
    if 'href="/public-extracts#track-nbs-live"' not in home_code:
        errors.append(
            "app/page.tsx missing /public-extracts#track-nbs-live NBS live "
            "candidate deeplink anchor (per tasking 424)"
        )
    else:
        ok("app/page.tsx links /public-extracts#track-nbs-live deeplink")
    if 'data-testid="home-public-extracts-nbs-live"' not in home_code:
        errors.append(
            "app/page.tsx missing data-testid='home-public-extracts-nbs-live' "
            "(per tasking 424 §NOW)"
        )
    else:
        ok("app/page.tsx testId=home-public-extracts-nbs-live")
    for label in ("LIVE_CANDIDATE", "drift 候选", "非 O1 收口"):
        if label not in home_code:
            errors.append(
                f"app/page.tsx NBS live deeplink row missing {label!r} marker "
                f"(per tasking 424)"
            )
    if all(
        s in home_code
        for s in (
            "LIVE_CANDIDATE",
            "drift 候选",
            "非 O1 收口",
            "/public-extracts#track-nbs-live",
            "home-public-extracts-nbs-live",
        )
    ):
        ok(
            "app/page.tsx NBS live deeplink row: LIVE_CANDIDATE / drift 候选 "
            "/ 非 O1 收口"
        )

    # 12c. LIVE_CANDIDATE 并列分轨 — knife 55 (tasking 358). Per `358` §SCHEMA:
    #     (1) live WORM 提取 fixture 在位 (LIVE_CANDIDATE 语义);
    #     (2) /public-extracts 展示 live 候选区块 (显式非 O1);
    #     (3) sample 分轨不被覆盖 (row_count 仍 63 / registry SHA 锚定不变).
    live_fixture_path = ROOT / "lib/public_extract_nbs_live_candidate.json"
    if not live_fixture_path.is_file():
        errors.append(
            "lib/public_extract_nbs_live_candidate.json missing (per tasking 358 §NOW-1)"
        )
    else:
        try:
            lfx = json.loads(live_fixture_path.read_text(encoding="utf-8"))
            if lfx.get("intake_status") != "LIVE_CANDIDATE":
                errors.append(
                    f"live candidate fixture: intake_status={lfx.get('intake_status')!r} "
                    f"!= LIVE_CANDIDATE"
                )
            if lfx.get("is_demo") != "true":
                errors.append("live candidate fixture: is_demo != 'true' (333 候选惯例)")
            if not isinstance(lfx.get("rows"), list) or len(lfx["rows"]) < 1:
                errors.append("live candidate fixture: rows empty (≥1 行可见 per 358)")
            else:
                ok(
                    f"public_extract_nbs_live_candidate.json: LIVE_CANDIDATE fixture "
                    f"在位 ({lfx.get('row_count')} 行)"
                )
            if fixture_path.is_file():
                sfx = json.loads(fixture_path.read_text(encoding="utf-8"))
                if sfx.get("row_count") != 63 or sfx.get("source_sha256") != (
                    "dea13b8a4ff116ca91403b189cdd60705545b28200f9023c3d56e6db03f3939d"
                ):
                    errors.append(
                        "REGISTRY_SAMPLE fixture 被覆盖/漂移 (row_count 或 registry "
                        "SHA 锚定变化; per 358 §红线 'sample 与 live candidate 分轨')"
                    )
        except json.JSONDecodeError as e:
            errors.append(f"public_extract_nbs_live_candidate.json is not valid JSON: {e}")
    if pe_page_path.is_file():
        pe_src_full = pe_page_path.read_text(encoding="utf-8")
        pe_code2 = re.sub(r"//[^\n]*", "", pe_src_full)
        pe_code2 = re.sub(r"/\*.*?\*/", "", pe_code2, flags=re.DOTALL)
        for needle, label in [
            ("public_extract_nbs_live_candidate.json", "live candidate fixture import"),
            ("LIVE_CANDIDATE", "LIVE_CANDIDATE 标注"),
            ("source_deeplink_url", "live deeplink provenance"),
            ("非 O1 收口", "非 O1 免责"),
        ]:
            if needle not in pe_code2:
                errors.append(f"public-extracts/page.tsx missing {label} (per tasking 358)")
        if all(
            n in pe_code2
            for n in (
                "public_extract_nbs_live_candidate.json",
                "LIVE_CANDIDATE",
                "source_deeplink_url",
                "非 O1 收口",
            )
        ):
            ok("public-extracts/page.tsx: LIVE_CANDIDATE 分轨区块 + 非 O1 免责")

    # 12d. 深圳 REGISTRY_SAMPLE 分节 — knife 59 (tasking 370). Per `370` §SCHEMA:
    #     (1) sz.gov.cn MUNICIPAL_BULLETIN 散文抽取 fixture 在位 (71 行);
    #     (2) /public-extracts 展示深圳 REGISTRY_SAMPLE 分节 (显式 demo);
    #     (3) NBS sample/live 两轨不被覆盖 (63 行 / registry SHA / live 锚不变).
    sz_fixture_path = ROOT / "lib/public_extract_sz.json"
    if not sz_fixture_path.is_file():
        errors.append(
            "lib/public_extract_sz.json missing (per tasking 370 §NOW-1)"
        )
    else:
        try:
            zfx = json.loads(sz_fixture_path.read_text(encoding="utf-8"))
            if zfx.get("domain") != "sz.gov.cn":
                errors.append(f"public_extract_sz.json: domain != sz.gov.cn")
            if zfx.get("category") != "MUNICIPAL_BULLETIN":
                errors.append(
                    f"public_extract_sz.json: category != MUNICIPAL_BULLETIN"
                )
            if zfx.get("row_count") != 71 or not isinstance(
                zfx.get("rows"), list
            ) or len(zfx["rows"]) != 71:
                errors.append(
                    "public_extract_sz.json: 散文抽取应为 71 行 "
                    "(row_count 与 rows 长度一致, per 368)"
                )
            else:
                ok("public_extract_sz.json: 深圳 REGISTRY_SAMPLE fixture 在位 (71 行)")
            if not str(zfx.get("source_sha256", "")).startswith("d5e2c73196b43cec"):
                errors.append(
                    "public_extract_sz.json: source_sha256 未锚定 registry "
                    "file_hash_sha256 (d5e2c731…, per 370 §红线)"
                )
            # NBS 双轨不回归: sample 63/dea13b8a + live fixture 锚不变.
            if fixture_path.is_file():
                sfx2 = json.loads(fixture_path.read_text(encoding="utf-8"))
                if sfx2.get("row_count") != 63 or sfx2.get("source_sha256") != (
                    "dea13b8a4ff116ca91403b189cdd60705545b28200f9023c3d56e6db03f3939d"
                ):
                    errors.append(
                        "NBS REGISTRY_SAMPLE fixture 被深圳分节覆盖/漂移 "
                        "(row_count 或 registry SHA 锚变化; per 370 §红线)"
                    )
            if live_fixture_path.is_file():
                lfx2 = json.loads(live_fixture_path.read_text(encoding="utf-8"))
                if lfx2.get("intake_status") != "LIVE_CANDIDATE" or not str(
                    lfx2.get("source_sha256", "")
                ).startswith("0b85212f70055c38"):
                    errors.append(
                        "NBS LIVE_CANDIDATE fixture 被深圳分节覆盖/漂移 "
                        "(intake_status 或 drift SHA 锚变化; per 370 §红线)"
                    )
        except json.JSONDecodeError as e:
            errors.append(f"public_extract_sz.json is not valid JSON: {e}")
    if pe_page_path.is_file():
        pe_src3 = pe_page_path.read_text(encoding="utf-8")
        pe_code3 = re.sub(r"//[^\n]*", "", pe_src3)
        pe_code3 = re.sub(r"/\*.*?\*/", "", pe_code3, flags=re.DOTALL)
        for needle, label in [
            ("public_extract_sz.json", "SZ fixture import"),
            ("MUNICIPAL_BULLETIN", "MUNICIPAL_BULLETIN 标注"),
            ("散文段落表", "深圳散文分节"),
            ("SSL 暂缓", "非 live 免责 (SSL 暂缓)"),
        ]:
            if needle not in pe_code3:
                errors.append(
                    f"public-extracts/page.tsx missing {label} (per tasking 370)"
                )
        if all(
            n in pe_code3
            for n in (
                "public_extract_sz.json",
                "MUNICIPAL_BULLETIN",
                "散文段落表",
                "SSL 暂缓",
            )
        ):
            ok("public-extracts/page.tsx: 深圳 REGISTRY_SAMPLE 分节 + 非 live 免责")

    # §12e — 湖北 PROVINCIAL_BULLETIN (xlsx) 第四分节 (per tasking 376)
    # LIVE NOT allowed: enabled=FALSE 暂缓; 仅 REGISTRY_SAMPLE demo.
    hb_fixture_path = ROOT / "lib/public_extract_hubei.json"
    if not hb_fixture_path.is_file():
        errors.append(
            "lib/public_extract_hubei.json missing (per tasking 376 §NOW-2)"
        )
    else:
        try:
            hfx = json.loads(hb_fixture_path.read_text(encoding="utf-8"))
            if hfx.get("domain") != "tjj.hubei.gov.cn":
                errors.append(
                    "public_extract_hubei.json: domain != tjj.hubei.gov.cn"
                )
            if hfx.get("category") != "PROVINCIAL_BULLETIN":
                errors.append(
                    "public_extract_hubei.json: category != PROVINCIAL_BULLETIN"
                )
            rc = hfx.get("row_count")
            rows = hfx.get("rows") or []
            if not isinstance(rows, list) or len(rows) < 1:
                errors.append(
                    "public_extract_hubei.json: rows empty (≥1 行可见 per 376)"
                )
            elif rc != len(rows):
                errors.append(
                    f"public_extract_hubei.json: row_count={rc} != len(rows)={len(rows)}"
                )
            elif rc != 21:
                errors.append(
                    f"public_extract_hubei.json: row_count={rc} (任务书 376 期望 ≈21)"
                )
            else:
                ok("public_extract_hubei.json: 湖北 REGISTRY_SAMPLE fixture 在位 (21 行)")
            sha = (hfx.get("source_sha256") or "").lower()
            if not sha.startswith("c5cf5abeb4fdf97a"):
                errors.append(
                    "public_extract_hubei.json: source_sha256 未锚定 registry (期望 c5cf5abeb4fdf97a…)"
                )
            else:
                ok("public_extract_hubei.json: source_sha256 与 registry 锚一致")
        except json.JSONDecodeError as e:
            errors.append(f"public_extract_hubei.json is not valid JSON: {e}")

    # 页面针 (§12e 配套) — 注释先剥再扫 (per 红线惯例)
    pe_page_path = ROOT / "app/public-extracts/page.tsx"
    if pe_page_path.is_file():
        pe_src4 = pe_page_path.read_text(encoding="utf-8")
        pe_code4 = re.sub(r"//[^\n]*", "", pe_src4)
        pe_code4 = re.sub(r"/\*.*?\*/", "", pe_code4, flags=re.DOTALL)
        for needle, label in [
            ("public_extract_hubei.json", "HB fixture import"),
            ("PROVINCIAL_BULLETIN", "PROVINCIAL_BULLETIN 标注"),
            ("月报统计表", "湖北月报分节"),
            ("enabled=FALSE", "live FALSE 暂缓"),
        ]:
            if needle not in pe_code4:
                errors.append(
                    f"public-extracts/page.tsx missing {label} (per tasking 376)"
                )
        if all(
            n in pe_code4
            for n in (
                "public_extract_hubei.json",
                "PROVINCIAL_BULLETIN",
                "月报统计表",
                "enabled=FALSE",
            )
        ):
            ok("public-extracts/page.tsx: 湖北 REGISTRY_SAMPLE 分节 + live FALSE 暂缓")

    # §12f — 四轨一览条 (overview strip) (per tasking 382)
    # 仅读自既有 4 fixture (NBS sample/live + SZ + HB), 不重算;
    # 锚点链到四分节 (id="track-nbs-sample" / "track-nbs-live" / "track-sz" / "track-hb").
    if pe_page_path.is_file():
        pe_src5 = pe_page_path.read_text(encoding="utf-8")
        pe_code5 = re.sub(r"//[^\n]*", "", pe_src5)
        pe_code5 = re.sub(r"/\*.*?\*/", "", pe_code5, flags=re.DOTALL)
        for needle, label in [
            ("public-extracts-page__overview-strip", "overview strip CSS class"),
            ("四轨一览 (overview)", "overview strip 标题"),
            ("track-nbs-sample", "NBS sample 锚点"),
            ("track-nbs-live", "NBS live 锚点"),
            ("track-sz", "深圳分节锚点"),
            ("track-hb", "湖北分节锚点"),
            ("#track-nbs-sample", "NBS sample 锚链"),
            ("#track-nbs-live", "NBS live 锚链"),
            ("#track-sz", "深圳分节锚链"),
            ("#track-hb", "湖北分节锚链"),
            ("REGISTRY_SAMPLE_INTAKED", "sample 轨标注"),
            ("LIVE_CANDIDATE, drift", "live 候选 drift 标注"),
            ("四轨皆 demo/candidate", "非 O1/Gate PASS 守门"),
        ]:
            if needle not in pe_code5:
                errors.append(
                    f"public-extracts/page.tsx missing {label} (per tasking 382)"
                )
        if all(
            n in pe_code5
            for n in (
                "public-extracts-page__overview-strip",
                "track-nbs-sample",
                "track-nbs-live",
                "track-sz",
                "track-hb",
                "四轨皆 demo/candidate",
            )
        ):
            ok(
                "public-extracts/page.tsx: 四轨一览条 overview strip 在位 + "
                "4 锚点 (sample/live/sz/hb) + 非 O1/Gate PASS 守门"
            )

    # §12g — JSON 静态下载 (per tasking 388)
    # 4 fixture 字节一致拷到 frontend/public/public-extracts/{nbs,nbs-live-candidate,
    # sz,hubei}.json; 一览表增「下载 JSON」列 (download attr + /public-extracts/*.json 锚).
    public_dir = ROOT / "public" / "public-extracts"
    public_files = {
        "nbs.json": ROOT / "lib" / "public_extract_nbs.json",
        "nbs-live-candidate.json": ROOT
        / "lib"
        / "public_extract_nbs_live_candidate.json",
        "sz.json": ROOT / "lib" / "public_extract_sz.json",
        "hubei.json": ROOT / "lib" / "public_extract_hubei.json",
    }
    for pub_name, fixture_path in public_files.items():
        pub_path = public_dir / pub_name
        if not pub_path.is_file():
            errors.append(
                f"public/public-extracts/{pub_name} missing (per tasking 388 §SCHEMA-1)"
            )
            continue
        try:
            pub_bytes = pub_path.read_bytes()
            fix_bytes = fixture_path.read_bytes()
            if pub_bytes != fix_bytes:
                errors.append(
                    f"public/public-extracts/{pub_name} 字节不一致 fixture "
                    f"(per tasking 388 §红线 字节一致)"
                )
            else:
                ok(
                    f"public/public-extracts/{pub_name} 字节 == "
                    f"{fixture_path.name} (size={len(pub_bytes)})"
                )
        except OSError as e:
            errors.append(
                f"public/public-extracts/{pub_name} read fail: {e}"
            )

    # 一览表「下载 JSON」列 + 4 download 链 + /public-extracts/*.json 锚
    if pe_page_path.is_file():
        pe_src6 = pe_page_path.read_text(encoding="utf-8")
        pe_code6 = re.sub(r"//[^\n]*", "", pe_src6)
        pe_code6 = re.sub(r"/\*.*?\*/", "", pe_code6, flags=re.DOTALL)
        for needle, label in [
            ("下载 JSON", "下载 JSON 列头"),
            ('href="/public-extracts/nbs.json"', "NBS 下载链"),
            ("download=\"public-extracts-nbs.json\"", "NBS download attr"),
            ('href="/public-extracts/nbs-live-candidate.json"', "NBS live 下载链"),
            (
                "download=\"public-extracts-nbs-live-candidate.json\"",
                "NBS live download attr",
            ),
            ('href="/public-extracts/sz.json"', "深圳下载链"),
            ("download=\"public-extracts-sz.json\"", "深圳 download attr"),
            ('href="/public-extracts/hubei.json"', "湖北下载链"),
            ("download=\"public-extracts-hubei.json\"", "湖北 download attr"),
        ]:
            if needle not in pe_code6:
                errors.append(
                    f"public-extracts/page.tsx missing {label} (per tasking 388 §SCHEMA-2)"
                )
        if all(
            n in pe_code6
            for n in (
                "下载 JSON",
                "/public-extracts/nbs.json",
                "/public-extracts/nbs-live-candidate.json",
                "/public-extracts/sz.json",
                "/public-extracts/hubei.json",
            )
        ):
            ok(
                "public-extracts/page.tsx: 下载 JSON 列 + 4 download 链 "
                "(nbs / nbs-live-candidate / sz / hubei)"
            )

    # §12h — 四轨轻量行筛选 (per tasking 397)
    # 每轨数据表上方独立 input (客户端包含匹配); 纯客户端 (use client +
    # useState), 不改 fixture 字节/SHA; 须标非权威库检索; 空匹配占位.
    if pe_page_path.is_file():
        pe_src7 = pe_page_path.read_text(encoding="utf-8")
        pe_code7 = re.sub(r"//[^\n]*", "", pe_src7)
        pe_code7 = re.sub(r"/\*.*?\*/", "", pe_code7, flags=re.DOTALL)
        for needle, label in [
            ('"use client"', "use client 指令 (纯客户端筛选)"),
            ("useState(", "useState 状态 (4 轨筛选查询)"),
            ("data-testid={props.testId}", "testId 渲染为 data-testid 属性"),
            (
                'testId="track-filter-nbs-sample"',
                "NBS sample 轨筛选 input",
            ),
            ('testId="track-filter-nbs-live"', "NBS live 轨筛选 input"),
            ('testId="track-filter-sz"', "深圳轨筛选 input"),
            ('testId="track-filter-hb"', "湖北轨筛选 input"),
            ("toLowerCase().includes(", "包含匹配 + 大小写不敏感过滤逻辑"),
            ("匹配 {props.matched} / {props.total} 行", "匹配计数行"),
            ("非权威库检索", "筛选非权威库检索守门"),
            ("无匹配行", "空匹配占位行"),
        ]:
            if needle not in pe_code7:
                errors.append(
                    f"public-extracts/page.tsx missing {label} (per tasking 397)"
                )
        if all(
            n in pe_code7
            for n in (
                '"use client"',
                "useState(",
                'testId="track-filter-nbs-sample"',
                'testId="track-filter-nbs-live"',
                'testId="track-filter-sz"',
                'testId="track-filter-hb"',
                "toLowerCase().includes(",
                "非权威库检索",
            )
        ):
            ok(
                "public-extracts/page.tsx: 四轨行筛选 input (testid ×4) + "
                "客户端包含匹配 + 非权威库检索守门"
            )

    # §12i — 四轨 CSV 静态下载 (per tasking 403)
    # 4 fixture 经 scripts/gen_public_extracts_csv.py 确定性渲染为
    # frontend/public/public-extracts/*.csv (列序=首行键序, 不重命名);
    # overview「下载 JSON / CSV」列同格第二链; JSON 链不回归; 非权威库守门.
    csv_dir = ROOT / "public" / "public-extracts"
    for csv_name in (
        "nbs.csv",
        "nbs-live-candidate.csv",
        "sz.csv",
        "hubei.csv",
    ):
        csv_path = csv_dir / csv_name
        if not csv_path.is_file():
            errors.append(
                f"public/public-extracts/{csv_name} missing (per tasking 403 §SCHEMA-1)"
            )
        elif csv_path.stat().st_size == 0:
            errors.append(
                f"public/public-extracts/{csv_name} empty (per tasking 403 §SCHEMA-1)"
            )
        else:
            ok(f"public/public-extracts/{csv_name} 在位 ({csv_path.stat().st_size} bytes)")
    if pe_page_path.is_file():
        pe_src8 = pe_page_path.read_text(encoding="utf-8")
        pe_code8 = re.sub(r"//[^\n]*", "", pe_src8)
        pe_code8 = re.sub(r"/\*.*?\*/", "", pe_code8, flags=re.DOTALL)
        for needle, label in [
            ("下载 JSON / CSV", "下载 JSON / CSV 列头"),
            ('href="/public-extracts/nbs.csv"', "NBS CSV 下载链"),
            ('download="public-extracts-nbs.csv"', "NBS CSV download attr"),
            ('href="/public-extracts/nbs-live-candidate.csv"', "NBS live CSV 下载链"),
            (
                'download="public-extracts-nbs-live-candidate.csv"',
                "NBS live CSV download attr",
            ),
            ('href="/public-extracts/sz.csv"', "深圳 CSV 下载链"),
            ('download="public-extracts-sz.csv"', "深圳 CSV download attr"),
            ('href="/public-extracts/hubei.csv"', "湖北 CSV 下载链"),
            ('download="public-extracts-hubei.csv"', "湖北 CSV download attr"),
            ("JSON / CSV 下载皆为 fixture 快照确定性导出", "CSV 非权威库守门"),
            ("非权威库", "非权威库字样"),
        ]:
            if needle not in pe_code8:
                errors.append(
                    f"public-extracts/page.tsx missing {label} (per tasking 403 §SCHEMA-2)"
                )
        # JSON 链不回归 (§12g 语义在 §12i 语境复检)
        for json_href in (
            "/public-extracts/nbs.json",
            "/public-extracts/nbs-live-candidate.json",
            "/public-extracts/sz.json",
            "/public-extracts/hubei.json",
        ):
            if json_href not in pe_code8:
                errors.append(
                    f"public-extracts/page.tsx JSON 下载链回归缺失: {json_href} "
                    f"(per tasking 403 §禁止 破坏 JSON 下载)"
                )
        if all(
            n in pe_code8
            for n in (
                "下载 JSON / CSV",
                "/public-extracts/nbs.csv",
                "/public-extracts/nbs-live-candidate.csv",
                "/public-extracts/sz.csv",
                "/public-extracts/hubei.csv",
                "非权威库",
            )
        ):
            ok(
                "public-extracts/page.tsx: 下载 JSON / CSV 列 + 4 CSV download 链 "
                "+ 非权威库守门 (JSON 链不回归)"
            )

    # §13 — 深圳城页链到 /public-extracts#track-sz (per tasking 391)
    # CityPage.tsx + CityPageMart.tsx 各含 slug/cityId === 'shenzhen'
    # 条件分支 → /public-extracts#track-sz 链 + REGISTRY_SAMPLE demo 标注 +
    # 非 O1 守门; 不允许无条件链接 (会污染其它城页).
    cp_path = ROOT / "app" / "components" / "CityPage.tsx"
    cpm_path = ROOT / "app" / "components" / "CityPageMart.tsx"
    for label, file_path, slug_cond in (
        ("CityPage", cp_path, 'slug === "shenzhen"'),
        ("CityPageMart", cpm_path, 'cityId === "shenzhen"'),
    ):
        if not file_path.is_file():
            errors.append(f"{label}.tsx missing (per tasking 391)")
            continue
        src = file_path.read_text(encoding="utf-8")
        code = re.sub(r"//[^\n]*", "", src)
        code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
        for needle, desc in (
            (slug_cond, f"{label} shenzhen 条件分支"),
            ("/public-extracts#track-sz", f"{label} /public-extracts#track-sz 链"),
            ("REGISTRY_SAMPLE", f"{label} demo 标注"),
            ("非 O1", f"{label} 非 O1 守门"),
        ):
            if needle not in code:
                errors.append(
                    f"{label}.tsx missing {desc} (per tasking 391)"
                )
        if all(
            n in code
            for n in (
                slug_cond,
                "/public-extracts#track-sz",
                "REGISTRY_SAMPLE",
                "非 O1",
            )
        ):
            ok(
                f"{label}.tsx: shenzhen 条件分支 → /public-extracts#track-sz 链 "
                f"+ REGISTRY_SAMPLE demo 标注 + 非 O1 守门"
            )

    # §13b — 首页湖北轨链 (per tasking 394; 无湖北专用页 → 首页兜底)
    # page.tsx 公开提取表格 + 一行「公开提取湖北轨」→ /public-extracts#track-hb
    # + REGISTRY_SAMPLE / xlsx / enabled=FALSE / 非 O1 提示.
    home_path = ROOT / "app" / "page.tsx"
    if home_path.is_file():
        home_src = home_path.read_text(encoding="utf-8")
        home_code = re.sub(r"//[^\n]*", "", home_src)
        home_code = re.sub(r"/\*.*?\*/", "", home_code, flags=re.DOTALL)
        for needle, desc in (
            ("公开提取湖北轨", "首页湖北轨行"),
            ("/public-extracts#track-hb", "首页 #track-hb 链"),
            ("PROVINCIAL_BULLETIN", "首页 PROVINCIAL_BULLETIN 标注"),
            ("enabled=FALSE", "首页 live FALSE 暂缓"),
            ("非 live O1", "首页非 O1 守门"),
        ):
            if needle not in home_code:
                errors.append(
                    f"app/page.tsx missing {desc} (per tasking 394)"
                )
        if all(
            n in home_code
            for n in (
                "公开提取湖北轨",
                "/public-extracts#track-hb",
                "enabled=FALSE",
                "非 live O1",
            )
        ):
            ok(
                "app/page.tsx: 公开提取湖北轨行 → /public-extracts#track-hb 链 "
                "+ REGISTRY_SAMPLE xlsx demo + enabled=FALSE 暂缓 + 非 O1 守门"
            )

    # §13c — 全站顶栏 /public-extracts 常驻链 (per tasking 409)
    # layout.tsx 含 <nav data-testid="site-nav"> + href="/public-extracts" + "四轨 demo"
    # 标注; 不分支 params.* (静态布局); 不走 Next.js Link (避免 dynamic params);
    # 仅纯 <a> 锚链; 含非 O1 守门; build 仍 ○ Static.
    layout_path = ROOT / "app" / "layout.tsx"
    if not layout_path.is_file():
        errors.append("app/layout.tsx missing (per tasking 409)")
    else:
        layout_src = layout_path.read_text(encoding="utf-8")
        layout_code = re.sub(r"//[^\n]*", "", layout_src)
        layout_code = re.sub(r"/\*.*?\*/", "", layout_code, flags=re.DOTALL)
        for needle, desc in (
            ('data-testid="site-nav"', "site-nav 容器"),
            ('href="/public-extracts"', "site-nav /public-extracts 链"),
            ('data-testid="site-nav-public-extracts"', "site-nav 链 testId"),
            ("四轨 demo", "site-nav 四轨 demo 标注"),
            ("非 O1", "site-nav 非 O1 守门"),
            ("不宣布 Gate PASS", "site-nav 非 Gate PASS 守门"),
        ):
            if needle not in layout_code:
                errors.append(f"app/layout.tsx missing {desc} (per tasking 409)")
        # 静态路由守门: 不得分支 params.* (per AGENTS.md standing red line)
        if re.search(r"params\s*\.|\.params\b", layout_code):
            errors.append(
                "app/layout.tsx branches on params.* (forbidden per AGENTS.md "
                "static-segment Next.js route rule)"
            )
        if all(
            n in layout_code
            for n in (
                'data-testid="site-nav"',
                'href="/public-extracts"',
                "四轨 demo",
                "非 O1",
            )
        ):
            ok(
                "app/layout.tsx: 顶栏 site-nav 在位 + /public-extracts 常驻链 "
                "+ 四轨 demo 标注 + 非 O1 守门 + 不分支 params.*"
            )

    if errors:
        for e in errors:
            fail(e)
        return 1

    print(
        "\n=== S2.0.1 + S2.7-a + S2.7-a2 + S2.7-b-lite + S2.7-b-full-lite mart-shape "
        "+ home nav (S2.7-a + S2.7-b + S2.8-lite + S2.9-lite, per tasking 280) smoke: PASS ==="
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())