# Great Expectations data contracts — CEGR Stage 1 / S1.11

> 5 core dataset contracts over `cegr_staging` dbt views.
> Per `docs/25-stage1-s11-data-contracts-plan-20260825.md` and `reviews/.../86-impl-tasking-20260825.md`.

---

## Quickstart

```bash
# 1. Install (Python 3.11 recommended — same reason as dbt venv)
python3.11 -m venv /tmp/ge_venv
/tmp/ge_venv/bin/pip install 'great_expectations>=0.18,<0.19' psycopg2-binary pydantic

# 2. Set DSN (optional — defaults match S1.10 API)
export CEGR_GE_DSN='postgresql://postgres:postgres@127.0.0.1:55440/cegr_test'

# 3. Run all 5 suites
make -C .. ge-check
# or:
../ge/scripts/ge_run.sh
```

## Suites (5)

| Suite | Dataset | dbt view | Expectations |
|---|---|---|---|
| `d1_source_registry_suite` | D1 | `cegr_staging.stg_source_registry` | 10 |
| `d2_source_document_suite` | D2 | `cegr_staging.stg_source_document` | 10 |
| `d3_ingestion_run_suite` | D3 | `cegr_staging.stg_ingestion_run` | 10 |
| `d4_observation_suite` | D4 | `cegr_staging.stg_observation` | 12 |
| `d5_indicator_timeseries_suite` | D5 | `cegr_staging.int_indicator_timeseries` | 10 |

## **Empty-table honesty** (per `docs/25` §5 — spike 00 lesson)

All expectations use `mostly` parameter — **never** strict mode.
Empty tables emit WARNING, never FAIL.

| Constraint type | `mostly` value | Example |
|---|---|---|
| PK / FK NOT NULL (事实约束) | `0.99` | `expect_column_values_to_not_be_null source_id` |
| 业务枚举 / regex (允许少量未分类) | `0.80` | `source_level MATCH '^S[1-5]$'` |
| 列对比较 (`updated_at >= created_at`) | `1.0` 仅业务逻辑必然 | D1 #10 |

## Layout

```
ge/
├── great_expectations.yml        # DSN chain + datasources
├── expectations/
│   ├── d1_source_registry_suite.json
│   ├── d2_source_document_suite.json
│   ├── d3_ingestion_run_suite.json
│   ├── d4_observation_suite.json
│   └── d5_indicator_timeseries_suite.json
├── checkpoints/
│   ├── ci_checkpoint.yml         # all 5 suites
│   └── dev_checkpoint.yml        # configurable single-suite
├── plugins/custom_data_docs/
│   └── empty_table_handler.py    # 3-state PASS/PASS_WITH_WARN/FAIL
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_ge_suites_loadable.py    # ≥3 tests
│   ├── test_empty_table_strategy.py  # ≥3 tests
│   └── test_checkpoints_loadable.py  # ≥2 tests
├── scripts/ge_run.sh
└── README.md                     # ← you are here
```

## CI

`.github/workflows/ge-check.yml` runs `great_expectations checkpoint run ci_checkpoint`
on PR + daily schedule. See `docs/25` §8.2.

## Red lines (per `docs/25` §9)

- ❌ No Gate 1 PASS / DSH / batch crawl / OCR relaxation
- ❌ No hardcoded DSN — env var only
- ❌ No pgvector / LangSmith (Stage 4+)
