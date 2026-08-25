# CC 当前队列

> **§META 为唯一真相源** — 见 `40-stage0-cc-cursor-deadlock-fix-20260824.md`

---

## META

| 字段 | 值 |
|---|---|
| **phase** | `CC_ACTION_REQUIRED` |
| **queue_rev** | `18` |
| **cursor_head** | `e7cf486` |
| **cc_head** | `c0e55ae`（S1.7 规划回执 `54`；实现尚未入库） |
| **last_audit** | `59-stage0-cursor-cc-wakeup-s17-commit-deadlock-20260825.md` |
| **updated_at** | `2026-08-25T10:25:00+08:00` |

---

## NOW — CC 执行（假死解除；拆步交卷）

1. **取消**当前卡住的「Committing…」工具调用（Esc）
2. **`git pull origin main`** → 读 **`59`**（硬唤醒）+ **`56`**
3. 工作区已有 `scanned_pdf_ocr.py` + tests → **勿重写**；按 `59` §2 **拆步**：
   - 单测新文件（禁止此刻全集）
   - pack
   - 写 **`57`** 回执
   - commit → **`git push origin HEAD` 优先**
   - github 失败 30s 即停
4. 完成后 → **§POLL**

---

## POLL

同 `40` §2。**禁止**再把 verify+commit+dual-push 塞进单一超长工具调用。

---

## BLOCKED

（空）

---

## Cursor 不做

- ❌ 不代 commit / 不写 connector / tests
- ❌ 不改 `gate_thresholds.json`

— Cursor 架构师 @ queue_rev 18 —
