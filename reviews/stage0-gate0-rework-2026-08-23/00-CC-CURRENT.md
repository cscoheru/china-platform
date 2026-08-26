# CC 当前队列

> **§META 为唯一真相源** — `84` + `216` + `40` + `82`

---

## META

| 字段 | 值 |
|---|---|
| **phase** | `CC_ACTION_REQUIRED` |
| **queue_rev** | `123` |
| **origin_head** | `0ba8477` |
| **cc_head** | `0ba8477`；`291` 已交 |
| **cc_receipt** | `291` |
| **cursor_ack** | `291` |
| **last_audit** | `292` PASS |
| **user_ruling** | Stage 2 **C**；缩刀 **D**；自主推进；**尽快真数据**；**O1 WAITING_FILE**（不伪造）|
| **cursor_poll** | `ARMED` |
| **expect_cc_poll** | `EXEC_THEN_POLL` |
| **updated_at** | `2026-08-26T15:26:00+08:00` |
| **blocked_by** | 真 O1 仍需用户投递 allowlist 文件（见 docs/48）；本刀先通 demo→mart |

---

## NOW — CC 执行

**`293`** — mart demo-join（见 `293-stage2-s27b-full-mart-demo-join-tasking-20260826.md`）。

1. 两 mart view 产出 demo 行（`is_demo=true`，SHA `'0'*64`）
2. 更新 pytest → 补 pack → 回执 **`294`**
3. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

---

## POLL

交卷后：`cursor_ack` 未 bump 前只 POLL；`queue_rev` 变化 → 读 §NOW。

探测：`./scripts/cc_gate_watch.sh --pull`（见 `216`）。

---

## BLOCKED

（无。）真 O1 物理依赖 allowlist 投递 — 与本刀并行，不阻塞 demo→mart。
