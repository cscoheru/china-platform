# CC 当前队列

> **§META 为唯一真相源** — `84` + `216` + `40` + `82`

---

## META

| 字段 | 值 |
|---|---|
| **phase** | `CC_ACTION_REQUIRED` |
| **queue_rev** | `152` |
| **origin_head** | `f7736d9` |
| **cc_head** | `f7736d9`；里程碑后恢复下刀 |
| **cc_receipt** | `365` |
| **cursor_ack** | `365` |
| **last_audit** | `366` PASS |
| **user_ruling** | Stage 2 **C**；缩刀 **D**；Cursor 代判；里程碑后 **恢复自主下刀**（深圳 sample 0 行修复）|
| **cursor_poll** | `ARMED` |
| **expect_cc_poll** | `EXEC_THEN_POLL` |
| **updated_at** | `2026-08-26T19:57:30+08:00` |
| **blocked_by** | — |

---

## NOW — CC 执行

**`367`** — 深圳样本表抽取修复（见 `367-…tasking…md`）。

1. 修 HTML 表抽取使深圳 sample ≥1 行；NBS 不回归
2. 回执 **`368`**（`-cc-`）
3. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

---

## POLL

交卷后：`cursor_ack` 未 bump 前只 POLL；`queue_rev` 变化 → 读 §NOW。

探测：`./scripts/cc_gate_watch.sh --pull`（见 `216`）。

---

## BLOCKED

（无。）仅登录/验证码/付费 escalate 用户。
