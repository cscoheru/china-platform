# CC 当前队列

> **§META 为唯一真相源** — `84` + `216` + `40` + `82`

---

## META

| 字段 | 值 |
|---|---|
| **phase** | `CC_ACTION_REQUIRED` |
| **queue_rev** | `145` |
| **origin_head** | `ce2700f` |
| **cc_head** | `ce2700f`；`347` 已交（协调 unblock push）|
| **cc_receipt** | `347` |
| **cursor_ack** | `347` |
| **last_audit** | `348` PASS |
| **user_ruling** | Stage 2 **C**；缩刀 **D**；源工程 Cursor 代判；湖北/深圳 live 暂缓；本地样本结构化已通 → **接前端呈现** |
| **cursor_poll** | `ARMED` |
| **expect_cc_poll** | `EXEC_THEN_POLL` |
| **updated_at** | `2026-08-26T18:40:00+08:00` |
| **blocked_by** | — |

---

## NOW — CC 执行

**`349`** — 公开提取 → 前端结构化呈现（见 `349-…tasking…md`）。

1. NBS `public_extracts` 63 行进 UI；标 `REGISTRY_SAMPLE`/demo
2. 补 pack → 回执 **`350`**
3. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

---

## POLL

交卷后：`cursor_ack` 未 bump 前只 POLL；`queue_rev` 变化 → 读 §NOW。

探测：`./scripts/cc_gate_watch.sh --pull`（见 `216`）。

---

## BLOCKED

（无。）仅登录/验证码/付费 escalate 用户。
