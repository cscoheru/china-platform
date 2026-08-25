# 38 — Stage 2 / S2.3 / project_event 规划

> 起草：CC · 2026-08-25 · queue_rev 78
> 前置：`200` S2.2-lite PASS；`201` S2.3 任务书；`docs/04` §3.8 五态机 + §3.x；`docs/06` §2.4/§2.5 六段 PROCESS/OUTPUT
> 本刀**仅规划**；不写生产 migration（per `201` §SCHEMA + 用户裁定 **D** 缩刀模式）

---

## 1. 目标

S2.3 是 Stage 2 「项目事件」维度的基础表刀。本刀完成 `project_event` + 五态机的**规划文档**，不写 migration。落地刀（tasking 203+ 视 Cursor 审验再下发）将：

- 迁移 `project_event` 至 docs/37 §2 等价字段契约（additive-only）
- 首批 ≤N 行手工 seed（`is_demo="true"`），不爬网
- 落地 dbt `stg_project_event` + `mart_project_event`（含 `is_demo` 过滤 + 五态机 ENUM 投影）
- pytest 覆盖：五态机合法迁移 / 重叠项目节点合法 / `is_demo` 过滤 / 无评分字段

参考 S2.1 / S2.2 节奏：先 `docs/38` 规划 → Cursor 审验 PASS → 落地 tasking → 实施。本文档对应 `docs/38`。

---

## 2. 表契约（per docs/04 §3.8 + Stage 2 PROCESS/OUTPUT 消费形状）

### 2.0 范围声明

| 包含 | 不包含（推后续刀） |
|---|---|
| `project_event`（含五态机 `project_status` ENUM）| `budget_allocation`（S2.4）|
| 五态机消费形态（PROCESS/OUTPUT 段）| `budget_execution`（S2.4）|
| 关键列 `lineage` JSONB（is_demo sentinel）| S2.1 person 全量（用户 D 缩刀仍生效）|
| `parties` 数组（参与方名）| `claim_evidence_link`（S2.5 之后）|
| `investment_amount` + `investment_unit` 投资额 | `inference_record`（S2.5）|

### 2.1 `project_event`（per docs/04 §3.8）

```sql
CREATE TABLE project_event (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_name        TEXT NOT NULL,
    geo_entity_id       UUID NOT NULL REFERENCES geo_entity(id) ON DELETE RESTRICT,
    project_type        TEXT,
    status              project_status NOT NULL,           -- 五态机 ENUM
    event_date          DATE NOT NULL,
    investment_amount   NUMERIC,
    investment_unit     TEXT,
    parties             TEXT[],
    description         TEXT,
    source_id           UUID NOT NULL REFERENCES source_document(id) ON DELETE RESTRICT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TYPE project_status AS ENUM (
    'ANNOUNCED', 'SIGNED', 'STARTED', 'PRODUCING', 'AT_CAPACITY'
);
```

新增列（本刀**只规划**；落地刀 migration 010 实施）：

| 列 | 类型 | 用途 | docs/37 §2 平行 |
|---|---|---|---|
| `canonical_project_name` | TEXT NULL | 归一化项目名（去批文号/版本后缀） | `policy_document.canonical_title` 平行 |
| `project_name_en` | TEXT NULL | 英文渲染（国际 cross-ref） | `policy_document.title_en` 平行 |
| `project_class` | TEXT NULL | enum-style: MANUFACTURING / INFRASTRUCTURE / REAL_ESTATE / TECH / ENERGY / AGRICULTURE / OTHER | `policy_document.classification` 平行 |
| `status_year` | INTEGER NULL | 从 event_date 提取（avoid JOIN to date_part） | `policy_document.effective_year` 平行 |
| `lineage` | JSONB NULL | per-row R3-E provenance: `{chain_id, source_file_sha256, source_file_url, extractor_version, is_demo}` | 同 S2.1/S2.2 模式 |
| `project_hash_canonical` | TEXT NULL | 同一项目的 stable 跨版本 SHA（per R12-A de-dupe；同一项目 N 次 event 共享）| `policy_document.policy_hash_canonical` 平行 |
| `investment_currency_canonical` | TEXT NULL | 归一化币种（avoid "亿元" vs "亿元(本币)" vs "RMB" drift）| `policy_target.target_unit_canonical` 平行 |
| `expected_output_text` | TEXT NULL | 期望产出（自然语言；不评分）| `policy_measure.expected_outcome_text` 平行 |
| `delay_reason` | TEXT NULL | 延期原因（如有延期事件记录）| — |
| `completion_year_planned` | INTEGER NULL | 计划达产年 | — |
| `completion_year_actual` | INTEGER NULL | 实际达产年（per AT_CAPACITY event）| — |

**不扩**：

- ❌ 不加 `EXCLUDE` on `(canonical_project_name, geo_entity_id, status, event_date)` —— 同一项目同日多状态合法（per docs/04 §3.8 五态独立）
- ❌ 不修改 `project_status` ENUM —— 落地刀不动 ENUM；新增态 = 后续 011+
- ❌ 不在 `project_event` 加 `score` / `rating` / `rank` / `total_score` 任一字段 —— 红线
- ❌ 不写触发器自动 `status → 下一态`（per docs/04 §3.8）—— 留应用层 + 评审
- ❌ 不做 `parties` JSONB 拆分 —— TEXT[] 已满足「参与方名」最小需求

### 2.2 五态机消费形态（per docs/04 §3.8 + docs/06 §2.4/§2.5）

| ENUM 态 | docs/06 §段 | 语义边界 | 与下一态关系 |
|---|---|---|---|
| `ANNOUNCED` | PROCESS | 项目签约前公开宣布（"拟投资 XXX 亿元"）| ≠ 签约；仅"意向" |
| `SIGNED` | PROCESS | 投资协议正式签署（含签约仪式 / 文本交付）| ≠ 开工；未动工 |
| `STARTED` | PROCESS | 项目破土动工（场地平整 / 设备到位）| ≠ 投产；未产生 |
| `PRODUCING` | OUTPUT | 项目试产或部分投产（产能 <100%）| ≠ 达产；未满产 |
| `AT_CAPACITY` | OUTPUT | 项目达产（产能 ≥ 设计值）| 终止态；后续追加投资另起事件 |

**钉死**（per docs/06 §2.5 末段）：
- 签约 ≠ 开工 ≠ 投产 ≠ 达产 —— 四种状态分别记录
- 五态**独立记录**（append-only），不合并为单一 `project` + 当前态字段
- 同一项目可有多条记录（"签约" + "开工"是两条 event）

---

## 3. dbt staging candidate 路径（per docs/19 §S1.19 + S2.1 §3 + S2.2 §3 平行）

### 3.1 sources（`_stg_sources.yml`）

新增 1 条：

```yaml
sources:
  - name: cegr
    tables:
      - name: project_event
        columns: [id, project_name, geo_entity_id, project_type, status,
                  event_date, investment_amount, investment_unit, parties,
                  description, source_id, created_at,
                  canonical_project_name, project_name_en, project_class,
                  status_year, lineage, project_hash_canonical,
                  investment_currency_canonical, expected_output_text,
                  delay_reason, completion_year_planned, completion_year_actual]
```

### 3.2 staging model（per `dbt/models/staging/stg_observation.sql` 模式）

| 模型 | 备注 |
|---|---|
| `stg_project_event.sql` | passthrough + JOIN geo_entity for `geo_canonical_name`；expose `status` enum 文本；expose `is_demo` from lineage |

```sql
{{ config(materialized='view', tags=['staging', 'project_event']) }}
```

### 3.3 mart（不**直接**改既有 mart）

新建 `mart_project_event`（仿 S2.1 §3 `mart_person_tenure` + S2.2 §3.3 `mart_policy_commitment`）：

```sql
{{ config(materialized='view', tags=['mart', 'project_event']) }}

SELECT
    pe.project_event_id,
    pe.project_name,
    pe.canonical_project_name,
    pe.project_name_en,
    pe.project_type,
    pe.project_class,
    pe.status,
    pe.status_year,
    pe.event_date,
    pe.investment_amount,
    pe.investment_currency_canonical,
    pe.investment_unit,
    pe.geo_entity_id,
    g.canonical_name AS geo_canonical_name,
    pe.parties,
    pe.expected_output_text,
    pe.delay_reason,
    pe.completion_year_planned,
    pe.completion_year_actual,
    pe.project_hash_canonical,
    COALESCE(pe.lineage->>'is_demo', 'false') AS is_demo
FROM {{ ref('stg_project_event') }} pe
LEFT JOIN {{ ref('stg_geo_entity') }} g ON g.geo_entity_id = pe.geo_entity_id
```

`is_demo` 显式暴露为最后一列（per docs/33 §3.2 sentinel + S2.1/S2.2 mart 同模式）。

### 3.4 五态机 mart 辅助视图（落地刀可选）

```sql
-- mart_project_event_status_timeline（每项目一条；五态时序）
CREATE OR REPLACE VIEW mart_project_event_status_timeline AS
SELECT
    pe.project_hash_canonical,
    pe.geo_entity_id,
    COUNT(*) FILTER (WHERE pe.status = 'ANNOUNCED') AS n_announced,
    COUNT(*) FILTER (WHERE pe.status = 'SIGNED')    AS n_signed,
    COUNT(*) FILTER (WHERE pe.status = 'STARTED')   AS n_started,
    COUNT(*) FILTER (WHERE pe.status = 'PRODUCING') AS n_producing,
    COUNT(*) FILTER (WHERE pe.status = 'AT_CAPACITY') AS n_at_capacity,
    MIN(pe.event_date) FILTER (WHERE pe.status = 'SIGNED') AS first_signed_date,
    MAX(pe.event_date) FILTER (WHERE pe.status = 'AT_CAPACITY') AS last_at_capacity_date
FROM stg_project_event pe
WHERE pe.project_hash_canonical IS NOT NULL
GROUP BY pe.project_hash_canonical, pe.geo_entity_id;
```

**不评分**：仅行数 + 时序；不计算「平均达产时间」「准时率」等派生评分（per 红线）。

---

## 4. 首批入库策略

### 4.1 来源（per `92` §1.1 R4 + 201 §SCHEMA）

| 来源 | 类型 | 红线 |
|---|---|---|
| 公开项目公告 | 发改委 / 工信部 / 省级政府门户 | **不**批量爬 2020-2025；首批 ≤8 项目 |
| 用户上传 | S2.0.2 admin_upload (Stage 1 §1.3.1) | 仅在 admin 角色提交；audit trail 写入 |
| 手工 seed | hand-curated JSON（per S1.12 + S2.1.7-a 平行） | `is_demo="true"`；不爬网 |

### 4.2 条数上限（首批 ≤N）

| 项目数 | event 数 | 理由 |
|---|---|---|
| ≤8 项目 | ≤32 events | 每项目平均 4 个 event（ANNOUNCED + SIGNED + STARTED + AT_CAPACITY）；首批演示完整五态时序 |
| ≤8 项目 | ≤40 events | 含部分 PRODUCIING 中间态 |

具体约束：

| 限制 | 上限 | 理由 |
|---|---|---|
| `project_event` 总行数 | ≤40 | 演示 ≤8 项目 × 5 态 |
| `project_hash_canonical` 唯一值 | ≤8 | ≤8 独立项目 |
| `geo_entity_id` 跨项目 | ≤10 | 跨省/跨市；首批演示多 geo |

### 4.3 `is_demo` 全 true（per S1.18 sentinel + S2.1 §4.3 + S2.2 §4.3 平行）

| 字段 | 值 |
|---|---|
| `project_event.lineage->>'is_demo'` | `"true"` |
| `source_file_sha256` | `"0"` × 64（per docs/33 §3.1） |
| `source_file_url` | `"(DEMO_SEED_NO_FILE)"` |

### 4.4 稳定 UUID（per S1.12 + S2.1 §4.4 + S2.2 §4.4 平行）

`a0000000-0000-0000-0000-00000000007X` 家族（X = 0..9 + a..z）。

### 4.5 seed 文件

`data/seeds/project_event_demo.json` + `scripts/seed_project_event_demo.py`（mirror `scripts/seed_person_tenure_s21lite.py` + `scripts/seed_policy_commitment_demo.py`（待 S2.2 落地后））。

---

## 5. 与 S2.7 六段 PROCESS / OUTPUT 消费对照

### 5.1 `mart_project_event` → `PROCESS` 段（per docs/06 §2.4 + S2.7-a mock）

| mart 列 | EvidenceChain 段消费字段 | 备注 |
|---|---|---|
| `project_name` | `items[].title` | 短文本直显 |
| `canonical_project_name` | `items[].title_canonical`（**新增**）| 后续刀 |
| `project_name_en` | `items[].title_en`（**新增**）| 仅国际 cross-ref 展示 |
| `geo_canonical_name` | `items[].geo` | |
| `status` | `items[].status_badge` | 五态映射 + 配色（ANNOUNCED=灰 / SIGNED=蓝 / STARTED=橙 / PRODUCING=黄 / AT_CAPACITY=绿）|
| `event_date` | `items[].event_date` | |
| `investment_amount` + `investment_currency_canonical` | `items[].investment_display` | "XXX 亿元" |
| `parties` | `items[].parties`（数组渲染）| |
| `lineage->>'is_demo'` | items 整体加 `is_demo=true` 角标 | S1.18 sentinel |

### 5.2 `mart_project_event` → `OUTPUT` 段（per docs/06 §2.5）

| mart 列 | EvidenceChain 段消费字段 | 备注 |
|---|---|---|
| `status = AT_CAPACITY` | `items[].facility_count`（若 planned/actual 提供）| "已建成 XX 座/公里" |
| `completion_year_actual` | `items[].completion_year` | 仅 AT_CAPACITY 行展示 |
| `expected_output_text` | `items[].expected_output`（AT_CAPACITY 时横比 "达成/未达成"）| **不评分**；仅文字陈列 |
| `delay_reason` | `items[].delay_note`（如有延期）| 文字说明 |

### 5.3 不接 S2.7-b（per 187 §SCHEMA 禁 + 201 §SCHEMA 禁）

本刀 S2.3-lite（落地刀）**不接** S2.7 PROCESS/OUTPUT 段。留给 S2.7-b 协同 knife：消费 `mart_project_event`，写入 EvidenceChain。

### 5.4 验证（落地刀）

```bash
# 1. mart 行数 ≥1
PGPASSWORD=postgres psql -h 127.0.0.1 -p 55440 -U postgres -d cegr_test \
    -c "SELECT COUNT(*) FROM cegr_staging.mart_project_event WHERE is_demo = 'true';"
# 预期: ≥1

# 2. 五态分布
PGPASSWORD=postgres psql ... \
    -c "SELECT status, COUNT(*) FROM cegr_staging.mart_project_event GROUP BY status ORDER BY status;"
# 预期: 5 行; 每态 ≥1（per 4.2 ≤40 行首批约束）

# 3. is_demo 过滤（per docs/33 §3.3 case 4）
PGPASSWORD=postgres psql ... \
    -c "SELECT COUNT(*) FROM cegr_staging.mart_project_event WHERE is_demo = 'false';"
# 预期: 0（仅 demo 数据）

# 4. project_hash_canonical de-dupe
PGPASSWORD=postgres psql ... \
    -c "SELECT COUNT(DISTINCT project_hash_canonical) FROM cegr_staging.mart_project_event;"
# 预期: ≤8（per 4.2 首批约束）
```

---

## 6. 验收清单

| # | 项 | 落地刀验证方式 |
|---|---|---|
| 1 | `project_event` 表 + docs/04 §3.8 字段 + §2 新增列齐全 | `\d cegr.project_event` |
| 2 | `project_status` ENUM 五态存在（per docs/04 §3.8）| `\dT+ cegr.project_status` |
| 3 | dbt run `--select stg_project_event+` exit 0；1 stg + 1 mart 创建 | dbt run log |
| 4 | mart 行数 = seed 行数（is_demo=true 过滤后）| SQL COUNT |
| 5 | 五态分布：每态 ≥1（首批演示完整时序）| SQL GROUP BY status |
| 6 | 既有 38 schema_negative 测试仍绿（含 s22lite 5 + s21lite 5）| pytest tests/ -q |
| 7 | 新增 pytest `tests/test_project_event_s23lite.py` ≥5 cases 全过 | pytest -v |
| 8 | pack invariant 528 → 528+N | JSON 解析守门 |
| 9 | smoke-check 仍 PASS（无 frontend 改动）| python3 frontend/smoke-check.py |
| 10 | 既有 S2.7-a2 + S2.1-lite + S2.2-lite 套件仍绿 | pytest tests/test_evidence_chain_s27a.py tests/test_person_tenure_s21lite.py tests/test_policy_commitment_s22lite.py |

---

## 7. 关键风险与回滚

| 风险 | 触发条件 | 回滚策略 |
|---|---|---|
| `project_status` ENUM 五态与 docs/04 §3.8 不一致 | ENUM 修改必须 ALTER TYPE | 落地刀不动 ENUM；新增态 = 011+ |
| 五态时序倒置（AT_CAPACITY 早于 STARTED）| 业务约束；不强制 | 不加 CHECK；评审层 catch（per docs/04 §3.8 独立记录原则）|
| `parties TEXT[]` 字段截断长字符串 | TEXT[] 元素无显式长度上限 | 不限；落地刀约定 ≤500 char/元素 |
| `project_hash_canonical` 全 NULL（首批不生成）| de-dupe 失效 | 落地刀 §4.4 稳定 UUID 钉死 8 个项目；不允许 NULL |
| `investment_amount` 单位 drift（"亿元" vs "亿元(本币)"）| 同 policy.target_unit drift | 落地刀统一 `investment_currency_canonical` |
| 同项目多 event 共享 `project_hash_canonical`（per R12-A）| 跨表外键 | 不加 FK（hash 而非 UUID 引用）；应用层守门 |

---

## 8. 不做什么（本刀 S2.3-lite 边界；推后续刀）

| ❌ | 推到 |
|---|---|
| ❌ 写生产 migration 010（**仅规划**）| S2.3 落地刀（tasking 203+）|
| ❌ dbt stg_project_event + mart_project_event | S2.3 落地刀 |
| ❌ 首批 ≤40 project_event 真实 seed | S2.3 落地刀（**严禁爬网**）|
| ❌ 接 S2.7-b PROCESS/OUTPUT 段消费 | S2.7-b 协同刀 |
| ❌ S2.1 person 全量（用户 D 缩刀）| 后续刀待用户裁定 |
| ❌ `budget_allocation` / `budget_execution`（S2.4）| S2.4 |
| ❌ `claim_evidence_link`（S2.5 末段）| S2.5 |
| ❌ 五态机自动跃迁触发器 | 应用层 + Gate 评审 |
| ❌ `score` / `rating` / `rank` / `total_score` 任一字段 | 红线 |
| ❌ 修改 `gate_thresholds.json` | spike-04 评测构件，只读 |
| ❌ 批量爬 2020-2025 项目公告 | 红线 |
| ❌ 启用 pgvector / RLS / partition | Stage 2 边界（per docs/04 §6）|
| ❌ 修改 `00-CC-CURRENT.md` | Cursor 拥有 |

---

## 9. 与现有文档的关系

| 引用 | 用途 |
|---|---|
| `docs/04-data-model.md` §3.8 | 五态机 ENUM + 独立记录原则 |
| `docs/06-governance-observation-method.md` §2.4 | PROCESS 段（项目节点） |
| `docs/06-governance-observation-method.md` §2.5 | OUTPUT 段（设施建成/签约/开工/投产） |
| `docs/06-governance-observation-method.md` §2.5 末段 | "签约≠开工≠投产≠达产" 钉死 |
| `docs/19-stage1-s19-dbt-staging-plan-20260825.md` | dbt staging 模式 |
| `docs/33-stage1-s18-demo-sha-lock-plan-20260825.md` §3.1 / §3.3 | `is_demo` sentinel + 评测基线 |
| `docs/34-stage2-s20-kickoff-plan-20260825.md` §4 序 7 | S2.3 范围 + budget/project 排序 |
| `docs/36-stage2-s21-person-tenure-plan-20260825.md` | S2.1 平行规划（风格基线） |
| `docs/37-stage2-s22-policy-plan-20260825.md` | S2.2 平行规划（命名 / lineage / 五段） |
| `schema/01-core.sql` §127-130 + §785-802 | 既有 `project_status` ENUM + `project_event` 表 |

---

## 10. CC 建议（供 Cursor 审阅 / 用户裁定）

### 10.1 `project_status` 落 strategy（per docs/04 §3.8）

| 选项 | 描述 | 选 |
|---|---|---|
| A | 沿用 docs/04 原 ENUM（落地刀**不动** ENUM；新列落地即可）| **推荐** |
| B | 改 ENUM 加 NULL "UNKNOWN" | 加固；ENUM 修改必须 ALTER TYPE，复杂度↑ |

### 10.2 `project_class` 落 strategy

| 选项 | 描述 | 选 |
|---|---|---|
| A | enum-style TEXT（per docs/37 §10.5 / §2.1）| **推荐** |
| B | schema-level CHECK + ENUM type | 加固；migration 010 复杂度↑ |

### 10.3 `parties` 落 strategy

| 选项 | 描述 | 选 |
|---|---|---|
| A | TEXT[]（per docs/04 §现有 + §2.1 钉死）| **推荐** |
| B | JSONB（结构化参与方 + 角色 + 股份）| 复杂；首批演示够用 TEXT[] |

### 10.4 `project_hash_canonical` 共享策略

| 选项 | 描述 | 选 |
|---|---|---|
| A | 同一项目 N 个 event 共享一个 hash（per R12-A de-dupe）| **推荐** |
| B | 每 event 独立 hash | 失去跨事件追踪能力 |

### 10.5 `expected_output_text` 必填性

| 选项 | 描述 | 选 |
|---|---|---|
| A | nullable TEXT；落到 mart 时 LEFT JOIN 缺失语言 fallback | **推荐**（per docs/37 §10.3） |
| B | required NOT NULL | 工作量大；首批演示会卡 |

### 10.6 `delay_reason` 必填性

| 选项 | 描述 | 选 |
|---|---|---|
| A | nullable TEXT（仅延期 event 填；其余 NULL）| **推荐** |
| B | required NOT NULL DEFAULT 'NONE' | 加固；但 NULL 是「未延期」更清晰的语义 |

---

— End of `docs/38` —

> 等待 Cursor 审验（预期 `204-stage0-cursor-s23-plan-audit-…md`）。
> 通过后下发落地任务（`205-stage2-s23-project-impl-tasking-…md`），进入 S2.3-lite 实施。
> S2.1-full 与 S2.2-dbt/seed 与 S2.3 落地可**并行**（不同 schema 域）；等 Cursor 裁定。