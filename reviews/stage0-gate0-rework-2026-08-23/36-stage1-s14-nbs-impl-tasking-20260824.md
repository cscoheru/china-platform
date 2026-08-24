# S1.4 — NBS 连接器实现任务书

- 编号：`36-stage1-s14-nbs-impl-tasking-20260824`
- 前置：`docs/18`

## NOW

1. `backend/src/china_platform/connectors/nbs_monthly.py` — 复用 spike 01 解析逻辑；默认读 repo 内 sample
2. `tests/test_nbs_monthly_connector.py` — ≥3 测试：hash、obs 数、ingest_run 状态
3. 禁止 skip；禁止批量 URL 列表
4. pytest 全集 + pack → commit 双推 + `37` 回执

## 红线

不 Gate 1 PASS；不批量 2020–2025；不降 OCR 门槛。
