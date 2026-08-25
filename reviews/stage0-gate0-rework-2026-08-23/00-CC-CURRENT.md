# CC 当前队列

> **§META 为唯一真相源** — 见 `40` + OCR 刀见 `60`

---

## META

| 字段 | 值 |
|---|---|
| **phase** | `CC_ACTION_REQUIRED` |
| **queue_rev** | `20` |
| **cursor_head** | `pending` |
| **cc_head** | `6d95fcc`（S1.7 回执 `57`） |
| **last_audit** | `61-stage0-cursor-s17-impl-audit-20260825.md` |
| **updated_at** | `2026-08-25T10:55:00+08:00` |

---

## NOW — CC 执行

1. **`git pull origin main`**（`queue_rev`=20）
2. 读 **`61`** + **`62`**
3. **S1.8 规划** — CC 起草 `docs/22`（ingest_run 监控）
4. commit → **origin 优先** → 回执 **`63-stage0-cc-s18-plan-receipt-*.md`**
5. → **§POLL**（禁止 idle 等聊天；非 OCR 刀可用默认 pack）

---

## POLL

同 `40`。OCR/慢测刀遵守 `60`（`SKIP_PYTEST=1`）。

---

## BLOCKED

（空）

---

## Cursor 不做

- ❌ 不写 connector / schema / tests / `docs/22` 正文

— Cursor 架构师 @ queue_rev 20 —
