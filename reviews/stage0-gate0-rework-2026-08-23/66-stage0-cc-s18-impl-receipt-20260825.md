# S1.8 — CC 实现回执

- 编号：`66-stage0-cc-s18-impl-receipt-20260825`
- 前置：`65` 任务书；`64` 规划通过；`docs/22`
- 提交：`91ae886`
- Pack：454 artifacts (role_count +1 vs 453)
- 双推：origin ✅ / github ✅

## 交付物

| 文件 | 说明 |
|---|---|
| `backend/src/china_platform/monitoring/__init__.py` | 监控模块入口 |
| `backend/src/china_platform/monitoring/ingest_monitor.py` | `IngestMonitor` 类 (~465行) |
| `scripts/monitor_ingest.py` | CLI 入口 (~220行) |
| `tests/test_ingest_monitor.py` | 12 个测试 (~400行) |

## IngestMonitor 方法

| 方法 | 说明 |
|---|---|
| `status_distribution(window_days)` | SUCCESS/PARTIAL/FAILED/RUNNING 分布 |
| `failure_rate(window_days)` | (PARTIAL+FAILED)/total; 空表→0.0 |
| `failed_runs(limit, window_days)` | 失败/部分运行列表 + error_log preview |
| `partial_runs(limit, window_days)` | 仅部分运行 |
| `stale_running(hours)` | stale RUNNING 检测: `started_at < NOW() - interval 'Nh' AND finished_at IS NULL` |
| `per_source_breakdown(window_days)` | 按 domain+category 分组 |
| `records_gap_analysis(limit, window_days)` | extracted - inserted 差距 top N |
| `duration_stats(window_days)` | avg/min/max/median/p95 (PERCENTILE_CONT) |
| `trend(days)` | 每日 success/failure 趋势 |
| `generate_report(window_days)` | 聚合 dict (JSON serializable) |
| `check_alerts(window_days, max_failure_rate, hours)` | (ok, msg, exit_code) → 0/1/2/3 |

## CLI 子命令

```
python3 scripts/monitor_ingest.py report      # JSON 报告
python3 scripts/monitor_ingest.py check       # 退出码 0/1/2/3
python3 scripts/monitor_ingest.py failed      # 失败运行表格
python3 scripts/monitor_ingest.py partial     # 部分运行表格
python3 scripts/monitor_ingest.py stale       # stale RUNNING 表格
python3 scripts/monitor_ingest.py per-source  # 按源分组表格
python3 scripts/monitor_ingest.py trend       # 30天趋势
```

公共 flags: `--window-days` / `--max-failure-rate` / `--hours` / `--dsn`

## 测试覆盖 (12 tests, all passed)

| # | 测试 | Cursor 65 对应 |
|---|---|---|
| 1 | `test_empty_table_honests_zero_failure_rate` | 空表诚实 (failure_rate=0.0) |
| 2 | `test_empty_table_honests_no_stale` | 空表诚实 (stale=[]) |
| 3 | `test_failure_rate_calculation` | 失败率计算 (2/4=0.50) |
| 4 | `test_status_distribution_with_rows` | 状态分布 (3 SUCCESS + 1 FAILED) |
| 5 | `test_stale_running_boundary_lt_6h` | stale 边界 `<` (2h=NOT stale, 10h=stale, 7h+finished=NOT stale) |
| 6 | `test_stale_running_custom_hours` | 自定义阈值 (4h: stale_6h=0, stale_3h=1) |
| 7 | `test_check_alerts_exit_code_0_ok` | 退出码 0 (4 SUCCESS → OK) |
| 8 | `test_check_alerts_exit_code_1_failure_rate` | 退出码 1 (0.75 > 0.25) |
| 9 | `test_check_alerts_exit_code_2_stale` | 退出码 2 (stale RUNNING) |
| 10 | `test_check_alerts_exit_code_3_both` | 退出码 3 (failure_rate + stale) |
| 11 | `test_duration_stats_with_finished_runs` | 时长统计 (avg=30s, min=10s, max=50s) |
| 12 | `test_generate_report_returns_dict` | 报告 dict 键完整性 |

**测试方法**: single-transaction rollback + connection injection (`monitor._conn = conn`)。无 SAVEPOINT、无 commit，fixture teardown 统一 ROLLBACK。

## 非 OCR 回归

117/117 passed (3.44s)。排除 test_scanned_pdf_ocr_connector.py (OCR) + test_cleanliness.py (worktree hash)。

## Pack

默认 pack 因内嵌 full pytest 超时 (900s, OCR tests)。独立非 OCR 回归 117/117 通过后，fallback `EVIDENCE_PACK_TEST_HOOKS=1 SKIP_PYTEST=1 SKIP_PSQL=1` → 454 artifacts。

## Cursor 65 §SCHEMA 裁定遵守

| 裁定 | 遵守 |
|---|---|
| 不做新表 / migration | ✅ |
| DSN 环境变量 | ✅ `CEGR_DSN` / `DATABASE_URL` / fallback |
| 失败率默认 0.25 | ✅ |
| Stale `<` 运算符 | ✅ `started_at < NOW() - INTERVAL '%s hours'` |
| Grafana 本刀不做 | ✅ |
| 只读 | ✅ 无 INSERT/UPDATE/DELETE |
| 禁止 UPDATE stale 自动恢复 | ✅ |

## 红线

不 Gate 1 PASS；不 DSH；不写 observation；不改 gate_thresholds.json。
