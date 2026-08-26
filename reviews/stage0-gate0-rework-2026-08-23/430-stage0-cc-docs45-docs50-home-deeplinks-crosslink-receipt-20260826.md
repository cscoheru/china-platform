# 430 — docs/45 ↔ docs/50 §4.4 首页 deeplink 互链 · CC 回执

- 编号：`430-stage0-cc-docs45-docs50-home-deeplinks-crosslink-receipt-20260826`
- 任务书：`430-stage2-docs45-docs50-home-deeplinks-crosslink-tasking-20260826`
- 作者：CC（heartbeat 84）
- cc_head：`TBD`（git commit 后回填）
- 日期：2026-08-26

---

## §NOW 对照

| 430 §SCHEMA 裁定 | 交付 | 证据 |
|---|---|---|
| (1) `docs/45` 刷新：文首 queue_rev 184 刷新行 + §1 + §6.2 + §7 互链 `docs/50` §4.4 新增 2 行首页 deeplink（回执 `428`；NBS sample `420` + NBS live `424`）| ✅ `docs/45-stage2-s210-lite-gate2-review-index-20260826.md`：<br>文首（line 25 area）`> 刷新：queue_rev 184（per 430-...）— §1 + §6.2 + §7 互链 docs/50 §4.4 新增 2 行首页 deeplink 里程碑...`<br>§1 新增段「`docs/50` §4.4 新增 2 行首页 deeplink 里程碑补登」（per `428` cc 回执；queue_rev 183 落地；commit `10f26cf` + cc_head backfill `4e385ed`）：明示 docs/50 §4.4 里程碑表末尾补登 2 行（NBS sample `#track-nbs-sample` 回执 `420` + cc_head backfill `bee7950` + NBS live `#track-nbs-live` 回执 `424` + cc_head backfill `29467c4`）；smoke §12b' + §12b'' 双门 + pytest 3 cases ×2 + 4 fixture byte SHA 锁 `nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`（双刀锁值完全一致）；docs/50 §4.4 新增 2 行是 Gate 2 评审包草稿里程碑表首页表内显式锚链演示节点，非 O1/Gate PASS；不动 4 fixture 字节；不引入 next/link 保留 build ○ Static；不分支 `params.*`；仍不宣布 Gate 2 PASS<br>§6.2 +1 行（line 248 area 新增）：`docs/50` §4.4 新增 2 行首页 deeplink 里程碑补登（per `428` cc 回执；queue_rev 183 落地；commit `10f26cf` + cc_head backfill `4e385ed`）—— docs/50 §4.4 里程碑表末尾补登 2 行（NBS sample `#track-nbs-sample` + NBS live `#track-nbs-live`），2 行均显式 demo/candidate 演示、非 O1/Gate PASS，链 docs/45 §1 + §6.2 + §7 + docs/53 §5，不引入 next/link 保留 build ○ Static，不分支 `params.*`<br>§7 pack invariant 行更新 741 → 743（line 276 area）：链头 `⏳ bump + commit 后 743 == 743 == 743（本刀 docs/45 + docs/53 ↔ docs/50 §4.4 首页 deeplink 互链 + 回执 430 + bump → 741 → 743；+2 = bump + receipt；docs/45/docs/53 皆 SHA REFRESH 不增计数；knife 80 = docs/50 §4.4 补登首页 deeplink 里程碑 +2 行 + 回执 428 + bump 739 → 741；...` | diff |
| (2) 可选 `docs/53` 一句 | ✅ `docs/53-stage2-public-ingest-ops-handbook-20260826.md` §5 预览清单第 11 项新增一行（line 118 后）：`> 🔗 `docs/45` ↔ `docs/50` §4.4 首页 deeplink 互链`（per `430` cc 回执；queue_rev 184 落地；commit `10f26cf` + cc_head backfill `4e385ed` → docs/45/docs/53/docs/50 互链）：明示 docs/50 §4.4 里程碑表末尾补登 2 行（NBS sample `420`/`bee7950` + NBS live `424`/`29467c4`）；docs/45 文首 queue_rev 184 + §1 + §6.2 + §7；docs/53 §5 第 11 项同步；链 `docs/45` §1 + §6.2 + §7 + `docs/53` §5（双向）；不引入 next/link 保留 build ○ Static；不分支 `params.*`；4 fixture byte SHA 前 8 锁不漂（双刀锁值完全一致：`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`） | diff |
| (3) 非 O1/Gate PASS | ✅ docs/45 §1 + §6.2 + §7 + docs/53 §5 第 11 项末尾均标注「**非 O1/Gate PASS**」+ 「**仍不宣布 Gate 2 PASS**」+ 「**不动 4 fixture 字节**」+ 「**不引入 next/link 保留 build ○ Static**」+ 「**不分支 `params.*`**」；与 §4.4 文首 ⚠ 守门一致（四轨皆 demo/candidate 演示）；docs/45 §7 红线自查表原样保留 | diff |
| (4) 回执 `430`（`-cc-`）| ✅ 本文件名 | — |

## 证据

```
$ grep -n "queue_rev 184\|docs/50 §4.4 新增 2 行\|首页 NBS sample 轨显式 deeplink\|首页 NBS live 候选轨显式 deeplink" docs/45-stage2-s210-lite-gate2-review-index-20260826.md | head -20
  25:| > 刷新：queue_rev 184（per `430-stage2-docs45-docs50-home-deeplinks-crosslink-tasking-20260826`）— §1 + §6.2 + §7 **互链 `docs/50` §4.4 新增 2 行首页 deeplink 里程碑**...
  45:| **`docs/50` §4.4 新增 2 行首页 deeplink 里程碑补登**（per `428` cc 回执；queue_rev 183 落地；commit `10f26cf` + cc_head backfill `4e385ed`）：...
  249:| **`docs/50` §4.4 新增 2 行首页 deeplink 里程碑补登**（per `428` cc 回执；queue_rev 183 落地；commit `10f26cf` + cc_head backfill `4e385ed`）| ...

$ grep -n "docs/45 ↔ docs/50 §4.4 首页 deeplink 互链" docs/53-stage2-public-ingest-ops-handbook-20260826.md
  120:> 🔗 **`docs/45` ↔ `docs/50` §4.4 首页 deeplink 互链**（per `430` cc 回执；queue_rev 184 落地；commit `10f26cf` + cc_head backfill `4e385ed` → docs/45/docs/53/docs/50 互链）：...

$ python3 scripts/_knife81_manifest_bump.py
ADD: scripts/_knife81_manifest_bump.py (…)
ADD: reviews/.../430-…-receipt-20260826.md (…)
UPDATE artifact_count: 741 → 743
INVARIANT: sum(role_count)=743 == artifact_count=743 == len(artifacts)=743
```

## 交付清单

| 文件 | 变更 | role |
|---|---|---|
| `docs/45-stage2-s210-lite-gate2-review-index-20260826.md` | MODIFIED（文首 +queue_rev 184 + §1 + §6.2 + §7 互链 docs/50 §4.4 新增 2 行）| 已入 manifest（SKIP，SHA REFRESH 不增计数 per knife 44 先例）|
| `docs/53-stage2-public-ingest-ops-handbook-20260826.md` | MODIFIED（§5 第 11 项 docs/45 ↔ docs/50 §4.4 互链同步登记）| 已入 manifest（SKIP，SHA REFRESH 不增计数 per knife 44 先例）|
| `scripts/_knife81_manifest_bump.py` | NEW | `spike_helper` |
| `reviews/.../430-stage0-cc-docs45-docs50-home-deeplinks-crosslink-receipt-20260826.md` | NEW（本文件）| `documentation` |

## Pack 不变量

`_knife81_manifest_bump.py`：NEW_ARTIFACTS +2（bump + receipt）→ **741 → 743**；`sum(role_count) == artifact_count == len(artifacts) == 743`（docs/45 + docs/53 已入 manifest，SHA REFRESH 不增计数；前置 knife 80 docs/50 §4.4 已落 739 → 741；前置 knife 78 + knife 79 已落 734 → 737 → 739）。

## docs/45 ↔ docs/50 §4.4 ↔ docs/53 三向互链对账

| 互链点 | docs/45 | docs/50 | docs/53 | 内容 |
|---|---|---|---|---|
| docs/50 §4.4 新增行 (a) NBS sample | §1 段 + §6.2 row | §4.4 行 196 | §5 第 11 项 | href `/public-extracts#track-nbs-sample` + testId + REGISTRY_SAMPLE demo + smoke §12b' 4 针 + pytest 3 cases + 4 fixture SHA 锁 |
| docs/50 §4.4 新增行 (b) NBS live | §1 段 + §6.2 row | §4.4 行 197 | §5 第 11 项 | href `/public-extracts#track-nbs-live` + testId + LIVE_CANDIDATE drift 候选 + smoke §12b'' 4 针 + pytest 3 cases + 4 fixture SHA 锁与 knife 76 一致 |

## 红线自查

- ❌ 未改代码（docs only per §NOW；knife 76 + knife 78 page.tsx 改动已在 `420`/`424` 闭环；docs/50 §4.4 +2 行已在 `428` 闭环）
- ❌ 未删减 OPEN（docs/45 §5.5 + §6.2 OPEN 清单原样；5 条 ⚠「预览路径不构成 O1 / Gate 2 收口」原样保留；仅增不改）
- ❌ 未 Gate/O1 PASS 宣告（docs/45 §1 + §6.2 + §7 + docs/53 §5 第 11 项末尾均显式「非 O1/Gate PASS」+ 「仍不宣布 Gate 2 PASS」+ docs/50 §4.4 文首 ⚠ 守门保留）
- ❌ 未动 `00-CC-CURRENT.md` / 未动 `gate_thresholds.json` / 未 --force / 未索要 PAT
- ✅ 回执文件名含 `-cc-`；receipt 位于 `reviews/stage0-gate0-rework-2026-08-23/`
- ✅ 不复述 Cursor 长文（仅引用回执号 + 简短语）
- ✅ docs/45 + docs/50 + docs/53 三向同步登记（双向链：docs/45 §7 pack invariant 链亦指向 docs/50 §4.4 新增 2 行；docs/53 §5 第 11 项双向指向 docs/50 §4.4 + docs/45 §1/§6.2/§7）
- ✅ 4 fixture byte SHA 前 8 锁在 receipt 中显式列出（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`，与 knife 76 + knife 78 + docs/50 §4.4 完全一致，fixture 字节保持不变）
- ✅ 不分支 `params.*`（AGENTS.md 静态路由红线，pytest `test_layout_does_not_branch_on_params` 锁定）
- ✅ 不引入 `next/link`（保留 build ○ Static 22/22）

## 下一步

`git push origin HEAD && git push github HEAD`（**必须双推** per §NOW）→ 回填 cc_head（单独 commit，再双推）→ `./scripts/cc_gate_watch.sh --pull` → **84 POLL**（等 Cursor 审计 `430`）。