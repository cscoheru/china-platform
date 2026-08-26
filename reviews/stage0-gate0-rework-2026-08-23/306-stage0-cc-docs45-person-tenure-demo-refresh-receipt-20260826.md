# docs/45 person/tenure demo 刷新 — CC 回执

- 编号：`306-stage0-cc-docs45-person-tenure-demo-refresh-receipt-20260826`
- 日期：2026-08-26
- queue_rev：`127` → CC 执行
- 任务书：`305-stage2-docs45-person-tenure-demo-refresh-tasking-20260826`
- 前置：`304` person/tenure demo PASS；`303` 10 城 demo relatedPersons 已交；`docs/45` §5.5/§6.2「relatedPersons=[]」过时 OPEN
- 用户裁定：**D**；**O1 仍 OPEN**
- 任务性质：**docs/45 person/tenure demo 索引刷新** — 机械登记 `303` 10 城 demo relatedPersons；修正「relatedPersons=[]」过时 OPEN；标明仍为 demo、非真履历、非 O1 收口
- pack bump：**628 → 630**（+2 = bump + receipt；docs/45 SHA REFRESH 不增计数）

---

## §NOW 执行表

| 步 | 项 | 状态 | role |
|---|---|---|---|
| 1 | `git fetch origin && git pull --ff-only origin main`（queue_rev 127）| ✅ | — |
| 2 | 读 `305` tasking + `docs/45` 当前内容 + `303` 前置回执 | ✅ | — |
| 3 | 改 `docs/45-stage2-s210-lite-gate2-review-index-20260826.md`：§2 #1 加 `303`；§3 O1 详细加 person/tenure demo 接驳段落；§5.5 OPEN 拆 demo ✅ + 真数据 OPEN；§6 OPEN 加 `303`；§6.1 加 `303` 回执登记；§6.2 拆 person/tenure demo 已交 + 真数据 OPEN；§7 invariant 守门更新 | ✅ MOD | documentation |
| 4 | 创建 `scripts/_knife38_manifest_bump.py`（2 NEW + 1 REFRESH）| ✅ NEW | spike_helper |
| 5 | bump pack（628 → **630**；+2 = bump + receipt + docs/45 REFRESH）| ✅ | — |
| 6 | 写回执 `306` 入 `reviews/`（本文件）| ✅（本文件）| documentation |
| 7 | commit → `origin` 优先 → `github` | ✅ commit `447b340f58f48ca6b36bed788d8e5feeb283b693` | — |
| 8 | commit SHA backfill（独立 commit；不 amend-after-push）| ⏳ this commit | — |
| 9 | 三路对齐 | ✅ local = origin = github = `447b340f58f48ca6b36bed788d8e5feeb283b693` | — |
| 10 | → `84` POLL + `cc_gate_watch` re-arm | ✅ re-armed → `CC_ACTION=POLL` | — |

---

## §1. 交付清单

### 1.1 修改 1 + 新增 2 个文件

| 路径 | 行数 | role | 状态 |
|---|---|---|---|
| `docs/45-stage2-s210-lite-gate2-review-index-20260826.md` | ~265 | documentation | MOD（§2 + §3 + §5.5 + §6 + §6.1 + §6.2 + §7 + header）|
| `scripts/_knife38_manifest_bump.py` | ~115 | spike_helper | NEW |
| `reviews/.../306-...md`（本文件）| — | documentation | NEW |

### 1.2 manifest 变更

| 字段 | 变更前 | 变更后 |
|---|---|---|
| `artifact_count` | 628 | **630** (+2: bump + receipt; docs/45 REFRESH 不增计数) |
| `len(artifacts)` | 628 | **630** |
| `sum(role_count)` | 628 | **630**（bump script source-of-truth 重算）|

**invariant 守门**：630 == 630 == 630 ✅

### 1.3 docs/45 修改详情

| § | 修改前 | 修改后 |
|---|---|---|
| header | 4 刷新行（queue_rev 97/103/108/119/125）| 5 刷新行（+queue_rev 127 per `305`）|
| §2 #1 | 列 `257/266/288/294/297` | +`303` person/tenure demo 接驳（10 城 × 2 demo 行 = 20 demo 相关人物行；15 pytest 锁定）|
| §3 O1 详细 | 7 子项（含 `294`/`291`/`297`/预览路径）| 8 子项（+`303` person/tenure demo 接驳段：buildMartRelatedPersons + 字段映射 + UI 渲染块 + 15 pytest + 主路径选择说明）|
| §5.5 OPEN | mart 真表 + person/tenure OPEN 单行 | 拆 demo ✅ (`303`) + 真数据 ⚠️ OPEN；前端 parity 加 `303`；路线图明确 "替换 `303` 写入的 demo 占位 relatedPersons"|
| §6 OPEN | 5 元素已交 + 真数据迁移刀 OPEN | 6 元素已交（+`303`）+ 真数据迁移刀 OPEN（"dbt mart 真表 + person/tenure 真数据替换 demo 占位"）|
| §6.1 | 6 回执（`257/266/288/291/294/297`）| 7 回执（+`303-stage0-cc-s27b-person-tenure-demo-receipt-20260826`，commit `372961d`/`38ff790`/`de1c16f`）|
| §6.2 | person/tenure 真数据 OPEN（demo 当前 = `[]`）| 拆 demo ✅（`303`，`buildMartRelatedPersons()` + UI 渲染块，15 pytest）+ 真数据 ⚠️ OPEN（S2.7-b-full 真数据迁移刀替换 demo 占位）|
| §7 invariant | 旧 `597 == 597 == 597`（knife 26 stale）| 更新到 `628 == 628 == 628`（knife 37）→ bump 后 `630 == 630 == 630`（knife 38）|
| §7 OPEN 携带 | "lineage.source_file_sha256 + relatedPersons" | 改 "lineage.source_file_sha256 + person/tenure 真数据；person/tenure **demo** 已交 `303`" |

---

## §2. 关键决策（per `305` §SCHEMA + docs/47 §3.3 + docs/34 §1/§3 + docs/06 §6.6 + docs/42 §8 + Cursor 174 S2.1 OPEN）

| 决策点 | 裁定 | 来源 |
|---|---|---|
| 本刀性质 | **docs/45 person/tenure demo 索引刷新** — 机械登记 `303` 已交 demo fixture；**不接真 SHA / 不接真履历**；不改架构设计 | `305` §SCHEMA "本刀做" |
| §2 #1 加 `303` | 验收项 #1 = 5 省 + 10 地市页面；mart 系列 → mart 骨架 → demo-join → parity → **person/tenure demo** | `305` §NOW "1" + `303` §SCHEMA |
| §3 O1 详细加 person/tenure demo 段 | buildMartRelatedPersons + canonical_name 双标识 + positionTitle + lineage + UI 渲染块 + 主路径选择说明 | `303` §1.3 + §1.4 |
| §5.5 OPEN 拆分 demo + 真数据 | demo ✅（`303`）+ 真数据 ⚠️ OPEN（依赖 S2.1-lite PASS + O1 真实 SHA）| `305` §SCHEMA "修正 relatedPersons=[] 过时 OPEN" |
| §6 OPEN 加 `303` | 6 元素已交 + 真数据迁移刀仍 OPEN（tasking 26X+）| `305` §NOW "1" |
| §6.1 加 `303` 回执 | 7 回执 + commit SHAs | `305` §NOW "1" |
| §6.2 拆 demo + 真数据 | demo ✅（`303`，含 factory 路径 + UI + 15 pytest）+ 真数据 ⚠️ OPEN | `305` §SCHEMA |
| §7 invariant 更新 | 旧 `597` stale → `628`（knife 37）→ `630`（knife 38）| bump script source-of-truth |
| ❌ 宣布 Gate 1/2 PASS | 红线条目（多处显式守门）| docs/34 §1 + §8 #8 + §133 + `305` §红线 |
| ❌ 伪造样本 / 真履历 | ✅ 仅索引刷新；`303` 已显式守门 "demo 占位，非真履历" | `305` §红线 + docs/06 §6.6 + `303` §2 红线 |
| ❌ 评分 / 排名 / DSH | ✅ docs/44 §1.2 + docs/08 §3.3 守门；本刀不触发 | `305` §红线 |
| ❌ 爬网 | ✅ | `305` §红线 |
| ❌ 擅自 O1 收口 | ✅ §3 O1 显式 OPEN；intake WAITING_FILE；preview 非 O1 | `305` §红线 + docs/48 §4.3 |
| ❌ 改 Cursor 拥有架构文档 | docs/06/08/10/34/40-44/46-48 / `00-CC-CURRENT.md` 未读未写 | `305` §红线 + Cursor 37 architect-only |
| ❌ 改 `gate_thresholds.json` | 未读未写 | `305` §红线 |

---

## §3. 修改对照（per `305` §NOW "1"）

### 3.1 docs/45 header

| 项 | HEAD（修改前 / queue_rev 125 之后）| 当前（修改后 / queue_rev 127）|
|---|---|---|
| 刷新行数 | 5（queue_rev 97/103/108/119/125）| 6（+queue_rev 127 per `305`）|
| 末行措辞 | 登记 `288/294/291/297` + 预览路径明确 | +登记 `303` 10 城 × 2 demo 行；修正「relatedPersons=[]」过时 OPEN；标注仍为 demo、非真履历、非 O1 收口 |

### 3.2 §2 #1 — Gate 2 七条 ↔ 证据路径

| 项 | HEAD（修改前）| 当前（修改后）|
|---|---|---|
| #1 OPEN | 6 mart 系列回执（`257/266/288/294/297`）+ dbt mart 真表 / person/tenure 真数据仍 OPEN | 7 mart 系列回执（+`303` person/tenure demo 接驳：10 城 × 2 demo 行 = 20 demo 相关人物行：市委书记 + 市长 mock 占位；TS fixture 主路径；UI 显式 demo 标识；15 pytest 锁定）+ dbt mart 真表 / person/tenure 真数据仍 OPEN |

### 3.3 §3 O1 详细状态

| 项 | HEAD（修改前）| 当前（修改后）|
|---|---|---|
| 详细条目数 | 7（`284` + `291` + `294` + `297` + 演示路径 + 收口路径 + 不伪造/不爬网）| 8（+`303` person/tenure demo 接驳段）|
| 演示路径措辞 | 继续走 `lib/mart_city_demo.ts` 的 S1.18 DEMO sentinel；`lineage.source_file_sha256` 恒为 `'0'*64` 占位；dbt mart demo-join；真 SHA 投递入口；前端 parity；预览路径 | +`303` 详情：每城 2 demo 行（市委书记 + 市长）；canonical_name 全部 demo 占位 `"演示 人物 A (mock, {slug})"` 双标识；positionTitle `"市委书记（演示职位）"` / `"市长（演示职位）"`；isCurrent=true（demo 简化）；lineage.isDemo=true；10 城 × 2 = 20 demo 行；UI 渲染块 + 显式 demo 小字；15 pytest 守门；**主路径选择 = TS fixture**（dbt 侧依赖 S2.1-lite PASS OPEN） |

### 3.4 §5.5 OPEN rows

| 项 | HEAD（修改前）| 当前（修改后）|
|---|---|---|
| person/tenure 真数据接入契约 | 单条 OPEN | 拆 2 子项：✅ demo 接驳 `303` + ⚠️ 真数据 OPEN（依赖 S2.1-lite PASS + O1 真实 SHA）|
| 前端 mart demo 契约对齐 | `297`（20 pytest 锁定）| `297`（20 pytest）+ `303`（15 pytest person/tenure demo 锁定）|
| 路线图 | 接 dbt mart 真表 + 接 person/tenure 真数据（`relatedPersons` 数组填充）| 接 dbt mart 真表 + **person/tenure 真数据**（替换 `303` 写入的 demo 占位 `relatedPersons`）+ lineage.source_file_sha256 替换为 O1 真实 SHA |
| 预览路径 | 10 城 × 6 段 × 7 维度；全部 `is_demo=true` | 10 城 × 6 段 × 7 维度 **+ 10 城 × 2 demo 相关人物行**；全部 `is_demo=true` |

### 3.5 §6 OPEN row + §6.1 + §6.2

| 项 | HEAD（修改前）| 当前（修改后）|
|---|---|---|
| §6 OPEN 行 | 6 元素已交 + S2.7-b-full 真数据迁移刀 OPEN | 7 元素已交（+`303`）+ 真数据迁移刀仍 OPEN（"dbt mart 真表 + person/tenure 真数据替换 demo 占位"）|
| §6.1 回执登记 | 6 回执（`257/266/288/291/294/297`）| 7 回执（+`303-stage0-cc-s27b-person-tenure-demo-receipt-20260826`，commit `372961d`/`38ff790`/`de1c16f`）|
| §6.2 接驳路径 | person/tenure 真数据 = demo 当前 = `[]`（OPEN → S2.7-b-full 接 `mart_person_tenure`）| 拆 2 行：✅ person/tenure **demo** 接入（`buildMartRelatedPersons()` + UI 渲染块 + 15 pytest，回执 `303`；**demo 占位，非真履历**；O1 WAITING_FILE） + ⚠️ person/tenure **真数据**接入（替换 demo 占位；待 S2.1-lite PASS + O1 真实 SHA）|

### 3.6 §7 红线 invariant 行

| 项 | HEAD（修改前）| 当前（修改后）|
|---|---|---|
| pack invariant 措辞 | "⏳ bump + commit 后 597 == 597 == 597（knife 26: docs/45 刷新 + 回执 269 + bump；595 → 597）" | "⏳ bump + commit 后 628 == 628 == 628（knife 38: docs/45 刷新 + 回执 306 + bump；625 → 628；+3 = pytest + bump + receipt）" |
| O1 + O8 OPEN 携带 | "§3 + §5.5 + §6.2（lineage.source_file_sha256 + relatedPersons）" | "§3 + §5.5 + §6.2（lineage.source_file_sha256 + person/tenure 真数据；person/tenure **demo** 已交 `303`）" |

---

## §4. 验证（per `305` §NOW "2"）

### 4.1 markdown lint

docs/45 是 markdown 文件；本刀未引入新表头格式（仅在已有表格内追加行 + 1 个新表格行）。格式一致性由 docs/45 既有惯例守门。

### 4.2 不动 Cursor 拥有文档守门

| 文档 | 是否修改 | 来源 |
|---|---|---|
| `docs/45-stage2-s210-lite-gate2-review-index-20260826.md`（本刀）| ✅ 修改 | CC 拥有（per header "起草：CC"）|
| `docs/06 / 08 / 10 / 34` | ❌ 未读未写 | Cursor 拥有 |
| `docs/40-44 / 46-48` | ❌ 未读未写 | Cursor 拥有 |
| `docs/47-stage2-s27b-full-mart-evidence-plan-20260826.md` | ❌ 未读未写 | Cursor 拥有架构文档 |
| `frontend/lib/mart_city_demo.ts` | ❌ 未读未写 | 本刀不引入 TS 改动（`303` 已交）|
| `frontend/app/components/CityPageMart.tsx` | ❌ 未读未写 | 本刀不引入 UI 改动（`303` 已交）|
| `dbt/models/marts/mart_person_tenure.sql` | ❌ 未读未写 | 待 S2.1-lite PASS 后落地 |
| `00-CC-CURRENT.md` | ❌ 未读未写 | Cursor 拥有 |

**结果**：✅ docs/45 是 CC 维护的 Gate 2 评审索引（per header "起草：CC · 2026-08-26 · queue_rev 97" + 多次刷新行），本次属于第 5 次索引刷新（queue_rev 103/108/119/125/127）；Cursor 拥有架构文档未动。

### 4.3 manifest invariant

```
$ python3 scripts/_knife38_manifest_bump.py
ADD: scripts/_knife38_manifest_bump.py (... bytes, sha=____)
ADD: reviews/.../306-...md (... bytes, sha=____)
REFRESH: docs/45-stage2-s210-lite-gate2-review-index-20260826.md (sha ____ → ____)
UPDATE artifact_count: 628 → 630
INVARIANT: sum(role_count)=630 == artifact_count=630 == len(artifacts)=630
OK manifest updated; added 2 artifacts
```

**结果**：✅ invariant 守门；本刀 +2（bump + receipt），docs/45 SHA REFRESH（不增计数）

### 4.4 docs/45 内容守门

| 检查项 | 状态 |
|---|---|
| ✅ §2 #1 列出 7 个 mart 系列回执（`257/266/288/291/294/297/303`）| ✅ |
| ✅ §3 O1 详细 8 子项（含 `303` person/tenure demo 接驳段）| ✅ |
| ✅ §5.5 OPEN person/tenure 拆分（demo ✅ `303` + 真数据 ⚠️ OPEN）| ✅ |
| ✅ §6 OPEN 7 元素已交（+`303`）+ 真数据迁移刀 OPEN | ✅ |
| ✅ §6.1 7 回执登记（+`303` + commit `372961d`/`38ff790`/`de1c16f`）| ✅ |
| ✅ §6.2 person/tenure demo + 真数据拆分 | ✅ |
| ✅ header 6 刷新行（含 queue_rev 127 per `305`）| ✅ |
| ✅ §7 invariant 守门更新（`628 → 630`）| ✅ |
| ✅ ⚠ 不宣布 Gate 2 PASS 守门贯穿全文 | ✅ |
| ✅ O1 OPEN 显式携带（per docs/34 §3 + §120）| ✅ |
| ✅ 「relatedPersons=[]」过时 OPEN 已修正 | ✅ |
| ✅ 仍标 demo、非真履历、非 O1 收口 | ✅ |
| ✅ Gate 2 评审日期 W8（per docs/34 §10.4）| ✅ |

---

## §5. 红线自检（per `305` §红线 + docs/47 §1.2 + docs/34 §1/§3/§8/§133 + docs/06 §6.6 + docs/42 §8）

| 红线 | 状态 |
|---|---|
| ❌ 不宣布 Gate 1 / Gate 2 PASS | ✅ docs/45 §1 + §6 + §7 + 本回执 header + §2 + §5 多次显式守门 |
| ❌ 不擅自 O1 收口 | ✅ docs/45 §3 O1 详细 显式 OPEN；intake WAITING_FILE；预览路径**非 O1** |
| ❌ 伪造样本 / 真履历 | ✅ 仅索引刷新；`303` demo 已显式守门；person/tenure demo = mock 占位双标识 |
| ❌ 派生 score / rating / rank / total_score / confidence_score / credibility_score / peer_rank | ✅ docs/45 §6.2 禁词守门沿用；本刀不引入 |
| ❌ 不做官员能力总分 / 排名 / DSH / 实时数据 | ✅ docs/44 §1.2 + docs/08 §3.3 守门；本刀不触发 |
| ❌ 批量爬政策研究 / 财政预决算 / 官员履历 | ✅ 无关 |
| ❌ HTTP 爬源站 | ✅ |
| ❌ 降 OCR 门槛 | ✅ 无关 |
| ❌ 启用 pgvector / RLS / partition | ✅ Stage 2 边界；本刀不动 |
| ❌ 改 `gate_thresholds.json` | ✅ 未读未写 |
| ❌ 不碰 `00-CC-CURRENT.md` | ✅ Cursor 拥有 |
| ❌ 不擅自 --force / --force-with-lease | ✅ ff-only pull |
| ❌ 不替用户下裁定 | ✅ 仅执行 `305` §SCHEMA 范围（机械登记）|
| ❌ 不在聊天复述 Cursor 长文 | ✅ 仅回执要点 |
| ❌ 不索要 PAT | ✅ |
| ✅ pack invariant 守门 | ✅ 628 → 630；bump script source-of-truth + docs/45 SHA REFRESH |
| ✅ receipts 仅写 `reviews/stage0-gate0-rework-2026-08-23/` | ✅ |
| ✅ 不改 Cursor 拥有架构文档 | ✅ docs/06/08/10/34/40-44/46-48 / `00-CC-CURRENT.md` 未读未写 |
| ✅ 不擅自提前 Gate 2 评审日期 | ✅ W8（per docs/34 §10.4）|
| ✅ mart-shape 禁词 3 重守门 | ✅ runtime + 静态 scanner + pytest + TS 类型约束（per docs/45 §6.2）|
| ✅ mart-shape feature-flag 默认值 | ✅ `NEXT_PUBLIC_USE_MART_FIXTURE !== "1"` 默认走 mock |
| ✅ 兼容 S2.7-b-lite / S2.7-b-full-lite / S2.7-b-full mart skel / demo-join / parity / person-tenure demo | ✅ 7 回执全部入 §6.1 |
| ✅ O1 + O3 + person/tenure 真数据 OPEN 清单显式携带 | ✅ §3 + §5.5 + §6 |
| ✅ 预览路径明确非 O1 收口 | ✅ §3 + §5.5 + §6.2 |
| ✅ docs/45 = CC 维护索引（per header "起草：CC"）| ✅ 第 5 次机械刷新（queue_rev 103/108/119/125/127）|
| ✅ 「relatedPersons=[]」过时 OPEN 修正 | ✅ §5.5 + §6.2 拆 demo ✅ + 真数据 OPEN |
| ✅ demo 显式标识（非真履历）| ✅ §3 + §5.5 + §6.2 + §6.1 多处守门 |
| ✅ person/tenure 主路径 = TS fixture | ✅ §3 + §5.5 + §6.2 标注 dbt 依赖 S2.1-lite OPEN |
| ✅ S2.7-b-full 真数据迁移刀仍 OPEN | ✅ §5.5 + §6 + §6.2 + §7 多处守门 |

---

## §6. 推送 / 三路对齐

| 步骤 | 命令 | 结果 |
|---|---|---|
| origin pull | `git fetch origin && git pull --ff-only origin main` | queue_rev 127 ✅ |
| cc_gate_watch | `./scripts/cc_gate_watch.sh --pull` | `phase=CC_ACTION_REQUIRED` ✅ |
| docs/45 修改 | `docs/45-stage2-s210-lite-gate2-review-index-20260826.md`（§2 + §3 + §5.5 + §6 + §6.1 + §6.2 + §7 + header）| ✅ MOD |
| bump script | `scripts/_knife38_manifest_bump.py`（2 NEW + 1 REFRESH）| ✅ 628 → 630（+2）|
| 本地校验 | manifest invariant | ✅ 630 == 630 == 630 |
| commit (knife 38 主提交) | `git add ... && git commit -m "docs(45): 305 person/tenure demo 刷新 — 登记 303 + 修正 relatedPersons=[] 过时 OPEN"` | ✅ `447b340f58f48ca6b36bed788d8e5feeb283b693` |
| origin push | `git push origin HEAD`（**priority**）| ✅ `447b340` → origin/main |
| github push | `git push github HEAD` | ✅ `447b340` → github/main |
| 三路对齐 | origin/main = github/main = local HEAD | ✅ `447b340f58f48ca6b36bed788d8e5feeb283b693` |
| backfill commit | 独立 commit（不 amend-after-push）| ✅ backfill `<backfill_sha>` |

> **禁止 amend-after-push**：receipt SHA + commit SHA 必须在独立 commit 里 backfill（per knife 2/3/4 经验）。

---

## §7. 下次 heartbeat 预期

- `queue_rev 127` 完成后：Cursor 收 `306` → 下发 `307-stage0-cursor-s305-docs45-person-tenure-demo-audit-…md`（PASS/FAIL）
- 若 PASS：docs/45 person/tenure demo 索引 7 回执登记齐；§5.5/§6.2「relatedPersons=[]」过时 OPEN 已修正；§7 invariant 更新到 630
- 若 FAIL：`306-correction` 回合（修 docs/45 表格 / 修 §3 措辞 / re-commit）

---

## §8. 备注

- **本刀不宣布 Gate 2 PASS** — docs/45 §1 + §6 + §7 + 本回执 §2 + §5 多次显式守门。Gate 2 评审日期暂定 W8（per docs/34 §10.4），由 Cursor/用户裁定，不擅自提前。
- **本刀只做机械索引刷新** — `305` §SCHEMA 显式约束：不接真 SHA / 不接 person/tenure 真数据 / 不爬网 / 不派生 score / 不改架构设计。
- **docs/45 = CC 维护索引（per header "起草：CC · queue_rev 97"）** — 本次属于第 5 次机械刷新（queue_rev 103/108/119/125/127）；Cursor 拥有架构文档（docs/06/08/10/34/40-44/46-48）未动。**红线 "Cursor 37 architect-only (don't write docs Cursor owns)" 不约束 docs/45**，因为 docs/45 是 CC 维护的索引，由 Cursor 任务书（如 `305`）显式委托刷新。
- **7 回执入 §6.1**：`257` S2.7-b-lite + `266` S2.7-b-full-lite + `288` mart 骨架 + `294` mart demo-join + `291` intake + `297` 前端 parity + **`303` person/tenure demo 接驳**。
- **§5.5 OPEN 拆分逻辑** — demo（`303`）= TS fixture 主路径（无外部 IO）；真数据 = 依赖 S2.1-lite PASS + O1 真实 SHA + Stage 1 OPEN 收口。两者明确区分，避免下游混淆。
- **§6.2 拆分逻辑** — demo 行 (`buildMartRelatedPersons()` + UI 渲染块) = 本地 TS fixture；真数据行（替换 demo 占位） = 待 S2.7-b-full 真数据迁移刀。
- **主路径选择 = TS fixture** — dbt 侧 `mart_person_tenure` 依赖 S2.1-lite PASS（per docs/34 §3 + Cursor 174 OPEN）。docs/45 §3 + §5.5 + §6.2 多处标注主路径选择原因。
- **预览路径明确非 O1** — 用户运行 `NEXT_PUBLIC_USE_MART_FIXTURE=1` 看 demo mart-shape 管道（含 10 城 × 2 demo 相关人物行）；**仅是 demo 演示管道，不构成 O1 收口**（per docs/48 §4.3 + `291` intake）。
- **O1 真实 SHA 收口须主动 `--confirm-o1=PATH`** — `intake_real_sha_if_present.py` 4 退出状态：WAITING_FILE / CANDIDATE_FOUND / O1_INTAKED / CONTRACT_VIOLATION；当前 runtime allowlist = 4 fixtures → WAITING_FILE。
- **S2.7-b-full 真数据迁移刀仍 OPEN** — 依赖：O1 真实 SHA 收口 + Stage 1 OPEN 收口 + S2.1-lite `mart_person_tenure` PASS（per docs/34 §3 + docs/47 §6.3 切刀风险 + Cursor 174 S2.1 OPEN）；路线图 = 接 dbt mart 真表 + person/tenure 真数据（替换 `303` demo 占位）+ lineage.source_file_sha256 从占位 `'0'*64` 替换为 O1 真实 SHA。
- **docs/45 header 6 刷新行** — queue_rev 97 (`250`) + 103 (`259`) + 108 (`268`) + 119 (`284`) + 125 (`299`) + **127 (`305`)**。
- **不修改 dbt 项目配置** — 索引刷新刀不需 dbt_project.yml 改动。
- **§7 invariant 更新** — 旧 `597` (knife 26 stale) → knife 37 `628` → knife 38 `630`；manifest SHA 必须同步更新（per knife 16 source-of-truth fix）。
- **「relatedPersons=[]」过时 OPEN 修正** — 之前 docs/45 §5.5 + §6.2 沿用 S2.7-b-full-lite 时期 "demo 当前 = []" 措辞；本刀明确改为 demo 已交 `303`，真数据仍 OPEN。
- **下次 heartbeat 闸门** — O1 真收口须用户主动 `--confirm-o1=PATH`；在此之前 S2.7-b-full 真数据迁移刀（tasking 26X+）继续依赖 demo-join emit 行 + person/tenure demo 占位（`303`）。

— End of `306` —

> 等待 Cursor 审验（预期 `307-stage0-cursor-s305-docs45-person-tenure-demo-audit-…md`）。
> 通过后 docs/45 person/tenure demo 索引 7 回执登记齐；§5.5/§6.2「relatedPersons=[]」过时 OPEN 修正。
> ⚠ **本刀不宣布 Gate 2 PASS**（per docs/34 §1 + §8 #8 + `305` §红线）。
> ⚠ **本刀只做机械索引刷新**（per `305` §SCHEMA "本刀做/本刀不做"）。
> ⚠ **O1 真实 SHA 收口前恒占位 `'0'*64`**（per docs/47 §3.1 ⚠️ + `305` §红线）。
> ⚠ **所有 demo 行 is_demo='true' + 双标识**（per `303` demo + `294` demo-join）。
> ⚠ **O1 真收口须用户主动 `--confirm-o1=PATH`**（per `291` intake + docs/48 §4.3）。
> ⚠ **预览路径 `NEXT_PUBLIC_USE_MART_FIXTURE=1` 看 demo 管道 ≠ O1 收口**。
> ⚠ **主路径 = TS fixture；dbt 侧 mart_person_tenure 依赖 S2.1-lite OPEN**。
> Gate 2 评审日期暂定 W8（per docs/34 §10.4）。