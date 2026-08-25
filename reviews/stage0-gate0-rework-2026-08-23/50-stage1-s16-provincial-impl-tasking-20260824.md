# S1.6 — 省级年鉴连接器实现任务书

- 编号：`50-stage1-s16-provincial-impl-tasking-20260824`
- 前置：`49` 规划通过；`docs/20`

## SCHEMA（Cursor 裁定 — 禁止 fixture 临时建表）

**必须** migration 004 + alembic cegr004：

| 列 | 类型 | 说明 |
|---|---|---|
| `observation.period_start` | `DATE` NULL | B-06 |
| `observation.period_end` | `DATE` NULL | B-06 |
| `observation.period_label` | `TEXT` NULL | 如 `2026年1-6月` |
| `observation.period_type` | `TEXT` NULL | 如 `CUMULATIVE_5MONTH`；**禁止**漂移为单一 `CUMULATIVE_HALF_YEAR` |
| `observation.lineage` | `JSONB` NULL | `{chain_id, source_file_sha256, source_file_url, extractor_version}` |
| `observation.caveat_text` | `TEXT` NULL | per-row caveat（R3-E） |

- 文件：`schema/migrations/004_observation_period_lineage.sql` + log + `alembic/versions/cegr004_*.py`
- conftest apply 链须自动含 004
- **禁止**把 B-06 元数据塞进 `notes` 敷衍；**禁止**测试里 CREATE TABLE

## NOW

1. migration 004（上表）
2. `backend/src/china_platform/connectors/provincial_yearbook.py` — import spike 02；默认 `hubei_2026_06.xlsx`
3. `tests/test_provincial_yearbook_connector.py` — ≥4：hash、obs≥1、ingest_run 状态、**period metadata 完整性**（含 ≥1 行 `quarterly_data_verified=False`）
4. `indicator_canonical` 写 FK 占位同 S1.4/S1.5；中文 `indicator_zh` 仅入 `lineage` JSON
5. pytest 全集 + pack → commit 双推 → 回执 **`51-stage0-cc-s16-impl-receipt-*.md`**
6. 完成后 → **§POLL**（`40` §2）

## 红线

不 Gate 1 PASS；不 3省×5年 crawl；不降 OCR；不 HTTP 默认。
