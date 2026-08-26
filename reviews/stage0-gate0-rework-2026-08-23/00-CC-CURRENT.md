# CC 当前队列

> **§META 为唯一真相源** — `84` + `216` + `40` + `82`

---

## META

| 字段 | 值 |
|---|---|
| **phase** | `CC_ACTION_REQUIRED` |
| **queue_rev** | `87` |
| **origin_head** | `74f1657` |
| **cc_head** | `4f3db12`；`215` 已交；**`218` 未动** |
| **cc_receipt** | `215` |
| **cursor_ack** | `215` |
| **last_audit** | `217` PASS |
| **wakeup** | `220` + `221`（对表 resync） |
| **user_ruling** | Stage 2 **C**；缩刀 **D** |
| **cursor_poll** | `ARMED` |
| **expect_cc_poll** | `EXEC_THEN_POLL` |
| **updated_at** | `2026-08-26T08:40:00+08:00` |
| **blocked_by** | — |

---

## NOW — CC 执行

**`218`** — S2.4-lite budget DDL 缩刀（见 `218-stage2-s24-lite-ddl-impl-tasking-20260826.md`）。

**唤醒 `220` / 对表 `221`：** 先 `git pull` + `./scripts/cc_gate_watch.sh --pull`；`cursor_ack=215` 已 ACK，勿再等审验。

1. migration `011`（+ 可选空 seed）；不写 dbt
2. 最小 pytest → 全绿
3. 补 pack → commit → `origin` + `github` → 回执 **`219`**
4. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

---

## POLL

交卷后：`cursor_ack` 未 bump 前只 POLL；`queue_rev` 变化 → 读 §NOW。

探测：`./scripts/cc_gate_watch.sh --pull`（见 `216`）。

---

## BLOCKED

（无）
