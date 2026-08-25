# S1.9 — CC 规划回执

- 编号：`70-stage0-cc-s19-plan-receipt-20260825`
- 前置：`69` 任务书；`docs/23`
- 提交：`01f7bba`
- Pack：455 artifacts (role_count +1 vs 454)
- 双推：origin ✅ / github **HOLD** (443 timeout ×2)

## 交付物

| 文件 | 说明 |
|---|---|
| `docs/23-stage1-s19-dbt-staging-plan-20260825.md` | S1.9 dbt staging 规划文档 (~550行) |

## 规划摘要

### dbt 项目结构
- 目录：`dbt/` (独立于 backend/)
- 输出 schema：`cegr_staging`（与 `cegr` 原始表隔离）
- DSN：环境变量（`CEGR_DB_HOST` / `CEGR_DB_PORT` / `CEGR_DB_USER` / `CEGR_DB_PASS`）
- profiles.yml 入 .gitignore；profiles.yml.example 入 git
- packages: `dbt_utils` 1.1.1 only
- materialization: 全部 `view`（本刀不做 incremental）

### 5 张 Staging Models

| # | 模型 | 来源 | 核心职责 |
|---|---|---|---|
| 1 | `stg_source_registry` | `cegr.source_registry` | 清洁 + `id→source_id` 重命名 + enabled 过滤 |
| 2 | `stg_ingestion_run` | `cegr.ingestion_run` + registry | duration_seconds 计算 + insertion_pct + is_stale 标志 |
| 3 | `stg_source_document` | `cegr.source_document` + registry | JOIN registry 元数据 + 标准化 |
| 4 | `stg_observation` | `cegr.observation` | FACT 过滤 + period 标准化 + migration 004 列透传 |
| 5 | `stg_observation_quality` | `cegr.observation` | 5 因子 quality_score (value/confidence/lineage/source/method) |

### 2 张 Intermediate Models

| # | 模型 | 用途 |
|---|---|---|
| 1 | `int_indicator_timeseries` | indicator+geo+period 时间序列（Gate 1 研究问题消费） |
| 2 | `int_source_coverage` | source 级覆盖率 + 失败率 + 质量基线（S1.11 data contracts 消费） |

### dbt Tests
- Schema tests: unique / not_null / accepted_values / relationships
- 5 custom generic tests: quality_score_range / insertion_pct_range / duration_non_negative / sha256_format / no_orphan_observations
- 空表诚实: 无数据时全 pass

### 下游消费方 (本刀不做)
- S1.10 FastAPI → `int_indicator_timeseries` / `int_source_coverage`
- S1.11 Great Expectations → `stg_observation_quality` / `int_source_coverage`
- Grafana 仪表板 → 本刀不做

## 红线遵守

| 红线 | 状态 |
|---|---|
| 不 Gate 1 PASS | ✅ |
| 不 DSH | ✅ |
| 不批量爬取 | ✅ |
| 不降 OCR | ✅ gate_thresholds.json 不改 |
| Cursor 不写 docs/23 正文 | ✅ CC 起草 |
| 只读 staging view | ✅ 不写 cegr 原始表 |
| profiles.yml 不入 git | ✅ .gitignore |

## Github HOLD

github 443 timeout ×2 (2026-08-25 12:12–12:14)。origin `01f7bba` 已入库。待网络恢复后手动 `git push github HEAD`。
