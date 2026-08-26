# CC 当前队列

> **§META 为唯一真相源** — `84` + `216` + `40` + `82`

---

## META

| 字段 | 值 |
|---|---|
| **phase** | `CC_ACTION_REQUIRED` |
| **queue_rev** | `147` |
| **origin_head** | `5a94fde` |
| **cc_head** | `5a94fde`；`353` 已交 |
| **cc_receipt** | `353` |
| **cursor_ack** | `353` |
| **last_audit** | `354` PASS |
| **user_ruling** | Stage 2 **C**；缩刀 **D**；源工程 Cursor 代判；extracts 已护住 → **收紧 JS-shell 误判 + NBS live** |
| **cursor_poll** | `ARMED` |
| **expect_cc_poll** | `EXEC_THEN_POLL` |
| **updated_at** | `2026-08-26T19:07:00+08:00` |
| **blocked_by** | — |

---

## NOW — CC 执行

**`355`** — JS-shell 启发式收紧 + NBS live（见 `355-…tasking…md`）。

1. 仅小体积+脚本 才判壳；大页放行解析
2. NBS 再 `--live`；回执 **`356`**（`-cc-`）
3. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

---

## POLL

交卷后：`cursor_ack` 未 bump 前只 POLL；`queue_rev` 变化 → 读 §NOW。

探测：`./scripts/cc_gate_watch.sh --pull`（见 `216`）。

---

## BLOCKED

（无。）仅登录/验证码/付费 escalate 用户。
