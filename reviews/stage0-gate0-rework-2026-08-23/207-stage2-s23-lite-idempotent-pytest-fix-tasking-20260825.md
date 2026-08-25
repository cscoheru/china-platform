# S2.3-lite — idempotent pytest 修复任务书

- 编号：`207-stage2-s23-lite-idempotent-pytest-fix-tasking-20260825`
- 前置：`206` FAIL；migration 010 **勿改**（已审 OK）
- 用户裁定：**D** / **C**

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 修复 | `tests/test_project_event_s23lite.py::test_migration_010_idempotent` — 跳过空/纯注释语句 |
| 验证 | `python3 -m pytest tests/test_project_event_s23lite.py` **全绿** |
| 范围 | 仅测试修复 + 短回执；不改 010 SQL（除非必须） |

## NOW

1. 修 idempotent 切分/过滤 → 全绿
2. commit → origin → 回执 **`208`**
3. → **`84` POLL**

## 红线

不扩 scope；不 Gate PASS；不改 `gate_thresholds.json`。
