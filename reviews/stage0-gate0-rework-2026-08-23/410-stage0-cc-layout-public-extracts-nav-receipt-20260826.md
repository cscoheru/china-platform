# 410 — 全站顶栏 /public-extracts 常驻链 · CC 回执

- 编号：`410-stage0-cc-layout-public-extracts-nav-receipt-20260826`
- 任务书：`409-stage2-layout-public-extracts-nav-tasking-20260826`
- 作者：CC（heartbeat 84）
- cc_head：`f5151ee`
- 日期：2026-08-26

---

## §NOW 对照

| 409 §SCHEMA 裁定 | 交付 | 证据 |
|---|---|---|
| (1) `frontend/app/layout.tsx` 顶栏增全站常驻链 `/public-extracts`（四轨 demo / 非 O1） | ✅ `layout.tsx` 在 `<header>` 后插入 `<nav data-testid="site-nav">`：含 `<a href="/" data-testid="site-nav-home">首页</a>` + `<a href="/public-extracts" data-testid="site-nav-public-extracts">公开提取样本（四轨 demo）</a>`；旁注「全站顶栏常驻链；四轨 demo / 非 O1 / 不宣布 Gate PASS（per tasking 409）」；纯 `<a>` 锚链未引入 next/link（保留 build ○ Static）；不分支 `params.*`（AGENTS.md 静态路由红线） | diff |
| (2) banner 补一句主演示入口 | ✅ nav 旁注 + 链接文案「公开提取样本（四轨 demo）」即主演示入口；nav 紧贴 `<header>` banner 之下，主入口语义清晰 | diff |
| (3) ≥1 smoke/pytest | ✅ **5 pytest cases + smoke §13c 门（6 针）**：<br>• `test_layout_has_site_nav_container`（`data-testid="site-nav"` 容器）；<br>• `test_layout_site_nav_links_public_extracts`（`href="/public-extracts"` + `data-testid="site-nav-public-extracts"`）；<br>• `test_layout_site_nav_disclaimer_and_no_o1_or_gate_pass_claim`（四轨 demo + 非 O1 + 不宣布 Gate PASS 三句必含）；<br>• `test_layout_does_not_branch_on_params`（AGENTS.md 静态路由红线）；<br>• `test_layout_site_nav_uses_anchor_not_nextjs_link`（纯 `<a>` 锚链 + 不引入 next/link）；<br>• smoke §13c — `site-nav` 容器 + `/public-extracts` 链 + 链 testId + 四轨 demo + 非 O1 + 不宣布 Gate PASS + 不分支 `params.*` | pytest + smoke |
| (4) 回执 `410`（`-cc-`） | ✅ 本文件名 | — |

## 证据

```
$ python3 frontend/smoke-check.py
✅ app/layout.tsx: 顶栏 site-nav 在位 + /public-extracts 常驻链 + 四轨 demo 标注 + 非 O1 守门 + 不分支 params.*
=== … smoke: PASS ===

$ python3 -m pytest tests/test_layout_site_nav_public_extracts.py -q
5 passed in 0.98s

$ python3 -m pytest tests/test_layout_site_nav_public_extracts.py \
                    tests/test_public_extract_frontend_fixture.py \
                    tests/test_public_extracts_csv_download.py \
                    tests/test_shenzhen_city_link_public_extract.py \
                    tests/test_hubei_home_link_public_extract.py -q
50 passed in 0.62s                  # 全回归绿

$ cd frontend && npm run build
✓ Generating static pages (22/22)
├ ○ /public-extracts    15.9 kB    103 kB      # 仍 ○ Static（无 dynamic 退化）

$ python3 scripts/_knife72_manifest_bump.py
ADD: tests/test_layout_site_nav_public_extracts.py (…)
ADD: scripts/_knife72_manifest_bump.py (…)
ADD: reviews/.../410-…-receipt-20260826.md (…)
UPDATE artifact_count: 720 → 723
INVARIANT: sum(role_count)=723 == artifact_count=723 == len(artifacts)=723
```

## 交付清单

| 文件 | 变更 | role |
|---|---|---|
| `frontend/app/layout.tsx` | MODIFIED（`<nav data-testid="site-nav">` + 首页 + `/public-extracts` 链 + 旁注四轨 demo / 非 O1 / 不宣布 Gate PASS） | 已入 manifest（SKIP，SHA REFRESH 不增计数 per knife 44 先例） |
| `frontend/smoke-check.py` | MODIFIED（+ §13c 门 6 针） | 已入 manifest（SKIP） |
| `tests/test_layout_site_nav_public_extracts.py` | NEW（5 cases：container / link / disclaimer / no-params-branch / anchor-not-Link） | `schema_negative_test` |
| `scripts/_knife72_manifest_bump.py` | NEW | `spike_helper` |
| `reviews/.../410-stage0-cc-layout-public-extracts-nav-receipt-20260826.md` | NEW（本文件） | `documentation` |

## Pack 不变量

`_knife72_manifest_bump.py`：NEW_ARTIFACTS +3（test + bump + receipt）→ **720 → 723**；`sum(role_count) == artifact_count == len(artifacts) == 723`（`layout.tsx` / `smoke-check.py` 皆 SHA REFRESH 不增计数；前置 knife 70 已落 710 → 718；knife 69 = docs/45+53 行筛选登记 708 → 710；knife 68 = 四轨客户端行筛选 706 → 708）。

## 红线自查

- ❌ 未改 fixture（仅 layout + smoke + test）
- ❌ 未 Gate/O1 PASS 宣告（nav 旁注 + smoke §13c + 三处 pytest case 显式「非 O1 / 不宣布 Gate PASS」守门）
- ❌ 未引入 next/link（纯 `<a href>` 锚链；不触发 dynamic params；build 仍 ○ Static）
- ❌ 未分支 `params.*`（layout 是 root 静态布局，pytest `test_layout_does_not_branch_on_params` 锁定）
- ❌ 未动 `00-CC-CURRENT.md` / 未动 `gate_thresholds.json` / 未 --force / 未索要 PAT
- ✅ 回执文件名含 `-cc-`；receipt 位于 `reviews/stage0-gate0-rework-2026-08-23/`
- ✅ 「公开提取样本（四轨 demo）」文案与首页 / public-extracts 内部一致；不谎称四轨=O1

## 下一步

`git push origin HEAD && git push github HEAD`（**必须双推** per §NOW）→ 回填 cc_head（单独 commit，再双推）→ `./scripts/cc_gate_watch.sh --pull` → **84 POLL**（等 Cursor 审计 411）。