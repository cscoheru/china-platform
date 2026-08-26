# 442 — docs/50 §4.4 首页公开提取入口一览里程碑补登 · CC 回执

- 编号：`442-stage0-cc-docs50-home-entry-index-milestone-receipt-20260826`
- 任务书：`442-stage2-docs50-home-entry-index-milestone-tasking-20260826`
- 作者：CC（heartbeat 84）
- cc_head：（待双推回填）
- 日期：2026-08-26

---

## §NOW 对照

| 442 §SCHEMA 裁定 | 交付 | 证据 |
|---|---|---|
| (1) `docs/50` §4.4 里程碑表补 1 行：**首页公开提取入口一览**（`docs/53` §5；回执 `440`；site-nav + 4 首页 deeplink）| ✅ docs/50-stage2-gate2-review-packet-draft-20260826.md §4.4 里程碑表末尾（首页四轨一览 overview 显式 deeplink 行后）新增 1 行：「**首页公开提取入口一览**（顶栏 site-nav + 首页表内 4 deeplink 端到端入口演示汇总）」；交付列描述 5 行 docs/53 §5 markdown 表（(a) 全站顶栏 site-nav → `/public-extracts` + (b) 首页表内 NBS sample 轨 → `#track-nbs-sample` + (c) 首页表内 NBS live 候选轨 → `#track-nbs-live` + (d) 首页表内四轨一览 overview strip → `#overview` + (e) 首页表内湖北轨 → `#track-hb`）；回执列 `440` + `6d54d63`；守门列 smoke §13c + §12b' + §12b'' + §12b'''（4 入口合计 18 针）+ pytest 3+5+3+3 = 14 cases（`test_layout_site_nav_public_extracts.py` + `test_nbs_home_deeplink_public_extract.py` + `test_nbs_live_home_deeplink_public_extract.py` + `test_overview_home_deeplink_public_extract.py`）+ 4 fixture byte SHA 前 8 锁不漂：`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c` 与 knife 76/78/81/82/84/85 完全一致；不引入 `next/link` 保留 build ○ Static 22/22；不分支 `params.*`（AGENTS.md 静态路由红线）；§4.4 intro ⚠ 收据链 +1（`344` → `413` → `436` → `440`） | diff |
| (2) 链 `docs/45`/`53` | ✅ docs/45 §6.2 +1 行（per knife 86 docs/53 §5 首页公开提取入口一览 互链 + 回执 `440`）+ docs/53 §5 新增 5 行 markdown 表（per 回执 `440` + commit `0ad62e0` + cc_head backfill `6d54d63`）；双向对账已在 knife 86 闭环 | diff（已闭环）|
| (3) 非 O1/Gate PASS | ✅ 新行回执列前缀「**首页公开提取入口一览**（顶栏 site-nav + 首页表内 4 deeplink 端到端入口演示汇总）」+ 交付列结尾「**5 行均显式 demo/candidate 演示、非 O1/Gate PASS**」；§4.4 intro ⚠「**全部为 demo/candidate 演示，非 O1/Gate 收口**」原样保留 | diff |
| (4) 回执 `442`（`-cc-`）| ✅ 本文件名 | — |

## 证据

```
$ grep -n "首页公开提取入口一览\|440.*6d54d63" docs/50-stage2-gate2-review-packet-draft-20260826.md | head -10
  183:> ⚠ **本节是公开提取演示里程碑的端到端交付清单**（回执链 `344` → `362` → `368` → `371` → `377` → `383` → `398` → `404` → `410` → `413` → `436` → `440`）；...
  199:| **首页公开提取入口一览**（顶栏 site-nav + 首页表内 4 deeplink 端到端入口演示汇总）| `docs/53-stage2-public-ingest-ops-handbook-20260826.md` §5 新增 5 行 markdown 表「首页公开提取入口一览」...

$ python3 scripts/_knife87_manifest_bump.py
ADD: scripts/_knife87_manifest_bump.py (…)
ADD: reviews/.../442-…-receipt-20260826.md (…)
UPDATE artifact_count: 754 → 756
INVARIANT: sum(role_count)=756 == artifact_count=756 == len(artifacts)=756
```

## 交付清单

| 文件 | 变更 | role |
|---|---|---|
| `docs/50-stage2-gate2-review-packet-draft-20260826.md` | MODIFIED（§4.4 里程碑表 +1 行 + §4.4 intro ⚠ 收据链 +1）| 已入 manifest（SKIP，SHA REFRESH 不增计数 per knife 44 先例）|
| `scripts/_knife87_manifest_bump.py` | NEW | `spike_helper` |
| `reviews/.../442-stage0-cc-docs50-home-entry-index-milestone-receipt-20260826.md` | NEW（本文件）| `documentation` |

## Pack 不变量

`_knife87_manifest_bump.py`：NEW_ARTIFACTS +2（bump + receipt）→ **754 → 756**；`sum(role_count) == artifact_count == len(artifacts) == 756`（docs/50 已入 manifest，SHA REFRESH 不增计数；前置 knife 86 docs/45 + docs/53 首页公开提取入口一览 + docs/53 §5 5 行表 已落 752 → 754；前置 knife 85 docs/45 + docs/53 ↔ docs/50 §4.4 overview 首页 deeplink 互链 已落 750 → 752）。

## docs/50 ↔ docs/45 + docs/53 三向对账

| docs/50 位置 | 内容 | 指向 |
|---|---|---|
| §4.4 intro ⚠ line 183 | 收据链 `344` → `413` → `436` → `440`（新增 `436` `440`）| knife 84 + 86 双闭环 |
| §4.4 行 199（新增）| 首页公开提取入口一览 行（5 行 markdown 表汇总）| docs/53 §5 line 126-136（5 行表）+ docs/45 §6.2 line 257 |
| §4.4 行 198 | 首页四轨一览 overview 显式 deeplink（per 回执 432 + `a23e5c8`）| docs/45 §6.2 + §7 + docs/53 §5 |
| §4.4 行 197 | 首页 NBS live 候选轨显式 deeplink（per 回执 424 + `29467c4`）| docs/45 §6.2 + §7 + docs/53 §5 |
| §4.4 行 196 | 首页 NBS sample 轨显式 deeplink（per 回执 420 + `bee7950`）| docs/45 §6.2 + §7 + docs/53 §5 |
| §4.4 行 195 | docs/45 + docs/53 同步登记（per 回执 407 + 413）| docs/45 §6.2 + §7 + docs/53 §5 |
| §4.4 行 194 | 全站顶栏 site-nav → `/public-extracts` 常驻链（per 回执 410）| docs/45 §6.2 + §7 + docs/53 §5 |

## docs/45 ↔ docs/53 闭环（已在 knife 86 落地）

| 位置 | 内容 |
|---|---|
| docs/45 §6.2 line 257 | `docs/53 §5 首页公开提取入口一览（per 410 + 420 + 424 + 432 + 377 cc 回执；queue_rev 188 落地）` 行（per 回执 440）|
| docs/45 文首 line 28 | 刷新 queue_rev 189 行（per 回执 440 自身登记 + 5 条回执引用）|
| docs/45 §7 line 285 | pack invariant 链 752 → 754 指向 knife 86 |
| docs/53 §5 line 126-136 | 5 行 markdown 表「首页公开提取入口一览」本刀登记源头 |

## 红线自查

- ❌ 未改代码（docs only per §NOW；5 个回执指向的 page.tsx / layout.tsx 改动已在 410/420/424/432 闭环）
- ❌ 未删减 OPEN（§4.4 intro ⚠「**全部为 demo/candidate 演示，非 O1/Gate 收口**」原样保留；§4.4 全部 12 行使 5 条 ⚠「预览路径不构成 O1 / Gate 2 收口」原样保留）
- ❌ 未 Gate/O1 PASS 宣告（新增行回执列前缀 + 交付列结尾 + §4.4 intro ⚠ 均显式「**非 O1/Gate PASS**」+ 「**全部为 demo/candidate 演示**」+ 「**不分支 `params.*`**」+ 「**不引入 `next/link` 保留 build ○ Static 22/22**」+ 「**仍不宣布 Gate 2 PASS**」）
- ❌ 未动 `00-CC-CURRENT.md` / 未动 `gate_thresholds.json` / 未 --force / 未索要 PAT
- ✅ 回执文件名含 `-cc-`；receipt 位于 `reviews/stage0-gate0-rework-2026-08-23/`
- ✅ 不复述 Cursor 长文（仅引用回执号 + 简短语）
- ✅ docs/50 §4.4 新增 1 行（行 199）+ §4.4 intro ⚠ 收据链 +1 + docs/45 §6.2 / docs/53 §5 / docs/45 §7 双向对账（双向，docs/45 §6.2 + §7 已通过 knife 86 闭环，docs/50 §4.4 行 199 双向引用 docs/53 §5 line 126-136）
- ✅ 4 fixture byte SHA 前 8 锁在 receipt + docs/50 §4.4 行 199 中显式列出（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`，与 knife 76 + knife 78 + knife 81 + knife 82 + knife 84 + knife 85 + knife 86 + docs/53 §5 5 行表 完全一致，fixture 字节保持不变）

## 下一步

`git push origin HEAD && git push github HEAD`（**必须双推** per §NOW）→ 回填 cc_head（单独 commit，再双推）→ `./scripts/cc_gate_watch.sh --pull` → **84 POLL**（等 Cursor 审计 `442`）。