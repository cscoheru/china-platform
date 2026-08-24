# S1.5 — 深圳公报连接器实现任务书

- 编号：`44-stage1-s15-shenzhen-impl-tasking-20260824`
- 前置：`43` 规划通过；`docs/19`

## NOW

1. `backend/src/china_platform/connectors/sz_municipal_bulletin.py` — import spike 03 `extract_statistics`；默认 `spikes/03-municipal-bulletin/sample.html`
2. `tests/test_sz_municipal_bulletin_connector.py` — ≥3 测试：hash、obs 数（≥1）、ingest_run 状态
3. 镜像 S1.4 持久化链（ingestion_run / source_document / observation；FK 失败 → PARTIAL）
4. 禁止 skip；禁止批量 2020–2024；禁止 spike 03 `fetch_bulletin()` 网络
5. pytest 全集 + pack rebuild → commit 双推 → 回执 **`45-stage0-cc-s15-impl-receipt-*.md`**
6. 完成后 → **§POLL**（`40` §2）

## 红线

不 Gate 1 PASS；不 HTTP 默认；不降 OCR 门槛。
