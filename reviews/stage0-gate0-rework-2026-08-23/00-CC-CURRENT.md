# CC 当前队列

> **§META 为唯一真相源** — `84` + `216` + `40` + `82`

---

## META

| 字段 | 值 |
|---|---|
| **phase** | `CC_ACTION_REQUIRED` |
| **queue_rev** | `143` |
| **origin_head** | `b495400` |
| **cc_head** | `b495400`；`340` 已交 |
| **cc_receipt** | `340` |
| **cursor_ack** | `340` |
| **last_audit** | `342` PASS |
| **user_ruling** | Stage 2 **C**；缩刀 **D**；源工程 **Cursor 代判（`341`）**；AUTH/付费才问用户；**湖北 JS 壳 → 暂缓** |
| **cursor_poll** | `ARMED` |
| **expect_cc_poll** | `EXEC_THEN_POLL` |
| **updated_at** | `2026-08-26T18:04:00+08:00` |
| **blocked_by** | — |

---

## NOW — CC 执行

**`343`** — 暂缓湖北 + 深圳 HTML connector（见 `343-…tasking…md`）。

1. registry 湖北 `enabled=FALSE`（注明 JS-shell 暂缓）
2. 深圳 `MUNICIPAL_BULLETIN` pilot + live；成功可 pin（`341`）
3. 补 pack → 回执 **`344`**
4. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

---

## POLL

交卷后：`cursor_ack` 未 bump 前只 POLL；`queue_rev` 变化 → 读 §NOW。

探测：`./scripts/cc_gate_watch.sh --pull`（见 `216`）。

---

## BLOCKED

（无。）仅登录/验证码/付费 escalate 用户。
