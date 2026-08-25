# S1.9 — CC 实现回执

- 编号：`73-stage0-cc-s19-impl-receipt-20260825`
- 前置：`72` 任务书；`71` 规划通过；`docs/23`
- 提交：`45f16b8`
- Pack：455 artifacts (extracted_artifact 数不变；dbt SQL 由 git 跟踪)
- 双推：origin ✅ / github ✅

## 交付物 (19 files changed, 692 insertions)

### dbt 项目
- `dbt/dbt_project.yml` — name=cegr, profile=cegr, staging/intermediate 全部 view
- `dbt/profiles.yml.example` — env var DSN, dev/prod targets
- `dbt/macros/generate_schema_name.sql` — 强制 `target.schema = cegr_staging`

### 5 Staging Models (cegr_staging schema)
| # | 模型 | 核心职责 |
|---|---|---|
| 1 | `stg_source_registry` | enabled filter + id→source_id |
| 2 | `stg_ingestion_run` | duration_seconds + insertion_pct + is_stale (与 S1.8 监控对齐) |
| 3 | `stg_source_document` | JOIN registry 元数据 |
| 4 | `stg_observation` | value_type='FACT' filter + migration 004 columns |
| 5 | `stg_observation_quality` | 5-factor quality_score (0-1) |

### 2 Intermediate Models
| # | 模型 | 用途 |
|---|---|---|
| 1 | `int_indicator_timeseries` | Gate 1 研究问题消费 (近5年江苏GDP等) |
| 2 | `int_source_coverage` | S1.11 Great Expectations baseline |

### 4 Custom Generic Tests (docs/23 §5.2)
- `quality_score_range` — quality_score ∈ [0, 1]
- `insertion_pct_range` — insertion_pct ∈ [0, 100]
- `duration_non_negative` — duration_seconds ≥ 0
- `sha256_format` — file_hash_sha256 ~ `^[a-f0-9]{64}$`

### YAML 模型定义
- `dbt/models/staging/_stg_sources.yml` — 4 source 表定义
- `dbt/models/staging/_stg_models.yml` — schema tests + custom test 引用
- `dbt/models/intermediate/_int_models.yml` — schema tests

### .gitignore 更新
- `dbt/profiles.yml`（PRD 11.5 + Cursor 72 §SCHEMA 决策）
- `dbt/target/` / `dbt/dbt_packages/` / `dbt/logs/` / `dbt/.user.yml`

## dbt run + test 验证

| 步骤 | 结果 |
|---|---|
| `dbt deps` | N/A（无 packages.yml；plain dbt） |
| `dbt run` | **7/7 PASS** (5 staging + 2 intermediate) |
| `dbt test` | **34/34 PASS** (unique/not_null/accepted_values/relationships/custom) |
| 空表诚实 | ✅ observation/ingestion_run 空 → schema tests vacuous truth + custom tests pass |
| 隔离 | ✅ 写入 `cegr_staging` schema；cegr 原表零改动 |

**总计**: 7 models + 34 tests, 全部 PASS。

## Python 环境说明

dbt-core 1.9.4 + dbt-postgres 1.9.0 在 **Python 3.14.3** 上有 mashumaro 兼容性 bug
(`Field "schema" of type Optional[str] in JSONObjectSchema is not serializable`)。

**验证环境**: `/tmp/dbt_venv`（Python 3.11.13 + dbt 1.9.4/1.9.0）via homebrew python3.11。

后续若需 `dbt run`/`dbt test` 持续验证，使用：
```bash
/opt/homebrew/bin/python3.11 -m venv /tmp/dbt_venv
/tmp/dbt_venv/bin/pip install "dbt-core==1.9.4" "dbt-postgres==1.9.0" psycopg2-binary
cd dbt && /tmp/dbt_venv/bin/dbt run && /tmp/dbt_venv/bin/dbt test
```

## Cursor 72 §SCHEMA 裁定遵守

| 裁定 | 遵守 |
|---|---|
| dbt 输出 schema `cegr_staging` (view only) | ✅ |
| materialization 全部 view | ✅ (staging/intermediate 5+2) |
| 密码仅 profiles.yml.example + env var | ✅ profiles.yml 入 .gitignore |
| 禁止写 cegr 原表 | ✅ 仅 SELECT |
| seeds 本刀不做 | ✅ seeds/ 目录空 |
| ≥3 custom generic tests | ✅ 4 个 (quality_score / insertion_pct / duration / sha256) |
| 空表 pass | ✅ 34/34 PASS |

## 红线遵守

| 红线 | 状态 |
|---|---|
| 不 Gate 1 PASS | ✅ |
| 不 DSH | ✅ |
| 不批量爬取 | ✅ |
| 不改 gate_thresholds.json | ✅ |
| 不降 OCR | ✅ |