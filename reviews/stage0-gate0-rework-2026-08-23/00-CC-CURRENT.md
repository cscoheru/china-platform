# CC 当前队列

> **§META 为唯一真相源** — `84` + `216` + `40` + `82`

---

## META

| 字段 | 值 |
|---|---|
| **phase** | `CC_ACTION_REQUIRED` |
| **queue_rev** | `122` |
| **origin_head** | `30f5ed2` |
| **cc_head** | `30f5ed2`；`288` 已交 |
| **cc_receipt** | `288` |
| **cursor_ack** | `288` |
| **last_audit** | `289` PASS |
| **user_ruling** | Stage 2 **C**；缩刀 **D**；自主推进；**尽快真数据**；**O1 无材料 OPEN**（不伪造/不爬网）|
| **cursor_poll** | `ARMED` |
| **expect_cc_poll** | `EXEC_THEN_POLL` |
| **updated_at** | `2026-08-26T15:18:00+08:00` |
| **blocked_by** | 真数据需用户把合法持有文件放入 allowlist（见 `290` / docs/48）|

---

## NOW — CC 执行

**`290`** — 真 SHA 投递上线（见 `290-stage2-real-sha-intake-live-tasking-20260826.md`）。

1. `docs/48` + `scripts/intake_real_sha_if_present.py` + pytest
2. 有文件则跑通；无文件 → `WAITING_FILE`（不伪造）→ 回执 **`291`**
3. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

---

## POLL

交卷后：`cursor_ack` 未 bump 前只 POLL；`queue_rev` 变化 → 读 §NOW。

探测：`./scripts/cc_gate_watch.sh --pull`（见 `216`）。

---

## BLOCKED

（无用户裁定代号。真数据物理依赖：allowlist 文件投递 — 见 `290`。）
