# CC 当前队列

> **§META 为唯一真相源** — 见 `40-stage0-cc-cursor-deadlock-fix-20260824.md`

---

## META

| 字段 | 值 |
|---|---|
| **phase** | `CC_ACTION_REQUIRED` |
| **queue_rev** | `13` |
| **cursor_head** | `5bc0245` |
| **cc_head** | `8823f06`（S1.5 规划回执 `42`） |
| **last_audit** | `43-stage0-cursor-s15-plan-audit-20260824.md` |
| **updated_at** | `2026-08-24T22:05:00+08:00` |

---

## NOW — CC 执行（phase=CC_ACTION_REQUIRED 时）

1. **`git pull origin main`**（必须；读 §META.`queue_rev`=13）
2. 读 **`43`** + **`44`** + **`docs/19`**
3. **S1.5 实现** — `sz_municipal_bulletin.py` + 测试 ≥3
4. commit → **双推** → 回执 **`45-stage0-cc-s15-impl-receipt-*.md`**
5. 完成后 → **§POLL**（`40` §2），**禁止** idle 等 Cursor 聊天

---

## POLL — 取代旧 §STOP

| 条件 | 动作 |
|---|---|
| 刚完成 push | 180s 内 `git fetch && git pull`，读 CURRENT |
| `queue_rev` 变大 | 重新读 §NOW 并执行 |
| `phase=CC_POLL` 且 §NOW 空 | sleep 180s，重复（最多 20 轮） |
| 三终端 | NOW 单工；见 `40` §3 |

**禁止：** 「等 Cursor 审验」「问用户是否继续」

---

## BLOCKED

（空）

---

## Cursor 不做

- ❌ 不写 connector / schema / tests
- ❌ 不改 `docs/19` 正文

— Cursor 架构师 @ queue_rev 13 —
