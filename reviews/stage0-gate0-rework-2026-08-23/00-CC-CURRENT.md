# CC 当前队列

> **§META 为唯一真相源** — `84` + `216` + `40` + `82`

---

## META

| 字段 | 值 |
|---|---|
| **phase** | `CC_ACTION_REQUIRED` |
| **queue_rev** | `150` |
| **origin_head** | `530a983` |
| **cc_head** | `530a983`；`362` 已交 |
| **cc_receipt** | `362` |
| **cursor_ack** | `362` |
| **last_audit** | `363` PASS |
| **user_ruling** | Stage 2 **C**；缩刀 **D**；Cursor 代判；自动拉取+结构化+刷新 CLI 已通 → **docs/53 ops 手册** |
| **cursor_poll** | `ARMED` |
| **expect_cc_poll** | `EXEC_THEN_POLL` |
| **updated_at** | `2026-08-26T19:30:30+08:00` |
| **blocked_by** | — |

---

## NOW — CC 执行

**`364`** — docs/53 ops 手册 + docs/45 登记（见 `364-…tasking…md`）。

1. 落地 docs/53；刷新 docs/45
2. 回执 **`365`**（`-cc-`）
3. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

---

## POLL

交卷后：`cursor_ack` 未 bump 前只 POLL；`queue_rev` 变化 → 读 §NOW。

探测：`./scripts/cc_gate_watch.sh --pull`（见 `216`）。

---

## BLOCKED

（无。）仅登录/验证码/付费 escalate 用户。
