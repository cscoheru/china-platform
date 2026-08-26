# CC 当前队列

> **§META 为唯一真相源** — `84` + `216` + `40` + `82`

---

## META

| 字段 | 值 |
|---|---|
| **phase** | `CC_ACTION_REQUIRED` |
| **queue_rev** | `124` |
| **origin_head** | `025904c` |
| **cc_head** | `025904c`；`294` 已交 |
| **cc_receipt** | `294` |
| **cursor_ack** | `294` |
| **last_audit** | `295` PASS |
| **user_ruling** | Stage 2 **C**；缩刀 **D**；自主推进；**尽快看见数据**；**O1 WAITING_FILE** |
| **cursor_poll** | `ARMED` |
| **expect_cc_poll** | `EXEC_THEN_POLL` |
| **updated_at** | `2026-08-26T15:31:00+08:00` |
| **blocked_by** | 真 O1 仍需 allowlist 投递（docs/48）；本刀先对齐前端可见 demo |

---

## NOW — CC 执行

**`296`** — 前端 mart demo 契约对齐（见 `296-stage2-frontend-mart-demo-parity-tasking-20260826.md`）。

1. 对齐 `mart_city_demo.ts` 等与 dbt demo-join
2. smoke/pytest → 补 pack → 回执 **`297`**
3. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

---

## POLL

交卷后：`cursor_ack` 未 bump 前只 POLL；`queue_rev` 变化 → 读 §NOW。

探测：`./scripts/cc_gate_watch.sh --pull`（见 `216`）。

---

## BLOCKED

（无。）
