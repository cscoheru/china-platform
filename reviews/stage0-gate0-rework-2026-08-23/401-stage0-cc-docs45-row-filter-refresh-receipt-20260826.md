# 401 — docs/45 + docs/53 行筛选登记 · CC 回执

- 编号：`401-stage0-cc-docs45-row-filter-refresh-receipt-20260826`
- 任务书：`400-stage2-docs45-row-filter-refresh-tasking-20260826`
- 作者：CC（heartbeat 84）
- cc_head：`0674fdd`
- 日期：2026-08-26

---

## §NOW 对照

| 400 §SCHEMA 裁定 | 交付 | 证据 |
|---|---|---|
| (1) `docs/45` 登记 `/public-extracts` 四轨客户端行筛选（回执 `398`；smoke §12h）；顺带注首页标题已改为「官方公开数据 · 结构化呈现（demo）」 | ✅ docs/45 四处：文首 +`刷新 queue_rev 166` 行；§1 回执链 +`→ 398（四轨客户端行筛选…）` 段 + 守门句扩为「四轨 + 一览条 + 行筛选皆 demo/candidate 演示（行筛选仅为客户端视图过滤，非权威库检索）」+ 首页标题注（commit `855602c`）；§6.2 +「`/public-extracts` 四轨客户端行筛选（视图过滤）」一行（input ×4 / filterRows 包含匹配 / use client ○ Static / §12h 11 针 + 3 pytest / 不改 fixture 字节 / 非权威库检索）；§7 pack invariant 行更新 692 → 710 链（含 knife 64-68） | diff |
| (2) 可选 `docs/53` 一句 | ✅ docs/53 两处：§5 预览清单 +第 6 项「各数据表 = 每轨独立行筛选」（含守门要点 + 回执 `398` + smoke §12h 门）；冒烟行 + §12h 门注记 | diff |
| (3) 显式非 O1/Gate PASS | ✅ 文首刷新行 + §1 守门句 + §6.2 状态列三处显式「行筛选是客户端视图过滤演示，非权威库检索、非 O1/Gate PASS；仍不宣布 Gate 2 PASS」 | diff |
| (4) 回执 `401`（`-cc-`） | ✅ 本文件名 | — |

## 证据

```
$ grep -c "398\|§12h" docs/45-stage2-s210-lite-gate2-review-index-20260826.md   # ≥4 处登记
$ grep -n "行筛选" docs/53-stage2-public-ingest-ops-handbook-20260826.md        # §5 第 6 项 + 冒烟注

$ python3 scripts/_knife69_manifest_bump.py
ADD: scripts/_knife69_manifest_bump.py (…)
ADD: reviews/.../401-…-receipt-20260826.md (…)
UPDATE artifact_count: 708 → 710
INVARIANT: sum(role_count)=710 == artifact_count=710 == len(artifacts)=710
```

## 交付清单

| 文件 | 变更 | role |
|---|---|---|
| `docs/45-stage2-s210-lite-gate2-review-index-20260826.md` | MODIFIED（+queue_rev 166 刷新行 + §1 回执链 398 段 + 首页标题注 + §6.2 行筛选行 + §7 不变量链 710） | 已入 manifest（SKIP，SHA REFRESH 不增计数 per knife 44 先例） |
| `docs/53-stage2-public-ingest-ops-handbook-20260826.md` | MODIFIED（§5 +第 6 项行筛选 + 冒烟 §12h 注） | 已入 manifest（SKIP） |
| `scripts/_knife69_manifest_bump.py` | NEW | `spike_helper` |
| `reviews/.../401-stage0-cc-docs45-row-filter-refresh-receipt-20260826.md` | NEW（本文件） | `documentation` |

## Pack 不变量

`_knife69_manifest_bump.py`：NEW_ARTIFACTS +2（bump + receipt）→ **708 → 710**；`sum(role_count) == artifact_count == len(artifacts) == 710`（docs/45 / docs/53 皆已入 manifest，SHA REFRESH 不增计数；前置 knife 68 已落 706 → 708）。

## 红线自查

- ❌ 未改页面 / 业务代码（docs only per §NOW；knife 68 的页面改动已在 `398`/`399` 闭环）
- ❌ 未谎称筛选=权威检索（三处显式「客户端视图过滤 / 非权威库检索」）
- ❌ 未删减 OPEN（§3/§5.5/§6 OPEN 清单原样；仅增不改）
- ❌ 未 Gate/O1 PASS 宣告（多处显式「仍不宣布 Gate 2 PASS」）
- ❌ 未动 `00-CC-CURRENT.md` / 未动 `gate_thresholds.json` / 未 --force / 未索要 PAT
- ✅ 回执文件名含 `-cc-`；receipt 位于 `reviews/stage0-gate0-rework-2026-08-23/`

## 下一步

`git push origin HEAD && git push github HEAD`（**必须双推** per §NOW）→ 回填 cc_head（单独 commit，再双推）→ `./scripts/cc_gate_watch.sh --pull` → **84 POLL**（等 Cursor 审计 402）。
