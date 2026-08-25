# S1.17 — R12 URL 健康探针 / ingest CLI 实现任务书

- 编号：`127-stage1-s17-r12-url-health-impl-tasking-20260825`
- 前置：`126` 规划通过；`docs/32`

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| migration | **无** |
| 新构件 | `scripts/url_health_probe.py` + `scripts/monitor_ingest.py` |
| 测试 | `tests/test_url_health_probe.py` + `tests/test_monitor_ingest_cli.py`（**mock，不联外**） |
| ingest_monitor | **只读复用**；不改 SQL 语义 |
| HTTP 上限 | 按 docs/32 §2.1（HEAD 默认；GET Range ≤1KB；≤1req/s；不绕验证码） |

## NOW

0. 补回执 **`125`**（规划）进 `reviews/`
1. 落地两 CLI + pytest（docs/32 §3.2–§3.3；用例 2 按 `126` §1 纠正）
2. 回归：`tests/test_ingest_monitor.py` 仍绿
3. commit → origin → 回执 **`128`** 进 `reviews/`
4. → **`84` POLL**

## 红线

不 Gate 1 PASS；不 DSH；不爬业务数据；不绕验证码；不改 `gate_thresholds.json`；CI/默认测试不联外网。
