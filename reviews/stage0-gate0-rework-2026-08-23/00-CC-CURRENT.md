# CC 当前队列

> **§META 为唯一真相源** — `84` + `216` + `40` + `82`

---

## META

| 字段 | 值 |
|---|---|
| **phase** | `CC_ACTION_REQUIRED` |
| **queue_rev** | `140` |
| **origin_head** | `6a73359` |
| **cc_head** | `6a73359`；`334` 已交 |
| **cc_receipt** | `334` |
| **cursor_ack** | `334` |
| **last_audit** | `335` PASS |
| **user_ruling** | Stage 2 **C**；缩刀 **D**；不再等投喂；AUTH 遇阻报告用户；**NBS SHA 漂移等用户 (a)更新哈希/(b)换稳定直链** |
| **cursor_poll** | `ARMED` |
| **expect_cc_poll** | `EXEC_THEN_POLL` |
| **updated_at** | `2026-08-26T17:39:30+08:00` |
| **blocked_by** | `USER_NBS_SHA_DRIFT`（并行不阻塞湖北刀） |

---

## NOW — CC 执行

**`336`** — 湖北 EXCEL 公开源 connector（见 `336-…tasking…md`）。

1. pilot=`tjj.hubei.gov.cn` / `PROVINCIAL_BULLETIN`；禁 headless
2. 复用 AUTH + drift；一次 live 探测
3. 补 pack → 回执 **`337`**
4. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

---

## POLL

交卷后：`cursor_ack` 未 bump 前只 POLL；`queue_rev` 变化 → 读 §NOW。

探测：`./scripts/cc_gate_watch.sh --pull`（见 `216`）。

---

## BLOCKED

NBS 正式 `O1_AUTO_INTAKED` 等用户 (a)/(b)。需授权源 escalate 用户，不绕过。
