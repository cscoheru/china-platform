# 426 — docs/45 + docs/53 登记首页 NBS live deeplink · CC 回执

- 编号：`426-stage0-cc-docs45-nbs-live-home-deeplink-refresh-receipt-20260826`
- 任务书：`426-stage2-docs45-nbs-live-home-deeplink-refresh-tasking-20260826`
- 作者：CC（heartbeat 84）
- cc_head：`f0648d6`
- 日期：2026-08-26

---

## §NOW 对照

| 426 §SCHEMA 裁定 | 交付 | 证据 |
|---|---|---|
| (1) `docs/45` 刷新：文首 queue_rev 182 刷新行 + §1 + §6.2 + §7 登记首页 NBS live 候选 → `/public-extracts#track-nbs-live`（回执 `424`；smoke §12b'' + 3 pytest）| ✅ docs/45 四处互链：**文首 +queue_rev 182 刷新行**（指向 page.tsx 改动 + smoke §12b'' 4 针 + pytest 3 cases + 4 fixture byte SHA 锁与 knife 76 完全一致；显式 candidate demo/drift 候选演示、非 O1/Gate PASS；不动 4 fixture 字节）+ **§1 新增段「首页 NBS live 候选轨显式 deeplink」**（page.tsx NBS sample 行后新增「公开提取 NBS live 候选轨（candidate demo）」行；href → `/public-extracts#track-nbs-live`；testId `home-public-extracts-nbs-live` + 数据模式 `LIVE_CANDIDATE · drift 候选 · 非 O1 收口`；smoke §12b'' 4 针 + pytest 3 cases + 4 fixture byte SHA 前 8 锁 `nbs=e30ee811`/`nbs_live=9232efdb`/`sz=937255a5`/`hb=9056001c` 与 knife 76 锁值完全一致；pytest `3 passed in 0.73s`；smoke PASS；commit `1ced2bd` + cc_head backfill `29467c4`）+ **§6.2 新增 1 行**（含回执 `424` cc + queue_rev 181 → page.tsx + smoke §12b'' + pytest 3 cases + bump 734 → 737 + commit + backfill；显式「首页 NBS live deeplink 是首页表内显式锚链演示，drift 候选非 O1 收口；不动 4 fixture 字节；不引入 next/link 保留 build ○ Static；不分支 `params.*`；公开提取入口扩到『首页表内 NBS live 轨 `#track-nbs-live`』」）+ **§7 pack invariant 行更新** `737 → 739`（knife 79 = docs/45+docs/53 登记首页 NBS live deeplink + 回执 426 + bump；前置 knife 78 = page.tsx + smoke §12b'' + pytest 3 cases + 回执 424 + bump 734 → 737）| diff |
| (2) 可选 `docs/53` §5 一句 | ✅ docs/53 §5 预览清单 docs/50 §4.4 互链后新增一行 `> 🔗 首页 NBS live 候选轨显式 deeplink`（per `424` cc 回执；queue_rev 181 落地；commit `1ced2bd` + cc_head backfill `29467c4`；含 page.tsx 改动摘要 + smoke §12b'' + pytest 3 cases + 4 fixture byte SHA 锁与 knife 76 完全一致；显式「首页 NBS live deeplink 是顶栏入口之外的首页表内显式锚链演示，drift 候选非 O1 收口；不动 4 fixture 字节；不引入 next/link 保留 build ○ Static；不分支 `params.*`」；镜像本表第 1 项 NBS sample `#track-nbs-sample` 行（per knife 76 tasking 420）+ 第 4 项湖北轨 `#track-hb` 行（per knife 67 tasking 394））| diff |
| (3) 非 O1/Gate PASS | ✅ docs/45 三处显式「**仍不宣布 Gate 2 PASS**」（文首刷新行 + §1 新增段 + §6.2 新增行）+ docs/53 新增一行「首页 NBS live deeplink ... drift 候选非 O1 收口」 | diff |
| (4) 回执 `426`（`-cc-`）| ✅ 本文件名 | — |

## 证据

```
$ grep -n "queue_rev 182\|NBS live 候选轨显式 deeplink\|424" docs/45-stage2-s210-lite-gate2-review-index-20260826.md | head -10
   24:> 刷新：queue_rev 182（per `426-stage2-docs45-nbs-live-home-deeplink-refresh-tasking-20260826`）— §1 + §6.2 + §7 登记 **首页 NBS live 候选轨显式 deeplink**...
   43:**首页 NBS live 候选轨显式 deeplink**（per `424` cc 回执；queue_rev 181 落地；commit `1ced2bd` + cc_head backfill `29467c4`）...
  243:| **首页 NBS live 候选轨显式 deeplink**（顶栏入口之外的首页表内显式锚链）...
  270:| ✅ pack invariant | ⏳ bump + commit 后 737 == 737 == 737（本刀 docs/45 + docs/53 登记首页 NBS live deeplink + 回执 426 + bump → 737 → 739...

$ grep -n "首页 NBS live\|424\|track-nbs-live" docs/53-stage2-public-ingest-ops-handbook-20260826.md | head -10
  118:> 🔗 **首页 NBS live 候选轨显式 deeplink**（per `424` cc 回执；queue_rev 181 落地；commit `1ced2bd` + cc_head backfill `29467c4`）...

$ python3 scripts/_knife79_manifest_bump.py
ADD: scripts/_knife79_manifest_bump.py (…)
ADD: reviews/.../426-…-receipt-20260826.md (…)
UPDATE artifact_count: 737 → 739
INVARIANT: sum(role_count)=739 == artifact_count=739 == len(artifacts)=739
```

## 交付清单

| 文件 | 变更 | role |
|---|---|---|
| `docs/45-stage2-s210-lite-gate2-review-index-20260826.md` | MODIFIED（+queue_rev 182 刷新行 + §1 新增段「首页 NBS live 候选轨显式 deeplink」 + §6.2 +1 行 + §7 pack invariant 链 739）| 已入 manifest（SKIP，SHA REFRESH 不增计数 per knife 44 先例）|
| `docs/53-stage2-public-ingest-ops-handbook-20260826.md` | MODIFIED（§5 预览清单 第 10 项「🔗 首页 NBS live 候选轨显式 deeplink」+docs/50 §4.4 后）| 已入 manifest（SKIP）|
| `scripts/_knife79_manifest_bump.py` | NEW | `spike_helper` |
| `reviews/.../426-stage0-cc-docs45-nbs-live-home-deeplink-refresh-receipt-20260826.md` | NEW（本文件）| `documentation` |

## Pack 不变量

`_knife79_manifest_bump.py`：NEW_ARTIFACTS +2（bump + receipt）→ **737 → 739**；`sum(role_count) == artifact_count == len(artifacts) == 739`（docs/45 / docs/53 皆已入 manifest，SHA REFRESH 不增计数；前置 knife 78 已落 734 → 737）。

## docs/45 ↔ knife 78 互链点对账

| docs/45 互链点 | 内容 | 指向 knife 78 |
|---|---|---|
| **文首刷新行** | `> 刷新：queue_rev 182（per 426-...）— §1 + §6.2 + §7 登记 首页 NBS live 候选轨显式 deeplink...` | ✅ 显式声明互链范围 |
| **§1 新增段** | 新增段：`**首页 NBS live 候选轨显式 deeplink**（per 424 cc 回执...）` | ✅ page.tsx 改动 + smoke §12b'' 4 针 + pytest 3 cases + 4 fixture byte SHA 锁（与 knife 76 一致）|
| **§6.2** | 新增 1 行表格：`**首页 NBS live 候选轨显式 deeplink**` | ✅ 含回执 `424` cc + queue_rev 181 + bump 链 + 公开提取入口扩到「首页表内 NBS live 轨 `#track-nbs-live`」|
| **§7 pack invariant** | 链 `737 → 739` 含 knife 79 = docs/45+docs/53 登记首页 NBS live deeplink + 回执 426 + bump | ✅ 计数链对账 |

## docs/53 §5 ↔ knife 78 互链点对账

| docs/53 互链点 | 内容 | 指向 knife 78 |
|---|---|---|
| **§5 预览清单 第 10 项**（docs/50 §4.4 后新增）| `> 🔗 首页 NBS live 候选轨显式 deeplink`（per `424` cc 回执...）| ✅ page.tsx 改动摘要 + smoke §12b'' + pytest 3 cases + 4 fixture byte SHA + drift 候选非 O1 收口 + 不引入 next/link + 不分支 params.* + 不动 4 fixture 字节 |

## 红线自查

- ❌ 未改代码（docs only per §NOW；knife 78 page.tsx 改动已在 `424` 闭环）
- ❌ 未删减 OPEN（§3/§5.5/§6 OPEN 清单原样；仅增不改）
- ❌ 未 Gate/O1 PASS 宣告（docs/45 三处「仍不宣布 Gate 2 PASS」+ docs/53 一处「drift 候选非 O1 收口」）
- ❌ 未动 `00-CC-CURRENT.md` / 未动 `gate_thresholds.json` / 未 --force / 未索要 PAT
- ✅ 回执文件名含 `-cc-`；receipt 位于 `reviews/stage0-gate0-rework-2026-08-23/`
- ✅ 不复述 Cursor 长文（仅引用回执号 + 简短语）
- ✅ docs/45 互链点对账与 docs/53 §5 互链点对账双侧一致
- ✅ 4 fixture byte SHA 前 8 锁在 receipt 中显式列出（`nbs=e30ee811`/`nbs_live=9232efdb`/`sz=937255a5`/`hb=9056001c`，与 knife 76 完全一致，fixture 字节保持不变）

## 下一步

`git push origin HEAD && git push github HEAD`（**必须双推** per §NOW）→ 回填 cc_head（单独 commit，再双推）→ `./scripts/cc_gate_watch.sh --pull` → **84 POLL**（等 Cursor 审计 `426`）。
