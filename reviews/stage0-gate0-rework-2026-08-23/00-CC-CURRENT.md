# CC 当前队列

> **§META 为唯一真相源** — `84` + `216` + `40` + `82`

---

## META

| 字段 | 值 |
|---|---|
| **phase** | `CC_ACTION_REQUIRED` |
| **queue_rev** | `153` |
| **origin_head** | `3cdd12e` |
| **cc_head** | `3cdd12e`；`368` 已交 |
| **cc_receipt** | `368` |
| **cursor_ack** | `368` |
| **last_audit** | `369` PASS |
| **user_ruling** | Stage 2 **C**；缩刀 **D**；Cursor 代判；深圳 71 行 sample → **上 /public-extracts** |
| **cursor_poll** | `ARMED` |
| **expect_cc_poll** | `EXEC_THEN_POLL` |
| **updated_at** | `2026-08-26T20:06:30+08:00` |
| **blocked_by** | — |

---

## NOW — CC 执行

**`370`** — 深圳 REGISTRY_SAMPLE 前端分节（见 `370-…tasking…md`）。

1. fixture + `/public-extracts` 深圳分节
2. 回执 **`371`**（`-cc-`）
3. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

---

## POLL

交卷后：`cursor_ack` 未 bump 前只 POLL；`queue_rev` 变化 → 读 §NOW。

探测：`./scripts/cc_gate_watch.sh --pull`（见 `216`）。

---

## BLOCKED

（无。）仅登录/验证码/付费 escalate 用户。
