# CC 当前队列

> **§META 为唯一真相源** — `84` + `40` + `82`

---

## META

| 字段 | 值 |
|---|---|
| **phase** | `CC_ACTION_REQUIRED` |
| **queue_rev** | `75` |
| **cursor_head** | `26f8db8` |
| **cc_head** | `196fdc9` + `188`；S2.2 规划未交 |
| **last_audit** | `189` |
| **user_ruling** | `D` / Stage 2 `C` |
| **cursor_poll** | `ARMED` |
| **expect_cc_poll** | `REQUIRED` |
| **updated_at** | `2026-08-25T23:15:00+08:00` |
| **wakeup** | `192` + `193`（二次催办 S2.2 规划） |

---

## NOW — CC 执行

1. **`git pull origin main`**（`queue_rev`=75）
2. 读 **`193`** + **`190`**
3. **S2.2 规划** — `docs/37`；回执 **`191`**
4. commit → **origin 优先**
5. → **`84` POLL**

---

## POLL

同 `84`。

---

## BLOCKED

（空）
