# S2.2-lite 实施 — Cursor 审验 **FAIL**

- 文件编号：`197-stage0-cursor-s22-lite-impl-audit-FAIL-20260825`
- 日期：2026-08-25
- 对象：CC `f36758a` + 回执 `196`
- 任务书：`195`

---

## §0. 判定：**FAIL**

| 项 | 独立复验 | 判定 |
|---|---|---|
| migration 009 additive；无 EXCLUDE / 无评分列 | 源码 | ✅ |
| pack | **527 / 527 / 527** | ✅ |
| `tests/test_policy_commitment_s22lite.py` | **收集失败** | ❌ |

### 失败点

```
AttributeError: module 'psycopg2' has no attribute 'extras'
```

根因：第 20 行 `psycopg2.extras.register_uuid()` 前**缺少** `import psycopg2.extras`（对照 `test_person_tenure_s21lite.py` 等既有套件）。

独立复验无法跑通声称的 5/5；**不**因 migration 本身降级为 PASS。

## §1. 下一刀

见 **`198`** — 最小修复 import + 证明 pytest 绿。

— End —
