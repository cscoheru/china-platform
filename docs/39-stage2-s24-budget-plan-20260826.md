# 39 — Stage 2 / S2.4 / budget_allocation & budget_execution 规划

> 起草：CC · 2026-08-26 · queue_rev 85
> 前置：`213` S2.3-lite PASS；`214` S2.4 任务书；`docs/04` §2 ERD + `schema/01-core.sql` §804-828；`docs/06` §2.4/§2.5 六段 PROCESS/OUTPUT；`docs/34` §4 序 8
> 本刀**仅规划**；不写生产 migration（per `214` §SCHEMA + 用户裁定 **D** 缩刀模式）

---

## 1. 目标

S2.4 是 Stage 2 「预算」维度的基础表刀。本刀完成 `budget_allocation` + `budget_execution` 的**规划文档**，不写 migration。落地刀（tasking 216+ 视 Cursor 审验再下发）将：

- 迁移两表至 docs/39 §2 等价字段契约（additive-only）
- 首批 ≤N 行手工 seed（`is_demo="true"`），不爬网
- 落地 dbt `stg_budget_allocation` + `stg_budget_execution` + `mart_budget_execution`（含 `is_demo` 过滤 + 执行率口径）
- pytest 覆盖：执行率合法 / 单位 drift 守门 / `is_demo` 过滤 / 无评分字段 / 最小关联守门

参考 S2.1 / S2.2 / S2.3 节奏：先 `docs/39` 规划 → Cursor 审验 PASS → 落地 tasking → 实施。本文档对应 `docs/39`。

---

## 2. 表契约（per docs/04 §2 ERD + schema/01-core.sql §804-828）

### 2.0 范围声明

| 包含 | 不包含（推后续刀）|
|---|---|
| `budget_allocation`（分配层）| `policy_commitment` × `budget_allocation` 双向 FK 启用（推迟到 S2.4 落地刀 视 Cursor 裁定）|
| `budget_execution`（执行层）| `inference_record`（S2.5）|
| 关键列 `lineage` JSONB（is_demo sentinel）| `claim_evidence_link`（S2.5 末段）|
| `canonical_unit` + `*_currency_canonical` 单位归一化 | `claim_evidence_link` 正反证据 |
| `budget_hash_canonical` 跨年共享（per R12-A de-dupe） | S2.1 person 全量（用户 D 缩刀仍生效）|
| `progress_note` / `variance_reason` 自由文本 | `government_commitment` → `budget_allocation` 联动 |

### 2.1 `budget_allocation`（既有，落地刀 additive）

```sql
-- 既有 (01-core.sql §804-814)
CREATE TABLE budget_allocation (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    geo_entity_id       UUID NOT NULL REFERENCES geo_entity(id) ON DELETE RESTRICT,
    fiscal_year         INTEGER NOT NULL,
    budget_type         TEXT,
    category            TEXT,
    allocated_amount    NUMERIC NOT NULL,
    unit                TEXT NOT NULL,
    source_id           UUID NOT NULL REFERENCES source_document(id) ON DELETE RESTRICT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

新增列（本刀**只规划**；落地刀 migration 011 实施）：

| 列 | 类型 | 用途 | docs/38 §2 平行 |
|---|---|---|---|
| `canonical_category` | TEXT NULL | 归一化类目（去"教育"/"教育支出"/"教育经费" drift）| `policy_document.canonical_title` 平行 |
| `canonical_unit` | TEXT NULL | 归一化单位（"亿元" vs "万元(本币)" vs "RMB" drift）| `policy_target.target_unit_canonical` 平行 |
| `allocation_currency_canonical` | TEXT NULL | 归一化币种（CNY/HKD/USD 锚定）| `project_event.investment_currency_canonical` 平行 |
| `budget_class` | TEXT NULL | enum-style: GENERAL / SPECIAL / BOND / SOCIAL_SECURITY / TRANSFER / OTHER | `project_event.project_class` 平行 |
| `fiscal_year_int` | INTEGER NULL | 从 `fiscal_year` 投影（避免 mart SELECT JOIN 年提取）| `project_event.status_year` 平行 |
| `lineage` | JSONB NULL | per-row R3-E provenance: `{chain_id, source_file_sha256, source_file_url, extractor_version, is_demo}` | 同 S2.1/S2.2/S2.3 模式 |
| `budget_hash_canonical` | TEXT NULL | 同一笔预算跨年/跨口径共享 stable SHA（per R12-A de-dupe；同一笔可能 N 个 execution 行）| `project_event.project_hash_canonical` 平行 |
| `progress_note` | TEXT NULL | 自由文本说明（不评分）| `policy_measure.expected_outcome_text` 平行 |

**不扩**：

- ❌ 不在 `budget_allocation` 加 `score` / `rating` / `rank` / `total_score` / `execution_score` 任一字段 — 红线
- ❌ 不加 `EXCLUDE` on `(geo_entity_id, fiscal_year, category)` —— 同一地市/同一财年/同类目多笔分配合法（专项 + 一般 + 转移叠加）
- ❌ 不写触发器自动派生执行率（per docs/04 §3.x §4.x）—— 留应用层 + mart SQL
- ❌ 不修改 `budget_type` / `category` 既有 TEXT 列 —— 落地刀不引入 schema-level ENUM（per docs/38 §10.2 平行）
- ❌ 不做 `category` JSONB 拆分 —— TEXT 已满足「类目」最小需求
- ❌ 不启用 FK `budget_allocation.policy_commitment_id`（推迟；S2.4 落地刀视 Cursor 裁定）

### 2.2 `budget_execution`（既有，落地刀 additive）

```sql
-- 既有 (01-core.sql §819-828)
CREATE TABLE budget_execution (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    budget_allocation_id UUID REFERENCES budget_allocation(id) ON DELETE RESTRICT,
    execution_period_id UUID NOT NULL REFERENCES calendar_period(id) ON DELETE RESTRICT,
    executed_amount     NUMERIC NOT NULL,
    unit                TEXT NOT NULL,
    execution_rate      NUMERIC,
    source_id           UUID NOT NULL REFERENCES source_document(id) ON DELETE RESTRICT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

新增列（本刀**只规划**；落地刀 migration 011 实施）：

| 列 | 类型 | 用途 | docs/38 §2 平行 |
|---|---|---|---|
| `canonical_unit` | TEXT NULL | 归一化单位（同 alloc 口径）| 同 S2.4 alloc |
| `execution_currency_canonical` | TEXT NULL | 归一化币种 | `project_event.investment_currency_canonical` 平行 |
| `execution_date` | DATE NULL | 自由填具体执行日期（避免每行 JOIN `calendar_period`）| `project_event.event_date` 平行 |
| `fiscal_year_int` | INTEGER NULL | 从 execution_period 投影；用于 mart 过滤 | 同 S2.4 alloc |
| `lineage` | JSONB NULL | per-row R3-E provenance（同上）| 同上 |
| `execution_hash_canonical` | TEXT NULL | 同一笔执行的 stable SHA（per R12-A de-dupe；同一笔可 N 次报送修订）| `budget_hash_canonical` 平行 |
| `variance_reason` | TEXT NULL | 偏差原因（仅执行率偏离 < 0.8 或 > 1.2 填；其余 NULL）| `project_event.delay_reason` 平行 |

**不扩**：

- ❌ 不在 `budget_execution` 加 `score` / `rating` / `rank` / `total_score` 任一字段 — 红线
- ❌ 不强制 `execution_rate` 在 [0, 1] / [0, 1.5] 区间 CHECK —— 容许灾年超额执行 + 一般预算年初数=0
- ❌ 不写触发器自动从 `executed_amount / allocated_amount` 算 `execution_rate` —— mart 派生（per §3.3）
- ❌ 不在执行表加 `category` 字段（通过 JOIN alloc 拿，避免冗余 + drift）

### 2.3 单位 drift 守门（per R3-E + §10.x CC 建议）

| drift 形态 | 后果 | 落地刀应对 |
|---|---|---|
| `unit = "亿元"` vs `unit = "万元"` | mart 行对齐时数量级错乱 | `canonical_unit` 投影为 `"CNY_100M"` / `"CNY_10K"` / `"CNY"` 三档 enum-style |
| `unit = "亿元"` vs `unit = "亿元(本币)"` | 看似同单位实则口径不同 | 落地刀 seed 统一 `"亿元"`；漂移值 → `canonical_unit = "OTHER_NOTE"` |
| `unit = "RMB"` vs `unit = "CNY"` | 英文/中文标签不一致 | `*_currency_canonical` 统一 `"CNY"` |
| `unit = "亿元"` vs `unit = "千元"` | 千进制差异 | 落地刀不接受（落到 `canonical_unit` 守门）|

### 2.4 执行率口径（per docs/06 §2.5 + §10.3 平行）

| 口径 | 公式 | mart 暴露 | 备注 |
|---|---|---|---|
| **期间内执行率** | `sum(executed_amount WHERE fiscal_year=Y AND category=C) / sum(allocated_amount WHERE fiscal_year=Y AND category=C)` | `mart_budget_execution.execution_rate_period` | 主要口径；可空（年初未发生） |
| **截止当前执行率** | `sum(executed_amount WHERE fiscal_year <= Y) / sum(allocated_amount WHERE fiscal_year = Y)` | `mart_budget_execution.execution_rate_cumulative` | 派生；不写物化列 |
| **项目执行率** | per-project JOIN（per S2.3 project_event） | 后续刀（S2.4 落地刀仅 demo budget 表；不接 S2.3） | 推迟 |

**钉死**（per docs/06 §2.5 末段）：
- 分配 ≠ 执行 ≠ 完成 —— 三种语义分别记录
- 执行率**仅算术比例**；不评分（"优秀率""达标率"等不引入）
- `variance_reason` 是文字说明，非派生评分

---

## 3. dbt staging candidate 路径（per docs/19 §S1.19 + S2.3 §3 平行）

### 3.1 sources（`_stg_sources.yml`）

新增 2 条：

```yaml
sources:
  - name: cegr
    tables:
      - name: budget_allocation
        columns: [id, geo_entity_id, fiscal_year, budget_type, category,
                  allocated_amount, unit, source_id, created_at,
                  canonical_category, canonical_unit,
                  allocation_currency_canonical, budget_class,
                  fiscal_year_int, lineage, budget_hash_canonical,
                  progress_note]
      - name: budget_execution
        columns: [id, budget_allocation_id, execution_period_id,
                  executed_amount, unit, execution_rate, source_id, created_at,
                  canonical_unit, execution_currency_canonical,
                  execution_date, fiscal_year_int, lineage,
                  execution_hash_canonical, variance_reason]
```

### 3.2 staging models（per `dbt/models/staging/stg_observation.sql` 模式）

| 模型 | 备注 |
|---|---|
| `stg_budget_allocation.sql` | passthrough + JOIN geo_entity for `geo_canonical_name`；expose `is_demo` from lineage |
| `stg_budget_execution.sql` | passthrough + JOIN `stg_budget_allocation` for `budget_allocation_id`；JOIN geo_entity via alloc for `geo_canonical_name`；expose `is_demo` |

```sql
{{ config(materialized='view', tags=['staging', 'budget']) }}
```

### 3.3 mart（仿 S2.1 §3 `mart_person_tenure` + S2.3 §3.3 `mart_project_event`）

新建 `mart_budget_execution`：

```sql
{{ config(materialized='view', tags=['mart', 'budget']) }}

WITH alloc AS (
    SELECT
        a.id AS budget_allocation_id,
        a.geo_entity_id,
        a.fiscal_year,
        a.category,
        a.canonical_category,
        a.budget_class,
        a.allocated_amount,
        a.unit AS alloc_unit,
        a.canonical_unit AS alloc_canonical_unit,
        a.allocation_currency_canonical,
        a.budget_hash_canonical,
        a.progress_note,
        a.lineage AS alloc_lineage,
        g.canonical_name AS geo_canonical_name
    FROM {{ ref('stg_budget_allocation') }} a
    LEFT JOIN {{ ref('stg_geo_entity') }} g ON g.geo_entity_id = a.geo_entity_id
),
exec_ AS (
    SELECT
        e.id AS budget_execution_id,
        e.budget_allocation_id,
        e.execution_period_id,
        e.execution_date,
        e.fiscal_year_int,
        e.executed_amount,
        e.unit AS exec_unit,
        e.canonical_unit AS exec_canonical_unit,
        e.execution_currency_canonical,
        e.execution_rate,
        e.variance_reason,
        e.execution_hash_canonical,
        e.lineage AS exec_lineage
    FROM {{ ref('stg_budget_execution') }} e
)
SELECT
    exec_.budget_execution_id,
    alloc.budget_allocation_id,
    alloc.geo_entity_id,
    alloc.geo_canonical_name,
    alloc.fiscal_year,
    alloc.category,
    alloc.canonical_category,
    alloc.budget_class,
    alloc.allocated_amount,
    exec_.executed_amount,
    -- 期间内执行率 (mart 派生；不写物化列)
    CASE
        WHEN alloc.allocated_amount IS NULL OR alloc.allocated_amount = 0
            THEN NULL
        ELSE exec_.executed_amount / alloc.allocated_amount
    END AS execution_rate_period,
    exec_.execution_rate AS execution_rate_reported,
    alloc.alloc_canonical_unit AS canonical_unit,
    exec_.execution_date,
    exec_.variance_reason,
    alloc.progress_note,
    alloc.budget_hash_canonical,
    exec_.execution_hash_canonical,
    -- is_demo 双保险：alloc 与 exec 任一为 true 即 true（落地刀约定双 true）
    COALESCE(
        (alloc.alloc_lineage->>'is_demo')::boolean OR (exec_.exec_lineage->>'is_demo')::boolean,
        FALSE
    ) AS is_demo
FROM exec_
LEFT JOIN alloc ON alloc.budget_allocation_id = exec_.budget_allocation_id
```

`is_demo` 显式暴露为最后一列（per docs/33 §3.2 sentinel + S2.1/S2.2/S2.3 mart 同模式）。

### 3.4 单位 drift mart 辅助视图（落地刀可选）

```sql
-- mart_budget_unit_drift（每 alloc 一条；检查 canonical_unit 覆盖率）
CREATE OR REPLACE VIEW mart_budget_unit_drift AS
SELECT
    a.geo_entity_id,
    a.fiscal_year,
    a.category,
    a.unit AS raw_unit,
    a.canonical_unit,
    CASE
        WHEN a.canonical_unit IS NULL THEN 'DRIFT_DETECTED'
        WHEN a.unit = a.canonical_unit THEN 'OK'
        ELSE 'NORMALIZED'
    END AS drift_status
FROM stg_budget_allocation a;
```

**不评分**：仅 drift 状态枚举；不计算"单位合规率"。

---

## 4. 首批入库策略

### 4.1 来源（per `92` §1.1 R4 + 214 §SCHEMA）

| 来源 | 类型 | 红线 |
|---|---|---|
| 公开财政预决算 | 财政部门 / 人大公开报告 | **不**批量爬 2020-2025；首批 ≤N 笔 |
| 用户上传 | S2.0.2 admin_upload (Stage 1 §1.3.1) | 仅在 admin 角色提交；audit trail 写入 |
| 手工 seed | hand-curated JSON（per S1.12 + S2.1.7-a 平行） | `is_demo="true"`；不爬网 |

### 4.2 条数上限（首批 ≤N）

| alloc 数 | execution 数 | 理由 |
|---|---|---|
| ≤6 alloc | ≤18 execution | 每 alloc 平均 3 个 execution（H1/H2/年末） |
| ≤8 alloc | ≤24 execution | 含部分中途调整的执行记录 |

具体约束：

| 限制 | 上限 | 理由 |
|---|---|---|
| `budget_allocation` 总行数 | ≤8 | 演示 ≤3 个省/市 × ≤3 个类目 |
| `budget_execution` 总行数 | ≤24 | ≤8 alloc × ≤3 execution |
| `budget_hash_canonical` 唯一值 | ≤8 | ≤8 独立预算笔 |
| `geo_entity_id` 跨 alloc | ≤5 | 跨省/跨市；首批演示多 geo |
| `fiscal_year` 覆盖 | ≥2 | 演示跨年（2023 + 2024） |
| 单位 drift `canonical_unit IS NULL` | 0 | 守门 — 落地刀 100% 归一化 |
| `execution_rate` 超出 [0, 1.5] | ≤2 行 | 演示灾年超额；其余合法区间 |

### 4.3 `is_demo` 全 true（per S1.18 sentinel + S2.1 §4.3 + S2.2 §4.3 + S2.3 §4.3 平行）

| 字段 | 值 |
|---|---|
| `budget_allocation.lineage->>'is_demo'` | `"true"` |
| `budget_execution.lineage->>'is_demo'` | `"true"` |
| `source_file_sha256` | `"0"` × 64（per docs/33 §3.1） |
| `source_file_url` | `"(DEMO_SEED_NO_FILE)"` |

### 4.4 稳定 UUID（per S1.12 + S2.1 §4.4 + S2.3 §4.4 平行）

| 表 | UUID 家族 |
|---|---|
| `budget_allocation` | `a0000000-0000-0000-0000-00000000008X`（X = 0..9 + a..z）|
| `budget_execution` | `a0000000-0000-0000-0000-00000000009X`（X = 0..9 + a..z）|
| `calendar_period`（外键） | 复用既有 demo calendar_period（per S2.3 §4.4）|

### 4.5 seed 文件

- `data/seeds/budget_allocation_demo.json` + `scripts/seed_budget_allocation_demo.py`（mirror `scripts/seed_project_event_demo.py`）
- `data/seeds/budget_execution_demo.json` + `scripts/seed_budget_execution_demo.py`（mirror 同上）
- 加载顺序 `alloc → execution`（FK 依赖）

---

## 5. 与 S2.7 六段 PROCESS / OUTPUT 消费对照

### 5.1 `mart_budget_execution` → `PROCESS` 段（per docs/06 §2.4 + S2.7-a mock）

| mart 列 | EvidenceChain 段消费字段 | 备注 |
|---|---|---|
| `geo_canonical_name` | `items[].geo` | |
| `fiscal_year` | `items[].year` | |
| `category` | `items[].category` | 原始 + canonical 双显 |
| `canonical_category` | `items[].category_canonical`（**新增**）| |
| `canonical_unit` | `items[].unit` | 归一化单位 |
| `progress_note` | `items[].budget_note` | 自由文本 |
| `lineage->>'is_demo'` | items 整体加 `is_demo=true` 角标 | S1.18 sentinel |

### 5.2 `mart_budget_execution` → `OUTPUT` 段（per docs/06 §2.5）

| mart 列 | EvidenceChain 段消费字段 | 备注 |
|---|---|---|
| `execution_rate_period` | `items[].execution_rate` | 显示百分比；NULL 时显示 "—" |
| `execution_rate_reported` | `items[].execution_rate_reported` | 源站报送值（如有；可与派生值不一致 — 标注口径差异）|
| `variance_reason` | `items[].variance_note`（如偏离）| 文字说明 |
| `allocated_amount` + `executed_amount` | `items[].amount_display` | "XXX 亿元（已执行 YY%）" |

### 5.3 不接 S2.7-b（per 187 §SCHEMA 禁 + 214 §SCHEMA 禁）

本刀 S2.4（落地刀）**不接** S2.7 PROCESS/OUTPUT 段。留给 S2.7-b 协同 knife：消费 `mart_budget_execution`，写入 EvidenceChain。

### 5.4 验证（落地刀）

```bash
# 1. mart 行数 ≥1
PGPASSWORD=postgres psql -h 127.0.0.1 -p 55440 -U postgres -d cegr_test \
    -c "SELECT COUNT(*) FROM cegr_staging.mart_budget_execution WHERE is_demo = true;"
# 预期: ≥1

# 2. 执行率分布（守门 [0, 1.5]）
PGPASSWORD=postgres psql ... \
    -c "SELECT
          COUNT(*) FILTER (WHERE execution_rate_period BETWEEN 0 AND 1.5) AS in_range,
          COUNT(*) FILTER (WHERE execution_rate_period IS NULL) AS null_rate,
          COUNT(*) FILTER (WHERE execution_rate_period < 0 OR execution_rate_period > 1.5) AS out_of_range
        FROM cegr_staging.mart_budget_execution WHERE is_demo = true;"
# 预期: in_range ≥ 1；null_rate + out_of_range ≤ 2（per 4.2）

# 3. is_demo 过滤（per docs/33 §3.3 case 4）
PGPASSWORD=postgres psql ... \
    -c "SELECT COUNT(*) FROM cegr_staging.mart_budget_execution WHERE is_demo = false;"
# 预期: 0（仅 demo 数据）

# 4. 单位 drift 守门
PGPASSWORD=postgres psql ... \
    -c "SELECT COUNT(*) FROM cegr_staging.mart_budget_unit_drift WHERE drift_status = 'DRIFT_DETECTED';"
# 预期: 0（per 4.2 守门）

# 5. budget_hash_canonical de-dupe
PGPASSWORD=postgres psql ... \
    -c "SELECT COUNT(DISTINCT budget_hash_canonical) FROM cegr_staging.mart_budget_execution;"
# 预期: ≤8（per 4.2 首批约束）

# 6. 跨年覆盖
PGPASSWORD=postgres psql ... \
    -c "SELECT COUNT(DISTINCT fiscal_year) FROM cegr_staging.mart_budget_execution;"
# 预期: ≥2（per 4.2）
```

---

## 6. 验收清单

| # | 项 | 落地刀验证方式 |
|---|---|---|
| 1 | `budget_allocation` 表 + docs/39 §2.1 新增列齐全 | `\d cegr.budget_allocation` |
| 2 | `budget_execution` 表 + docs/39 §2.2 新增列齐全 | `\d cegr.budget_execution` |
| 3 | 既有 FK（alloc→geo_entity, execution→alloc, execution→calendar_period）保留 | `\d` 引用列表 |
| 4 | dbt run `--select stg_budget_allocation+ mart_budget_execution` exit 0；2 stg + 1 mart + 1 drift view 创建 | dbt run log |
| 5 | mart 行数 = execution 行数（is_demo=true 过滤后）| SQL COUNT |
| 6 | 执行率分布 in_range ≥ 1（per §5.4 #2）| SQL GROUP BY |
| 7 | 单位 drift `DRIFT_DETECTED` 数 = 0 | SQL COUNT |
| 8 | `budget_hash_canonical` 唯一值 ≤8（per §4.2）| SQL COUNT DISTINCT |
| 9 | `fiscal_year` 跨年覆盖 ≥2（per §4.2）| SQL COUNT DISTINCT |
| 10 | 既有 55 schema_negative 测试仍绿（含 s21lite 5 + s22lite 5 + s23lite 8 + others）| pytest tests/ -q |
| 11 | 新增 pytest `tests/test_budget_s24lite.py` ≥5 cases 全过 | pytest -v |
| 12 | pack invariant 535 → 535+N | JSON 解析守门 |
| 13 | smoke-check 仍 PASS（无 frontend 改动）| python3 frontend/smoke-check.py |
| 14 | 既有 S2.7-a2 + S2.1-lite + S2.2-lite + S2.3-lite 套件仍绿 | pytest tests/test_evidence_chain_s27a.py tests/test_person_tenure_s21lite.py tests/test_policy_commitment_s22lite.py tests/test_project_event_s23lite.py |

---

## 7. 关键风险与回滚

| 风险 | 触发条件 | 回滚策略 |
|---|---|---|
| `budget_allocation` 与 `budget_execution` 同名单位 drift | alloc 用 "亿元" / execution 用 "万元" | mart `canonical_unit` 守门；demo 数据 100% 归一化 |
| 执行率 > 1.5 或 < 0 引发评审质疑 | 灾年/调整数据 | 不强制 CHECK；mart 派生 NULL 兜底；`variance_reason` 文字标注 |
| `execution_period_id` 跨年未对齐 | 财年与日历期间错位 | `fiscal_year_int` 投影；mart WHERE 显式过滤 |
| `budget_hash_canonical` 全 NULL（首批不生成）| de-dupe 失效 | 落地刀 §4.4 稳定 UUID 钉死 8 笔；不允许 NULL |
| 同 alloc 多 execution 共享 `budget_hash_canonical`（per R12-A）| 跨表外键 | 不加 FK（hash 而非 UUID 引用）；应用层守门 |
| 现有 01-core.sql `unit TEXT NOT NULL` 与新增 `canonical_unit TEXT NULL` 字段冗余 | 视觉冲突 | 落地刀不修改既有 `unit`；`canonical_unit` 为归一化投影 |
| `execution_rate_reported` 与派生 `execution_rate_period` 不一致 | 源站报送口径 ≠ mart 派生 | 双显：reported 反映原始来源；period 反映 mart 派生 — UI 标注口径差异（不评分）|

---

## 8. 不做什么（本刀 S2.4 边界；推后续刀）

| ❌ | 推到 |
|---|---|
| ❌ 写生产 migration 011（**仅规划**）| S2.4 落地刀（tasking 216+）|
| ❌ dbt stg_budget_* + mart_budget_execution + mart_budget_unit_drift | S2.4 落地刀 |
| ❌ 首批 ≤8 alloc + ≤24 execution 真实 seed | S2.4 落地刀（**严禁爬网**）|
| ❌ 接 S2.7-b PROCESS/OUTPUT 段消费 | S2.7-b 协同刀 |
| ❌ S2.1 person 全量（用户 D 缩刀）| 后续刀待用户裁定 |
| ❌ `policy_commitment` ↔ `budget_allocation` FK 启用 | 后续刀（per Cursor 裁定）|
| ❌ `inference_record`（S2.5）| S2.5 |
| ❌ `claim_evidence_link`（S2.5 末段）| S2.5 |
| ❌ 执行率评分（"达标率""优秀率"）| 红线 |
| ❌ `score` / `rating` / `rank` / `total_score` / `execution_score` 任一字段 | 红线 |
| ❌ 修改 `gate_thresholds.json` | spike-04 评测构件，只读 |
| ❌ 批量爬 2020-2025 财政预决算 | 红线 |
| ❌ 启用 pgvector / RLS / partition | Stage 2 边界（per docs/04 §6）|
| ❌ 修改 `00-CC-CURRENT.md` | Cursor 拥有 |

---

## 9. 与现有文档的关系

| 引用 | 用途 |
|---|---|
| `docs/04-data-model.md` §2 ERD | `budget_allocation` ↔ `budget_execution` 关系 |
| `docs/04-data-model.md` §6 | Stage 0 边界（不扩 pgvector / RLS / partition）|
| `docs/06-governance-observation-method.md` §2.4 | PROCESS 段（预算分配节点） |
| `docs/06-governance-observation-method.md` §2.5 | OUTPUT 段（预算执行 + 执行率） |
| `docs/06-governance-observation-method.md` §2.5 末段 | "分配≠执行≠完成" 钉死 |
| `docs/19-stage1-s19-dbt-staging-plan-20260825.md` | dbt staging 模式 |
| `docs/33-stage1-s18-demo-sha-lock-plan-20260825.md` §3.1 / §3.3 | `is_demo` sentinel + 评测基线 |
| `docs/34-stage2-s20-kickoff-plan-20260825.md` §4 序 8 | S2.4 范围 + budget 排位 |
| `docs/36-stage2-s21-person-tenure-plan-20260825.md` | S2.1 平行规划（命名 / lineage）|
| `docs/37-stage2-s22-policy-plan-20260825.md` | S2.2 平行规划（unit drift 守门经验）|
| `docs/38-stage2-s23-project-plan-20260825.md` | S2.3 平行规划（hash_canonical + 五态机类比）|
| `schema/01-core.sql` §804-828 | 既有 `budget_allocation` + `budget_execution` 表 |

---

## 10. CC 建议（供 Cursor 审阅 / 用户裁定）

### 10.1 `budget_class` 落 strategy（per docs/04 §2 + §10.x 平行）

| 选项 | 描述 | 选 |
|---|---|---|
| A | enum-style TEXT（per docs/38 §10.2 平行）| **推荐** |
| B | schema-level CHECK + ENUM type | 加固；migration 011 复杂度↑ |

### 10.2 `canonical_unit` 归一化档位

| 选项 | 描述 | 选 |
|---|---|---|
| A | 三档 enum-style: `CNY_100M` / `CNY_10K` / `CNY`（per docs/37 §10.x 类目归一）| **推荐** |
| B | 任意字符串 + drift view 守门 | 灵活；但 seed 难对齐 |

### 10.3 `budget_hash_canonical` 共享策略

| 选项 | 描述 | 选 |
|---|---|---|
|---|---|---|
| A | 同一笔预算跨 execution 共享一个 hash（per R12-A de-dupe）| **推荐**（与 S2.3 `project_hash_canonical` 平行）|
| B | 每 execution 独立 hash | 失去跨执行追踪能力 |

### 10.4 执行率派生 vs 报送双显

| 选项 | 描述 | 选 |
|---|---|---|
| A | mart 同时暴露 `execution_rate_period`（派生）+ `execution_rate_reported`（报送）| **推荐**（per §5.2）|
| B | 仅暴露派生；报送值丢弃 | 丢失源站原始口径 |

### 10.5 `variance_reason` 必填性

| 选项 | 描述 | 选 |
|---|---|---|
| A | nullable TEXT（仅偏离 [0, 0.8] ∪ [1.2, ∞] 填；其余 NULL）| **推荐**（per S2.3 `delay_reason` 平行）|
| B | required NOT NULL DEFAULT 'NONE' | 加固；但 NULL 是"未偏离"更清晰的语义 |

### 10.6 单位 drift 暴露策略

| 选项 | 描述 | 选 |
|---|---|---|
| A | mart 派生 `mart_budget_unit_drift` view（per §3.4）| **推荐** |
| B | 不暴露；触发器强制 `canonical_unit IS NOT NULL` | 加固；但偏离当前"加列"节奏（per 缩刀 D）|

---

— End of `docs/39` —

> 等待 Cursor 审验（预期 `217-stage0-cursor-s24-plan-audit-…md`）。
> 通过后下发落地任务（`218-stage2-s24-budget-impl-tasking-…md`），进入 S2.4 实施。
> S2.1-full 与 S2.2-dbt/seed 与 S2.3 落地可**并行**（不同 schema 域）；等 Cursor 裁定。