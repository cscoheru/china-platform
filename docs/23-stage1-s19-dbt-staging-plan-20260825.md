# S1.9 — dbt Staging 模型层规划

- 编号：`23-stage1-s19-dbt-staging-plan-20260825`
- 前置：`69` 任务书；`68` S1.8 通过；`docs/08` §2.1 S1.9
- 日期：2026-08-25
- 状态：**规划** — 实现另开任务书

---

## §0 TL;DR

在已有 `cegr` schema 四张核心表（`source_registry` / `source_document` / `ingestion_run` / `observation`）之上，引入 dbt 构建 **5 张 staging view + 2 张 intermediate model**，为 S1.10 FastAPI 查询层 + S1.11 数据契约提供清洁的下游消费接口。

**本刀不做**：全量历史入库、Gate 1 PASS、DSH、批量爬取、降 OCR。
**可基于**：已有 4 个 connector 的试点数据 + 空表诚实。

---

## §1 目录

| 节 | 内容 |
|---|---|
| §0 | TL;DR |
| §1 | 目录 |
| §2 | dbt 项目初始化 |
| §3 | Staging 模型设计 (5 张) |
| §4 | Intermediate 模型设计 (2 张) |
| §5 | dbt tests 设计 |
| §6 | 依赖 + 消费方 |
| §7 | 红线 |
| §8 | 已知遗留 |
| §9 | 引用 |

---

## §2 dbt 项目初始化

### §2.1 目录结构

```
china-platform/
├── dbt/                          # dbt project root
│   ├── dbt_project.yml
│   ├── profiles.yml              # 不入 git；.gitignore 排除
│   ├── profiles.yml.example      # 入 git；模板
│   ├── models/
│   │   ├── staging/
│   │   │   ├── _stg_sources.yml  # source freshness config
│   │   │   ├── stg_source_registry.sql
│   │   │   ├── stg_ingestion_run.sql
│   │   │   ├── stg_source_document.sql
│   │   │   ├── stg_observation.sql
│   │   │   └── stg_observation_quality.sql
│   │   └── intermediate/
│   │       ├── int_indicator_timeseries.sql
│   │       └── int_source_coverage.sql
│   ├── tests/
│   │   └── generic/              # custom dbt tests
│   ├── macros/
│   │   └── generate_schema_name.sql
│   └── seeds/                    # 可选: 参考数据 (geo_entity, indicator_definition)
├── backend/
│   ├── sql/                      # 现有 DDL (不变)
│   └── src/                      # 现有 connector 代码 (不变)
└── ...
```

### §2.2 profiles.yml 设计

```yaml
cegr:
  target: dev
  outputs:
    dev:
      type: postgres
      host: "{{ env_var('CEGR_DB_HOST', '127.0.0.1') }}"
      port: "{{ env_var('CEGR_DB_PORT', '55440') | int }}"
      user: "{{ env_var('CEGR_DB_USER', 'postgres') }}"
      pass: "{{ env_var('CEGR_DB_PASS', 'postgres') }}"
      dbname: "{{ env_var('CEGR_DB_NAME', 'cegr_test') }}"
      schema: cegr_staging          # dbt 输出 schema (隔离)
      threads: 4
    prod:
      type: postgres
      host: "{{ env_var('CEGR_DB_HOST') }}"
      port: "{{ env_var('CEGR_DB_PORT') | int }}"
      user: "{{ env_var('CEGR_DB_USER') }}"
      pass: "{{ env_var('CEGR_DB_PASS') }}"
      dbname: "{{ env_var('CEGR_DB_NAME') }}"
      schema: cegr_staging
      threads: 2
```

**决策**：
- 输出 schema = `cegr_staging`（与 `cegr` 原始表隔离；不污染源数据）
- 所有连接参数走环境变量（禁止硬编码密码）
- dev target 默认连 `cegr_test`（试点数据）
- `profiles.yml` 入 `.gitignore`；`profiles.yml.example` 入 git

### §2.3 dbt_project.yml 要点

```yaml
name: 'cegr'
version: '0.1.0'
config-version: 2
profile: 'cegr'

model-paths: ["models"]
test-paths: ["tests"]
seed-paths: ["seeds"]
macro-paths: ["macros"]

target-path: "target"
clean-targets: ["target", "dbt_packages"]

models:
  cegr:
    staging:
      +materialized: view           # staging 全部 materialized=view
      +schema: staging              # → cegr_staging schema
    intermediate:
      +materialized: view
      +schema: staging
```

**决策**：
- staging + intermediate 全部 `materialized: view`（不做 table/incremental；本刀不批量入库）
- 后续若数据量增长，intermediate 可切 incremental（本刀不做）

### §2.4 packages

```yaml
packages:
  - package: dbt-labs/dbt_utils
    version: "1.1.1"
```

仅引入 `dbt_utils`（`surrogate_key` / `star` / `pivot` 等）。本刀不引入 `codegen` / `audit_helper`。

---

## §3 Staging 模型设计 (5 张)

### §3.1 `stg_source_registry`

**来源**：`cegr.source_registry`
**职责**：清洁 source_registry，标准化字段名，过滤 disabled sources

```sql
SELECT
    id                          AS source_id,
    domain,
    organization,
    category,
    primary_url,
    access_method,
    source_level,
    declared_source_level,
    update_frequency,
    enabled,
    file_hash_sha256,
    created_at,
    updated_at
FROM {{ source('cegr', 'source_registry') }}
WHERE enabled = TRUE
```

**字段映射**：`id → source_id`（与下游 observation.source_id 语义对齐）

### §3.2 `stg_ingestion_run`

**来源**：`cegr.ingestion_run`
**职责**：清洗 ingestion_run + 计算 duration + 标准化 status

```sql
SELECT
    ir.id                       AS run_id,
    ir.source_registry_id       AS source_id,
    sr.domain,
    sr.category,
    ir.status,
    ir.started_at,
    ir.finished_at,
    CASE
        WHEN ir.finished_at IS NOT NULL
        THEN EXTRACT(EPOCH FROM (ir.finished_at - ir.started_at))
        ELSE NULL
    END                         AS duration_seconds,
    ir.records_extracted,
    ir.records_inserted,
    ir.records_updated,
    CASE
        WHEN ir.records_extracted > 0
        THEN ROUND((ir.records_inserted::numeric / ir.records_extracted) * 100, 1)
        ELSE NULL
    END                         AS insertion_pct,
    ir.error_log,
    ir.triggered_by,
    CASE
        WHEN ir.status = 'RUNNING' AND ir.finished_at IS NULL
             AND ir.started_at < NOW() - INTERVAL '6 hours'
        THEN TRUE
        ELSE FALSE
    END                         AS is_stale
FROM {{ source('cegr', 'ingestion_run') }} ir
JOIN {{ source('cegr', 'source_registry') }} sr
    ON ir.source_registry_id = sr.id
```

**字段**：
- `duration_seconds`：计算列（finished - started）
- `insertion_pct`：inserted / extracted * 100
- `is_stale`：stale RUNNING 标志（与 S1.8 IngestMonitor 对齐）

### §3.3 `stg_source_document`

**来源**：`cegr.source_document`
**职责**：清洗 source_document + JOIN registry 元数据 + 标准化 verification

```sql
SELECT
    sd.id                       AS document_id,
    sd.source_registry_id       AS source_id,
    sr.domain,
    sr.category,
    sd.source_level,
    sd.declared_source_level,
    sd.verification_status,
    sd.title,
    sd.publisher,
    sd.publication_date,
    sd.url,
    sd.file_path,
    sd.file_hash_sha256,
    sd.file_format,
    sd.file_size_bytes,
    sd.language,
    sd.extraction_method,
    sd.caveat_text,
    sd.created_at
FROM {{ source('cegr', 'source_document') }} sd
JOIN {{ source('cegr', 'source_registry') }} sr
    ON sd.source_registry_id = sr.id
```

### §3.4 `stg_observation`

**来源**：`cegr.observation`
**职责**：清洗 observation + FK 解析 + period 标准化

```sql
SELECT
    o.id                        AS observation_id,
    o.indicator_id,
    o.geo_entity_id,
    o.calendar_period_id,
    o.value,
    o.raw_value,
    o.unit,
    o.is_imputed,
    o.missing_reason,
    o.value_type,
    o.status,
    o.comparison_basis,
    o.source_id,
    o.ingestion_run_id,
    o.extraction_method,
    o.confidence,
    -- Migration 004 columns
    o.period_start,
    o.period_end,
    o.period_label,
    o.period_type,
    o.lineage,
    o.caveat_text,
    -- Period standardization
    CASE
        WHEN o.period_type = 'CUMULATIVE_HALF_YEAR'
        THEN o.period_start
        ELSE o.period_start
    END                         AS effective_period_start,
    o.extracted_at
FROM {{ source('cegr', 'observation') }} o
WHERE o.value_type = 'FACT'     -- 只取 FACT；DERIVED/INFERENCE 另处理
```

**决策**：
- 仅取 `value_type = 'FACT'`（`information_layer` 枚举）
- DERIVED / INFERENCE / JUDGMENT 留待 intermediate 层处理（本刀不做）
- `effective_period_start`：为后续 CUMULATIVE 类型做 period 对齐（本刀简化，直接透传）

### §3.5 `stg_observation_quality`

**来源**：`cegr.observation`
**职责**：逐行数据质量标记（为 dbt tests + data contracts 提供输入）

```sql
SELECT
    o.id                        AS observation_id,
    o.source_id,
    o.ingestion_run_id,
    o.value,
    o.missing_reason,
    o.confidence,
    o.extraction_method,
    o.value_type,
    -- Quality flags
    CASE
        WHEN o.value IS NULL AND o.missing_reason IS NOT NULL
        THEN TRUE
        ELSE FALSE
    END                         AS is_missing_with_reason,
    CASE
        WHEN o.confidence IS NOT NULL AND o.confidence < 0.5
        THEN TRUE
        ELSE FALSE
    END                         AS is_low_confidence,
    CASE
        WHEN o.is_imputed = TRUE
        THEN TRUE
        ELSE FALSE
    END                         AS is_imputed_flag,
    CASE
        WHEN o.lineage IS NOT NULL
              AND o.lineage ? 'source_file_sha256'
        THEN TRUE
        ELSE FALSE
    END                         AS has_provenance,
    CASE
        WHEN o.caveat_text IS NOT NULL AND o.caveat_text != ''
        THEN TRUE
        ELSE FALSE
    END                         AS has_caveat,
    -- Composite quality score (0-1)
    ROUND(
        (CASE WHEN o.value IS NOT NULL THEN 0.3 ELSE 0 END
         + CASE WHEN o.confidence >= 0.8 THEN 0.2
                WHEN o.confidence >= 0.5 THEN 0.1
                ELSE 0 END
         + CASE WHEN o.lineage IS NOT NULL THEN 0.2 ELSE 0 END
         + CASE WHEN o.source_id IS NOT NULL THEN 0.2 ELSE 0 END
         + CASE WHEN o.extraction_method IS NOT NULL THEN 0.1 ELSE 0 END
        )::numeric, 2
    )                           AS quality_score
FROM {{ source('cegr', 'observation') }} o
```

**quality_score 组成**（0–1）：
- 0.3: value 非空
- 0.2: confidence ≥ 0.8（0.1 if ≥ 0.5）
- 0.2: lineage JSONB 存在
- 0.2: source_id 非空（FK 完整）
- 0.1: extraction_method 非空

---

## §4 Intermediate 模型设计 (2 张)

### §4.1 `int_indicator_timeseries`

**来源**：`stg_observation` + `stg_source_document`
**职责**：按 indicator + geo + period 聚合时间序列（为 FastAPI 查询层提供预聚合视图）

```sql
SELECT
    o.indicator_id,
    o.geo_entity_id,
    o.period_start,
    o.period_end,
    o.period_type,
    o.value,
    o.unit,
    o.status,
    o.comparison_basis,
    sd.domain                   AS source_domain,
    sd.category                 AS source_category,
    sd.source_level,
    sd.verification_status,
    o.extraction_method,
    o.confidence,
    o.quality_score,
    o.extracted_at
FROM {{ ref('stg_observation') }} o
JOIN {{ ref('stg_source_document') }} sd
    ON o.source_id = sd.document_id
WHERE o.value IS NOT NULL       -- 只取有值的行（missing 另处理）
ORDER BY o.indicator_id, o.geo_entity_id, o.period_start
```

**用途**：回答 Gate 1 的 "近5年江苏GDP增长趋势" 类研究问题。

### §4.2 `int_source_coverage`

**来源**：`stg_source_registry` + `stg_ingestion_run` + `stg_observation_quality`
**职责**：按 source 聚合覆盖率指标（为 S1.11 data contracts 提供输入）

```sql
SELECT
    sr.source_id,
    sr.domain,
    sr.category,
    sr.source_level,
    -- Ingestion stats
    COUNT(DISTINCT ir.run_id)   AS total_runs,
    COUNT(DISTINCT ir.run_id) FILTER (WHERE ir.status = 'SUCCESS')
                                AS success_runs,
    COUNT(DISTINCT ir.run_id) FILTER (WHERE ir.status IN ('PARTIAL', 'FAILED'))
                                AS failure_runs,
    CASE
        WHEN COUNT(DISTINCT ir.run_id) > 0
        THEN ROUND(
            COUNT(DISTINCT ir.run_id) FILTER (WHERE ir.status IN ('PARTIAL', 'FAILED'))::numeric
            / COUNT(DISTINCT ir.run_id), 3)
        ELSE 0.0
    END                         AS failure_rate,
    -- Observation stats
    SUM(ir.records_extracted)   AS total_extracted,
    SUM(ir.records_inserted)    AS total_inserted,
    CASE
        WHEN SUM(ir.records_extracted) > 0
        THEN ROUND((SUM(ir.records_inserted)::numeric / SUM(ir.records_extracted)) * 100, 1)
        ELSE NULL
    END                         AS overall_insertion_pct,
    -- Quality stats
    oq.avg_quality_score,
    oq.low_confidence_count,
    oq.missing_with_reason_count,
    -- Freshness
    MAX(ir.started_at)          AS last_run_at,
    sr.enabled
FROM {{ ref('stg_source_registry') }} sr
LEFT JOIN {{ ref('stg_ingestion_run') }} ir
    ON sr.source_id = ir.source_id
LEFT JOIN (
    SELECT
        source_id,
        AVG(quality_score)      AS avg_quality_score,
        COUNT(*) FILTER (WHERE is_low_confidence) AS low_confidence_count,
        COUNT(*) FILTER (WHERE is_missing_with_reason) AS missing_with_reason_count
    FROM {{ ref('stg_observation_quality') }}
    GROUP BY source_id
) oq ON sr.source_id = oq.source_id
GROUP BY sr.source_id, sr.domain, sr.category, sr.source_level,
         oq.avg_quality_score, oq.low_confidence_count, oq.missing_with_reason_count,
         sr.enabled
```

**用途**：为 S1.11 Great Expectations 提供 source-level 质量基线。

---

## §5 dbt tests 设计

### §5.1 Schema tests (内置)

| 模型 | 测试 |
|---|---|
| `stg_source_registry` | `unique(source_id)`, `not_null(source_id)`, `not_null(domain)` |
| `stg_ingestion_run` | `unique(run_id)`, `not_null(run_id)`, `not_null(status)`, `accepted_values(status, ['RUNNING','SUCCESS','PARTIAL','FAILED'])` |
| `stg_source_document` | `unique(document_id)`, `not_null(document_id)`, `not_null(file_hash_sha256)`, `relationships(source_id → stg_source_registry.source_id)` |
| `stg_observation` | `unique(observation_id)`, `not_null(observation_id)`, `not_null(source_id)`, `relationships(source_id → stg_source_document.document_id)`, `accepted_values(value_type, ['FACT'])` |
| `stg_observation_quality` | `unique(observation_id)`, `not_null(observation_id)`, `accepted_values(quality_score, range 0-1)` |

### §5.2 自定义 generic tests

| 测试名 | 描述 | 目标 |
|---|---|---|
| `test_quality_score_range` | quality_score ∈ [0, 1] | `stg_observation_quality` |
| `test_insertion_pct_range` | insertion_pct ∈ [0, 100] | `stg_ingestion_run` |
| `test_duration_non_negative` | duration_seconds ≥ 0 | `stg_ingestion_run` |
| `test_sha256_format` | file_hash_sha256 ~ '^[a-f0-9]{64}$' | `stg_source_document` |
| `test_no_orphan_observations` | observation.source_id 必须在 source_document 中存在 | `stg_observation` |

### §5.3 空表诚实

所有 staging model 对空表返回 0 行（不报错）。`dbt test` 在无数据时全 pass（schema tests 的 `not_null` / `unique` 对空表 vacuous truth）。

**不引入** source freshness tests（本刀无定时 ingestion；空表诚实优先）。

---

## §6 依赖 + 消费方

### §6.1 上游依赖（已有）

| 表 | 来源 | 写入方 |
|---|---|---|
| `cegr.source_registry` | `scripts/import_registry_csv.py` | S1.1 |
| `cegr.source_document` | 4 个 connector | S1.4–1.7 |
| `cegr.ingestion_run` | 4 个 connector | S1.4–1.7 |
| `cegr.observation` | 4 个 connector | S1.4–1.7 |

### §6.2 下游消费方（本刀不做）

| 消费方 | 任务书 | 依赖 |
|---|---|---|
| S1.10 FastAPI 查询层 | 另开 | `int_indicator_timeseries` / `int_source_coverage` |
| S1.11 数据契约 (Great Expectations) | 另开 | `stg_observation_quality` / `int_source_coverage` |
| Gate 1 研究问题回答 | `docs/08` §2.3 | `int_indicator_timeseries` |
| Grafana 仪表板 | 本刀不做 | `stg_ingestion_run` / `int_source_coverage` |

---

## §7 红线

| 红线 | 说明 |
|---|---|
| 不 Gate 1 PASS | 本刀不声称 Gate 1 通过 |
| 不 DSH | 不引入 data stage house |
| 不批量爬取 | 不 HTTP 爬源站；不批量历史入库 |
| 不降 OCR | gate_thresholds.json 不改 |
| 不写 `docs/23` 正文 | Cursor 拥有 |
| 只读 | staging view 不写 cegr 原始表 |
| profiles.yml 不入 git | .gitignore 排除 |

---

## §8 已知遗留

| 项 | 说明 | 处理 |
|---|---|---|
| indicator_definition / geo_entity / calendar_period 表 | observation FK 引用但 staging 未 JOIN | 本刀不做；S1.10 按需扩展 |
| DERIVED / INFERENCE / JUDGMENT 观测 | value_type 非 FACT 的行被 staging 过滤 | 本刀不做；S1.10+ 处理 |
| observation_revision 追加表 | immutability trigger 引用的修订链 | 本刀不做；S1.10+ 处理 |
| seed 数据 (geo_entity, indicator) | 参考数据可作为 dbt seed | 本刀不做；手动 SQL 填充 |
| incremental materialization | 数据量增长后 staging view 可能性能不足 | S1.10+ 评估切 incremental |
| source freshness tests | 无定时 ingestion 故不做 freshness | S1.10+ 定时 ingestion 后启用 |
| 生产 DSN | profiles.yml prod target 需真实 DB 凭证 | 部署时通过 env var 注入 |

---

## §9 引用

| 文档 | 说明 |
|---|---|
| `docs/08-mvp-plan.md` §2.1 | S1.9 任务定义 |
| `docs/08-mvp-plan.md` §2.3 | Gate 1 标准 |
| `schema/01-core.sql` | 4 张核心表 DDL |
| `backend/sql/migrations/004_*.sql` | period + lineage 列 |
| `docs/22-stage1-s18-*.md` | S1.8 监控（stale RUNNING SQL 参考） |
| `69-stage1-s19-dbt-planning-tasking` | 本刀任务书 |
