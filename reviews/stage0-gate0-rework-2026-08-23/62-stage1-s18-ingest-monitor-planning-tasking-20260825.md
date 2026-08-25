# S1.8 — ingest_run 监控规划任务书

- 编号：`62-stage1-s18-ingest-monitor-planning-tasking-20260825`
- 前置：`61` S1.7 通过；`docs/08` §2.1 S1.8
- 范围：**规划 only**（监控/告警设计；不强制上 Grafana 云）

## NOW（CC 交付）

1. 起草 **`docs/22-stage1-s18-ingest-run-monitoring-plan-20260825.md`**（CC 拥有）
2. 覆盖：`ingestion_run` 状态机查询、失败率、PARTIAL/FAILED 列表、最小告警（日志/脚本即可；Grafana 可选）
3. 复用已有 connector 写入的 run 行；**不**批量爬取；**不**降 OCR 门槛
4. 规划 only — 实现另开任务书

## 红线

不 Gate 1 PASS；不引入 DSH；Cursor 不写 `docs/22` 正文。
