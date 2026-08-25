# S1.11 — CC 规划回执

- 编号：`83-stage0-cc-s11-plan-receipt-20260825`
- 前置：`81` 任务书；`docs/08` §2.1 S1.11；`docs/10` §2 / §5.2 / §5.4
- 提交：`a6af940`
- Pack：458 artifacts (role_count +1 vs 457)
- 双推：origin ✅ / github ✅

## 交付物

| 文件 | 说明 |
|---|---|
| `docs/25-stage1-s11-data-contracts-plan-20260825.md` | S1.11 GE 数据契约规划 (~335 行) |

## 规划摘要

### 5 个核心数据集

| # | 数据集 | 来源 | 角色 |
|---|---|---|---|
| D1 | `stg_source_registry` | cegr_staging | 来源目录 |
| D2 | `stg_source_document` | cegr_staging | 文档存证 |
| D3 | `stg_ingestion_run` | cegr_staging | 入库运行 |
| D4 | `stg_observation` | cegr_staging | 观测事实 |
| D5 | `int_indicator_timeseries` | cegr_staging | 研究级时间序列 |

### GE 0.18+ 目录

```
ge/
├── great_expectations.yml        # DSN 链：CEGR_GE_DSN → CEGR_API_DSN → ...
├── expectations/d[1-5]_*.json
├── checkpoints/ci|dev_*.yml
├── plugins/custom_data_docs/...
├── tests/test_ge_suites_loadable.py   # ≥3 tests
├── scripts/ge_run.sh
└── README.md                     # 显式承诺「空表不爆」
```

### 空表诚实策略（spike 00 教训）

| 规则 | 实现 |
|---|---|
| `mostly=0.99` 当 NOT NULL 是事实约束 | PK/FK NOT NULL |
| `mostly=0.80` 当语义约束允许少量空 | `caveat_text` 等 |
| **不用** `mostly=1.0`（=严格模式） | spike 00 已踩坑 |
| 空表 row_count=0 → emit WARNING + 跳过 strict-only | `custom_empty_table_handler` plugin |
| 3 态结果：PASS / PASS_WITH_WARN / FAIL | 避免假阳性 |

### D1 草样（10 个 expectation）

1. `expect_table_columns_to_match_ordered_list`
2. `expect_column_values_to_not_be_null source_id mostly=0.99`
3. `expect_column_values_to_be_unique source_id`（PK）
4. `expect_column_values_to_match_regex source_level='^S[1-5]$' mostly=0.80`
5. `expect_column_values_to_be_in_set category`
6. `expect_column_values_to_be_between enabled [0,1]`
7. `expect_table_row_count_to_be_between [0, 10000]`
8. `expect_column_unique_value_count_to_be_between domain [1, ...] mostly=0.50`
9. `expect_column_values_to_match_regex domain pattern`
10. `expect_column_pair_values_A_to_be_greater_than_B updated_at >= created_at mostly=1.0`

### docs/10 映射

| docs/10 § | GE suite |
|---|---|
| §2.1 observation 可回溯 source_document | d4 #3 + d2 #2 |
| §2.4 缺失数据带原因 | d4 value_type='MISSING' → missing_reason NOT NULL |
| §2.5 URL 漂移告警 | d1 domain regex + 次刀 suite |

### 期望类型 3 类

1. **Schema 不变量**（`expect_table_columns_to_match_ordered_list` / `expect_column_to_exist` / 类型）
2. **基数与形状**（`expect_table_row_count_to_be_between` / 唯一性比例）
3. **业务关键约束**（`expect_column_values_to_match_regex` / 枚举 / 列对比较）

### CI

- 新增 `.github/workflows/ge-check.yml`（实现刀 push）
- `Makefile` targets: `ge-check` / `ge-docs` / `ge-suite-%`
- 顺序：`pytest → dbt test → ge-check → curl /api/.../series`

## 红线遵守

| 红线 | 状态 |
|---|---|
| 不 Gate 1 PASS | ✅ |
| 不 DSH / pgvector / LangSmith | ✅ |
| 不批量 2020-2025 入库 | ✅ |
| 不 HTTP 爬源站 | ✅ |
| 不降 OCR 门槛 | ✅ 不改 `gate_thresholds.json` |
| Cursor 不写 `docs/25` 正文 | ✅ CC 起草 |
| 不替用户下裁定 | ✅ |
| 空表不 FAIL | ✅ §5 强制 mostly/empty |

## 下一步

- S1.11 实现刀（任务书另开）：5 suite JSON + `great_expectations.yml` + checkpoint + `test_ge_suites_loadable.py` + `ge_run.sh` + Makefile + `.github/workflows/ge-check.yml` + commit + 回执

— CC @ queue_rev 27 → 28 等待（84 dual heartbeat ARMED） —