# 434 — docs/45 + docs/53 登记首页四轨一览 overview 显式 deeplink · CC 回执

- 编号：`434-stage0-cc-docs45-overview-home-deeplink-refresh-receipt-20260826`
- 任务书：`434-stage2-docs45-overview-home-deeplink-refresh-tasking-20260826`
- 作者：CC（heartbeat 84）
- cc_head：`911cf53`（backfill commit `TBD`，后续单独 commit 回填；前序 commit `911cf53` = knife 83 主落地）
- 日期：2026-08-26

---

## §NOW 对照

| 434 §SCHEMA 裁定 | 交付 | 证据 |
|---|---|---|
| (1) `docs/45` 刷新：文首 queue_rev 186 刷新行 + §1 + §6.2 + §7 登记首页 overview → `/public-extracts#overview`（回执 `432`；smoke §12b''' + 3 pytest）| ✅ `docs/45-stage2-s210-lite-gate2-review-index-20260826.md`：<br>文首（line 26 area）`> 刷新：queue_rev 186（per 434-...）— §1 + §6.2 + §7 登记 首页四轨一览 overview 显式 deeplink...`<br>§1 新增段「首页四轨一览 overview 显式 deeplink」（per `432` cc 回执；queue_rev 185 落地；commit `624f02a` + cc_head backfill `a23e5c8`）：明示 `frontend/app/page.tsx` 公开提取表内湖北行后新增「公开提取四轨一览（overview strip）」行；href `/public-extracts#overview`；新增 `data-testid="home-public-extracts-overview"`；数据模式 `OVERVIEW · 四轨 demo · 非 O1`；smoke §12b''' 4 针 + `tests/test_overview_home_deeplink_public_extract.py` 3 pytest cases；4 fixture byte SHA 锁 `nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`（与 knife 76/78/81 锁值完全一致）；pytest `9 passed in 0.68s`（3 新 + 6 prior home deeplink regression — 无交叉污染）；smoke §12b''' PASS<br>§6.2 +1 行（line 250 area 新增）：`首页四轨一览 overview 显式 deeplink（per 432 cc 回执；queue_rev 185 落地；commit 624f02a + cc_head backfill a23e5c8）`—— page.tsx 公开提取表内湖北行后新增「公开提取四轨一览（overview strip）」行；href `/public-extracts#overview`；描述列含 stats.gov.cn/sz.gov.cn/tjj.hubei.gov.cn 7 列 × 4 行；数据模式 `OVERVIEW · 四轨 demo · 非 O1`；结构镜像 knife 76/78/67 行；smoke §12b''' 4 针 + pytest 3 cases + 4 fixture byte SHA 锁不漂<br>§7 pack invariant 行更新 746 → 748（line 277 area）：链头 `⏳ bump + commit 后 748 == 748 == 748（本刀 docs/45 + docs/53 登记首页四轨一览 overview 显式 deeplink + 回执 434 + bump → 746 → 748；+2 = bump + receipt；docs/45/docs/53 皆 SHA REFRESH 不增计数；knife 82 = 首页四轨一览 overview 显式 deeplink（page.tsx href → /public-extracts#overview + testId + smoke §12b''' 4 针 + pytest 3 cases test_overview_home_deeplink_public_extract.py + 回执 432）743 → 746；...` | diff |
| (2) 可选 `docs/53` §5 一句 | ✅ `docs/53-stage2-public-ingest-ops-handbook-20260826.md` §5 预览清单第 12 项新增一行（line 120 后）：`> 🔗 首页四轨一览 overview 显式 deeplink`（per `432` cc 回执；queue_rev 185 落地；commit `624f02a` + cc_head backfill `a23e5c8`）：明示 page.tsx 公开提取表内湖北行后新增「公开提取四轨一览（overview strip）」行；href `/public-extracts#overview` + testId；描述列含 7 列 × 4 行 overview；数据模式 `OVERVIEW · 四轨 demo · 非 O1`；smoke §12b''' 4 针 + `tests/test_overview_home_deeplink_public_extract.py` 3 cases；4 fixture byte SHA 前 8 锁不漂（与 knife 76/78/81 锁值完全一致：`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`）；pytest `9 passed in 0.68s`（3 新 + 6 prior home deeplink regression） | diff |
| (3) 非 O1/Gate PASS | ✅ docs/45 §1 + §6.2 + §7 + docs/53 §5 第 12 项末尾均标注「**非 O1/Gate PASS**」+ 「**不动 4 fixture 字节**」+ 「**不引入 next/link 保留 build ○ Static**」+ 「**不分支 `params.*`**」；与 docs/50 §4.4 文首 ⚠ 守门一致；docs/45 §7 红线自查表原样保留 | diff |
| (4) 回执 `434`（`-cc-`）| ✅ 本文件名 | — |

## 证据

```
$ grep -n "queue_rev 186\|首页四轨一览 overview 显式 deeplink" docs/45-stage2-s210-lite-gate2-review-index-20260826.md | head -10
  26:| > 刷新：queue_rev 186（per `434-stage2-docs45-overview-home-deeplink-refresh-tasking-20260826`）— §1 + §6.2 + §7 登记 **首页四轨一览 overview 显式 deeplink**...
  49:| **首页四轨一览 overview 显式 deeplink**（per `432` cc 回执；queue_rev 185 落地；commit `624f02a` + cc_head backfill `a23e5c8`）：...
  251:| **首页四轨一览 overview 显式 deeplink**（per `432` cc 回执；queue_rev 185 落地；commit `624f02a` + cc_head backfill `a23e5c8`）| ...

$ grep -n "首页四轨一览 overview 显式 deeplink" docs/53-stage2-public-ingest-ops-handbook-20260826.md
  122:> 🔗 **首页四轨一览 overview 显式 deeplink**（per `432` cc 回执；queue_rev 185 落地；commit `624f02a` + cc_head backfill `a23e5c8`）：...

$ python3 scripts/_knife83_manifest_bump.py
ADD: scripts/_knife83_manifest_bump.py (…)
ADD: reviews/.../434-…-receipt-20260826.md (…)
UPDATE artifact_count: 746 → 748
INVARIANT: sum(role_count)=748 == artifact_count=748 == len(artifacts)=748
```

## 交付清单

| 文件 | 变更 | role |
|---|---|---|
| `docs/45-stage2-s210-lite-gate2-review-index-20260826.md` | MODIFIED（文首 +queue_rev 186 + §1 + §6.2 + §7 登记首页四轨一览 overview deeplink）| 已入 manifest（SKIP，SHA REFRESH 不增计数 per knife 44 先例）|
| `docs/53-stage2-public-ingest-ops-handbook-20260826.md` | MODIFIED（§5 第 12 项 首页四轨一览 overview deeplink 同步登记）| 已入 manifest（SKIP，SHA REFRESH 不增计数 per knife 44 先例）|
| `scripts/_knife83_manifest_bump.py` | NEW | `spike_helper` |
| `reviews/.../434-stage0-cc-docs45-overview-home-deeplink-refresh-receipt-20260826.md` | NEW（本文件）| `documentation` |

## Pack 不变量

`_knife83_manifest_bump.py`：NEW_ARTIFACTS +2（bump + receipt）→ **746 → 748**；`sum(role_count) == artifact_count == len(artifacts) == 748`（docs/45 + docs/53 已入 manifest，SHA REFRESH 不增计数；前置 knife 82 首页四轨一览 overview deeplink 已落 743 → 746；前置 knife 81 docs/45/docs/53/docs/50 互链已落 741 → 743；前置 knife 80 docs/50 §4.4 +2 行已落 739 → 741；前置 knife 78 + knife 79 已落 734 → 737 → 739）。

## docs/45 + docs/53 三向互链对账

| 互链点 | docs/45 | docs/50 | docs/53 | 内容 |
|---|---|---|---|---|
| 首页 NBS sample `#track-nbs-sample` | §1 段 + §6.2 row | §4.4 行 196 | §5 第 10 项 | href `/public-extracts#track-nbs-sample` + testId + REGISTRY_SAMPLE demo + smoke §12b' 4 针 + pytest 3 cases + 4 fixture SHA 锁 |
| 首页 NBS live `#track-nbs-live` | §1 段 + §6.2 row | §4.4 行 197 | §5 第 10 项 | href `/public-extracts#track-nbs-live` + testId + LIVE_CANDIDATE drift 候选 + smoke §12b'' 4 针 + pytest 3 cases + 4 fixture SHA 锁 |
| 首页四轨一览 `#overview`（本刀新增）| §1 段 + §6.2 row | （待补） | §5 第 12 项 | href `/public-extracts#overview` + testId + OVERVIEW 四轨 demo + smoke §12b''' 4 针 + pytest 3 cases + 4 fixture SHA 锁 |

## 红线自查

- ❌ 未改代码（docs only per §NOW；knife 82 page.tsx + smoke + pytest 改动已在 `432` 闭环）
- ❌ 未删减 OPEN（docs/45 §5.5 + §6.2 OPEN 清单原样；5 条 ⚠「预览路径不构成 O1 / Gate 2 收口」原样保留；仅增不改）
- ❌ 未 Gate/O1 PASS 宣告（docs/45 §1 + §6.2 + §7 + docs/53 §5 第 12 项末尾均显式「非 O1/Gate PASS」+ 「不动 4 fixture 字节」+ 「不引入 next/link」+ 「不分支 params.*」）
- ❌ 未动 `00-CC-CURRENT.md` / 未动 `gate_thresholds.json` / 未 --force / 未索要 PAT
- ✅ 回执文件名含 `-cc-`；receipt 位于 `reviews/stage0-gate0-rework-2026-08-23/`
- ✅ 不复述 Cursor 长文（仅引用回执号 + 简短语）
- ✅ docs/45 + docs/53 双向同步登记（双向链：docs/45 §7 pack invariant 链亦指向 docs/53 §5 第 12 项；docs/53 §5 第 12 项双向指向 docs/45 §1/§6.2/§7）
- ✅ 4 fixture byte SHA 前 8 锁在 receipt 中显式列出（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`，与 knife 76 + knife 78 + knife 80 + knife 81 + knife 82 完全一致，fixture 字节保持不变）
- ✅ 不分支 `params.*`（AGENTS.md 静态路由红线，pytest `test_no_overview_deeplink_pollutes_province_or_city_pages` 锁定 5 省 + 10 城 CityPage/CityPageMart）
- ✅ 不引入 `next/link`（保留 build ○ Static 22/22）
- ✅ pytest `9 passed in 0.68s`（3 新 + 6 prior home deeplink regression — 无交叉污染）

## 下一步

`git push origin HEAD && git push github HEAD`（**必须双推** per §NOW）→ 回填 cc_head（单独 commit，再双推）→ `./scripts/cc_gate_watch.sh --pull` → **84 POLL**（等 Cursor 审计 `434`）。