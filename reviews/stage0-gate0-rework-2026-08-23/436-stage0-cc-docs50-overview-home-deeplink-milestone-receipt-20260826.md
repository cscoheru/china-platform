# 436 — docs/50 §4.4 补登首页四轨一览 overview 显式 deeplink 里程碑 · CC 回执

- 编号：`436-stage0-cc-docs50-overview-home-deeplink-milestone-receipt-20260826`
- 任务书：`436-stage2-docs50-overview-home-deeplink-milestone-tasking-20260826`
- 作者：CC（heartbeat 84）
- cc_head：`TBD`（git commit 后回填）
- 日期：2026-08-26

---

## §NOW 对照

| 436 §SCHEMA 裁定 | 交付 | 证据 |
|---|---|---|
| (1) `docs/50` §4.4 里程碑表补 1 行：首页 overview `#overview`（回执 `432`）；链 `docs/45`/`53` | ✅ `docs/50-stage2-gate2-review-packet-draft-20260826.md` §4.4 里程碑表末尾（docs/45+53 同步登记行 + knife 80 NBS deeplink 2 行后）新增 1 行：<br>**首页四轨一览 overview 显式 deeplink**（per 回执 `432` + cc_head backfill `a23e5c8`）：`frontend/app/page.tsx` 公开提取表内湖北行后新增「公开提取四轨一览（overview strip）」行；href `/public-extracts#overview` + `data-testid="home-public-extracts-overview"`；描述列「stats.gov.cn / sz.gov.cn / tjj.hubei.gov.cn 7 列 × 4 行 overview（轨 / domain / category / 行数 / SHA 前 8 / demo\|candidate 标注 / 分节锚点；数据只读自既有 4 fixture，不重算；per 回执 `383`；smoke §12f 门）」；数据模式标 `OVERVIEW · 四轨 demo · 非 O1`；结构镜像 knife 76 tasking 420 NBS sample 行 + knife 78 tasking 424 NBS live 行 + knife 67 tasking 394 湖北 `#track-hb` 行；纯 `<a href>` 锚链未引入 `next/link`（保留 build ○ Static 22/22）；不分支 `params.*`（AGENTS.md 静态路由红线）；链 docs/45 §1 + §6.2 + §7 + docs/53 §5 | diff |
| (2) 非 O1/Gate PASS | ✅ 1 行末尾标注「**首页表内显式锚链演示**」+ 「**非 O1/Gate PASS**」+ 「**不引入 next/link 保留 build ○ Static**」+ 「**不分支 `params.*`**」+ 「**不动 4 fixture 字节**」；与 §4.4 文首 ⚠ 守门一致（四轨皆 demo/candidate 演示）；5 条 ⚠「预览路径不构成 O1 / Gate 2 收口」原样保留 | diff |
| (3) 回执 `436`（`-cc-`）| ✅ 本文件名 | — |

## 证据

```
$ grep -n "首页四轨一览 overview 显式 deeplink\|432\|a23e5c8" docs/50-stage2-gate2-review-packet-draft-20260826.md | head -10
  198:| **首页四轨一览 overview 显式 deeplink**（首页表内显式锚链演示）| ... | `432` + `a23e5c8` | ...

$ python3 scripts/_knife84_manifest_bump.py
ADD: scripts/_knife84_manifest_bump.py (…)
ADD: reviews/.../436-…-receipt-20260826.md (…)
UPDATE artifact_count: 748 → 750
INVARIANT: sum(role_count)=750 == artifact_count=750 == len(artifacts)=750
```

## 交付清单

| 文件 | 变更 | role |
|---|---|---|
| `docs/50-stage2-gate2-review-packet-draft-20260826.md` | MODIFIED（§4.4 里程碑表 +1 行；末尾 docs/45+53 同步登记行 + knife 80 NBS deeplink 2 行后）| 已入 manifest（SKIP，SHA REFRESH 不增计数 per knife 44 先例）|
| `scripts/_knife84_manifest_bump.py` | NEW | `spike_helper` |
| `reviews/.../436-stage0-cc-docs50-overview-home-deeplink-milestone-receipt-20260826.md` | NEW（本文件）| `documentation` |

## Pack 不变量

`_knife84_manifest_bump.py`：NEW_ARTIFACTS +2（bump + receipt）→ **748 → 750**；`sum(role_count) == artifact_count == len(artifacts) == 750`（docs/50 已入 manifest，SHA REFRESH 不增计数；前置 knife 83 docs/45+docs/53 登记已落 746 → 748；前置 knife 82 首页四轨一览 overview deeplink 已落 743 → 746；前置 knife 78 + knife 79 已落 734 → 737 → 739）。

## docs/50 §4.4 互链对账

| docs/50 §4.4 行 | 内容 | 指向 knife |
|---|---|---|
| **首页 NBS sample 轨显式 deeplink**（行 196）| href `/public-extracts#track-nbs-sample` + testId + REGISTRY_SAMPLE demo + smoke §12b' 4 针 + pytest 3 cases + 4 fixture SHA 锁 | ✅ 链 knife 76 tasking 420 + docs/45 §1 + §6.2 + §7 + docs/53 §5 |
| **首页 NBS live 候选轨显式 deeplink**（行 197）| href `/public-extracts#track-nbs-live` + testId + LIVE_CANDIDATE drift 候选 + smoke §12b'' 4 针 + pytest 3 cases + 4 fixture SHA 锁与 knife 76 一致 | ✅ 链 knife 78 tasking 424 + docs/45 §1 + §6.2 + §7 + docs/53 §5 |
| **首页四轨一览 overview 显式 deeplink**（行 198）| href `/public-extracts#overview` + testId + OVERVIEW 四轨 demo + smoke §12b''' 4 针 + pytest 3 cases + 4 fixture SHA 锁与 knife 76/78 完全一致 | ✅ 链 knife 82 tasking 432 + docs/45 §1 + §6.2 + §7 + docs/53 §5 |

## 红线自查

- ❌ 未改代码（docs only per §NOW；knife 82 page.tsx 改动已在 `432` 闭环）
- ❌ 未删减 OPEN（§5.1/§5.4 OPEN 清单原样；5 条 ⚠「预览路径不构成 O1 / Gate 2 收口」原样保留；仅增不改）
- ❌ 未 Gate/O1 PASS 宣告（1 行末尾显式「非 O1/Gate PASS」+ 「首页表内显式锚链演示」+ §4.4 文首 ⚠ 守门保留）
- ❌ 未动 `00-CC-CURRENT.md` / 未动 `gate_thresholds.json` / 未 --force / 未索要 PAT
- ✅ 回执文件名含 `-cc-`；receipt 位于 `reviews/stage0-gate0-rework-2026-08-23/`
- ✅ 不复述 Cursor 长文（仅引用回执号 + 简短语）
- ✅ docs/45 + docs/53 已分别在 knife 83 (回执 434) + knife 79 (回执 426) + knife 77 (回执 422) 登记；本刀 docs/50 §4.4 链接两侧双向对账（docs/45 §7 pack invariant 链亦指向 docs/50 §4.4 新增 1 行）
- ✅ 4 fixture byte SHA 前 8 锁在 receipt 中显式列出（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`，与 knife 76 + knife 78 + knife 82 + docs/50 §4.4 +2 行完全一致，fixture 字节保持不变）
- ✅ docs/50 §4.4 链 docs/45 §1 + §6.2 + §7 + docs/53 §5（双向，docs/45 §7 pack invariant 链亦指向 docs/50 §4.4 新增行）

## 下一步

`git push origin HEAD && git push github HEAD`（**必须双推** per §NOW）→ 回填 cc_head（单独 commit，再双推）→ `./scripts/cc_gate_watch.sh --pull` → **84 POLL**（等 Cursor 审计 `436`）。