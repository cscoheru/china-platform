# S2.2-lite — pytest import 修复任务书

- 编号：`198-stage2-s22-lite-pytest-import-fix-tasking-20260825`
- 前置：`197` FAIL；`195` 仍有效
- 用户裁定：**D** / **C**

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 修复 | `tests/test_policy_commitment_s22lite.py` 增加 `import psycopg2.extras`（与 s21lite 同款） |
| 范围 | **仅**此修复 + 必要时回执补丁；**不**改 migration 009（已审 OK） |
| 验证 | `python3 -m pytest tests/test_policy_commitment_s22lite.py` **5 passed** |

## NOW

1. 修 import → 本地跑通 5/5
2. commit → origin → 回执 **`199`**（可短）
3. → **`84` POLL**

## 红线

不扩 scope；不改 `gate_thresholds.json`；不 Gate PASS。
