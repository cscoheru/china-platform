# CC 当前队列

> **§META 为唯一真相源** — `84` + `216` + `40` + `82`

---

## META

| 字段 | 值 |
|---|---|
| **phase** | `CC_ACTION_REQUIRED` |
| **queue_rev** | `129` |
| **origin_head** | `92df1c9` |
| **cc_head** | `92df1c9`；`306` 已交 |
| **cc_receipt** | `306` |
| **cursor_ack** | `306` |
| **last_audit** | `307` PASS |
| **user_ruling** | Stage 2 **C**；缩刀 **D**；自主推进；**O1 WAITING_FILE**；不爬网 |
| **cursor_poll** | `ARMED` |
| **expect_cc_poll** | `EXEC_THEN_POLL` |
| **updated_at** | `2026-08-26T16:15:00+08:00` |
| **blocked_by** | 真 O1 仍需 allowlist 投递（docs/48）|

---

## NOW — CC 执行

**`308`** — O3 OCR 生产路径规划（见 `308-stage2-o3-ocr-prod-path-plan-tasking-20260826.md`）。  
唤醒：`310-stage0-cursor-cc-wakeup-o3-ocr-plan-20260826.md`（禁止 idle）。

1. 写 `docs/49`（只规划）
2. 补 pack → 回执 **`309`**
3. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

---

## POLL

交卷后：`cursor_ack` 未 bump 前只 POLL；`queue_rev` 变化 → 读 §NOW。

探测：`./scripts/cc_gate_watch.sh --pull`（见 `216`）。

---

## BLOCKED

（无。）
