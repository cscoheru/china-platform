# CC↔Cursor 双向心跳 — 强制对表（消除「审完了对方不知道」）

- 文件编号：`84-stage0-cc-cursor-dual-heartbeat-20260825`
- 日期：2026-08-25
- 效力：**覆盖** `21` T3 / `40` §2 / `82` 中一切「可停 POLL」的软表述
- 用户裁定：两小时巡检制；**双方必须自轮询**；用户不是路由器

---

## §0. 唯一信道

| 信道 | 用途 | 禁止 |
|---|---|---|
| **`origin/main` + `00-CC-CURRENT.md` §META** | 全部协调 | 聊天传话、等对方终端通知 |
| `queue_rev` | 版本号；变了 = 有新指令 | 凭记忆推断「还在旧刀」 |
| `reviews/*.md` | 审验 / 任务书 / 回执正文 | Cursor 聊天里口头 ACK |

**没有第二条信道。** Cursor 推了 CURRENT ≠ CC 自动知道；CC **必须**自己 `git pull`。

---

## §1. 双环（必须同时武装）

```
┌──────────── CC 环 ────────────┐     ┌────────── Cursor 环 ──────────┐
│ 交卷 push → 立即 §POLL        │     │ 发现新回执 → 审验 → push     │
│ sleep 180 → pull → 读 META    │◄───►│ sleep 180 → pull → 读 META    │
│ queue_rev↑ → 执行 §NOW        │     │ cc_head 新 → audit + 下刀     │
│ 禁止 STOP idle 等聊天         │     │ 禁止只在聊天说「过了」        │
└───────────────────────────────┘     └───────────────────────────────┘
         共享真相：origin/main 上的 queue_rev / phase / §NOW
```

| 角色 | 武装时机 | 间隔 | 退出条件 |
|---|---|---|---|
| **CC** | 会话 bootstrap **之后立刻** + **每次交卷 push 之后** | **180s** | 仅 `phase=BLOCKED` 且无其它活；或用户喊停 |
| **Cursor** | 自治监管启动后（`82`） | **180s** | Stage 1 收口或用户喊停 |

**废除** `40` §2「最多 20 轮 ≈ 1h 然后静默停」——自治期内 **无限 POLL**（直到 BLOCKED / 用户停 / Stage 1 收口）。

---

## §2. CC 强制武装（复制即用）

会话第一条命令（`AGENTS.md`）跑完后，若未进入长任务，**立即**武装：

```bash
# 在仓库根；记录起点 rev，然后死循环直到 queue_rev 变化并有 NOW
REV=$(grep -E '\| \*\*queue_rev\*\*' reviews/stage0-gate0-rework-2026-08-23/00-CC-CURRENT.md | head -1)
while true; do
  git fetch origin && git pull --ff-only origin main
  NEW=$(grep -E '\| \*\*queue_rev\*\*' reviews/stage0-gate0-rework-2026-08-23/00-CC-CURRENT.md | head -1)
  PHASE=$(grep -E '\| \*\*phase\*\*' reviews/stage0-gate0-rework-2026-08-23/00-CC-CURRENT.md | head -1)
  echo "CC_HEARTBEAT $(date -Iseconds) $NEW $PHASE"
  if echo "$PHASE" | grep -q 'CC_ACTION_REQUIRED'; then
    # 有活：退出循环，读全文 CURRENT，执行 §NOW
    break
  fi
  if echo "$PHASE" | grep -q 'BLOCKED'; then
    echo "CC_HEARTBEAT blocked — wait user ruling via Cursor CURRENT"
    sleep 180
    continue
  fi
  sleep 180
done
cat reviews/stage0-gate0-rework-2026-08-23/00-CC-CURRENT.md
# → 执行 §NOW；完成后 push 回执；再立刻重新进入本 while
```

**交卷后禁止结束会话：** push 回执 → **马上**再进上面 while（不要等用户「审验」二字）。

多终端：§NOW **单工**（`40` §3）；§POLL **可并行**。

---

## §3. Cursor 强制义务（对称）

每次审验 / 下刀，**同一 push 批次**必须含：

1. audit 或 tasking 文件  
2. **完整** `00-CC-CURRENT.md`（`queue_rev` **+1**，§NOW 可执行，`phase` 正确）  
3. `git push origin HEAD`

发现 CC 新回执的判定（任一条）：

- `reviews/*-cc-*-receipt-*.md` 新文件且不在 `last_audit` 对象里  
- `origin/main` 上出现 CC 业务 commit，且 CURRENT 的 `cc_head` 仍旧  

→ **本 tick 内**完成审验 + 下刀 + push（禁止攒着等用户）。

---

## §4. 握手字段（可选观测，不阻塞）

CURRENT §META 可增加（Cursor 写）：

| 字段 | 含义 |
|---|---|
| `cursor_poll` | `ARMED` / `OFF` |
| `expect_cc_poll` | `REQUIRED`（自治期内恒为 REQUIRED） |

CC **不必**回写磁盘心跳（避免多终端抢写）；用终端 `CC_HEARTBEAT` 日志自证即可。

---

## §5. 与旧文关系

| 文 | 关系 |
|---|---|
| `40` | 主状态机仍有效；§2「20 轮停」→ **本文件废除**，改无限 POLL |
| `21` | T1/T2/T4/T5 有效；T3 间隔以本文件 180s 为准 |
| `82` | Cursor 自治监管仍有效；本文件补 **CC 对称环** |
| `AGENTS.md` | bootstrap 后必须武装 §2 循环 |

---

## §6. 用户只做什么

1. 保证至少 **一个** CC 会话开着并跑过 bootstrap（会自武装 POLL）  
2. 两小时看一眼；**只有 §BLOCKED** 才需要回代号  
3. 不要在 CC/Cursor 之间传「审完了」

— End dual heartbeat —
