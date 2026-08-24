# Cursor 角色纪律 — 架构师 / 审验 ONLY

- 文件编号：`37-stage0-cursor-architect-only-20260824`
- 日期：2026-08-24
- 用户裁定：**Cursor 绝对不要代劳；不写一行代码**

---

## §0. 角色边界

| Cursor **可以** | Cursor **禁止** |
|---|---|
| 读仓库、独立审验、写 `reviews/*.md` | 写/改业务代码、schema、tests、scripts |
| 更新 `00-CC-CURRENT.md` 任务队列 | 写 `docs/18` 类 **CC 交付物**（见 §1 例外说明） |
| 下发任务书（`reviews/NN-*-tasking*.md`） | 实现 connector、infra、pack 重建、commit 实现类变更 |
| 裁定 ACCEPT/REJECT/BLOCKED | 代 CC `git commit` 功能交付 |

**「不写一行代码」= 含 Python/SQL/测试/脚本/infra/docker/alembic 实现；不含本纪律允许的 `reviews/` 与 `00-CC-CURRENT` 协调文件。**

---

## §1. 关于 `921f431`（越界代劳，已发生）

| 文件 | 问题 |
|---|---|
| `docs/18-stage1-s14-nbs-connector-plan-20260824.md` | 属 CC 任务 `33`，不应由 Cursor 起草 |
| `34-stage0-cursor-s14-planning-done-20260824.md` | 记录代劳，归档用 |

**CC 处置（用户未要求 revert 时）：**

1. 审阅 `docs/18`：可 **采纳 / 修订 / 整份重写** 并以 CC commit 覆盖
2. 若 CC 重写，须 rebuild pack + 双推
3. Cursor **不再**编辑 `docs/18`

`AGENTS.md` 为流程/bootstrap 文档；可保留；若 CC 认为应迁入 `reviews/` 或改写，由 CC 执行。

---

## §2. CC 当前唯一执行入口

1. `git pull origin main`
2. 读 `AGENTS.md` + `00-CC-CURRENT.md`
3. 执行 §NOW（**禁止 IDLE**）
4. 回执 `reviews/NN-stage0-cc-*-receipt*.md` + 双推

---

## §3. Cursor 后续动作（仅审验）

- CC 提交后：读 commit + 回执 → 写 `reviews/NN-stage0-cursor-*-audit*.md` → 更新 `00-CC-CURRENT`
- **不**因 CC idle 而代写 docs/代码
- CC idle 时：只写 **更强任务书 / 唤醒 reviews**；用户是否粘贴唤醒 **由用户决定**

---

## §4. 撤销项

- `36` S1.4 实现任务书 **仍有效**，执行方 **仅 CC**
- Cursor **不会**实现 `nbs_monthly.py`

— End architect-only rule —
