# S2.1 — person / tenure / position 规划

> **§META 为唯一真相源** — `171` + `docs/04` §2/§3.6 + `docs/34` §4 序 4

---

## 1. 目标

S2.1 是 Stage 2 的「人」维度基础表刀：把『地方主政者是谁、任期几何、所任何职』结构化入库，
为后续 S2.7-b（六段证据链 person/tenure 接入）和 S2.5（inference_record）提供唯一真相源。

本刀**只规划**，**不写**生产 migration；交付物是本文档 + 数据契约 + dbt staging candidate 路径 + 首批入库策略。

---

## 2. 表契约（per docs/04 §2 + §3.6）

### 2.1 `person`（个人主表）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | UUID | ✅ | 稳定主键 |
| `canonical_name` | TEXT | ✅ | 规范姓名（中文） |
| `canonical_name_pinyin` | TEXT | — | 拼音（便于检索） |
| `birth_year` | INTEGER | — | 出生年；用于交叉验证履历 |
| `gender` | TEXT | — | 仅当来源文档明示时填；**不**做推断 |
| `ethnicity` | TEXT | — | 同上；仅当来源明示时填 |
| `notes` | TEXT | — | 自由文本；非分析输入 |

**钉死约束**：
- 不存个人证件号、籍贯详址、家庭成员、教育明细（per PRD 红线 + Gate 2 评审口径）
- 同名异人通过 `person_alias` 关联（不直接合并）；歧义未消前**不入** mart 层

### 2.2 `person_alias`（别名 / 笔名 / 旧名）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | UUID | ✅ | |
| `person_id` | UUID (FK → person) | ✅ | |
| `alias` | TEXT | ✅ | |
| `alias_type` | ENUM(常用,曾用名,笔名,其他) | ✅ | |
| `valid_from` | DATE | — | |
| `valid_to` | DATE | — | |

**钉死约束**：alias 必须是**公开来源可证**的；私人/非公开称呼不入库。

### 2.3 `position`（职位字典表）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | UUID | ✅ | |
| `canonical_title` | TEXT | ✅ | 如"省委书记"、"省长"、"市委书记" |
| `title_en` | TEXT | — | |
| `rank_level` | TEXT | — | 正省部级 / 副省部级 / 局级...（**非评分用**，仅用于检索过滤） |
| `jurisdiction_geo_id` | UUID (FK → geo_entity) | — | 该职位所属行政区 |
| `is_standing_committee` | BOOLEAN | — | 党委常委标志 |

**钉死约束**：`rank_level` 是**行政级别**而非『能力分』；不接受任何衍生评分。

### 2.4 `tenure`（任期）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | UUID | ✅ | |
| `person_id` | UUID (FK → person) | ✅ | |
| `position_id` | UUID (FK → position) | ✅ | |
| `geo_entity_id` | UUID (FK → geo_entity) | ✅ | 任职地理范围 |
| `start_date` | DATE | ✅ | |
| `end_date` | DATE | — | NULL = 在任 |
| `is_current` | BOOLEAN | (derived) | end_date IS NULL 时为 TRUE |
| `appointment_event_id` | UUID (FK → appointment_event) | — | 上任事件溯源 |
| `departure_event_id` | UUID (FK → appointment_event) | — | 离任事件溯源 |

**钉死约束（per docs/04 §3.6）**：
- **不加 `EXCLUDE` 约束** — 重叠任期合法（同时任书记 + 省长）
- 不写「主政者是谁」的 deterministic view（避免单一裁定）
- 同一人同期可有多条 tenure（不同职位 / 不同地区）

### 2.5 `appointment_event`（任免事件）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | UUID | ✅ | |
| `person_id` | UUID (FK → person) | ✅ | |
| `position_id` | UUID (FK → position) | — | 空 = 离任未指定新职 |
| `geo_entity_id` | UUID (FK → geo_entity) | — | |
| `event_type` | ENUM(任命, 免职, 兼任, 辞任, 其他) | ✅ | |
| `event_date` | DATE | ✅ | |
| `announcement_doc_id` | UUID (FK → source_document) | — | 任免公告原文 |
| `announcement_url` | TEXT | — | 公开来源 URL |
| `caveat_text` | TEXT | — | 解析说明 / 存疑 |

**钉死约束**：append-only；不修改既有事件；纠错走 observation_revision 模式（per docs/04 §3.4）。

### 2.6 `person_source_evidence`（人 ↔ 证据链）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | UUID | ✅ | |
| `person_id` | UUID (FK → person) | ✅ | |
| `source_document_id` | UUID (FK → source_document) | ✅ | |
| `source_location_id` | UUID (FK → source_location) | — | 公告 / 履历中的位置 |
| `evidence_type` | ENUM(履历条目, 任免公告, 简历来源, 其他) | ✅ | |
| `excerpt` | TEXT | — | 原文摘录（≤200 字） |

**钉死约束**：每条 `person` 至少有 1 条 `person_source_evidence`（无源 = 不入 mart）。

---

## 3. dbt staging candidate 路径（per S1.19）

每张表 = 一个 staging candidate CTE + 一个 mart view：

```
sources/cegr/
  person.sql                       ← snapshot of cegr.person（dbt source）
models/staging/cegr/
  stg_person.sql                   ← stg_person CTE（1:1 passthrough + UUID cast）
  stg_tenure.sql
  stg_position.sql
  stg_appointment_event.sql
  stg_person_source_evidence.sql
models/marts/cegr/
  mart_person_tenure.sql           ← JOIN person × tenure × position × geo
                                   ← 暴露 `is_demo` 过滤列给下游
```

**约束（per docs/34 §5 + 133 §1）**：
- **不**直接改既有 mart 层（`mart_observation_quality` / `mart_source_disagreement`）
- 新 mart 必须**显式包含 `is_demo` 字段**，下游消费方可过滤（S1.18 契约）
- dbt run --select staging+ 仍纳入现有 `seed_jiangsu_gdp_demo.py` 的 staging rebuild（per S1.12 / S2.0.2.1）

---

## 4. 首批入库策略（per tasking 171 §SCHEMA）

### 4.1 数据来源

| 来源 | 类型 | 用途 |
|------|------|------|
| 公开履历（百科条目 / 政府官网） | 手工 | person + person_source_evidence |
| 任免公告（人民网 / 当地党报） | 手工 | appointment_event |
| `data/seeds/person_demo.json`（**新增**） | 手工 seed | S2.1 实现刀的 test 路径 |

**红线**：不爬网抓履历；不批量抓任免公告。首批 ≤30 条 tenure（手工），覆盖江苏 / 浙江 2 省各 3-5 任主要职位。

### 4.2 条数上限

| 表 | 首批上限 | 后续上限（每刀） |
|------|----------|----------------|
| `person` | 30 | ≤50 |
| `tenure` | 60 | ≤100 |
| `position` | 20 | ≤30 |
| `appointment_event` | 60 | ≤100 |
| `person_source_evidence` | 60 | ≤100 |

超出上限 → 走 Cursor 174+ 任务书审批；本刀**不**沉淀「试错 schema」（per docs/34 §5）。

### 4.3 `is_demo` 策略

- 首批 30 条 person **全部** `is_demo="true"`（手工 seed 占位）
- S2.1 实现刀若引入公开来源的真实履历，需走 `replace_demo_with_real`（per S2.0.2.2）+ allowlist 前缀 SHA 锁定
- `is_demo` 字段加在 `tenure` 行级 JSONB（与 S1.18 observation lineage 同款）

---

## 5. 与 S2.7-a UI 雏形的字段对照

| 六段 | S2.1 消费字段 | 备注 |
|------|---------------|------|
| CONDITION | `tenure.geo_entity_id` + `tenure.start_date` | 提供"在何时何地执政"的时点 |
| COMMITMENT | `appointment_event.excerpt` + `caveat_text` | 上任时的承诺摘录（如有） |
| INPUT | (S2.4 刀，不在本刀) | — |
| PROCESS | `tenure.start_date` → `tenure.end_date` 时间窗 | 期间发生的 PROCESS 段证据按时间窗 JOIN |
| OUTPUT | (S2.3 刀) | — |
| OUTCOME_RISK | (S2.5 刀) | — |

**S2.7-b 接入约定**：
- `EvidenceChain` 组件**不**新增 scoring props
- person/tenure 接入**只**追加 evidence items 到现有六段，**不**改 contract
- `EvidenceChain` 的 runtime guard（缺段抛错）保留

---

## 6. 验收清单

| # | 验收 | 工具 |
|---|------|------|
| 1 | S2.1 实现刀继承 docs/36 §2 字段集（不私自加减字段） | schema diff in PR |
| 2 | dbt staging candidate 5 张表可独立 `dbt run --select stg_person+` | dbt run logs |
| 3 | 新 mart `mart_person_tenure` 含 `is_demo` 列；下游 `WHERE is_demo != 'true'` 可过滤 | pytest + mart query |
| 4 | 首批 ≤30 / 60 / 20 / 60 / 60 行；超出走审批 | COUNT(*) 守门 |
| 5 | 任一 tenure 至少有 1 条 `person_source_evidence` | LEFT JOIN ... IS NULL 守门 |
| 6 | `tenure` 重叠合法测试（同年同地区两人不同职位） | pytest |
| 7 | 既有 S2.7-a 套件（13 cases）+ S2.0.x 套件（41 cases）仍绿 | pytest |
| 8 | 既有 frontend smoke-check（34 checks）仍绿 | smoke-check.py |

---

## 7. 关键风险与回滚

| 风险 | 触发条件 | 回滚策略 |
|---|---|---|
| S2.1 schema 字段反复调整（试错 schema） | 实现刀中字段加减 >2 次 | 走数据契约 ADR；本刀 §2 已钉死 |
| `is_demo` 漏设导致下游误用真实履历为 demo | 字段 nullable + 默认值漂移 | mart 加 `is_demo IS NOT NULL` 守门；pytest |
| S2.7-b 接入时 EvidenceChain 误接 scoring props | 贡献者忽略红线程 | smoke + pytest 已禁 score/rating/rank/total_score（双重守门） |
| 履历混入敏感字段（证件号、籍贯详址） | 字段 nullable 误用 | §2.1 钉死约束；新增 INSERT 触发器拒绝（可选，S2.1 实现刀讨论） |
| 任免公告 URL 失效 | 公开来源链接腐烂 | `announcement_doc_id` FK 优先于 URL；URL 仅作 fallback |

---

## 8. 不做什么（per tasking 171 §红线 + docs/34 §7）

1. ❌ **不**宣布 Gate 1/2 PASS
2. ❌ **不**做官员能力分 / 总分 / 排名；`rank_level` 仅用于检索
3. ❌ **不**爬网抓履历；**不**批量抓任免公告
4. ❌ **不**做 DSH（按 docs/07 决策）
5. ❌ **不**扩 policy_document / budget / project 表（属于 S2.2 / S2.4 / S2.3 刀）
6. ❌ **不**改 `gate_thresholds.json`（spike-04 评测构件，只读）
7. ❌ **不**把 1909 代表中国 / **不**把陕西标为门控
8. ❌ **不**写本刀 production migration（规划刀；实现刀后续）
9. ❌ **不**改 `00-CC-CURRENT.md`（Cursor 拥有）
10. ❌ **不**擅自 --force / --force-with-lease
11. ❌ **不**替用户下裁定（条目数 / 来源优先级 / 公开口径判定）
12. ❌ **不**在 chat 复述 Cursor 长文
13. ❌ **不**索要 PAT

---

## 9. 与现有文档的关系

| 文档 | 关系 |
|------|------|
| `docs/04` §2 ER 图 | S2.1 字段集的**单一真相源**；本规划**不**重定义 |
| `docs/04` §3.6 | tenure 重叠合法性的来源 |
| `docs/06` §2 | 六段证据链 contract；S2.7-b 接入的形状约束 |
| `docs/08` §3.2 | Gate 2 验收口径 |
| `docs/34` §4 序 4 | S2.1 在 Stage 2 中的位置与依赖 |
| `docs/35` §4.3 | S2.0.2.2 `replace_demo_with_real` 流程（首批入库策略复用） |
| `docs/33` §3.2 | `is_demo="true"` sentinel 契约 |

---

## 10. CC 建议（供 Cursor 审阅 / 用户裁定）

1. **首批入库 30 person + 60 tenure**：与 S2.7-a mock 量级匹配；超出会拖慢 S2.7-b 接入节奏
2. **`is_demo` 加在 `tenure` 行级 JSONB**（与 S1.18 同款）：保持下游 mart 的过滤一致性
3. **`rank_level` 仅枚举值**：避免未来贡献者填入衍生分；S2.1 实现刀讨论是否需 schema-level CHECK 约束
4. **不留「主政者是谁」deterministic view**：单一定位责任在 UI 而非 DB；与 docs/06 §2「不替代相邻段」一致
5. **`appointment_event.excerpt` ≤200 字**：与 `source_document.caveat_text` 同长度上限，保持 extract 模式一致

— End —
