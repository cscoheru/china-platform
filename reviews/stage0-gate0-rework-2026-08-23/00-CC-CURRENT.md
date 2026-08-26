# CC 当前队列

> **§META 为唯一真相源** — `84` + `216` + `40` + `82`

---

## META

| 字段 | 值 |
|---|---|
| **phase** | `CC_ACTION_REQUIRED` |
| **queue_rev** | `139` |
| **origin_head** | `218b4d6` |
| **cc_head** | `218b4d6`；`331` 已交 |
| **cc_receipt** | `331` |
| **cursor_ack** | `331` |
| **last_audit** | `332` PASS |
| **user_ruling** | Stage 2 **C**；缩刀 **D**；**不再等用户投喂**；官方公开源自动获取+结构化呈现；**遇登录/验证码/付费 → 报告用户（用户可提供授权），禁止绕过** |
| **cursor_poll** | `ARMED` |
| **expect_cc_poll** | `EXEC_THEN_POLL` |
| **updated_at** | `2026-08-26T17:21:30+08:00` |
| **blocked_by** | — |

---

## NOW — CC 执行

**`333`** — live 探测 + SHA 漂移候选（见 `333-…tasking…md`）。

1. drift → `CANDIDATE_AUTO` 归档（非 O1 收口）+ drift 报告
2. 一次 NBS `--live` 探测；AUTH 遇阻报告用户
3. 补 pack → 回执 **`334`**
4. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

---

## POLL

交卷后：`cursor_ack` 未 bump 前只 POLL；`queue_rev` 变化 → 读 §NOW。

探测：`./scripts/cc_gate_watch.sh --pull`（见 `216`）。

---

## BLOCKED

（无。）需授权源一律 escalate 用户，不绕过。
