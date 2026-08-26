# CC 当前队列

> **§META 为唯一真相源** — `84` + `216` + `40` + `82`

---

## META

| 字段 | 值 |
|---|---|
| **phase** | `CC_ACTION_REQUIRED` |
| **queue_rev** | `121` |
| **origin_head** | `24a74ae` |
| **cc_head** | `24a74ae`；`285` 已交 |
| **cc_receipt** | `285` |
| **cursor_ack** | `285` |
| **last_audit** | `286` PASS |
| **user_ruling** | Stage 2 **C**；缩刀 **D**；自主推进；**O1 无材料 OPEN**（已入 docs/45）|
| **cursor_poll** | `ARMED` |
| **expect_cc_poll** | `EXEC_THEN_POLL` |
| **updated_at** | `2026-08-26T15:07:00+08:00` |
| **blocked_by** | — |

---

## NOW — CC 执行

**`287`** — S2.7-b-full-dbt-skel（见 `287-stage2-s27b-full-dbt-mart-skeleton-tasking-20260826.md`）。

1. 落地 `mart_city_evidence_chain` + `mart_city_seven_dim_overview` dbt view 骨架（`docs/47` §3.1/§3.2）
2. 最小 pytest → 补 pack → 回执 **`288`**
3. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

---

## POLL

交卷后：`cursor_ack` 未 bump 前只 POLL；`queue_rev` 变化 → 读 §NOW。

探测：`./scripts/cc_gate_watch.sh --pull`（见 `216`）。

---

## BLOCKED

（无）
