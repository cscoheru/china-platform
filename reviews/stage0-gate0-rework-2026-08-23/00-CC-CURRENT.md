# CC 当前队列

> **§META 为唯一真相源** — `84` + `216` + `40` + `82`

---

## META

| 字段 | 值 |
|---|---|
| **phase** | `CC_ACTION_REQUIRED` |
| **queue_rev** | `117` |
| **origin_head** | `dd8d18f` |
| **cc_head** | `dd8d18f`；`278` 已交 |
| **cc_receipt** | `278` |
| **cursor_ack** | `278` |
| **last_audit** | `279` PASS |
| **user_ruling** | Stage 2 **C**；缩刀 **D**；自主推进；O1 OPEN |
| **cursor_poll** | `ARMED` |
| **expect_cc_poll** | `EXEC_THEN_POLL` |
| **updated_at** | `2026-08-26T14:27:00+08:00` |
| **blocked_by** | — |

---

## NOW — CC 执行

**`280`** — 首页导航 smoke（见 `280-stage2-home-nav-smoke-tasking-20260826.md`）。

唤醒：`282-stage0-cursor-cc-wakeup-home-nav-smoke-20260826.md`（第一轮）。

1. 扩展 `smoke-check.py`
2. 跑通 → 补 pack → 回执 **`281`**
3. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

---

## POLL

交卷后：`cursor_ack` 未 bump 前只 POLL；`queue_rev` 变化 → 读 §NOW。

探测：`./scripts/cc_gate_watch.sh --pull`（见 `216`）。

---

## BLOCKED

（无）
