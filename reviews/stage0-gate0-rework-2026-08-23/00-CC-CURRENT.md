# CC 当前队列

> **§META 为唯一真相源** — `84` + `216` + `40` + `82`

---

## META

| 字段 | 值 |
|---|---|
| **phase** | `CC_ACTION_REQUIRED` |
| **queue_rev** | `146` |
| **origin_head** | `9688f0f` |
| **cc_head** | `9688f0f`；`350` 已交（命名已纠偏）|
| **cc_receipt** | `350` |
| **cursor_ack** | `350` |
| **last_audit** | `351` PASS |
| **user_ruling** | Stage 2 **C**；缩刀 **D**；源工程 Cursor 代判；结构化呈现已接线 → **护 extracts 不被测脏** |
| **cursor_poll** | `ARMED` |
| **expect_cc_poll** | `EXEC_THEN_POLL` |
| **updated_at** | `2026-08-26T18:55:00+08:00` |
| **blocked_by** | — |

---

## NOW — CC 执行

**`352`** — 禁止 pytest 覆写 `data/public_extracts`（见 `352-…tasking…md`）。

1. `--extract-root` / env + 回归测
2. 回执 **`353`**（文件名必须含 `-cc-`）
3. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

---

## POLL

交卷后：`cursor_ack` 未 bump 前只 POLL；`queue_rev` 变化 → 读 §NOW。

探测：`./scripts/cc_gate_watch.sh --pull`（见 `216`）。

---

## BLOCKED

（无。）仅登录/验证码/付费 escalate 用户。
