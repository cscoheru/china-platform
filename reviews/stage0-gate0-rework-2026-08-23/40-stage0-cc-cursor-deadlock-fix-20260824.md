# CC↔Cursor 死锁消除 — 常驻协议（彻底修复 idle 等审验）

- 文件编号：`40-stage0-cc-cursor-deadlock-fix-20260824`
- 日期：2026-08-24
- 效力：**覆盖** `00-CC-CURRENT` 旧 §STOP、`24` §4「进入 IDLE」、`15`「本回执后 STOP」中一切**被动等待 Cursor 聊天**的表述
- 用户裁定：用户不是路由器；CC **不得**因「等 Cursor 审验」在终端 idle

---

## §0. 根因（已证实）

| 现象 | 原因 |
|---|---|
| CC 三终端 idle | 会话内读了旧版 `00-CC-CURRENT` 或未 `git pull` |
| CC 以为 Cursor 未审 | Cursor 结论在 **git / reviews**，不在 CC 聊天 |
| CC 交付后仍显示旧 §NOW | Cursor 审验未 commit，或 CC 未 pull 新 CURRENT |
| 「STOP → 等审验 39+」 | **错误语义**：STOP = 结束会话；应进入 **§POLL** |

**结论：** 不存在「等 Cursor 说话」这一状态；只存在 **git 上的队列版本**。

---

## §1. `00-CC-CURRENT.md` 状态机（强制）

`00-CC-CURRENT.md` 顶部 **§META** 为唯一真相源：

| `phase` | 含义 | CC 行为 |
|---|---|---|
| `CC_ACTION_REQUIRED` | §NOW 有活 | **立即执行** §NOW；禁止问用户 |
| `CC_POLL` | CC 已交卷或暂无新刀 | **§POLL 循环**（§2）；禁止 idle 等聊天 |
| `BLOCKED` | 需用户代号 | 写回执停等；可 §POLL 但不执行 §NOW |
| `CURSOR_AUDIT_PENDING` | （废弃别名） | 等同 `CC_POLL` |

| 字段 | 谁写 | 用途 |
|---|---|---|
| `queue_rev` | Cursor 每次改 CURRENT **+1** | CC 对比本地记忆，变了就读新版 |
| `cursor_head` | Cursor | 上次 Cursor commit SHA |
| `cc_head` | Cursor 审验时写 | 上次验收的 CC commit |
| `updated_at` | Cursor | ISO 时间 |

**禁止** 在无 §META 的旧 CURRENT 上推断状态。

---

## §2. §POLL 循环（取代 STOP / IDLE 等审）

CC 在以下时刻**必须**进入 §POLL，而不是停住：

- 完成 §NOW 并 push 回执之后
- 发现 `git fetch` 显示 `origin/main` 领先于本会话已知 SHA
- 空闲 **>3 分钟**且仍绑定本仓库（覆盖 `21` T3 的 15–30 分）

```bash
# 单会话 poll（可手工重复，或 while 直到 phase 变）
git fetch origin
git pull --ff-only origin main
# 必读：
sed -n '1,80p' reviews/stage0-gate0-rework-2026-08-23/00-CC-CURRENT.md
```

**循环规则：**

1. 读 §META.`queue_rev` → 若大于本会话上次读到的 rev → 当作新队列，**重新执行 §2 算法**（`21` §2）
2. 若 `phase=CC_ACTION_REQUIRED` 且 §NOW 非空 → **退出 POLL，执行 NOW**
3. 若 `phase=CC_POLL` 且 §NOW 空 → sleep **180s**，回到步骤 1（**最多 20 轮** ≈ 1h，然后静默停；下一会话 T1 再启）
4. **禁止** 向用户发送「Cursor 审完了吗」「是否继续」
5. **禁止** 假设 Cursor 会在 CC 终端/chat 里通知

---

## §3. 多 CC 终端（三开场景）

| 规则 | 说明 |
|---|---|
| **POLL 可并行** | 多个终端同时 `git pull` 无害 |
| **NOW 单工** | 同一 `queue_rev` 下 **只允许一个终端** 执行 §NOW 实现；其余终端 POLL 或退出 |
| 认领方式 | 先 push 者为准；后 pull 看到 `origin/main` 已有回执 commit → **不要重复实现**，转 POLL |
| 用户不必协调 | 不要求用户在三终端间传话 |

---

## §4. Cursor 对称义务（消除「已审验 CC 不知道」）

Cursor **每次**审验或改队列，**同一 commit 批次**必须包含：

1. `reviews/NN-stage0-cursor-*-audit*.md`（或有实质变更的任务书）
2. **完整更新** `00-CC-CURRENT.md`（§META + §NOW + `phase`）
3. `git push origin HEAD`（`github` 尽力；失败写 reviews，不阻塞 origin）

**禁止：** 仅在 Cursor 聊天里说「已审验通过」而不 commit CURRENT。  
**禁止：** 只改 CURRENT 不写审验文件。

CC 唯一认：`origin/main` 上的 `queue_rev` 与 §NOW。

---

## §5. CC 会话 bootstrap（覆盖 AGENTS.md）

**第一条命令**（强制，先于任何其它工具）：

```bash
git fetch origin && git pull --ff-only origin main
grep -E '^(## META|phase|queue_rev)' reviews/stage0-gate0-rework-2026-08-23/00-CC-CURRENT.md
cat reviews/stage0-gate0-rework-2026-08-23/00-CC-CURRENT.md
```

然后：

- `phase=CC_ACTION_REQUIRED` → 执行 §NOW（**禁止 IDLE**）
- 否则 → §POLL §2

---

## §6. 与 `21` 的关系

- `21` T1/T2/T4/T5 **仍有效**
- `21` T3 间隔改为 **3 分钟**（本文件优先）
- `21` §2 算法中「否则 STOP」→ 改为「否则 **§POLL**」

— End deadlock fix —
