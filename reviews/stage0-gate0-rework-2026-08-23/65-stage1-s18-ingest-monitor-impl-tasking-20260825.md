# S1.8 — ingest_run 监控实现任务书

- 编号：`65-stage1-s18-ingest-monitor-impl-tasking-20260825`
- 前置：`64` 规划通过；`docs/22`

## SCHEMA / 语义裁定

| 决策点 | 裁定 |
|---|---|
| 新表 / migration | **不做** |
| DSN | 环境变量 `CEGR_DSN`（或 `DATABASE_URL`）；禁止把生产密码写进仓库 |
| 失败率默认 | **0.25**（可 CLI 覆盖） |
| Stale RUNNING | `status='RUNNING' AND finished_at IS NULL AND started_at < NOW() - interval 'Nh'`（**用 `<`，见 docs/22 §3.4**）；默认 N=6 |
| Grafana | **本刀不做** |
| 写库 | **只读**；禁止 UPDATE stale 自动恢复 |

## NOW

1. `backend/src/china_platform/monitoring/ingest_monitor.py` — `IngestMonitor`（docs/22 §2.1 核心方法至少：`status_distribution` / `failure_rate` / `failed_runs` / `stale_running` / `generate_report` / `check_alerts`）
2. `scripts/monitor_ingest.py` — CLI：`report` / `check`（退出码 0/1/2/3）
3. `tests/test_ingest_monitor.py` — ≥4：失败率计算、stale 边界（`<`）、空表诚实、退出码映射；**用 fixture/mock DB，不跑 OCR**
4. pytest 定向单测 + **默认 pack**（非 OCR；勿 `SKIP_PYTEST` 除非失败）→ commit → **origin 优先** → 回执 **`66-stage0-cc-s18-impl-receipt-*.md`**
5. → **§POLL**

## 红线

不 Gate 1 PASS；不 DSH；不写 observation；不改 `gate_thresholds.json`。
