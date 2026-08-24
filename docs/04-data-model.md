# 04 — 数据模型与实体关系（Data Model & ER Design）

> Stage 0 交付物 #04；对应 PRD 第 15 章第 5 项 + 第 5 章。
> 完整 DDL 见 `schema/01-core.sql`；本文档说明**设计理由**与**关键约束**。
> **R3 更新（2026-08-23）**：observation 自然键已移除 `status`（schema/01-core.sql:470-474）；
> 状态变更只能走 observation_revision（append-only），禁止直接 UPDATE。
> DB 测试：tests/test_schema_negative.py 39/39 通过（PG16 + PG17 验证）。
> F-2 已落地：source_document.source_registry_id UUID NOT NULL（schema/01-core.sql:314），测试 test_source_document_null_registry_rejected。

## 1. 核心原则

1. **原始资料不可变**：抓到的 `source_document` 文件（HTML/PDF/Excel）入库后只读
2. **观测值不删除**：错值通过 `observation_revision` 追加，原始值保留
3. **每个事实点带出处**：`observation.source_id` + `source_location_id` 必填
4. **行政区划时变**：`geo_code_version` 用时段约束防重叠
5. **方法版本化**：统计口径变化写 `indicator_methodology_version`，不直接改 `indicator_definition`

## 2. 实体关系总览

```
                    ┌─────────────────────┐
                    │  source_registry    │ (S0-S4 等级 + 启用开关)
                    │  source_document    │ (原始文件 + SHA-256)
                    │  source_location    │ (sheet/page/cell/段落定位)
                    │  ingestion_run      │ (每次抓取运行)
                    └─────────────────────┘
                              │
                              ▼
┌─────────────┐       ┌──────────────────┐       ┌──────────────────┐
│geo_entity   │◀──────│   observation    │──────▶│indicator_       │
│geo_code_    │       │                  │       │definition       │
│version      │       │                  │       │indicator_       │
│boundary_    │       │  (事实记录)       │       │methodology_     │
│change_event │       │                  │       │version          │
└─────────────┘       └──────────────────┘       └──────────────────┘
                              │                            │
                              ▼                            │
                  ┌──────────────────────┐                 │
                  │ observation_revision │ (append-only)   │
                  │ observation_quality_ │                 │
                  │ flag                 │                 │
                  └──────────────────────┘                 │
                                                           │
                                                           ▼
                                                  ┌────────────────┐
                                                  │calendar_period │
                                                  └────────────────┘

┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   person    │◀────────│   tenure    │────────▶│  position   │
│   alias     │         │  任期表     │         │  职位定义   │
└─────────────┘         └─────────────┘         └─────────────┘
       │                     │
       ▼                     ▼
┌─────────────┐         ┌─────────────────────┐
│person_      │         │appointment_event    │
│source_      │         │(任免事件)           │
│evidence     │         └─────────────────────┘
└─────────────┘

┌──────────────────┐    ┌────────────────────┐    ┌──────────────────┐
│policy_document   │───▶│policy_target       │───▶│government_       │
│(政策文件)        │    │policy_measure      │    │commitment        │
└──────────────────┘    └────────────────────┘    └──────────────────┘
                                                          │
                                                          ▼
                                                ┌────────────────────┐
                                                │commitment_progress │
                                                └────────────────────┘

┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│project_event     │    │budget_allocation │───▶│budget_execution   │
│(五态机)          │    │                  │    │                  │
└──────────────────┘    └──────────────────┘    └──────────────────┘

┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│research_question │───▶│ analysis_run     │───▶│model_specification│
│                  │    │                  │    │comparison_group   │
└──────────────────┘    └──────────────────┘    └──────────────────┘
                              │
                              ▼
              ┌────────────────────────────────────┐
              │inference_record / derived_metric  │
              │uncertainty_record / research_note  │
              │claim_evidence_link (正反证据)      │
              └────────────────────────────────────┘
```

## 3. 关键设计决策（per Spike 验证）

### 3.1 `observation` 的"严格事实"语义

```sql
CREATE TABLE observation (
    ...
    value NUMERIC,                    -- 可空；per PRD 9.4 缺失不补零
    is_imputed BOOLEAN DEFAULT FALSE,  -- 是否填补
    missing_reason TEXT,               -- 缺失原因
    ...
);
```

**决策**：
- `value` 可为 NULL（per PRD 9.4；"…"抑制数据写 NULL + 缺失原因）
- 区分 `is_imputed`（填补，如线性插值）与真缺失
- `missing_reason` 写明为什么缺（"未发布"/"OCR 失败"/"源数据缺失"等）

**Spike 验证依据**：
- Spike 1：stats.gov.cn zxfb 双行表头中"…" = 抑制，写 NULL
- Spike 3：公报中"…略" 章节跳过写 NULL

### 3.2 `source_location` 多形态定位

```sql
CREATE TABLE source_location (
    sheet_name TEXT,          -- Excel
    page_number INTEGER,      -- PDF
    table_index INTEGER,      -- 表序
    cell_range TEXT,          -- "B5:D15"
    bbox JSONB,               -- {x,y,w,h,page} 扫描 PDF
    section_heading TEXT,     -- "一、综合"
    paragraph_index INTEGER,  -- HTML 段落
    context_quote TEXT,       -- ≤200 字上下文
    ...
);
```

**决策**：
- 不用单一字段；用**多形态字段** + 任一非空即可定位
- `context_quote` 长度约束 5-200 字（per Spike 3：防过短缺上下文、防过长截断）
- `bbox` 用 JSONB 而非 GEOMETRY，因为坐标系统可能多样

**Spike 验证依据**：
- Spike 1：双行表头 → `cell_range` 必须含列组说明（如 "B3:D15, header_group=GDP_growth"）
- Spike 3：散文 → `section_heading` + `paragraph_index` 必填

### 3.3 `geo_code_version` 时段约束

```sql
CREATE TABLE geo_code_version (
    ...
    EXCLUDE USING gist (
        geo_entity_id WITH =,
        tstzrange(valid_from, COALESCE(valid_to, '9999-12-31'::date)) WITH &&
    )
);
```

**决策**：
- PostgreSQL `EXCLUDE USING gist` 约束：同一 `geo_entity_id` 不能有重叠时段
- `valid_to` 可为 NULL（= 至今有效）
- 边界变化通过 `boundary_change_event` 触发新版本插入

**为什么用 EXCLUDE 而非 trigger**：
- 数据库原生保证，无需应用层触发器
- Gist 索引自动支持，查询时也可利用
- 性能影响小（每 entity 平均 5-10 个版本）

**对应 PRD 12.2 R02**。

### 3.4 `observation_revision` 追加而非覆盖

```sql
CREATE TABLE observation_revision (
    ...
    revision_no INTEGER NOT NULL,
    value NUMERIC,
    status observation_status NOT NULL,  -- PRELIMINARY/REVISED/FINAL
    ...
);
```

**决策**：
- 修订值是**新行**，不是 UPDATE
- 同一 `observation_id` 可以有多条 revision_no
- 当前最新值由 `observation` 表记录（冗余但便于查询）
- 三态机：PRELIMINARY（初值）→ REVISED（修订）→ FINAL（终值）

**对应 PRD 12.1 R01**（统计口径变化溯源）。

### 3.5 `indicator_methodology_version` 独立

```sql
CREATE TABLE indicator_methodology_version (
    ...
    EXCLUDE USING gist (
        indicator_id WITH =,
        tstzrange(valid_from, COALESCE(valid_to, '9999-12-31'::date)) WITH &&
    )
);
```

**决策**：
- 与 `geo_code_version` 同样的时段约束
- 同一指标（如"GDP"）可能有多次口径修订
- `change_summary` 写明变化内容
- `impact_note` 写明是否回溯调整（"2010-2015 数据已回溯"）

**业务例子**：
- 2017 年行业分类修订（GB/T 4754-2017）→ 旧分类 observation 仍可查，但 UI 上提示口径
- 第五次经济普查（2023）发布后 → GDP 历史值全面修订；新旧值都保留

### 3.6 `tenure` 重叠合法

```sql
CREATE TABLE tenure (
    ...
    start_date DATE NOT NULL,
    end_date DATE,  -- NULL = 在任
    ...
);
```

**决策**：
- 不加 `EXCLUDE` 约束（与 geo/indicator 不同）
- 允许同一时期同一地区多个职位（书记+省长+人大常委会主任）
- 重叠任期是常态，不是异常

**对应 PRD 6.5.1**（多职位记录）。

### 3.7 `government_commitment` 可验证门槛

```sql
CREATE TABLE government_commitment (
    ...
    target_indicator_id UUID,    -- 关联指标
    target_value NUMERIC,        -- 目标值
    target_unit TEXT,
    target_year INTEGER,
    measurable BOOLEAN DEFAULT TRUE,
    ...
);
```

**决策**：
- 不允许"努力做好"式承诺入库
- 必须有：可量化目标 / 关联指标 / 时点
- 抽象口号写在 `policy_document.summary` 但**不入 commitment 表**

**对应 PRD 6.2 关键约束**（per doc 06 第 2.2 节）。

### 3.8 `project_event` 五态机

```sql
CREATE TYPE project_status AS ENUM (
    'ANNOUNCED', 'SIGNED', 'STARTED', 'PRODUCING', 'AT_CAPACITY'
);
```

**决策**：
- 五态独立记录（append-only）
- 同一项目可以有多条记录（"签约"和"开工"是两条 event）
- 不合并成单一 `project` 表 + 当前状态字段
- **为什么**：状态变化需要时序溯源

**对应 PRD 12.7 R07**（活动 vs 产出 vs 结果）。

### 3.9 `claim_evidence_link` 正反证据都记录

```sql
CREATE TABLE claim_evidence_link (
    ...
    polarity TEXT NOT NULL,  -- 'SUPPORTS' / 'CONTRADICTS'
    ...
);
```

**决策**：
- 每条主张（claim）不仅关联支持证据，也关联反对证据
- 防 PRD 12.10 R10（确认偏差）
- 评审 Gate 3 检查"是否有反例被忽略"

### 3.10 `policy_document.full_text_tsv` 全文检索

```sql
CREATE TABLE policy_document (
    ...
    full_text_tSVECTOR,  -- tsvector
);
CREATE TRIGGER policy_doc_tsv ...
```

**决策**：
- 政策文件必须可全文检索（per PRD 9.5）
- tsvector 由 trigger 自动维护
- 用 `simple` 配置（中文 jieba 字典 Stage 2 再加）

## 4. 视图（常用查询）

### 4.1 `v_observation_with_evidence`

```sql
CREATE OR REPLACE VIEW v_observation_with_evidence AS
SELECT o.id, i.canonical_name AS indicator, g.canonical_name AS geo,
       gv.admin_code, cp.period_label AS period,
       o.value, o.unit, o.status, o.value_type,
       s.title AS source_title, s.url AS source_url,
       s.file_hash_sha256 AS source_hash,
       o.confidence, o.is_imputed
FROM observation o
JOIN indicator_definition i ON i.id = o.indicator_id
JOIN geo_entity g ON g.id = o.geo_entity_id
JOIN geo_code_version gv ON gv.id = o.geo_code_version_id
JOIN calendar_period cp ON cp.id = o.calendar_period_id
JOIN source_document s ON s.id = o.source_id;
```

**用途**：每行直接看到 source + hash + period，支持一键回放。

## 5. 索引策略

| 表 | 主索引 | 次索引 |
|---|---|---|
| `observation` | `(indicator_id, geo_entity_id, calendar_period_id, status, geo_code_version_id) UNIQUE` | status / confidence / extracted_at |
| `geo_entity` | id PK | (canonical_name), (level), (parent_id) |
| `indicator_definition` | id PK | (short_code UNIQUE), (canonical_name) |
| `policy_document` | id PK | (doc_type), (publication_date), full_text_tsv GIN |
| `tenure` | id PK | (person_id), (position_id), (start_date, end_date) |
| `commitment` | id PK | (geo_entity_id), (status), (due_date) |

## 6. 不做什么（Stage 0 边界）

- ❌ 不启用 pgvector（Stage 4 评估后决定）
- ❌ 不实施 RLS（行级安全，Stage 2 多用户场景再加）
- ❌ 不做 partition（数据量 <1M 行时不必要）
- ❌ 不写 ETL 迁移脚本（schema/migrations/ Stage 1）
- ❌ 不实现全文检索 jieba 字典（先用 `simple`）

## 7. Stage 0 spike 验证后 schema 调整（增量）

> 此节记录 spike 期间发现的 schema 调整。每条都有 spike 证据。

### 7.1 `source_document.caveat_text` — 关键解析说明（来自 Spike 2）

**问题**：湖北 2026 年 6 月月报标题写"1-6月"，实际 GDP/收入数据是 Q2 单季（脚注说明）。如果不提取脚注，**整批数据全错**。

**调整**：
```sql
ALTER TABLE source_document ADD COLUMN caveat_text TEXT;
CREATE INDEX idx_source_doc_caveat ON source_document (caveat_text) WHERE caveat_text IS NOT NULL;
```

**配套**：
- 连接器必须**强制提取脚注**（`.notes` / `[Content_Types].xml` 等隐藏区域）
- 该文档下所有 observation 建议写 `observation_quality_flag` 提示"标题 vs 数据不一致"
- UI 显示该文档时弹 warning

**对应 PRD 12.3 R03**（地方数据缺失和不一致）。

### 7.2 `observation.unit` 改为可空 — 容纳 rate-only 行（来自 Spike 2）

**问题**：省 xlsx 一些行只有增速（如"5.2%"）无明确单位；过去 `unit TEXT NOT NULL` 会强制写单位导致混乱。

**调整**：
```sql
ALTER TABLE observation ALTER COLUMN unit DROP NOT NULL;
```

**业务语义**：
- `unit IS NULL` + `comparison_basis='YOY_RATE'` → 增长率 observation（值已含 % 意义）
- `unit='%'` → 百分比（percent，如 5.2 表示 5.2%）
- `unit='ppt'` → 百分点（percentage point，如利率上调 0.25 个百分点）
- `unit='元/人'`、`unit='亿元'` → 标准单位

**对应 PRD 9.4 缺失值处理**（unit 也可"缺失"）。

### 7.3 `comparison_basis` 扩展值（来自 Spike 2）

新增枚举值：
- schema `comparison_basis` 已移除 `Q2_ONLY`（`schema/01-core.sql:94`）；spike 02 改为 per-indicator 周期元数据（`CUMULATIVE_5MONTH` / `PERIOD_END_OF_MONTH` 等，`TestR3PeriodMetadata`），不再强制单一 Q2 口径。
- `H1_ACCUMULATED` — 真正的半年累计
- `CUMULATIVE` — 累计口径
- `INSTANTANEOUS` — 时点指标（如人口、库存）
- 原有：`NOMINAL`/`REAL`/`CHAIN`

## 7. 与其他文档的关系

- 完整 DDL：`schema/01-core.sql`
- 指标口径方法：`docs/05-indicator-methodology.md`
- 来源登记：`docs/03-source-registry.md`
- 治理观察方法：`docs/06-governance-observation-method.md`（与 `tenure` / `commitment_progress` / `inference_record` 直接相关）
- 验收测试：`docs/10-acceptance-tests.md`（2.7 区划有效期、2.6 修订值冲突）
- 风险登记：`docs/09-risk-register.md`（R01-R21）