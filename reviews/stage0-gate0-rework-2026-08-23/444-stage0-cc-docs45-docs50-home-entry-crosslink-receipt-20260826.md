# 444 — docs/45 + docs/53 ↔ docs/50 §4.4 首页公开提取入口一览行 互链 · CC 回执

- 编号：`444-stage0-cc-docs45-docs50-home-entry-crosslink-receipt-20260826`
- 任务书：`444-stage2-docs45-docs50-home-entry-crosslink-tasking-20260826`
- 作者：CC（heartbeat 84）
- cc_head：`7e50ba6`（双推：origin 7b7a56a..7e50ba6，github 7b7a56a..7e50ba6）
- 日期：2026-08-26

---

## §NOW 对照

| 444 §SCHEMA 裁定 | 交付 | 证据 |
|---|---|---|
| (1) `docs/45` 刷新：文首 queue_rev 191 刷新行 + §1 + §6.2 + §7 互链 **`docs/50` §4.4 首页公开提取入口一览行**（回执 `442`；`docs/53` §5 `440`）| ✅ docs/45 文首新增 1 行（queue_rev 191，per 回执 `442` + cc_head backfill `6de6c5a`；docs/50 §4.4 行 199 新增 1 行「**首页公开提取入口一览**（顶栏 site-nav + 首页表内 4 deeplink 端到端入口演示汇总）」：交付列描述 docs/53 §5 5 行 markdown 表（site-nav + 4 首页 deeplink）+ 回执列 `440` + `6d54d63` + 守门列 smoke §13c + §12b' + §12b'' + §12b''' 合计 18 针 + pytest 3+5+3+3 = 14 cases + 4 fixture byte SHA 前 8 锁不漂：`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c` 与 knife 76/78/81/82/84/85/86 完全一致）；§1 +1 段「`docs/50` §4.4 新增 1 行 首页公开提取入口一览 里程碑补登」（per 回执 `442` + commit `0021930` + cc_head backfill `6de6c5a`）；§6.2 +1 行（镜像 knife 85 docs/45 docs/50 overview home deeplinks crosslink 行结构）；§7 pack invariant 链 754 → 756 → 758 同步指向 knife 88 + 87 + 86 | diff |
| (2) 可选 `docs/53` 一句 | ✅ docs/53 §5 新增 1 行（`🔗 **`docs/45` ↔ `docs/50` §4.4 首页公开提取入口一览行 互链**`，per 回执 `442` + commit `0021930` + cc_head backfill `6de6c5a`；docs/50 §4.4 里程碑表末尾补登 1 行；docs/45 文首 + §1 + §6.2 + §7 + docs/53 §5 第 15 项双向对账；4 fixture byte SHA 锁不漂与 knife 76/78/81/82/84/85/86 一致；不引入 `next/link` 保留 build ○ Static；不分支 `params.*`） | diff |
| (3) 非 O1/Gate PASS | ✅ 文首 + §1 + §6.2 + §7 + docs/53 §5 第 15 项均显式标注「**docs/50 §4.4 行 199 是 Gate 2 评审包草稿里程碑表顶栏 site-nav + 首页表内 4 deeplink 端到端入口演示节点，非 O1/Gate PASS；不动 4 fixture 字节；不引入 next/link 保留 build ○ Static；不分支 `params.*`；仍不宣布 Gate 2 PASS**」；与 §4.4 intro ⚠ 守门一致（四轨皆 demo/candidate 演示）；5 条 ⚠「预览路径不构成 O1 / Gate 2 收口」原样保留 | diff |
| (4) 回执 `444`（`-cc-`）| ✅ 本文件名 | — |

## 证据

```
$ grep -n "queue_rev 191\|442\|0021930\|6de6c5a" docs/45-stage2-s210-lite-gate2-review-index-20260826.md | head -10
  29:> 刷新：queue_rev 191（per `444-stage2-docs45-docs50-home-entry-crosslink-tasking-20260826`）— ...
  53:**`docs/50` §4.4 新增 1 行 首页公开提取入口一览 里程碑补登**（per `442` cc 回执；queue_rev 190 落地；commit `0021930` + cc_head backfill `6de6c5a`）...
  260:| **`docs/50` §4.4 新增 1 行 首页公开提取入口一览 里程碑补登**（per `442` cc 回执；queue_rev 190 落地；commit `0021930` + cc_head backfill `6de6c5a`）...

$ grep -n "第 15 项\|442\|0021930\|6de6c5a" docs/53-stage2-public-ingest-ops-handbook-20260826.md | head -5
  138:> 🔗 **`docs/45` ↔ `docs/50` §4.4 首页公开提取入口一览行 互链**（per `442` cc 回执；queue_rev 190 落地；commit `0021930` + cc_head backfill `6de6c5a`）...

$ python3 scripts/_knife88_manifest_bump.py
ADD: scripts/_knife88_manifest_bump.py (…)
ADD: reviews/.../444-…-receipt-20260826.md (…)
UPDATE artifact_count: 756 → 758
INVARIANT: sum(role_count)=758 == artifact_count=758 == len(artifacts)=758
```

## 交付清单

| 文件 | 变更 | role |
|---|---|---|
| `docs/45-stage2-s210-lite-gate2-review-index-20260826.md` | MODIFIED（文首 +1 刷新行 + §1 +1 段 + §6.2 +1 行 + §7 pack invariant 链同步）| 已入 manifest（SKIP，SHA REFRESH 不增计数 per knife 44 先例）|
| `docs/53-stage2-public-ingest-ops-handbook-20260826.md` | MODIFIED（§5 第 15 项）| 已入 manifest（SKIP，SHA REFRESH 不增计数 per knife 44 先例）|
| `scripts/_knife88_manifest_bump.py` | NEW | `spike_helper` |
| `reviews/.../444-stage0-cc-docs45-docs50-home-entry-crosslink-receipt-20260826.md` | NEW（本文件）| `documentation` |

## Pack 不变量

`_knife88_manifest_bump.py`：NEW_ARTIFACTS +2（bump + receipt）→ **756 → 758**；`sum(role_count) == artifact_count == len(artifacts) == 758`（docs/45 + docs/53 已入 manifest，SHA REFRESH 不增计数；前置 knife 87 docs/50 §4.4 补登首页公开提取入口一览 里程碑 +1 行 已落 754 → 756；前置 knife 86 docs/53 §5 首页公开提取入口一览 5 行表 已落 752 → 754；前置 knife 85 docs/45 + docs/53 ↔ docs/50 §4.4 overview 首页 deeplink 互链 已落 750 → 752）。

## docs/45 ↔ docs/50 §4.4 首页入口一览 互链对账

| docs/45 位置 | 内容 | 指向 |
|---|---|---|
| 文首 line 29 | `> 刷新：queue_rev 191（per 444...）— §1 + §6.2 + §7 互链 docs/50 §4.4 首页公开提取入口一览行 里程碑补登（per 回执 442 + cc_head backfill 6de6c5a）` | docs/50 §4.4 行 199 |
| §1 line 53 | `**docs/50 §4.4 新增 1 行 首页公开提取入口一览 里程碑补登**` 段（per 回执 442 + commit 0021930 + cc_head backfill 6de6c5a）| docs/50 §4.4 行 199 |
| §6.2 line 260 | `**docs/50 §4.4 新增 1 行 首页公开提取入口一览 里程碑补登**` 行（per 回执 442 + commit 0021930 + cc_head backfill 6de6c5a）| docs/50 §4.4 行 199 |
| §7 line 288 | pack invariant 链 754 → 756 → 758 同步指向 knife 88 + 87 + 86 + 85 + 84 + 83 | docs/50 §4.4 行 199 + 198 + 197 |

## docs/53 ↔ docs/50 §4.4 首页入口一览 互链对账

| docs/53 位置 | 内容 | 指向 |
|---|---|---|
| §5 line 138（新增第 15 项）| `🔗 docs/45 ↔ docs/50 §4.4 首页公开提取入口一览行 互链`（per 回执 442 + commit 0021930 + cc_head backfill 6de6c5a）| docs/50 §4.4 行 199 |

## 红线自查

- ❌ 未改代码（docs only per §NOW；knife 87 docs/50 §4.4 改动已在 `442` 闭环）
- ❌ 未删减 OPEN（§5.1/§5.4 OPEN 清单原样；5 条 ⚠「预览路径不构成 O1 / Gate 2 收口」原样保留；仅增不改）
- ❌ 未 Gate/O1 PASS 宣告（文首 + §1 + §6.2 + §7 + docs/53 §5 第 15 项均显式「**非 O1/Gate PASS**」+ 「**顶栏 site-nav + 首页表内 4 deeplink 端到端入口演示节点**」+ 「**不动 4 fixture 字节**」+ 「**不引入 next/link 保留 build ○ Static**」+ 「**不分支 `params.*`**」+ 「**仍不宣布 Gate 2 PASS**」；§4.4 intro ⚠ 守门保留）
- ❌ 未动 `00-CC-CURRENT.md` / 未动 `gate_thresholds.json` / 未 --force / 未索要 PAT
- ✅ 回执文件名含 `-cc-`；receipt 位于 `reviews/stage0-gate0-rework-2026-08-23/`
- ✅ 不复述 Cursor 长文（仅引用回执号 + 简短语）
- ✅ docs/45 4 位置（文首 + §1 + §6.2 + §7）+ docs/53 §5 第 15 项 + docs/50 §4.4 行 199 三向对账（双向，docs/45 §7 pack invariant 链亦指向 docs/50 §4.4 新增 1 行）
- ✅ 4 fixture byte SHA 前 8 锁在 receipt 中显式列出（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`，与 knife 76 + knife 78 + knife 81 + knife 82 + knife 84 + knife 85 + knife 86 + knife 87 + docs/50 §4.4 行 199 完全一致，fixture 字节保持不变）
- ✅ docs/50 §4.4 链 docs/45 §1 + §6.2 + §7 + docs/53 §5（双向，docs/45 §7 pack invariant 链亦指向 docs/50 §4.4 新增 1 行）

## 下一步

`git push origin HEAD && git push github HEAD`（**必须双推** per §NOW）→ 回填 cc_head（单独 commit，再双推）→ `./scripts/cc_gate_watch.sh --pull` → **84 POLL**（等 Cursor 审计 `444`）。