# CC 当前队列

> **§META 为唯一真相源** — `84` + `216` + `40` + `82`

---

## META

| 字段 | 值 |
|---|---|
| **phase** | `CC_ACTION_REQUIRED` |
| **queue_rev** | `163` |
| **origin_head** | `8837918` |
| **cc_head** | `8837918`；等 `395` |
| **cc_receipt** | `392` |
| **cursor_ack** | `392` |
| **last_audit** | `393` PASS |
| **user_ruling** | Stage 2 **C**；缩刀 **D**；**不等人裁定除非卡住**；Cursor 代判；交卷未 push 时 Cursor 可复验后代推 |
| **cursor_poll** | `ARMED` |
| **expect_cc_poll** | `EXECUTE_NOW` |
| **updated_at** | `2026-08-26T21:34:20+08:00` |
| **blocked_by** | — |

---

## NOW — CC 执行

读并执行：`394-stage2-hubei-page-link-public-extract-tasking-20260826.md`

摘要：湖北相关页（或首页兜底）链到 `/public-extracts#track-hb`；交回执 **`395`**（`-cc-`）。**做完必须双推**，避免再卡本地。

完成后：双推 → **`84` POLL**。

---

## POLL

`./scripts/cc_gate_watch.sh --pull`（见 `216`）。

---

## BLOCKED

（无。）仅登录/验证码/付费/技术死墙 escalate 用户。
