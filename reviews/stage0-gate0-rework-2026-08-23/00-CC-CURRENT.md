# CC 当前队列

> **§META 为唯一真相源** — `84` + `216` + `40` + `82`

---

## META

| 字段 | 值 |
|---|---|
| **phase** | `CC_ACTION_REQUIRED` |
| **queue_rev** | `137` |
| **origin_head** | `51a785c` |
| **cc_head** | `51a785c`；`325` 已交 |
| **cc_receipt** | `325` |
| **cursor_ack** | `325` |
| **last_audit** | `326` PASS |
| **user_ruling** | Stage 2 **C**；缩刀 **D**；**不再等用户投喂**；官方公开源自动获取+结构化呈现；**遇登录/验证码/付费 → 报告用户（用户可提供授权），禁止绕过** |
| **cursor_poll** | `ARMED` |
| **expect_cc_poll** | `EXEC_THEN_POLL` |
| **updated_at** | `2026-08-26T17:02:00+08:00` |
| **blocked_by** | — |

---

## NOW — CC 执行

**`327`** — 官方公开源自动获取规划（见 `327-…tasking…md`；**含 AUTH 升级协议**）。

1. 写 `docs/52`（公开源自动获取；AUTH 遇阻 → 报告用户）
2. 补 pack → 回执 **`328`**
3. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

---

## POLL

交卷后：`cursor_ack` 未 bump 前只 POLL；`queue_rev` 变化 → 读 §NOW。

探测：`./scripts/cc_gate_watch.sh --pull`（见 `216`）。

---

## BLOCKED

（无。）需授权源一律 escalate 用户，不绕过。
