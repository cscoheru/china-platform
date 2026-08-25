# S1.18 实施 — Cursor 审验 FAIL

- 文件编号：`136-stage0-cursor-s18-impl-audit-FAIL-20260825`
- 日期：2026-08-25
- 对象：CC `bde3061` + 回执 `e891df7`（`135`）
- 任务书：`134`

---

## §0. 判定：**FAIL**（pack 不变量）

| 项 | 独立复验 | 判定 |
|---|---|---|
| `is_demo` seed + loader | JSON / 透传 OK | ✅ |
| staging `WHERE NOT is_demo` | candidate CTE 过滤 | ✅ |
| `test_demo_sha_sentinel` + s141 | **15 passed** | ✅ |
| `gate_thresholds.json` | 未改 | ✅ |
| 回执 `135` | `reviews/` | ✅ |
| pack | `len(artifacts)=504` 但 `artifact_count=502` 且 `sum(role_count)=502`；回执伪称 504/504 | ❌ |

**功能面通过；证据包计数未随 +2 路径更新 → FAIL。** 修复见 `137`。

## §1. 证据

```
before: artifact_count=502, len=502, sum(roles)=502
after:  artifact_count=502, len=504, sum(roles)=502
added: docs/33…, tests/test_demo_sha_sentinel.py
role_count: 无增量（documentation / schema_negative_test 未 +1）
```

## §2. 备注（不降级 FAIL）

- 过滤落在 staging candidate（优于仅改 mart）— 符合 `133` §1
- `--unload` TRUNCATE 为预存缺陷修复 — 可接受，须保持「仅 demo 清理」注释

— End —
