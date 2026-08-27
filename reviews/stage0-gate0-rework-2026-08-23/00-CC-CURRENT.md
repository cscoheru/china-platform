# CC 当前队列

> **§META 为唯一真相源** — `84` + `216` + `40` + `82`

---

## META

| 字段 | 值 |
|---|---|
| **phase** | `CC_ACTION_REQUIRED` |
| **queue_rev** | `193` |
| **origin_head** | `576eaff` |
| **cc_head** | `576eaff`；等 `446` |
| **cc_receipt** | `444` |
| **cursor_ack** | `444` |
| **last_audit** | `445` PASS |
| **user_ruling** | Stage 2 **C**；缩刀 **D**；POLL 空闲 → 续刀 |
| **cursor_poll** | `ARMED` |
| **expect_cc_poll** | `EXECUTE_NOW` |
| **updated_at** | `2026-08-27T09:32:00+08:00` |
| **blocked_by** | — |

---

## NOW — CC 执行

读并执行：`446-stage2-preview-redeploy-home-deeplinks-tasking-20260826.md`

摘要：预览 redeploy + 首页 deeplink HTTP 验收；交回执 **`446`**。**必须双推**。

**源站纠正（勿连 hk）：** `china.3strategy.cc` → SSH **`newvps`**（`207.57.133.177:52134`），路径 **`/opt/china-platform/frontend`**，systemd `china-platform-frontend`，nginx → `127.0.0.1:3000`。**不是** `hk`/`103.59.103.85`（该机无 `/opt/china-platform`）。Cursor 已于该源站完成 rsync+build+restart；CC 做 HTTP 验收 + 回执 **`446`** 即可。

完成后：双推 → **`84` POLL**。

---

## POLL

`./scripts/cc_gate_watch.sh --pull`（见 `216`）。

---

## BLOCKED

（无。）
