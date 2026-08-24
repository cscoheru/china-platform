# CC 当前队列（唯一入口 — 每次开工先读本文件）

> **路径固定：** `reviews/stage0-gate0-rework-2026-08-23/00-CC-CURRENT.md`  
> Cursor 每次下发/审验后**必须更新本文件**；CC **禁止**等用户口头转发。  
> 更新时间：2026-08-24（Cursor；用户交接完成 + 轮询协议已上远端）

---

## NOW（立刻做）

1. **`git pull origin main`**（期望 HEAD ≥ `bc26ca8`，含本文件与 `20`/`21`）
2. 读 `21-stage0-cc-proactive-poll-standing-order-20260824.md`
3. **IDLE** — 无业务任务；**不要**问用户「下一步」

### 已关闭（勿重复）

| 项 | 状态 | 证据 |
|---|---|---|
| 陕西 research-track | ✅ | `9d0d30e` |
| Pack 440/0 | ✅ | `11` + 后续 |
| U-4 = A | ✅ | E-1 非门控 |
| GitHub F + 双端同步 | ✅ | `19` / `f0974d4`+ |
| 轮询协议入库 | ✅ | `bc26ca8`（`00`/`20`/`21`） |
| 用户传话链路 | ✅ 关闭 | 用户已交 Cursor；见 `22` |

### 对照审验

- `22-stage0-cursor-handoff-complete-20260824.md`（交接 ACK）

---

## NEXT（无需用户指示）

| 优先级 | 动作 |
|---|---|
| P0 | 会话开始 / 空闲 15–30min → `git pull` → 读本文件 |
| P1 | 见未入库 `reviews/` → commit → 双推 `origin`+`github` |
| P2 | IDLE：不进 Stage 1；不改门槛；不 ping 用户 |

---

## BLOCKED（仅 Cursor 会话裁定）

| 代号 | 状态 |
|---|---|
| （无） | — |

---

## STOP

§NOW 完成或 IDLE → 有 commit 则双推 → **停** → 下一刀只来自 Cursor 更新本文件

— Cursor 维护；CC 勿改 §BLOCKED —
