# CC 当前队列

> **§META 为唯一真相源** — `84` + `216` + `40` + `82`

---

## META

| 字段 | 值 |
|---|---|
| **phase** | `CC_ACTION_REQUIRED` |
| **queue_rev** | `148` |
| **origin_head** | `bfb9fa0` |
| **cc_head** | `bfb9fa0`；`356` 已交 |
| **cc_receipt** | `356` |
| **cursor_ack** | `356` |
| **last_audit** | `357` PASS |
| **user_ruling** | Stage 2 **C**；缩刀 **D**；Cursor 代判；NBS live 已通（drift 候选）→ **live WORM 结构化 + 前端并列，不覆盖 sample** |
| **cursor_poll** | `ARMED` |
| **expect_cc_poll** | `EXEC_THEN_POLL` |
| **updated_at** | `2026-08-26T19:15:30+08:00` |
| **blocked_by** | — |

---

## NOW — CC 执行

**`358`** — live WORM 提取 + 前端 LIVE_CANDIDATE（见 `358-…tasking…md`）。

1. 从 `…/zxfb` 抽出 JSON；不覆盖 sample
2. `/public-extracts` 并列展示；回执 **`359`**（`-cc-`）
3. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

---

## POLL

交卷后：`cursor_ack` 未 bump 前只 POLL；`queue_rev` 变化 → 读 §NOW。

探测：`./scripts/cc_gate_watch.sh --pull`（见 `216`）。

---

## BLOCKED

（无。）仅登录/验证码/付费 escalate 用户。
