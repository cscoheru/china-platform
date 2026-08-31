# 00-DUAL-POLL — Cursor ↔ CC 双向轮询协议（2026-08-31）

> 用户裁定：本 Cursor 会话制定轮询计划。  
> 对表唯一真相：`origin/main`（双推后）+ `00-EXEC-QUEUE.md` + `docs/00-COMPASS.md`。  
> **禁止**靠聊天传「做完了吗」。

---

## 0. 角色

| 端 | 节奏 | 触发条件 | 动作 |
|---|---|---|---|
| **Cursor（本会话）** | **每 30 分钟** | 始终轮询（本会话 loop 武装期间） | `git fetch/pull` → 判是否有待审回执 → 有则审验+签发下一单+更新队列 |
| **CC（执行端）** | **每 5 分钟** | **仅当本刀已 commit 且双推成功之后** | `git pull` → 读审验报告 + §NOW 新任务书 → 有则执行；无则继续 5m POLL |
| **CC** | **不轮询** | 尚未 commit/push 本刀交付 | 专心实现；禁止空转问 Cursor |

---

## 1. 「已执行完毕」判定（Cursor）

同时满足任一充分条件即进入审验：

1. `origin/main` 出现当前 §NOW 刀号的 `*-cc-*-receipt-*.md`（且尚无同刀 `*-audit-PASS*` / `*-audit-FAIL*`）  
2. 或 `00-EXEC-QUEUE` §CURRENT 将该刀标为 `DELIVERED` / `DELIVERED · 待审`，且 `cc_head` 相对上次审计已前进  
3. 探针：`./scripts/dual_poll_status.sh --pull` 输出 `CURSOR_ACTION=AUDIT_NOW`

若仅有本地未推送改动 → **不算**完毕（CC 未满足双推门闩）。

---

## 2. Cursor tick（30m）清单

```text
1. git fetch origin && git pull --ff-only origin main（失败则报告，不强推）
2. ./scripts/dual_poll_status.sh
3. 若 CURSOR_ACTION=AUDIT_NOW:
     - 读回执 → 独立复验（pytest/SQL/红线）
     - 写 *-audit-PASS|FAIL*
     - PASS → 签发下一刀 tasking；更新 EXEC-QUEUE + COMPASS
     - 双推（若用户已授常设「审计后双推」；否则写清待用户授权）
4. 若 CURSOR_ACTION=WAIT:
     - 一行状态：仍等 CC / 刀号 / 最新 origin SHA
5. 保持 30m loop；禁止「STOP idle」
```

---

## 3. CC 交卷后门闩 + 5m POLL

**交卷定义：** 回执已写 + **commit** + **`git push origin HEAD && git push github HEAD` 成功**。

交卷后立刻进入：

```bash
while true; do
  git fetch origin && git pull --ff-only origin main
  ./scripts/dual_poll_status.sh
  # CC_ACTION=EXECUTE_NOW → 读 audit + 新 tasking，退出循环去执行
  # CC_ACTION=POLL → sleep 300（5 分钟）
  # 若本刀从未 push → 禁止进入本循环
  sleep 300
done
```

**未 commit/push：禁止 5m 轮询**（避免空烧上下文）。

---

## 4. 与旧协议关系

- 覆盖 `AGENTS.md` 中「交卷后 180s POLL」的默认间隔：**交卷后改为 300s**；未交卷不 POLL。  
- `scripts/cc_gate_watch.sh` 仍可用；本文件 + `dual_poll_status.sh` 为 M2 起首选。  
- `00-CC-CURRENT.md` 仍冻结；调度只认 `00-EXEC-QUEUE.md`。

---

## 5. 停止

- 用户说「停轮询 / stop loop」→ Cursor 杀 30m loop PID。  
- CC 收到新 §NOW 并开始执行 → 退出 5m POLL，直到再次交卷。

— End —
