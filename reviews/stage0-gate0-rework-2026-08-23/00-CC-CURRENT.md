# CC 当前队列

> **§META 为唯一真相源** — `84` + `216` + `40` + `82`

---

## META

| 字段 | 值 |
|---|---|
| **phase** | `CC_ACTION_REQUIRED` |
| **queue_rev** | `144` |
| **origin_head** | `a07d657` |
| **cc_head** | `a07d657`；`344` 已交 |
| **cc_receipt** | `344` |
| **cursor_ack** | `344` |
| **last_audit** | `345` PASS |
| **user_ruling** | Stage 2 **C**；缩刀 **D**；源工程 **Cursor 代判（`341`）**；湖北 JS 暂缓；**深圳 HTTPS SSL 暂缓（禁 HTTP pin）**；下一刀本地样本结构化 |
| **cursor_poll** | `ARMED` |
| **expect_cc_poll** | `EXEC_THEN_POLL` |
| **updated_at** | `2026-08-26T18:21:30+08:00` |
| **blocked_by** | — |

---

## NOW — CC 执行

**`346`** — registry 本地样本结构化提取 + NBS 再探（见 `346-…tasking…md`）。

1. `--from-local-sample` → WORM + extract JSON；`REGISTRY_SAMPLE_INTAKED` / `is_demo=true`
2. 深圳 registry 注 SSL 暂缓；NBS 再 `--live` 一次
3. 补 pack → 回执 **`347`**
4. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

---

## POLL

交卷后：`cursor_ack` 未 bump 前只 POLL；`queue_rev` 变化 → 读 §NOW。

探测：`./scripts/cc_gate_watch.sh --pull`（见 `216`）。

---

## BLOCKED

（无。）仅登录/验证码/付费 escalate 用户。
