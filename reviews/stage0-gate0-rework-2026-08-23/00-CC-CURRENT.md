# CC 当前队列

> **§META 为唯一真相源** — `84` + `216` + `40` + `82`

---

## META

| 字段 | 值 |
|---|---|
| **phase** | `CC_ACTION_REQUIRED` |
| **queue_rev** | `149` |
| **origin_head** | `a25e05e` |
| **cc_head** | `a25e05e`；`359` 已交 |
| **cc_receipt** | `359` |
| **cursor_ack** | `359` |
| **last_audit** | `360` PASS |
| **user_ruling** | Stage 2 **C**；缩刀 **D**；Cursor 代判；双轨呈现已通 → **LIVE_CANDIDATE 一键刷新 CLI** |
| **cursor_poll** | `ARMED` |
| **expect_cc_poll** | `EXEC_THEN_POLL` |
| **updated_at** | `2026-08-26T19:21:30+08:00` |
| **blocked_by** | — |

---

## NOW — CC 执行

**`361`** — LIVE_CANDIDATE 一键刷新（见 `361-…tasking…md`）。

1. `--refresh-live-candidate`：live→WORM→extract→双写 JSON；不碰 sample
2. 回执 **`362`**（`-cc-`）
3. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

---

## POLL

交卷后：`cursor_ack` 未 bump 前只 POLL；`queue_rev` 变化 → 读 §NOW。

探测：`./scripts/cc_gate_watch.sh --pull`（见 `216`）。

---

## BLOCKED

（无。）仅登录/验证码/付费 escalate 用户。
