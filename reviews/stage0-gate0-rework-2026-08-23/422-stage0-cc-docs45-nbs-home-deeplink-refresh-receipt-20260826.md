# 422 — docs/45 + docs/53 登记首页 NBS deeplink · CC 回执

- 编号：`422-stage0-cc-docs45-nbs-home-deeplink-refresh-receipt-20260826`
- 任务书：`422-stage2-docs45-nbs-home-deeplink-refresh-tasking-20260826`
- 作者：CC（heartbeat 84）
- cc_head：`d313e41`
- 日期：2026-08-26

---

## §NOW 对照

| 422 §SCHEMA 裁定 | 交付 | 证据 |
|---|---|---|
| (1) `docs/45` 刷新：文首 queue_rev 180 刷新行 + §1 + §6.2 + §7 登记首页 NBS sample → `/public-extracts#track-nbs-sample`（回执 `420`；smoke §12b' + 3 pytest）| ✅ docs/45 四处互链：**文首 +queue_rev 180 刷新行**（指向 page.tsx 改动 + smoke §12b' 4 针 + pytest 3 cases + 4 fixture byte SHA 锁；显式 demo/candidate 演示、非 O1/Gate PASS；不动 4 fixture 字节）+ **§1 新增段「首页 NBS sample 轨显式 deeplink」**（page.tsx 「公开提取样本（四轨 demo）」行 → 「公开提取 NBS sample 轨（demo）」；href → `/public-extracts#track-nbs-sample`；testId + 数据模式；镜像湖北 `#track-hb` 行；smoke §12b' 4 针 + pytest 3 cases + 4 fixture byte SHA 前 8 锁 `nbs=e30ee811`/`nbs_live=9232efdb`/`sz=937255a5`/`hb=9056001c`；pytest `3 passed in 0.72s`；smoke PASS；commit `a70a557` + cc_head backfill `bee7950`）+ **§6.2 新增 1 行**（含回执 `420` cc + queue_rev 179 → page.tsx + smoke §12b' + pytest 3 cases + bump 729 → 732 + commit + backfill；显式「首页 NBS deeplink 是首页表内显式锚链演示，非 O1/Gate PASS；不动 4 fixture 字节；公开提取入口扩到『首页表内 NBS 轨 `#track-nbs-sample`』」）+ **§7 pack invariant 行更新** `732 → 734`（knife 77 = docs/45+docs/53 登记首页 NBS deeplink + 回执 422 + bump；前置 knife 76 = page.tsx + smoke §12b' + pytest 3 cases + 回执 420 + bump 729 → 732）| diff |
| (2) 可选 `docs/53` §5 一句 | ✅ docs/53 §5 预览清单 docs/50 §4.4 互链后新增一行 `> 🔗 首页 NBS sample 轨显式 deeplink`（per `420` cc 回执；queue_rev 179 落地；commit `a70a557` + cc_head backfill `bee7950`；含 page.tsx 改动摘要 + smoke §12b' + pytest 3 cases + 4 fixture byte SHA 锁；显式「首页 NBS deeplink 是顶栏入口之外的首页表内显式锚链演示，非 O1/Gate PASS；不动 4 fixture 字节；不引入 next/link；不分支 `params.*`」；镜像本表第 4 项湖北轨 `#track-hb` 行（per knife 67 tasking 394））| diff |
| (3) 非 O1/Gate PASS | ✅ docs/45 三处显式「**仍不宣布 Gate 2 PASS**」（文首刷新行 + §1 新增段 + §6.2 新增行）+ docs/53 新增一行「首页 NBS deeplink ... 非 O1/Gate PASS」 | diff |
| (4) 回执 `422`（`-cc-`）| ✅ 本文件名 | — |

## 证据

```
$ grep -n "queue_rev 180\|NBS sample 轨显式 deeplink\|420" docs/45-stage2-s210-lite-gate2-review-index-20260826.md | head -10
   23:> 刷新：queue_rev 180（per `422-stage2-docs45-nbs-home-deeplink-refresh-tasking-20260826`）— §1 + §6.2 + §7 登记 **首页 NBS sample 轨显式 deeplink**...
   39:**首页 NBS sample 轨显式 deeplink**（per `420` cc 回执；queue_rev 179 落地；commit `a70a557` + cc_head backfill `bee7950`）...
  235:| **首页 NBS sample 轨显式 deeplink**（顶栏入口之外的首页表内显式锚链）...
  264:| ✅ pack invariant | ⏳ bump + commit 后 732 == 732 == 732（本刀 docs/45 + docs/53 登记首页 NBS deeplink + 回执 422 + bump → 732 → 734...

$ grep -n "首页 NBS\|420\|track-nbs-sample" docs/53-stage2-public-ingest-ops-handbook-20260826.md | head -10
  116:> 🔗 **首页 NBS sample 轨显式 deeplink**（per `420` cc 回执；queue_rev 179 落地；commit `a70a557` + cc_head backfill `bee7950`）...

$ python3 scripts/_knife77_manifest_bump.py
ADD: scripts/_knife77_manifest_bump.py (…)
ADD: reviews/.../422-…-receipt-20260826.md (…)
UPDATE artifact_count: 732 → 734
INVARIANT: sum(role_count)=734 == artifact_count=734 == len(artifacts)=734
```

## 交付清单

| 文件 | 变更 | role |
|---|---|---|
| `docs/45-stage2-s210-lite-gate2-review-index-20260826.md` | MODIFIED（+queue_rev 180 刷新行 + §1 新增段「首页 NBS sample 轨显式 deeplink」 + §6.2 +1 行 + §7 pack invariant 链 734）| 已入 manifest（SKIP，SHA REFRESH 不增计数 per knife 44 先例）|
| `docs/53-stage2-public-ingest-ops-handbook-20260826.md` | MODIFIED（§5 预览清单 第 9 项「🔗 首页 NBS sample 轨显式 deeplink」+docs/50 §4.4 后）| 已入 manifest（SKIP）|
| `scripts/_knife77_manifest_bump.py` | NEW | `spike_helper` |
| `reviews/.../422-stage0-cc-docs45-nbs-home-deeplink-refresh-receipt-20260826.md` | NEW（本文件）| `documentation` |

## Pack 不变量

`_knife77_manifest_bump.py`：NEW_ARTIFACTS +2（bump + receipt）→ **732 → 734**；`sum(role_count) == artifact_count == len(artifacts) == 734`（docs/45 / docs/53 皆已入 manifest，SHA REFRESH 不增计数；前置 knife 76 已落 729 → 732）。

## docs/45 ↔ knife 76 互链点对账

| docs/45 互链点 | 内容 | 指向 knife 76 |
|---|---|---|
| **文首刷新行** | `> 刷新：queue_rev 180（per 422-...）— §1 + §6.2 + §7 登记 首页 NBS sample 轨显式 deeplink...` | ✅ 显式声明互链范围 |
| **§1 新增段** | 新增段：`**首页 NBS sample 轨显式 deeplink**（per 420 cc 回执...）` | ✅ page.tsx 改动 + smoke §12b' 4 针 + pytest 3 cases + 4 fixture byte SHA 锁 |
| **§6.2** | 新增 1 行表格：`**首页 NBS sample 轨显式 deeplink**` | ✅ 含回执 `420` cc + queue_rev 179 + bump 链 + 公开提取入口扩到「首页表内 NBS 轨 `#track-nbs-sample`」 |
| **§7 pack invariant** | 链 `732 → 734` 含 knife 77 = docs/45+docs/53 登记首页 NBS deeplink + 回执 422 + bump | ✅ 计数链对账 |

## docs/53 §5 ↔ knife 76 互链点对账

| docs/53 互链点 | 内容 | 指向 knife 76 |
|---|---|---|
| **§5 预览清单 第 9 项**（docs/50 §4.4 后新增）| `> 🔗 首页 NBS sample 轨显式 deeplink`（per `420` cc 回执...）| ✅ page.tsx 改动摘要 + smoke §12b' + pytest 3 cases + 4 fixture byte SHA + 非 O1/Gate PASS + 不引入 next/link + 不分支 params.* |

## 红线自查

- ❌ 未改代码（docs only per §NOW；knife 76 page.tsx 改动已在 `420` 闭环）
- ❌ 未删减 OPEN（§3/§5.5/§6 OPEN 清单原样；仅增不改）
- ❌ 未 Gate/O1 PASS 宣告（docs/45 三处「仍不宣布 Gate 2 PASS」+ docs/53 一处「非 O1/Gate PASS」）
- ❌ 未动 `00-CC-CURRENT.md` / 未动 `gate_thresholds.json` / 未 --force / 未索要 PAT
- ✅ 回执文件名含 `-cc-`；receipt 位于 `reviews/stage0-gate0-rework-2026-08-23/`
- ✅ 不复述 Cursor 长文（仅引用回执号 + 简短语）
- ✅ docs/45 互链点对账与 docs/53 §5 互链点对账双侧一致
- ✅ 4 fixture byte SHA 前 8 锁在 receipt 中显式列出（`nbs=e30ee811`/`nbs_live=9232efdb`/`sz=937255a5`/`hb=9056001c`）

## 下一步

`git push origin HEAD && git push github HEAD`（**必须双推** per §NOW）→ 回填 cc_head（单独 commit，再双推）→ `./scripts/cc_gate_watch.sh --pull` → **84 POLL**（等 Cursor 审计 `422`）。