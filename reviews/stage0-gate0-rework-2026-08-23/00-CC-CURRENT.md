# CC 当前队列（唯一入口 — 每次开工先读本文件）

> **路径固定：** `reviews/stage0-gate0-rework-2026-08-23/00-CC-CURRENT.md`  
> Cursor 每次下发/审验后**必须更新本文件**；CC **禁止**等用户口头转发。  
> 更新时间：2026-08-24（Cursor；GitHub F 同步审验后）

---

## NOW（立刻做）

1. **`git pull origin main`**（拿最新 `00-CC-CURRENT` / 审验文件）
2. 读本文件 §NOW + §NEXT；再读文末「对照审验」链接
3. 本轮：**无阻塞业务任务**。执行 §IDLE 自律，然后 STOP 写短回执（可选，仅当有新 commit）

### 已关闭（勿重复）

| 项 | 状态 | 证据 |
|---|---|---|
| 陕西 research-track | 已入库 | `9d0d30e` 系 |
| Pack 440/0 | 已过 | `11` P0 + 后续 commit |
| U-4 = A | 用户已裁 | E-1 非门控；不宣布 OCR PASS |
| GitHub = F + 双端同步 | ✅ | CC `19`；本机复验 `origin`=`github`=`f0974d4` |
| 凭证 | OK | `16` |

### 对照审验（本轮）

- 读：`20-stage0-cursor-github-sync-ack-and-proactive-loop-20260824.md`
- 读：`21-stage0-cc-proactive-poll-standing-order-20260824.md`（常驻轮询）

---

## NEXT（无需用户指示即可做）

| 优先级 | 动作 | 完成标准 |
|---|---|---|
| P0 | 服从 `21` 轮询：每次会话开始 / 空闲 15–30min / 感知到 `reviews/` 或 `origin` 有新 Cursor 文件 → **立即** `git pull` 并执行最新 `00-CC-CURRENT` | 不向用户要「下一步」 |
| P1 | 工作区若有未跟踪 Cursor/CC reviews → commit → **双推** `origin`+`github` | `git status` 空；两侧同 SHA |
| P2 | 无任务时：保持干净；**不要**进 Stage 1；**不要**改门槛 | STOP 即可，不必 ping 用户 |

---

## BLOCKED（仅这些才等用户 — 在 Cursor 会话裁定）

| 代号 | 何时出现 | CC 动作 |
|---|---|---|
| （当前无） | — | — |

历史已裁：U-4=A；GitHub=F；凭证 OK。

---

## STOP 条件

- `00-CC-CURRENT` §NOW 全部完成或为空闲  
- 已 `git push origin`（+ github 若有新 commit）  
- 写回执到 `reviews/` **仅当**有实质结果；纯空闲可省略  
- **然后停** — 下一刀只来自 Cursor 更新本文件，**不是**用户传话

— 本文件由 Cursor 覆盖更新；CC 勿改 §BLOCKED 口径 —
