# CC 当前队列（唯一入口 — 每次开工先读本文件）

> **路径固定：** `reviews/stage0-gate0-rework-2026-08-23/00-CC-CURRENT.md`  
> 更新时间：2026-08-24 — **Stage 1 已授权启动**

---

## NOW（立刻做）

1. **`git pull origin main`**
2. 读 **`23-stage1-kickoff-20260824.md`**（Stage 1 启动任务书）
3. 执行 **`23` §2 任务 S1-K0**（Gate 0 正式收口文档）→ commit → 双推
4. 执行 **`23` §2 任务 S1-K1**（Stage 1 规划分支 / `docs/08` 状态更新）→ 停等 Cursor 审验 **S1.1 技术方案** 后再动 PostgreSQL 部署

### Gate 0 终态（用户 + Cursor 裁定，2026-08-24）

| 项 | 状态 |
|---|---|
| Gate 0 | ✅ **CLOSED**（U-4=A；用户授权启动 Stage 1） |
| E-1 / spike 04 门控 | ⚪ 非门控（U-3） |
| P-1 / P-2 | 不变 |
| 工程基线 | 251 tests；pack 440/0；陕西 research-track |

### 对照

- `23-stage1-kickoff-20260824.md`
- `docs/08-mvp-plan.md` §2（Stage 1 任务清单）

---

## NEXT

| 优先级 | 动作 |
|---|---|
| P0 | 完成 S1-K0/K1 后写回执 `24-stage0-cc-stage1-kickoff-receipt-*.md` |
| P1 | `git push origin` + `github`（github 失败则重试，不 force 除非已裁 F） |
| P2 | **不要**自行开始全国抓取 / 官员评分 / DSH / 降 OCR 门槛 |

---

## BLOCKED

| 代号 | 状态 |
|---|---|
| S1.1 生产 PostgreSQL 部署 | ⏸ 等 Cursor 审验 S1-K1 规划后开 §3 |

---

## STOP

S1-K0/K1 完成并双推（或 github 停报）→ 回执 → **STOP** 等 Cursor `23` §3 或新 `00` 更新

— Cursor 维护 —
