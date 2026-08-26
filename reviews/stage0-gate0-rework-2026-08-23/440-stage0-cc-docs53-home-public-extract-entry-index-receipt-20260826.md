# 440 — docs/53 §5 首页公开提取入口一览 · CC 回执

- 编号：`440-stage0-cc-docs53-home-public-extract-entry-index-receipt-20260826`
- 任务书：`440-stage2-docs53-home-public-extract-entry-index-tasking-20260826`
- 作者：CC（heartbeat 84）
- cc_head：`0ad62e0`（双推：origin 19484a7..0ad62e0，github 19484a7..0ad62e0）
- 日期：2026-08-26

---

## §NOW 对照

| 440 §SCHEMA 裁定 | 交付 | 证据 |
|---|---|---|
| (1) `docs/53` §5 增「首页公开提取入口一览」表（site-nav + `/public-extracts` + `#track-nbs-sample` + `#track-nbs-live` + `#overview` + `#track-hb`；链回执 `410`/`420`/`424`/`432`/`377`）| ✅ docs/53 §5 新增 5 行 markdown 表（`> 📍 首页公开提取入口一览`），列：入口 / 锚链 / 数据模式 / 用途 / 来源回执，覆盖：(a) 全站顶栏 site-nav → `/public-extracts`（回执 410 / smoke §13c 门 6 针 + 5 pytest `test_layout_site_nav_public_extracts.py`）；(b) 首页表内 NBS sample 轨 → `/public-extracts#track-nbs-sample`（回执 420 / commit `a70a557` + cc_head backfill `bee7950` / smoke §12b' 4 针 + pytest 3 cases `test_nbs_home_deeplink_public_extract.py`）；(c) 首页表内 NBS live 候选轨 → `/public-extracts#track-nbs-live`（回执 424 / commit `1ced2bd` + cc_head backfill `29467c4` / smoke §12b'' 4 针 + pytest 3 cases `test_nbs_live_home_deeplink_public_extract.py`）；(d) 首页表内四轨一览 overview strip → `/public-extracts#overview`（回执 432 / commit `624f02a` + cc_head backfill `a23e5c8` / smoke §12b''' 4 针 + pytest 3 cases `test_overview_home_deeplink_public_extract.py`）；(e) 首页表内湖北轨 → `/public-extracts#track-hb`（per knife 67 tasking 394 / 回执 377 / smoke §12e 门 + pytest 4 轨交叉检查）；5 行均显式 demo/candidate 演示、非 O1/Gate PASS；4 fixture byte SHA 前 8 锁不漂：`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c` 与 knife 76/78/81/82/84/85 完全一致 | diff |
| (2) 可选 `docs/45` §6.2 一句 | ✅ docs/45 §6.2 +1 行（镜像 knife 81 + knife 85 docs/45 docs/50 home deeplinks crosslink 行结构；`docs/53 §5 首页公开提取入口一览（per 410 + 420 + 424 + 432 + 377 cc 回执；queue_rev 188 落地）`）+ 文首 queue_rev 189 刷新行（per 回执 410 + 420 + 424 + 432 + 377 cc + 回执 440 自身登记）+ §7 pack invariant 链 752 → 754 | diff |
| (3) 非 O1/Gate PASS | ✅ docs/53 §5 表尾「**首页公开提取入口一览是顶栏 site-nav + 首页表内 4 行显式 deeplink 的端到端入口演示汇总，非 O1/Gate PASS；不动 4 fixture 字节；不引入 `next/link` 保留 build ○ Static；不分支 `params.*`；4 fixture byte SHA 前 8 锁不漂**」+ docs/45 文首「**非 O1/Gate PASS**」+ §7 pack invariant 链结尾 「**仍不宣布 Gate 2 PASS**」 | diff |
| (4) 回执 `440`（`-cc-`）| ✅ 本文件名 | — |

## 证据

```
$ grep -n "首页公开提取入口一览\|410\|420\|424\|432\|377" docs/53-stage2-public-ingest-ops-handbook-20260826.md | head -10
  126:> 📍 **首页公开提取入口一览**（per 回执 `410` + `420` + `424` + `432` + `377` cc；queue_rev 188 落地）：
  130:| **全站顶栏 site-nav**（`<nav data-testid="site-nav">`）| `/public-extracts` | … | `410`（smoke §13c 门 6 针 + 5 pytest `test_layout_site_nav_public_extracts.py`） |
  131:| **首页表内 NBS sample 轨**（`data-testid="home-public-extracts-nbs-sample"`）| `/public-extracts#track-nbs-sample` | … | `420`（commit `a70a557` + cc_head backfill `bee7950`；smoke §12b' 4 针 + pytest 3 cases `test_nbs_home_deeplink_public_extract.py`）|
  132:| **首页表内 NBS live 候选轨**（`data-testid="home-public-extracts-nbs-live"`）| `/public-extracts#track-nbs-live` | … | `424`（commit `1ced2bd` + cc_head backfill `29467c4`；smoke §12b'' 4 针 + pytest 3 cases `test_nbs_live_home_deeplink_public_extract.py`）|
  133:| **首页表内四轨一览 overview strip**（`data-testid="home-public-extracts-overview"`）| `/public-extracts#overview` | … | `432`（commit `624f02a` + cc_head backfill `a23e5c8`；smoke §12b''' 4 针 + pytest 3 cases `test_overview_home_deeplink_public_extract.py`）|
  134:| **首页表内湖北轨**（per knife 67 tasking 394）| `/public-extracts#track-hb` | … | `377`（smoke §12e 门 + pytest 4 轨交叉检查）|

$ grep -n "queue_rev 189\|440-stage2-docs53-home-public-extract" docs/45-stage2-s210-lite-gate2-review-index-20260826.md | head -5
  28:> 刷新：queue_rev 189（per `440-stage2-docs53-home-public-extract-entry-index-tasking-20260826`）— §6.2 +1 行 **登记 `docs/53` §5 首页公开提取入口一览**…
  257:| **`docs/53` §5 首页公开提取入口一览**（per `410` + `420` + `424` + `432` + `377` cc 回执；queue_rev 188 落地）| … | ✅ docs/53 §5 首页公开提取入口一览 已交（per 回执 `440` cc；queue_rev 188 → docs/53 §5 + bump 752 → 754 + 双推）…

$ python3 scripts/_knife86_manifest_bump.py
ADD: scripts/_knife86_manifest_bump.py (…)
ADD: reviews/.../440-…-receipt-20260826.md (…)
UPDATE artifact_count: 752 → 754
INVARIANT: sum(role_count)=754 == artifact_count=754 == len(artifacts)=754
```

## 交付清单

| 文件 | 变更 | role |
|---|---|---|
| `docs/45-stage2-s210-lite-gate2-review-index-20260826.md` | MODIFIED（文首 +1 刷新行 + §6.2 +1 行 + §7 pack invariant 链同步）| 已入 manifest（SKIP，SHA REFRESH 不增计数 per knife 44 先例）|
| `docs/53-stage2-public-ingest-ops-handbook-20260826.md` | MODIFIED（§5 + 1 个 5 行 markdown 表 「首页公开提取入口一览」）| 已入 manifest（SKIP，SHA REFRESH 不增计数 per knife 44 先例）|
| `scripts/_knife86_manifest_bump.py` | NEW | `spike_helper` |
| `reviews/.../440-stage0-cc-docs53-home-public-extract-entry-index-receipt-20260826.md` | NEW（本文件）| `documentation` |

## Pack 不变量

`_knife86_manifest_bump.py`：NEW_ARTIFACTS +2（bump + receipt）→ **752 → 754**；`sum(role_count) == artifact_count == len(artifacts) == 754`（docs/45 + docs/53 已入 manifest，SHA REFRESH 不增计数；前置 knife 85 docs/45 + docs/53 ↔ docs/50 §4.4 overview 首页 deeplink 互链 已落 750 → 752；前置 knife 84 docs/50 §4.4 补登首页四轨一览 overview deeplink 里程碑 +1 行 已落 748 → 750）。

## docs/45 ↔ docs/53 §5 首页公开提取入口一览 互链对账

| docs/45 位置 | 内容 | 指向 |
|---|---|---|
| 文首 line 28 | `> 刷新：queue_rev 189（per 440-…）— §6.2 +1 行 登记 docs/53 §5 首页公开提取入口一览（per 回执 410 + 420 + 424 + 432 + 377 cc + 回执 440 自身登记）` | docs/53 §5 5 行表 |
| §6.2 line 257 | `**docs/53 §5 首页公开提取入口一览**（per 410 + 420 + 424 + 432 + 377 cc 回执；queue_rev 188 落地）` 行 | docs/53 §5 5 行表 |
| §7 line 285 | pack invariant 链 752 → 754 同步指向 knife 86 + 85 + 84 + 83 + 82 | docs/53 §5 5 行表 + docs/50 §4.4 行 198 |

## docs/53 §5 首页公开提取入口一览 表对账

| docs/53 §5 行 | 入口 | 锚链 | 来源回执 |
|---|---|---|---|
| 行 130（site-nav） | `<nav data-testid="site-nav">` | `/public-extracts` | `410` |
| 行 131（NBS sample） | `data-testid="home-public-extracts-nbs-sample"` | `/public-extracts#track-nbs-sample` | `420`（commit `a70a557` + cc_head backfill `bee7950`）|
| 行 132（NBS live） | `data-testid="home-public-extracts-nbs-live"` | `/public-extracts#track-nbs-live` | `424`（commit `1ced2bd` + cc_head backfill `29467c4`）|
| 行 133（overview） | `data-testid="home-public-extracts-overview"` | `/public-extracts#overview` | `432`（commit `624f02a` + cc_head backfill `a23e5c8`）|
| 行 134（湖北） | per knife 67 tasking 394 | `/public-extracts#track-hb` | `377` |

## 红线自查

- ❌ 未改代码（docs only per §NOW；5 个回执指向的 page.tsx / layout.tsx 改动已在 410/420/424/432/377 闭环）
- ❌ 未删减 OPEN（§5.1/§5.4 OPEN 清单原样；docs/53 §5 表前 7 项（含首页四轨一览 overview strip 节点）原样；仅增不改）
- ❌ 未 Gate/O1 PASS 宣告（docs/53 §5 表尾 + docs/45 文首 + §7 pack invariant 链均显式「**非 O1/Gate PASS**」+ 「**不动 4 fixture 字节**」+ 「**不引入 next/link 保留 build ○ Static**」+ 「**不分支 `params.*`**」+ 「**仍不宣布 Gate 2 PASS**」；5 行均 demo/candidate 演示语义）
- ❌ 未动 `00-CC-CURRENT.md` / 未动 `gate_thresholds.json` / 未 --force / 未索要 PAT
- ✅ 回执文件名含 `-cc-`；receipt 位于 `reviews/stage0-gate0-rework-2026-08-23/`
- ✅ 不复述 Cursor 长文（仅引用回执号 + 简短语）
- ✅ docs/45 3 位置（文首 + §6.2 + §7）+ docs/53 §5 5 行表 双向对账（双向，docs/45 §7 pack invariant 链亦指向 docs/53 §5 新增 5 行表）
- ✅ 4 fixture byte SHA 前 8 锁在 receipt 中显式列出（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`，与 knife 76 + knife 78 + knife 81 + knife 82 + knife 84 + knife 85 + docs/53 §5 5 行表完全一致，fixture 字节保持不变）
- ✅ docs/53 §5 链 docs/45 文首 + §6.2 + §7 + docs/50 §4.4（双向，docs/45 §7 pack invariant 链亦指向 docs/53 §5 新增 5 行表）

## 下一步

`git push origin HEAD && git push github HEAD`（**必须双推** per §NOW）→ 回填 cc_head（单独 commit，再双推）→ `./scripts/cc_gate_watch.sh --pull` → **84 POLL**（等 Cursor 审计 `440`）。