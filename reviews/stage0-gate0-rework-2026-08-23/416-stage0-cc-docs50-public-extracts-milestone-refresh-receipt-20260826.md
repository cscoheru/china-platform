# 416 — docs/50 公开提取演示里程碑刷新 · CC 回执

- 编号：`416-stage0-cc-docs50-public-extracts-milestone-refresh-receipt-20260826`
- 任务书：`415-stage2-docs50-public-extracts-milestone-refresh-tasking-20260826`
- 作者：CC（heartbeat 84）
- cc_head：`TBD-pre-push`
- 日期：2026-08-26

---

## §NOW 对照

| 415 §SCHEMA 裁定 | 交付 | 证据 |
|---|---|---|
| (1) 刷新 `docs/50` Gate2 评审包草稿：增 **§公开提取演示里程碑**（四轨 + 一览 + 行筛选 + JSON/CSV + site-nav + 预览 URL；回执链至 `413`；显式 demo/非 O1）| ✅ docs/50 新增 **§4.4 公开提取演示里程碑**（位于 §4 演示场景 末尾，§5 OPEN 清单之前）：含 9 行里程碑表（公开源 connector + NBS 双轨 + 深圳轨 + 湖北轨 + 四轨一览条 + 四轨客户端行筛选 + 四轨 CSV 静态下载 + 全站顶栏 site-nav + docs/45+53 同步登记），覆盖 `344`→`413` 整条回执链；附 **预览 URL 块**（`/public-extracts` + 首页第三表链 + 城页 shenzhen + 任意省/地市页）+ **预览路径不构成 O1 / Gate 2 收口** 5 条 ⚠ 守门（四轨皆 demo / 行筛选仅视图过滤 / CSV 是 fixture 快照 / site-nav 仅顶栏入口 / live SHA drift 等 user 裁定）| diff |
| (2) 链到 `docs/45`/`53` | ✅ §4.4 文首显式「链到 `docs/45` §6.2 + `docs/53` §5」；表内最后一行里程碑单独标注「`docs/45 + docs/53` 同步登记」指向回执 `407`+`413` | diff |
| (3) **不**宣布 Gate2 PASS | ✅ §4.4 文首三连声明：「**全部为 demo/candidate 演示，非 O1/Gate 收口**」+「显式 demo/candidate 演示、非 O1/Gate PASS」（最后一行里程碑）+ 「预览路径不构成 O1 / Gate 2 收口」清单 5 条 ⚠ 守门 | diff |
| (4) 回执 `416`（`-cc-`）| ✅ 本文件名 | — |

## 证据

```
$ grep -n "§4.4\|公开提取演示里程碑" docs/50-stage2-gate2-review-packet-draft-20260826.md
181:#### 4.4 公开提取演示里程碑（per 回执链 `344`→`413`）
183:> ⚠ **本节是公开提取演示里程碑的端到端交付清单**（回执链 `344` → `362` → `368` → `371` → `377` → `383` → `398` → `404` → `410` → `413`）；**全部为 demo/candidate 演示，非 O1/Gate 收口**；链到 `docs/45` §6.2 + `docs/53` §5。
197:**预览 URL（per §4.4）**：
$ grep -n "344\|362\|368\|371\|377\|383\|398\|404\|407\|410\|413" docs/50-stage2-gate2-review-packet-draft-20260826.md | grep -v "4\.4" | head -20
$ grep -n "非 O1\|不宣布 Gate\|demo/candidate" docs/50-stage2-gate2-review-packet-draft-20260826.md | head -10

$ python3 scripts/_knife74_manifest_bump.py
ADD: scripts/_knife74_manifest_bump.py (…)
ADD: reviews/.../416-…-receipt-20260826.md (…)
UPDATE artifact_count: 725 → 727
INVARIANT: sum(role_count)=727 == artifact_count=727 == len(artifacts)=727
```

## 交付清单

| 文件 | 变更 | role |
|---|---|---|
| `docs/50-stage2-gate2-review-packet-draft-20260826.md` | MODIFIED（+§4.4「公开提取演示里程碑」共 ~32 行：文首警告 + 9 行里程碑表 + 预览 URL 块 + 预览路径不构成 O1/Gate 2 收口 5 条 ⚠ 守门）| 已入 manifest（SKIP，SHA REFRESH 不增计数 per knife 44 先例）|
| `scripts/_knife74_manifest_bump.py` | NEW | `spike_helper` |
| `reviews/.../416-stage0-cc-docs50-public-extracts-milestone-refresh-receipt-20260826.md` | NEW（本文件）| `documentation` |

## Pack 不变量

`_knife74_manifest_bump.py`：NEW_ARTIFACTS +2（bump + receipt）→ **725 → 727**；`sum(role_count) == artifact_count == len(artifacts) == 727`（docs/50 已入 manifest，SHA REFRESH 不增计数；前置 knife 73 已落 723 → 725）。

## §4.4 表内回执链覆盖（11 个里程碑点）

| # | 里程碑 | 关联回执 | 在 docs/50 §4.4 内 |
|---|---|---|---|
| 1 | 公开源自动获取 connector | `344` + `347` | ✅ 表 1 行 |
| 2 | NBS 双轨（sample ↔ LIVE_CANDIDATE）| `350`+`353`+`356`+`359`+`362` | ✅ 表 2 行 |
| 3 | 深圳散文轨 | `368` + `371` | ✅ 表 3 行 |
| 4 | 湖北 xlsx 轨 | `377` | ✅ 表 4 行 |
| 5 | 四轨一览条 overview strip | `383` | ✅ 表 5 行 |
| 6 | 四轨客户端行筛选 | `398` | ✅ 表 6 行 |
| 7 | 四轨 CSV 静态下载 | `404` + `407` | ✅ 表 7 行 |
| 8 | 全站顶栏 site-nav 常驻链 | `410` + `413` | ✅ 表 8 行 |
| 9 | docs/45 + docs/53 同步登记 | `407` + `413` | ✅ 表 9 行 |

## 红线自查

- ❌ 未改代码（docs only per §NOW；knife 72 layout 改动已在 `410`/`411` 闭环）
- ❌ 未删减 OPEN（§3/§5.1/§5.2/§5.3/§5.4/§5.5/§6 OPEN 清单原样；仅增不改）
- ❌ 未 Gate/O1 PASS 宣告（三连声明：§4.4 文首「**全部为 demo/candidate 演示，非 O1/Gate 收口**」+ 第 9 行里程碑表「**非 O1/Gate PASS**」+ 「预览路径不构成 O1 / Gate 2 收口」5 条 ⚠ 守门）
- ❌ 未动 `00-CC-CURRENT.md` / 未动 `gate_thresholds.json` / 未 --force / 未索要 PAT
- ✅ 回执文件名含 `-cc-`；receipt 位于 `reviews/stage0-gate0-rework-2026-08-23/`
- ✅ 不复述 Cursor 长文（仅引用回执号 + 简短语）
- ✅ §4.4 文首「链到 `docs/45` §6.2 + `docs/53` §5」与 knife 73 docs/45+53 登记对账
- ✅ 预览 URL 块附「不构成 O1/Gate 2 收口」紧随其后，避免误读为 Gate 收口演示

## 下一步

`git push origin HEAD && git push github HEAD`（**必须双推** per §NOW）→ 回填 cc_head（单独 commit，再双推）→ `./scripts/cc_gate_watch.sh --pull` → **84 POLL**（等 Cursor 审计 `415`）。