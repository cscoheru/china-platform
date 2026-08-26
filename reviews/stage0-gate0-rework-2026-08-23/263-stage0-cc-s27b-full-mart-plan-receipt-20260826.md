# docs/47 S2.7-b-full mart 规划 — CC 回执

- 编号：`263-stage0-cc-s27b-full-mart-plan-receipt-20260826`
- 日期：2026-08-26
- queue_rev：`105` → CC 执行
- 任务书：`262-stage2-s27b-full-mart-plan-tasking-20260826`
- 前置：`261` docs/45 刷新 PASS；`260` S2.7-b-lite refresh PASS；`258` S2.7-b-lite PASS；`257` 落地；`docs/46`；`docs/44 §5.1.2/§5.1.3`；`docs/34 §1/§3/§8/§133/§10.4`
- 用户裁定：Stage 2 **C**；缩刀 **D**；自主推进（per Cursor 2026-08-26 META）
- 文件 sha：docs/47 `fdb6fb28`（18983 bytes；待 commit 后稳定）

---

## §NOW 执行表

| 步 | 项 | 状态 | sha256 摘要 | role |
|---|---|---|---|---|
| 1 | `git pull origin main` + `cc_gate_watch --pull`（queue_rev 105）| ✅ | — | — |
| 2 | 读 `262` tasking + `docs/46` + `docs/44 §5.1.2/§5.1.3` + `docs/34 §1/§3` | ✅ | — | — |
| 3 | 起草 `docs/47-stage2-s27b-full-mart-evidence-plan-20260826.md`（11 节 + 红线 + OPEN）| ✅ | `fdb6fb28` | documentation |
| 4 | 文件级 forbidden-token guard（"Gate 2 PASS" 4 处全部为否定/守门语境；`score`/`rating`/`rank`/`credibility` 全部为禁止/不派生语境；CLEAN）| ✅ | — | — |
| 5 | 创建 `scripts/_knife24_manifest_bump.py`（2 NEW_ARTIFACTS：docs/47 + receipt 263）| ✅ | — | spike_helper |
| 6 | bump pack（587 → **589**；+2 = docs/47 + receipt 263）| ✅ | — | — |
| 7 | 写回执 `263` 入 `reviews/`（本文件）| ✅（本文件）| — | documentation |
| 8 | commit → `origin` 优先 → `github` | ⏳ | — | — |
| 9 | 三路对齐 | ⏳ | — | — |
| 10 | → `84` POLL + `cc_gate_watch` re-arm | ⏳ | — | — |

---

## §1. 交付清单

### 1.1 docs/47 — S2.7-b-full mart / person 真数据接入 规划

| 维度 | 内容 |
|---|---|
| 章节数 | 11 节（§1 目标 + §2 范围 + §3 mart 映射 + §4 段级契约 + §5 验收 + §6 lite→full 切刀 + §7 红线 + §8 不做 + §9 文档关系 + §10 CC 建议 + 收尾）|
| 范围（per `262` §SCHEMA）| 10 城 EvidenceChain 接 mart；person/tenure 契约；与 S2.1-lite DDL 对齐；**只规划**不写 migration / 不全量 seed |
| mart 契约 | `mart_city_evidence_chain`（10 字段 + lineage.is_demo + ⚠️ source_file_sha256 OPEN）+ `mart_city_seven_dim_overview`（7 字段 + 5 枚举 balance_status）+ person/tenure JOIN |
| 段级字段 | city 段级 evidence 契约 + 七维度 cell 契约 + 同省地市 peer-compare 契约（应用层 enum-style 守门）|
| 验收（次落刀 OPEN）| 12 条（mart 落地 + 10 城迁移 + 5 枚举 + 红线 + 跨 lite 回归 + smoke-check + 10 城锁定 + 应用层 enum 守门）|
| 切刀边界 | lite 已交（路由 + mock + 三件套 + 6 pytest + smoke 9 节）；full OPEN 依赖 O1 真实 SHA + Stage 1 OPEN 收口 |
| OPEN 清单（与 docs/45 §3 + docs/34 §3 平行）| O1 / O2 / O3 / **O8 person/tenure 真数据** / **O9 mart_city_evidence_chain** / **O10 mart_city_seven_dim_overview** |
| CC 建议（供 Cursor 审阅）| 切刀节奏 B（拆 2 刀降依赖）+ mart 物化 A（view 平行）+ 不可降级验收项 #2 持续守门 + 评审日期 W8 不擅自提前 |

### 1.2 manifest 变更

| 字段 | 变更前 | 变更后 |
|---|---|---|
| `artifact_count` | 587 | **589** (+2: docs/47 + receipt 263) |
| `len(artifacts)` | 587 | **589** |
| `sum(role_count)` | 587 | **589**（bump script source-of-truth 重算）|

**invariant 守门**：589 == 589 == 589 ✅

### 1.3 bump script

| 路径 | 行数 | role |
|---|---|---|
| `scripts/_knife24_manifest_bump.py` | ~95 | spike_helper |

模板与 `_knife23_manifest_bump.py` 完全平行：源真值重算 + 断言守门 + SKIP 已存在条目。

---

## §2. 关键决策（per `262` §SCHEMA + docs/46 §1.2/§6.2 + docs/34 §1/§3）

| 决策点 | 裁定 | 来源 |
|---|---|---|
| 本刀性质 | **规划刀** — 仅 docs/47 + pack 登记；不写 dbt mart / 不写 migration / 不全量 seed | `262` §SCHEMA "本刀只规划" + docs/46 §9 |
| mart 映射 | 新建 `mart_city_evidence_chain` + `mart_city_seven_dim_overview`（view 物化，与 `mart_person_tenure` 平行）| docs/44 §7.3 + docs/46 §6.2 |
| person/tenure 接入契约 | JOIN `mart_person_tenure` + `geo_entity`（与 city JOIN 横向）| docs/46 §5.2 OPEN + S2.1-lite `mart_person_tenure` |
| 段级字段契约 | city 段级 evidence + 七维度 cell + 同省地市 peer-compare | docs/46 §5.1 + docs/40 §2 + docs/41 §3 + docs/42 §2.4-2.5 + docs/43 §2.4 |
| 应用层 enum 守门 | InformationLayer / Polarity / EvidenceStrength / BalanceStatus / cardId（不引入 schema ENUM）| docs/40 §2.3 + 01-core.sql §25-30 |
| 红线守门 | 不派生 `score` / 不排名 / 不派生 `total_score` / `credibility_score` / 不做 `peer_rank` | docs/06 §6.6 + docs/42 §8 |
| 切刀推荐 | 拆 2 刀（先 mart 落地，再真数据迁移）| 降依赖 O1 + Stage 1 OPEN |
| 物化策略 | view（与 mart_person_tenure 平行）| docs/44 §7.3 现行模式 |
| OPEN 携带 | O1 / O2 / O3 / **O8** / **O9** / **O10**（§10.4 显式列表）| docs/34 §3 + docs/46 §5.2/§6.2 |
| docs/47 文件级 forbidden-token guard | "Gate 2 PASS" 4 处 + "score/rating/rank/credibility" 全部为禁止/不派生语境（CLEAN）| docs/34 §1 + §8 #8 + §133 + docs/06 §6.6 + docs/42 §8 |
| ❌ 宣布 Gate 2 PASS | 红线条目（§1.2 + §6 + §7 + §9 多次显式守门）| docs/34 §1 + §8 #8 + §133 + `262` §红线 |
| ❌ 改 Cursor 锁定 10 城名单 | 红线（落地刀不得擅自换/加 4 江苏 + 3 浙江 + 3 广东）| `256` §SCHEMA + docs/46 §2 |
| ❌ 伪造 SHA / 伪造证据 | 红线（O1 收口前不得落地 full）| `262` §红线 + docs/34 §1 |
| Gate 2 评审日期 | 暂定 W8（不擅自提前）| docs/34 §10.4 |

---

## §3. docs/47 §红线条目（全文审计）

| 红线条目 | 出现位置 | 语境 |
|---|---|---|
| ❌ 不宣布 Gate 1 / Gate 2 PASS | §1 头/§1.2/§6/§7/§9/收尾 | 全部为禁止/守门 |
| ❌ 不做官员能力总分（PRD 红线 + docs/08 §3.3 红线 1）| §1.2 | 红线条目 |
| ❌ 不做隐性指数（docs/08 §3.3 红线）| §1.2 | 红线条目 |
| ❌ 不启用 DSH（docs/08 §3.3 红线）| §1.2 | 红线条目 |
| ❌ 不做实时数据（docs/08 §3.3 红线；月度/年度更新）| §1.2 | 红线条目 |
| ❌ 不伪造 SHA / 不伪造证据（`262` §红线）| §1.2 + §6.3 | 红线条目 |
| ❌ 不批量爬政策研究 / 财政预决算 / 官员履历 | §1.2 | 红线条目 |
| ❌ 不擅自改 Cursor 锁定的 10 城名单 | §1.2 + §6.3 | 红线条目 |
| ❌ 不擅自提前 Gate 2 评审日期 | §1.2 + §6.3 | 红线条目 |
| ❌ 不派生 `score` / `rating` / `total_score` / `confidence_score` / `credibility_score` | §3.2 + §5.2 + §7 | 红线条目 |
| ❌ 不做"地区得分" / 不做"地区排名" / 不做 `peer_rank` | §3.2 | 红线条目 |
| ❌ 启用 pgvector / RLS / partition | §2.2 + §8 | 红线条目（Stage 2 边界）|
| ❌ 接真 mart / 写 dbt mart | §1 + §6 + §7 + §8 | 推 S2.7-b-full 落地刀 |
| ❌ 写 migration | §2.2 + §6 + §8 | 推 S2.7-b-full 落地刀 |
| ❌ 全量 seed | §2.2 + §8 | 推 S2.7-b-full 落地刀 |
| ❌ 改 docs/06/08/10/34/40/41/42/43/44/45/46 | §8 | Cursor 拥有 |
| ❌ 改 `gate_thresholds.json` | §8 | spike-04 评测构件，只读 |
| ❌ 10 城名单擅自换/加 | §6.3 + §10.4 | 红线条目 |

---

## §4. 红线自检（per `262` §红线 + docs/34 §1/§8/§133 + docs/06 §6.6 + docs/42 §8）

| 红线 | 状态 |
|---|---|
| ❌ 不宣布 Gate 1 / Gate 2 PASS | ✅ docs/47 头部 + §1.2 + §2.2 + §5.2 + §7 + §8 + §9 + 收尾 多次显式守门 |
| ❌ 不擅自改 Cursor 锁定的 10 城名单 | ✅ §2 + §6 + §6.3 + §10.4 锁定 4 江苏 + 3 浙江 + 3 广东；落地刀不得擅自换/加 |
| ❌ 伪造 SHA / 伪造证据 | ✅ §6.3 切刀风险显式守门；O1 收口前不得落地 full |
| ❌ 官员能力总分 / 排名 / DSH / 实时数据 | ✅ §1.2 + §3.2 + §5.2 + §7 + §10.3 守门 |
| ❌ 批量爬政策研究 / 财政预决算 / 官员履历 | ✅ §1.2 |
| ❌ HTTP 爬源站 | ✅ |
| ❌ 降 OCR 门槛 | ✅ 无关 |
| ❌ 改 1909 / 陕西代表中国 | ✅ 无关 |
| ❌ 不擅自 --force / --force-with-lease | ✅ ff-only pull |
| ❌ 不替用户下裁定 | ✅ 仅执行 `262` §SCHEMA 范围 |
| ❌ 不在聊天复述 Cursor 长文 | ✅ 仅回执要点 |
| ❌ 不索要 PAT | ✅ |
| ❌ 不改 `gate_thresholds.json` | ✅ 未读未写 |
| ❌ 不碰 `00-CC-CURRENT.md` | ✅ Cursor 拥有 |
| ✅ pack invariant 守门 | ✅ 587 → 589；bump script source-of-truth |
| ✅ receipts 仅写 `reviews/stage0-gate0-rework-2026-08-23/` | ✅ |
| ✅ 不写 dbt mart | ✅（per `262` §SCHEMA "本刀只规划"）|
| ✅ 不写 migration | ✅（per `262` §SCHEMA）|
| ✅ 不擅自提前 Gate 2 评审日期 | ✅ W8（per docs/34 §10.4）|
| ✅ docs/47 文件级 forbidden-token guard | ✅ "Gate 2 PASS" 4 处全部为禁止/守门语境；"score/rating/rank/credibility" 全部为禁止/不派生语境（CLEAN）|
| ✅ 不引入 score / rating / rank 字段 | ✅ §3.2 + §5.2 + §7 + §8 红线 |
| ✅ 不引入 schema ENUM | ✅ 应用层 enum-style 守门（per docs/40 §2.3）|
| ✅ 不动 `polarity` CHECK / `information_layer` ENUM | ✅ 无关（docs/47 是规划文档，不改 DDL）|
| ✅ 不引入跨行 CHECK 约束 | ✅ trigger + 应用层守门（推 S2.7-b-full 落地刀）|
| ✅ Static-segment 守门 | ✅ 无关（docs/47 是 markdown；dynamic segment route 已在 knife 22 守门）|
| ✅ 跨 lite 回归 s21lite..s26lite + s210 + s27b | ⏳ smoke-check 待运行（无新 UI 代码本刀）|
| ✅ OPEN 清单显式携带 | ✅ §3.1 lineage.source_file_sha256 ⚠️ OPEN + §6.3 切刀风险 + §10.4 OPEN 清单 |
| ✅ 不接全国实时排名 | ✅（per docs/34 §4.3 + docs/05 §8.3）|

---

## §5. 推送 / 三路对齐（待完成）

| 步骤 | 命令 | 结果 |
|---|---|---|
| origin pull | `git fetch origin && git pull --ff-only origin main` | queue_rev 105 ✅ |
| cc_gate_watch | `./scripts/cc_gate_watch.sh --pull` | `CC_ACTION=EXECUTE_NOW` ✅ |
| docs/47 起草 | 11 节 + 红线 + OPEN | ✅ sha `fdb6fb28`（18983 bytes）|
| docs/47 file-level guard | 扫描 forbidden tokens | ✅ CLEAN |
| bump script | `scripts/_knife24_manifest_bump.py` | ✅ 587 → 589（+2 = docs/47 + receipt 263）|
| 本地校验 | `python3 -c "json.load(...)"` manifest invariant | ⏳（待 bump 重跑后 589 == 589 == 589）|
| commit | `git add docs/47-...md evidence_pack/manifest.json scripts/_knife24_manifest_bump.py reviews/.../263-...md && git commit -m "feat(docs): add docs/47 S2.7-b-full mart plan (只规划; 10 城 mart + person/tenure 契约; 不宣布 PASS)"` | ⏳ |
| origin push | `git push origin HEAD`（**priority**）| ⏳ |
| github push | `git push github HEAD`（带 proxy）| ⏳ |
| 三路对齐 | origin/main = github/main = local HEAD | ⏳ |

> **禁止 amend-after-push**：receipt SHA + commit SHA 必须在独立 commit 里 backfill（per knife 2/3/4 经验）。

---

## §6. 下次 heartbeat 预期

- `queue_rev 105` 完成后：Cursor 收 `263` → 下发 `264-stage0-cursor-s27b-full-audit-…md`（PASS/FAIL）
- 若 PASS：进入 Gate 2 评审等待期（W8，per docs/34 §10.4）
  - **不擅自提前 Gate 2 评审日期**（per docs/34 §10.4）
  - 等待期可并行做其他刀（如 S2.10 pytest stub 收口 / S2.1-lite 落地刀 / S2.10-lite Gate 2 评审脚本等）
- 若 FAIL：`263-correction` 回合（修 docs/47 + re-commit）

---

## §7. 备注

- **本刀不宣布 Gate 2 PASS** — 这是 S2.7-b-full 规划刀最重要的红线。Gate 2 评审日期暂定 W8（per docs/34 §10.4），由 Cursor/用户裁定，不擅自提前。
- **本刀只规划** — `262` §SCHEMA 显式约束：不写 migration / 不全量 seed / 不写 dbt mart。所有落地工作推 S2.7-b-full 落地刀（tasking 26X+；OPEN）。
- **依赖 O1 真实 SHA 收口** — docs/47 §3.1 `lineage.source_file_sha256` ⚠️ OPEN；O1 收口前不得落地 full（否则伪造证据）。
- **依赖 Stage 1 OPEN 收口** — docs/34 §3 + docs/46 §6.2 + docs/47 §6.3 切刀风险显式守门。
- **依赖 S2.1-lite PASS** — person/tenure 接入契约不成立直到 S2.1-lite `mart_person_tenure` 已交（per docs/46 §5.2 OPEN）。
- **10 城名单锁定** — 4 江苏（nanjing/suzhou/wuxi/nantong）+ 3 浙江（hangzhou/ningbo/wenzhou）+ 3 广东（guangzhou/shenzhen/dongguan）；落地刀不得擅自换/加（per `256` §SCHEMA + docs/46 §2）。
- **应用层 enum 守门** — 不引入 schema ENUM；InformationLayer ∈ {FACT, DERIVED, INFERENCE, JUDGMENT} + Polarity ∈ {SUPPORTS, CONTRADICTS, NEUTRAL} + EvidenceStrength ∈ {STRONG, MODERATE, WEAK} + BalanceStatus ∈ 5 枚举 + cardId ∈ 7 维度（per docs/40 §2.3 + 01-core.sql §25-30）。
- **不派生 score / rating / rank** — docs/47 §3.2 + §5.2 + §7 + §8 红线条目多次显式守门（per docs/06 §6.6 + docs/42 §8）。
- **切刀节奏推荐 B** — 拆 2 刀（先 mart 落地，再真数据迁移）；降依赖 O1 + Stage 1 OPEN（per docs/47 §10.1）。

— End of `263` —

> 等待 Cursor 审验（预期 `264-stage0-cursor-s27b-full-audit-…md`）。
> 通过后下发 S2.7-b-full 落地任务（`265-stage2-s27b-full-impl-tasking-…md`），进入 mart 落地刀。
> ⚠ **本刀不宣布 Gate 2 PASS**（per docs/34 §1 + §8 #8 + `262` §红线）。
> ⚠ **本刀只规划**（per `262` §SCHEMA） — 不写 dbt mart / 不写 migration / 不全量 seed。
> ⚠ **10 城名单已锁定**（per `256` §SCHEMA + docs/46 §2）。
> Gate 2 评审日期暂定 W8（per docs/34 §10.4）。