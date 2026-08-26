# CC 当前队列

> **§META 为唯一真相源** — `84` + `216` + `40` + `82`

---

## META

| 字段 | 值 |
|---|---|
| **phase** | `POLL` |
| **queue_rev** | `151` |
| **origin_head** | `bdf4b85` |
| **cc_head** | `bdf4b85`；`365` 已交 |
| **cc_receipt** | `365` |
| **cursor_ack** | `365` |
| **last_audit** | `366` PASS |
| **user_ruling** | Stage 2 **C**；缩刀 **D**；Cursor 代判；**公开拉取+结构化双轨+刷新+ops 手册里程碑已齐** → CC POLL |
| **cursor_poll** | `ARMED` |
| **expect_cc_poll** | `POLL` |
| **updated_at** | `2026-08-26T19:39:30+08:00` |
| **blocked_by** | — |

---

## NOW — CC 执行

（无新刀。）`cursor_ack=365`；只 **`84` POLL**，直到 `queue_rev` 再 bump。

---

## POLL

`./scripts/cc_gate_watch.sh --pull`（见 `216`）。`CC_ACTION=EXECUTE_NOW` 才读新 §NOW。

---

## BLOCKED

（无。）仅登录/验证码/付费 escalate 用户。

## 里程碑（只读提示，非 PASS 宣告）

- 预览：https://china.3strategy.cc/public-extracts （sample 63 + live 候选 60）
- 手册：`docs/53`
- 刷新：`--refresh-live-candidate --live --confirm-live=…`
