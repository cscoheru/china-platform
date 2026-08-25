# CC 当前队列

> **§META 为唯一真相源** — 见 `40` + **`60`（OCR pack 死锁）**

---

## META

| 字段 | 值 |
|---|---|
| **phase** | `CC_ACTION_REQUIRED` |
| **queue_rev** | `19` |
| **cursor_head** | `3a13301` |
| **cc_head** | `c0e55ae`（实现文件+`57` 已在工作区未入库） |
| **last_audit** | `60-stage0-cursor-s17-pack-pytest-ocr-deadlock-20260825.md` |
| **updated_at** | `2026-08-25T10:45:00+08:00` |

---

## NOW — CC 立即交卷（假等待已 kill）

1. **Esc** 取消「Committing / Pack 600s」  
2. `git pull` → 读 **`60`**  
3. **`SKIP_PYTEST=1 SKIP_PSQL=1 python3 scripts/build_evidence_pack.py`**（禁止裸跑 pack）  
4. 或 pack>3min → 跳过 pack，直接 commit  
5. commit 三文件（+manifest 若有）→ **`git push origin HEAD`**  
6. github 失败即停 → §POLL  

实现与 `57` **已在磁盘** — **禁止重写 connector/tests**。

---

## POLL

同 `40`。禁止再 background wait pack 600s。

---

## BLOCKED

（空）

— Cursor 架构师 @ queue_rev 19 —
