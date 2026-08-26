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

    if errors:
        for e in errors:
            fail(e)
        return 1

    print("\n=== S2.0.1 + S2.7-a + S2.7-a2 + S2.7-b-lite skeleton smoke: PASS ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())