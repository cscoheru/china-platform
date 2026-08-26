# 413 — docs/45 + docs/53 site-nav + CSV 再登记 · CC 回执

- 编号：`413-stage0-cc-docs45-site-nav-csv-refresh-receipt-20260826`
- 任务书：`412-stage2-docs45-site-nav-csv-refresh-tasking-20260826`
- 作者：CC（heartbeat 84）
- cc_head：`TODO_BACKFILL`
- 日期：2026-08-27

---

## §NOW 对照

| 412 §SCHEMA 裁定 | 交付 | 证据 |
|---|---|---|
| (1) `docs/45` 登记全站 `site-nav` → `/public-extracts`（回执 `410`；smoke §13c）+ 四轨 CSV 静态下载（回执 `404`/`407`；`public/public-extracts/*.csv`） | ✅ docs/45 五处：文首 +`刷新 queue_rev 174` 行（含 site-nav + 再述 CSV 双针）；§1 回执链 +`→ 410（全站顶栏 site-nav → /public-extracts 常驻链）` 段 + 守门句扩为「四轨 + 一览条 + 行筛选 + CSV 下载 + 全站顶栏 site-nav 皆 demo/candidate 演示」；§6.2 +「**全站顶栏 `site-nav` → `/public-extracts` 常驻链**（顶栏入口演示）」一行（`<nav data-testid="site-nav">` + 首页 + `/public-extracts` 链 + 旁注 + 纯 `<a href>` 不引入 `next/link` + 不分支 `params.*` + smoke §13c 6 针 + 5 pytest + 回执 410，build 仍 ○ Static）；§7 pack invariant 行更新 720 → 725 链（knife 72 + knife 73）| diff |
| (2) 可选 `docs/53` 一句 | ✅ docs/53 两处：§5 预览清单 +第 7 项「全站顶栏 `site-nav` = `/public-extracts` 常驻入口」（含 `<nav data-testid="site-nav">` + 首页 + `/public-extracts` 链 + 旁注 + 纯 `<a href>` 不引入 `next/link` + build 仍 ○ Static + 不分支 `params.*` + 回执 410 + smoke §13c 门 6 针 + 5 pytest + 非 O1/Gate PASS + 不引入 next/link 保留 build ○ Static 特征）；冒烟行 + §13c 门注记（保持 §12i 不出现的现状，不重复字段）| diff |
| (3) 非 O1/Gate PASS | ✅ 文首刷新行 + §1 守门句 + §6.2 状态列三处显式「site-nav 是顶栏入口演示，非 O1/Gate PASS；CSV 是 fixture 快照确定性导出 (demo/candidate)，非权威库、非 O1/Gate PASS；仍不宣布 Gate 2 PASS」| diff |
| (4) 回执 `413`（`-cc-`） | ✅ 本文件名 | — |

## 证据

```
$ grep -c "410\|§13c\|site-nav" docs/45-stage2-s210-lite-gate2-review-index-20260826.md   # ≥4 处登记
$ grep -n "site-nav\|§13c" docs/53-stage2-public-ingest-ops-handbook-20260826.md          # §5 第 7 项 + 冒烟注

$ python3 scripts/_knife73_manifest_bump.py
ADD: scripts/_knife73_manifest_bump.py (…)
ADD: reviews/.../413-…-receipt-20260826.md (…)
UPDATE artifact_count: 723 → 725
INVARIANT: sum(role_count)=725 == artifact_count=725 == len(artifacts)=725
```

## 交付清单

| 文件 | 变更 | role |
|---|---|---|
| `docs/45-stage2-s210-lite-gate2-review-index-20260826.md` | MODIFIED（+queue_rev 174 刷新行 + §1 回执链 410 段 + 守门句扩为含 site-nav + §6.2 site-nav 行 + §7 不变量链 725）| 已入 manifest（SKIP，SHA REFRESH 不增计数 per knife 44 先例）|
| `docs/53-stage2-public-ingest-ops-handbook-20260826.md` | MODIFIED（§5 +第 7 项 site-nav + 冒烟 §13c 注）| 已入 manifest（SKIP）|
| `scripts/_knife73_manifest_bump.py` | NEW | `spike_helper` |
| `reviews/.../413-stage0-cc-docs45-site-nav-csv-refresh-receipt-20260826.md` | NEW（本文件）| `documentation` |

## Pack 不变量

`_knife73_manifest_bump.py`：NEW_ARTIFACTS +2（bump + receipt）→ **723 → 725**；`sum(role_count) == artifact_count == len(artifacts) == 725`（docs/45 / docs/53 皆已入 manifest，SHA REFRESH 不增计数；前置 knife 72 已落 720 → 723）。

## 红线自查

- ❌ 未改代码（docs only per §NOW；knife 72 的 layout 改动已在 `410`/`411` 闭环）
- ❌ 未删减 OPEN（§3/§5.5/§6 OPEN 清单原样；仅增不改）
- ❌ 未 Gate/O1 PASS 宣告（三处显式「site-nav 是顶栏入口演示，非 O1/Gate PASS；CSV 是 fixture 快照确定性导出 (demo/candidate)，非权威库、非 O1/Gate PASS；仍不宣布 Gate 2 PASS」）
- ❌ 未动 `00-CC-CURRENT.md` / 未动 `gate_thresholds.json` / 未 --force / 未索要 PAT
- ✅ 回执文件名含 `-cc-`；receipt 位于 `reviews/stage0-gate0-rework-2026-08-23/`
- ✅ 不再述 CSV 字段（指向既有 §6.2 CSV 行）；不重复 §12i 描述（保持 linter 维护的现状）；site-nav 字段再述含 build ○ Static + 不分支 params.*

## 下一步

`git push origin HEAD && git push github HEAD`（**必须双推** per §NOW）→ 回填 cc_head（单独 commit，再双推）→ `./scripts/cc_gate_watch.sh --pull` → **84 POLL**（等 Cursor 审计 414）。