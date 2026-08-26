# CC 当前队列

> **§META 为唯一真相源** — `84` + `216` + `40` + `82`

---

## META

| 字段 | 值 |
|---|---|
| **phase** | `POLL` |
| **queue_rev** | `156` |
| **origin_head** | `8a999c4` |
| **cc_head** | `8a999c4`；`374` 已交 |
| **cc_receipt** | `374` |
| **cursor_ack** | `374` |
| **last_audit** | `375` PASS |
| **user_ruling** | Stage 2 **C**；缩刀 **D**；Cursor 代判；三轨已入 docs/45 → **POLL** |
| **cursor_poll** | `ARMED` |
| **expect_cc_poll** | `POLL` |
| **updated_at** | `2026-08-26T20:33:40+08:00` |
| **blocked_by** | — |

---

## NOW — CC 执行

（无新刀。）只 **`84` POLL**，直到 `queue_rev` 再 bump。

---

## POLL

`./scripts/cc_gate_watch.sh --pull`（见 `216`）。

---

## BLOCKED

（无。）仅登录/验证码/付费 escalate 用户。
