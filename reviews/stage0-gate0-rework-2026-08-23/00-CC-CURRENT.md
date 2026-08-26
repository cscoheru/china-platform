# CC 当前队列

> **§META 为唯一真相源** — `84` + `216` + `40` + `82`

---

## META

| 字段 | 值 |
|---|---|
| **phase** | `CC_ACTION_REQUIRED` |
| **queue_rev** | `157` |
| **origin_head** | `a308b0a` |
| **cc_head** | `a308b0a`；等 `377` |
| **cc_receipt** | `374`（已 ACK） |
| **cursor_ack** | `374` |
| **last_audit** | `375` PASS |
| **user_ruling** | Stage 2 **C**；缩刀 **D**；**2026-08-26：不要等用户裁定，除非卡住（登录/验证码/付费/技术死墙）**；Cursor 代判继续下刀 |
| **cursor_poll** | `ARMED` |
| **expect_cc_poll** | `EXECUTE_NOW` |
| **updated_at** | `2026-08-26T20:46:10+08:00` |
| **blocked_by** | — |

---

## NOW — CC 执行

读并执行：`376-stage2-hubei-provincial-sample-extract-frontend-tasking-20260826.md`

摘要：湖北 `PROVINCIAL_BULLETIN` **local-sample**（`--allow-disabled-local-sample`）→ extract + `/public-extracts` 第四分节；交回执 **`377`**（`-cc-`）。**禁止** live/headless。

完成后：双推 → **`84` POLL**。

---

## POLL

`./scripts/cc_gate_watch.sh --pull`（见 `216`）。

---

## BLOCKED

（无。）仅登录/验证码/付费/技术死墙 escalate 用户。
