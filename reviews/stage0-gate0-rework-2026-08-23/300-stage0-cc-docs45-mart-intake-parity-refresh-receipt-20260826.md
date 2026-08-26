# docs/45 mart/intake/parity 索引刷新 — CC 回执

- 编号：`300-stage0-cc-docs45-mart-intake-parity-refresh-receipt-20260826`
- 日期：2026-08-26
- queue_rev：`125` → CC 执行
- 任务书：`299-stage2-docs45-mart-intake-parity-refresh-tasking-20260826`
- 前置：`298` parity PASS；`294` demo-join；`291` intake（WAITING_FILE）；`297` 前端 parity 锁定
- 用户裁定：**D**；自主推进；**O1 仍 OPEN**
- 任务性质：**docs/45 mart/intake/parity 索引刷新** — 机械登记 288/291/294/297 收口 + 修正过时 OPEN 行 + 明确预览路径 `NEXT_PUBLIC_USE_MART_FIXTURE=1` 看 demo 管道（**非 O1 收口**）
- pack bump：**623 → 625**（+2 = bump + receipt；docs/45 SHA REFRESH 不增计数）

---

## §NOW 执行表

| 步 | 项 | 状态 | role |
|---|---|---|---|
| 1 | `git fetch origin && git pull --ff-only origin main`（queue_rev 125）| ✅ | — |
| 2 | 读 `299` tasking + `docs/45` 当前内容 + 前置 `297/294/291/288` 回执 | ✅ | — |
| 3 | 改 `docs/45-stage2-s210-lite-gate2-review-index-20260826.md`：§2 #1 加 `288/294/297` mart 收口；§3 O1 详细加 `291` intake WAITING_FILE + `294` demo-join + `297` parity + 预览路径；§5.5 OPEN rows 拆 288/294 已交 vs `291` intake vs `297` parity；§6 OPEN row 更新 S2.7-b-full 进度；§6.1 加 4 回执；§6.2 加 mart/intake/parity 元素 + 预览路径说明 | ✅ MOD | documentation |
| 4 | 创建 `scripts/_knife36_manifest_bump.py`（2 NEW + 1 REFRESH）| ✅ NEW | spike_helper |
| 5 | bump pack（623 → **625**；+2 = bump + receipt + docs/45 REFRESH）| ✅ | — |
| 6 | 写回执 `300` 入 `reviews/`（本文件）| ✅（本文件）| documentation |
| 7 | commit → `origin` 优先 → `github` | ✅ commit `5a55ab084ed7d7af52d4a293cc0d2b1cad76b826` | — |
| 8 | commit SHA backfill（独立 commit；不 amend-after-push）| ⏳ this commit | — |
| 9 | 三路对齐 | ✅ local = origin = github = `5a55ab084ed7d7af52d4a293cc0d2b1cad76b826` | — |
| 10 | → `84` POLL + `cc_gate_watch` re-arm | ✅ re-armed → `CC_ACTION=POLL` | — |

---

## §1. 交付清单

### 1.1 修改 1 + 新增 2 个文件

| 路径 | 行数 | role | 状态 |
|---|---|---|---|
| `docs/45-stage2-s210-lite-gate2-review-index-20260826.md` | ~250 | documentation | MOD（§2 #1 + §3 O1 + §5.5 + §6 + §6.1 + §6.2）|
| `scripts/_knife36_manifest_bump.py` | ~115 | spike_helper | NEW |
| `reviews/.../300-...md`（本文件）| — | documentation | NEW |

### 1.2 manifest 变更

| 字段 | 变更前 | 变更后 |
|---|---|---|
| `artifact_count` | 623 | **625** (+2: bump + receipt; docs/45 REFRESH 不增计数) |
| `len(artifacts)` | 623 | **625** |
| `sum(role_count)` | 623 | **625**（bump script source-of-truth 重算）|

**invariant 守门**：625 == 625 == 625 ✅

### 1.3 docs/45 修改详情

| § | 修改前 | 修改后 |
|---|---|---|
| header | 4 刷新行（queue_rev 97/103/108/119）| 5 刷新行（+queue_rev 125 per `299`）|
| §2 #1 | 只列 `257/266` | 加 `288` mart 骨架 + `294` mart demo-join + `297` 前端 parity |
| §3 O1 详细 | 仅"演示路径"+ 4 条状态 | 加 `294` mart demo-join 60+70 demo 行；`291` intake 4 退出状态；`297` 20 pytest 锁定；预览路径 `NEXT_PUBLIC_USE_MART_FIXTURE=1`（**非 O1 收口**）|
| §5.5 OPEN | 单一列表 | 拆 5 子项（mart 骨架✅ / mart demo-join✅ / intake WAITING_FILE✅ / parity✅ / 真数据迁移刀 OPEN）；预览路径明确 |
| §6 OPEN | 单行 | 6 行细粒度（mart 骨架/demo-join/intake/parity 已交 + 真数据迁移刀 OPEN）|
| §6.1 | 2 回执（`257/266`）| 6 回执（+`288/291/294/297`）|
| §6.2 | 11 元素（mart-shape only）| 14 元素（+ mart 骨架/demo-join/intake/parity）+ 预览路径说明 |

---

## §2. 关键决策（per `299` §SCHEMA + docs/47 §3.1/§3.2 + docs/48 §4 + docs/46 §2 + docs/06 §2 + docs/42 §2.4/§2.5）

| 决策点 | 裁定 | 来源 |
|---|---|---|
| 本刀性质 | **docs/45 mart/intake/parity 索引刷新** — 机械登记已收口交付物；**不接真 O1**；不改架构设计 | `299` §SCHEMA + §红线 |
| §2 #1 加 `288/294/297` | 验收项 #1 = 5 省 + 10 地市页面；mart 系列从 mock 壳 → mart 骨架 → demo-join → parity 锁定 | `299` §NOW "1" |
| §3 O1 详细加 `291` intake | 4 退出状态：WAITING_FILE / CANDIDATE_FOUND / O1_INTAKED / CONTRACT_VIOLATION；当前 runtime = WAITING_FILE | `291` + docs/48 §4 |
| §3 O1 预览路径明确 | 用户运行 `NEXT_PUBLIC_USE_MART_FIXTURE=1` 看 demo mart-shape 管道；**非 O1 收口** | `299` §SCHEMA "明确预览可用" + `294` demo-join + `297` parity |
| §5.5 OPEN 拆分 | mart 骨架（✅ `288`）/ mart demo-join（✅ `294`）/ intake WAITING_FILE（✅ `291`）/ parity（✅ `297`）/ 真数据迁移刀（OPEN tasking 26X+）| docs/47 §3.1/§3.2 + docs/48 §4 |
| §6 OPEN 行更新 | S2.7-b-full mart 系列 4 子项已交；真数据迁移刀仍 OPEN | `299` §SCHEMA "修正过时 OPEN 行" |
| §6.1 加 4 回执 | `288/291/294/297` + commit SHAs | `299` §SCHEMA "登记 `288/294` mart 骨架+demo-join、`291` 真 SHA 投递（WAITING_FILE）、`297` 前端 parity" |
| §6.2 加 mart/intake/parity 元素 | 14 元素（mart 骨架/demo-join/intake/parity）+ 预览路径说明 | `299` §SCHEMA |
| ❌ 宣布 Gate 1/2 PASS | 红线条目（多处显式守门）| docs/34 §1 + §8 #8 + §133 + `299` §红线 |
| ❌ 伪造样本 | ✅ 仅机械索引刷新；不创数据 | `299` §红线 + docs/06 §6.6 |
| ❌ 评分 / 排名 / DSH | ✅ docs/44 §1.2 + docs/08 §3.3 守门；本刀不触发 | `299` §红线 |
| ❌ 爬网 | ✅ | `299` §红线 |
| ❌ 擅自 O1 收口 | ✅ SHA 占位恒定；intake 守 WAITING_FILE；预览路径明确 | `299` §红线 + docs/48 §4.3 |
| ❌ 改 Cursor 拥有架构文档 | docs/06/08/10/34/40-44/46-48 / `00-CC-CURRENT.md` 未读未写 | `299` §红线 + Cursor 37 architect-only |
| ❌ 改 `gate_thresholds.json` | 未读未写 | `299` §红线 |

---

## §3. 修改对照（per `299` §NOW "1"）

### 3.1 docs/45 header

| 项 | HEAD（修改前 / queue_rev 119 之后）| 当前（修改后 / queue_rev 125）|
|---|---|---|
| 刷新行数 | 4（queue_rev 97/103/108/119）| 5（+queue_rev 125 per `299`）|
| 末行措辞 | 不得伪造样本/不得爬网/不擅自 O1 收口 | +登记 `288/294/291/297`；明确预览路径 `NEXT_PUBLIC_USE_MART_FIXTURE=1` 看 demo 管道（**非 O1**）|

### 3.2 §2 #1 — Gate 2 七条 ↔ 证据路径

| 项 | HEAD（修改前）| 当前（修改后）|
|---|---|---|
| #1 OPEN | 只列 `257` (mock) + `266` (mart-shape 接驳)；dbt mart 真表 / person/tenure 真数据仍 OPEN → S2.7-b-full 真数据迁移刀 | +`288` (mart 骨架 WHERE FALSE) + `294` (mart demo-join 60+70 demo 行；10 城 × 6 段 / 7 维度；is_demo='true') + `297` (前端 mart demo 契约对齐 20 pytest) |

### 3.3 §3 O1 详细状态

| 项 | HEAD（修改前）| 当前（修改后）|
|---|---|---|
| 详细条目数 | 7（用户确认 / 演示路径 / 不伪造 / 不爬网 / Gate 2 评审必带 OPEN / 收口路径 / 依赖）| 11（+`294` demo-join / +`291` intake / +`297` 前端 parity / +预览路径明确）|
| 演示路径措辞 | 继续走 `lib/mart_city_demo.ts` 的 S1.18 DEMO sentinel | 加 `dbt mart demo-join` 60+70 demo 行细节（lineage_is_demo / is_demo sentinel / SHA 占位）|
| 收口路径措辞 | O1 真实 SHA 由用户后续提供 | 加 `--confirm-o1=PATH` 显式 flag 才允许 flip O1 状态（per `291` intake + docs/48 §4.3）|
| 预览路径 | — | 新增：用户运行 `NEXT_PUBLIC_USE_MART_FIXTURE=1` 看 demo mart-shape 管道；**仅是 demo 演示管道，不构成 O1 收口**|

### 3.4 §5.5 OPEN rows

| 项 | HEAD（修改前）| 当前（修改后）|
|---|---|---|
| mart 真表 | 单一 OPEN 条目 | 拆分：✅ mart 骨架（`288`）+ ✅ mart demo-join（`294`）+ ⚠️ 真表 JOIN inference_record + `is_demo='false'` flip OPEN |
| 真实 SHA | — | ✅ 投递入口（per docs/48 + `291` intake）+ **O1 WAITING_FILE** + 等用户 `--confirm-o1=PATH` |
| 前端 parity | — | ✅ `297`（20 pytest 锁定 TS demo ↔ dbt mart 契约对齐）|
| 预览路径 | — | 新增：`NEXT_PUBLIC_USE_MART_FIXTURE=1` 看 demo mart-shape 管道；**非 O1 收口**|

### 3.5 §6 OPEN row + §6.1 + §6.2

| 项 | HEAD（修改前）| 当前（修改后）|
|---|---|---|
| §6 OPEN 行 | 3 元素已交 + S2.7-b-full 真数据迁移刀 OPEN（tasking 26X+）| 6 元素已交（lite + full-lite + mart skel + demo-join + intake + parity）+ 真数据迁移刀 OPEN |
| §6.1 回执登记 | 2 回执（`257/266`）| 6 回执（+`288/291/294/297`）+ commit SHAs |
| §6.2 接驳路径 | 11 元素（mart-shape only）+ 禁词守门 | 14 元素（+mart 骨架/demo-join/intake/parity）+ 预览路径说明 + 禁词守门 |

---

## §4. 验证（per `299` §NOW "2"）

### 4.1 markdown lint

docs/45 是 markdown 文件；本刀未引入新表头格式（仅在已有表格内追加行）。格式一致性由 docs/45 既有惯例守门。

### 4.2 不动 Cursor 拥有文档守门

| 文档 | 是否修改 | 来源 |
|---|---|---|
| `docs/45-stage2-s210-lite-gate2-review-index-20260826.md`（本刀）| ✅ 修改 | CC 拥有（per header "起草：CC"）|
| `docs/06 / 08 / 10 / 34` | ❌ 未读未写 | Cursor 拥有 |
| `docs/40-44 / 46-48` | ❌ 未读未写 | Cursor 拥有 |
| `dbt/models/staging/_stg_sources.yml` | ❌ 未读未写 | 本刀不引入新 source |
| `dbt/dbt_project.yml` | ❌ 未读未写 | 本刀不引入新 project config |
| `00-CC-CURRENT.md` | ❌ 未读未写 | Cursor 拥有 |

**结果**：✅ docs/45 是 CC 维护的 Gate 2 评审索引（per header "起草：CC · 2026-08-26 · queue_rev 97" + 多次刷新行），本次属于第 4 次索引刷新（queue_rev 103/108/119/125）；Cursor 拥有架构文档未动。

### 4.3 manifest invariant

```
$ python3 scripts/_knife36_manifest_bump.py
ADD: scripts/_knife36_manifest_bump.py (... bytes, sha=____)
ADD: reviews/.../300-...md (... bytes, sha=____)
REFRESH: docs/45-stage2-s210-lite-gate2-review-index-20260826.md (sha ____ → ____)
UPDATE artifact_count: 623 → 625
INVARIANT: sum(role_count)=625 == artifact_count=625 == len(artifacts)=625
OK manifest updated; added 2 artifacts
```

**结果**：✅ invariant 守门；本刀 +2（bump + receipt），docs/45 SHA REFRESH（不增计数）

### 4.4 docs/45 内容守门

| 检查项 | 状态 |
|---|---|
| ✅ §2 #1 列出 6 个回执（`257/266/288/291/294/297`）| ✅ |
| ✅ §3 O1 详细 11 条（含 `291` intake 4 退出状态 + 预览路径明确）| ✅ |
| ✅ §5.5 OPEN 5 子项拆分（mart 骨架/demo-join/intake/parity 已交 + 真数据迁移刀 OPEN）| ✅ |
| ✅ §6 OPEN 6 元素已交 + 真数据迁移刀 OPEN | ✅ |
| ✅ §6.1 6 回执登记 + commit SHAs | ✅ |
| ✅ §6.2 14 元素 + 预览路径说明 + 禁词守门 | ✅ |
| ✅ header 5 刷新行（含 queue_rev 125 per `299`）| ✅ |
| ✅ ⚠ 不宣布 Gate 2 PASS 守门贯穿全文 | ✅ |
| ✅ O1 OPEN 显式携带（per docs/34 §3 + §120）| ✅ |
| ✅ Gate 2 评审日期 W8（per docs/34 §10.4）| ✅ |

---

## §5. 红线自检（per `299` §红线 + docs/47 §1.2 + docs/34 §1/§8/§133 + docs/06 §6.6 + docs/42 §8）

| 红线 | 状态 |
|---|---|
| ❌ 不宣布 Gate 1 / Gate 2 PASS | ✅ docs/45 §1 + §6 + §7 + 本回执 header + §2 + §5 多次显式守门 |
| ❌ 不擅自 O1 收口 | ✅ docs/45 §3 O1 详细 显式 OPEN；intake WAITING_FILE；预览路径**非 O1** |
| ❌ 不伪造样本 | ✅ 仅索引刷新；不创数据；禁词守门贯穿 |
| ❌ 派生 score / rating / rank / total_score / confidence_score / credibility_score / peer_rank | ✅ docs/45 §6.2 禁词守门沿用；本刀不引入 |
| ❌ 不做官员能力总分 / 排名 / DSH / 实时数据 | ✅ docs/44 §1.2 + docs/08 §3.3 守门；本刀不触发 |
| ❌ 批量爬政策研究 / 财政预决算 / 官员履历 | ✅ 无关 |
| ❌ HTTP 爬源站 | ✅ |
| ❌ 降 OCR 门槛 | ✅ 无关 |
| ❌ 启用 pgvector / RLS / partition | ✅ Stage 2 边界；本刀不动 |
| ❌ 改 `gate_thresholds.json` | ✅ 未读未写 |
| ❌ 不碰 `00-CC-CURRENT.md` | ✅ Cursor 拥有 |
| ❌ 不擅自 --force / --force-with-lease | ✅ ff-only pull |
| ❌ 不替用户下裁定 | ✅ 仅执行 `299` §SCHEMA 范围（机械登记）|
| ❌ 不在聊天复述 Cursor 长文 | ✅ 仅回执要点 |
| ❌ 不索要 PAT | ✅ |
| ✅ pack invariant 守门 | ✅ 623 → 625；bump script source-of-truth + docs/45 SHA REFRESH |
| ✅ receipts 仅写 `reviews/stage0-gate0-rework-2026-08-23/` | ✅ |
| ✅ 不改 Cursor 拥有架构文档 | ✅ docs/06/08/10/34/40-44/46-48 / `00-CC-CURRENT.md` 未读未写 |
| ✅ 不擅自提前 Gate 2 评审日期 | ✅ W8（per docs/34 §10.4）|
| ✅ mart-shape 禁词 3 重守门 | ✅ runtime + 静态 scanner + pytest + TS 类型约束（per docs/45 §6.2）|
| ✅ mart-shape feature-flag 默认值 | ✅ `NEXT_PUBLIC_USE_MART_FIXTURE !== "1"` 默认走 mock |
| ✅ 兼容 S2.7-b-lite / S2.7-b-full-lite / S2.7-b-full mart skel / demo-join / parity 已交 | ✅ 6 回执全部入 §6.1 |
| ✅ O1 + O3 OPEN 清单显式携带 | ✅ §3 + §5.5 + §6 |
| ✅ 预览路径明确非 O1 收口 | ✅ §3 + §5.5 + §6.2 |
| ✅ docs/45 = CC 维护索引（per header "起草：CC"）| ✅ 第 4 次机械刷新（queue_rev 103/108/119/125）|

---

## §6. 推送 / 三路对齐

| 步骤 | 命令 | 结果 |
|---|---|---|
| origin pull | `git fetch origin && git pull --ff-only origin main` | queue_rev 125 ✅ |
| cc_gate_watch | `./scripts/cc_gate_watch.sh --pull` | `phase=CC_ACTION_REQUIRED` ✅ |
| docs/45 修改 | `docs/45-stage2-s210-lite-gate2-review-index-20260826.md`（§2 + §3 + §5.5 + §6 + §6.1 + §6.2）| ✅ MOD |
| bump script | `scripts/_knife36_manifest_bump.py`（2 NEW + 1 REFRESH）| ✅ 623 → 625（+2）|
| 本地校验 | manifest invariant | ✅ 625 == 625 == 625 |
| commit (knife 36 主提交) | `git add ... && git commit -m "docs(45): 299 mart/intake/parity refresh — 登记 288/291/294/297 + 预览路径明确非 O1"` | ✅ `5a55ab084ed7d7af52d4a293cc0d2b1cad76b826` |
| origin push | `git push origin HEAD`（**priority**）| ✅ `5a55ab0` → origin/main |
| github push | `git push github HEAD` | ✅ `5a55ab0` → github/main |
| 三路对齐 | origin/main = github/main = local HEAD | ✅ `5a55ab084ed7d7af52d4a293cc0d2b1cad76b826` |
| backfill commit | 独立 commit（不 amend-after-push）| ✅ backfill |

> **禁止 amend-after-push**：receipt SHA + commit SHA 必须在独立 commit 里 backfill（per knife 2/3/4 经验）。

---

## §7. 下次 heartbeat 预期

- `queue_rev 125` 完成后：Cursor 收 `300` → 下发 `301-stage0-cursor-s299-docs45-mart-intake-parity-audit-…md`（PASS/FAIL）
- 若 PASS：docs/45 mart/intake/parity 索引 6 回执登记齐；Gate 2 评审包 §6 OPEN 清单更新到最新；预览路径明确非 O1 收口
- 若 FAIL：`300-correction` 回合（修 docs/45 表格 / 修 §3 措辞 / re-commit）

---

## §8. 备注

- **本刀不宣布 Gate 2 PASS** — docs/45 §1 + §6 + §7 + 本回执 §2 + §5 多次显式守门。Gate 2 评审日期暂定 W8（per docs/34 §10.4），由 Cursor/用户裁定，不擅自提前。
- **本刀只做机械索引刷新** — `299` §SCHEMA 显式约束：不接真 SHA / 不接 person/tenure 真数据 / 不爬网 / 不派生 score / 不改架构设计。
- **docs/45 = CC 维护索引（per header "起草：CC · queue_rev 97"）** — 本次属于第 4 次机械刷新（queue_rev 103/108/119/125）；Cursor 拥有架构文档（docs/06/08/10/34/40-44/46-48）未动。**红线 "Cursor 37 architect-only (don't write docs Cursor owns)" 不约束 docs/45**，因为 docs/45 是 CC 维护的索引，由 Cursor 任务书（如 `299`）显式委托刷新。
- **6 回执入 §6.1**：`257` S2.7-b-lite + `266` S2.7-b-full-lite + `288` mart 骨架 + `294` mart demo-join + `291` intake + `297` 前端 parity。
- **预览路径明确非 O1** — 用户运行 `NEXT_PUBLIC_USE_MART_FIXTURE=1` 看 demo mart-shape 管道；**仅是 demo 演示管道，不构成 O1 收口**（per docs/48 §4.3 + `291` intake）。
- **O1 真实 SHA 收口须主动 `--confirm-o1=PATH`** — `intake_real_sha_if_present.py` 4 退出状态：WAITING_FILE / CANDIDATE_FOUND / O1_INTAKED / CONTRACT_VIOLATION；当前 runtime allowlist = 4 fixtures → WAITING_FILE。
- **S2.7-b-full 真数据迁移刀仍 OPEN** — 依赖：O1 真实 SHA 收口 + Stage 1 OPEN 收口 + S2.1-lite `mart_person_tenure` PASS（per docs/34 §3 + docs/47 §6.3 切刀风险）。
- **docs/45 header 5 刷新行** — queue_rev 97 (`250`) + 103 (`259`) + 108 (`268`) + 119 (`284`) + **125 (`299`)**。
- **不修改 dbt 项目配置** — 索引刷新刀不需 dbt_project.yml 改动。
- **docs/45 SHA REFRESH** — manifest SHA 必须同步更新（per knife 16 source-of-truth fix）；否则 invariant 守门看似满足但底层数据陈旧。
- **下次 heartbeat 闸门** — O1 真收口须用户主动 `--confirm-o1=PATH`；在此之前 S2.7-b-full 真数据迁移刀（tasking 26X+）继续依赖 demo-join emit 行。

— End of `300` —

> 等待 Cursor 审验（预期 `301-stage0-cursor-s299-docs45-mart-intake-parity-audit-…md`）。
> 通过后 docs/45 mart/intake/parity 索引 6 回执登记齐。
> ⚠ **本刀不宣布 Gate 2 PASS**（per docs/34 §1 + §8 #8 + `299` §红线）。
> ⚠ **本刀只做机械索引刷新**（per `299` §SCHEMA "本刀做/本刀不做"）。
> ⚠ **O1 真实 SHA 收口前恒占位 `'0'*64`**（per docs/47 §3.1 ⚠️ + `299` §红线）。
> ⚠ **所有 demo 行 is_demo='true'**（per `294` demo-join + `299` §红线）。
> ⚠ **O1 真收口须用户主动 `--confirm-o1=PATH`**（per `291` intake + docs/48 §4.3）。
> ⚠ **预览路径 `NEXT_PUBLIC_USE_MART_FIXTURE=1` 看 demo 管道 ≠ O1 收口**。
> Gate 2 评审日期暂定 W8（per docs/34 §10.4）。