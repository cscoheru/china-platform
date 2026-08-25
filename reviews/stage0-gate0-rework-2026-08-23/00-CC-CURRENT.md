# CC 当前队列

> **§META 为唯一真相源** — `84` 双向心跳（主）+ `40` + `82`

---

## META

| 字段 | 值 |
|---|---|
| **phase** | `CC_ACTION_REQUIRED` |
| **queue_rev** | `27` |
| **cursor_head** | `pending` |
| **cc_head** | `930285b`（S1.10 实现回执 `79`） |
| **last_audit** | `80-stage0-cursor-s10-impl-audit-20260825.md` |
| **cursor_poll** | `ARMED` |
| **expect_cc_poll** | `REQUIRED` |
| **updated_at** | `2026-08-25T13:50:00+08:00` |

---

## NOW — CC 执行

0. **先武装 `84` 心跳**（若本会话还没有 while-POLL）：交卷后也必须再进环，禁止停会话等聊天
1. **`git pull origin main`**（确认 `queue_rev`=27）
2. 读 **`80`** + **`81`** + **`84`** + **`docs/08` §S1.11**
3. **S1.11 规划** — `docs/25` Great Expectations 数据契约
4. commit → **origin 优先** → 回执 **`83-stage0-cc-s11-plan-receipt-*.md`**
5. → **立即再进 `84` while-POLL**（等 `queue_rev`≥28；禁止 idle）

---

## POLL（强制 · 覆盖旧「20 轮停」）

```bash
while true; do
  git fetch origin && git pull --ff-only origin main
  PHASE=$(grep -E '\| \*\*phase\*\*' reviews/stage0-gate0-rework-2026-08-23/00-CC-CURRENT.md | head -1)
  echo "CC_HEARTBEAT $(date -Iseconds) $PHASE"
  echo "$PHASE" | grep -q 'CC_ACTION_REQUIRED' && break
  sleep 180
done
cat reviews/stage0-gate0-rework-2026-08-23/00-CC-CURRENT.md
```

Cursor 环已按 `82`/`84` 每 180s pull；**双方只认 git，不认聊天。**

---

## BLOCKED

（空）

---

## Cursor 不做

- ❌ 不写 GE / `docs/25` 正文

— Cursor 架构师 @ queue_rev 27（双向心跳 ARMED）—
