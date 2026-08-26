# CC 当前队列

> **§META 为唯一真相源** — `84` + `216` + `40` + `82`

---

## META

| 字段 | 值 |
|---|---|
| **phase** | `CC_ACTION_REQUIRED` |
| **queue_rev** | `142` |
| **origin_head** | `352b4f3` |
| **cc_head** | `352b4f3`；等 `340` |
| **cc_receipt** | `337` |
| **cursor_ack** | `337` |
| **last_audit** | `338` PASS |
| **user_ruling** | Stage 2 **C**；缩刀 **D**；不再等投喂；AUTH/付费才问用户；**源工程 Cursor 代判（`341`）**：不 pin 易变列表页哈希；深链稳定附件后可写 registry |
| **cursor_poll** | `ARMED` |
| **expect_cc_poll** | `EXEC_THEN_POLL` |
| **updated_at** | `2026-08-26T17:57:30+08:00` |
| **blocked_by** | — |

---

## NOW — CC 执行

**`339`**（已按 `341` 修订）— 无 headless 深链；见 `339-…tasking…md` + `341-…ruling…md`。

1. 深链 `.xlsx`；成功 → pin registry + 可 O1_AUTO_INTAKED；失败/JS 壳 → tech-blocked
2. Hubei 再 live
3. 补 pack → 回执 **`340`**
4. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

---

## POLL

交卷后：`cursor_ack` 未 bump 前只 POLL；`queue_rev` 变化 → 读 §NOW。

探测：`./scripts/cc_gate_watch.sh --pull`（见 `216`）。

---

## BLOCKED

（无。）仅登录/验证码/付费 escalate 用户。
