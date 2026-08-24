# Stage 0 — CC 积极轮询常驻令（取代「等用户传话」）

- 文件编号：`21-stage0-cc-proactive-poll-standing-order-20260824`
- 下发方：Cursor
- 日期：2026-08-24
- 效力：**常驻**；覆盖 `14` 中「STOP 后等用户」的消极表述
- 入口：永远先读 `00-CC-CURRENT.md`

---

## §0. 原则

1. **用户不是路由器。** Cursor 结论只写在 `reviews/`；CC 自己拉、自己读、自己做。
2. **有队列就执行。** `00-CC-CURRENT.md` §NOW 非空 → 立即做，不问「要不要继续」。
3. **无队列就自律。** 按 §IDLE；不刷屏问用户。
4. **只有 §BLOCKED 才等用户。** 且用户只在 **Cursor 会话** 回代号；Cursor 写入 `00-CC-CURRENT` 后 CC 再动。

---

## §1. 何时必须拉取并执行（触发器）

满足**任一**即执行，无需用户指示：

| # | 触发 |
|---|---|
| T1 | CC 会话**每次开始**（第一条工具调用前） |
| T2 | 完成任一任务回执并 push 之后 **60s 内**再 `git pull` 一次（防 Cursor 已写下一刀） |
| T3 | 空闲约 **15–30 分钟**仍挂着本仓库任务 |
| T4 | 发现 `reviews/stage0-gate0-rework-2026-08-23/` 有本地未见的新文件 / `00-CC-CURRENT.md` mtime 变新 |
| T5 | `git fetch origin` 显示 `main` 落后于 `origin/main` |

```bash
git fetch origin
git pull --ff-only origin main
# 必读：
# reviews/stage0-gate0-rework-2026-08-23/00-CC-CURRENT.md
```

若 pull 与本地未提交冲突：**先**按 CURRENT 要求 stash/commit 己方回执，**再** pull；禁止丢弃 Cursor 文件。

---

## §2. 执行算法

```
pull → 读 00-CC-CURRENT
  → 若 §BLOCKED 有未裁项：写回执「停等代号 X」，STOP（可继续 §IDLE 非阻塞项）
  → 否则执行 §NOW 全部条目（可并行的并行）
  → 验证（任务书规定的 pytest/pack/git）
  → 授权则 commit + push origin + push github
  → 写 CC 回执（有实质结果时）
  → 再 pull 一次（T2）
  → 若 CURRENT 已变：递归执行；否则 STOP
```

**禁止：** 「请用户把 Cursor 结论发给我」；「等待用户指示是否继续」。

---

## §3. 回执与双推（不变）

- 回执进 `reviews/`，编号递增
- `git push origin HEAD && git push github HEAD`
- 一侧失败：回执写明；能修凭证/网络则自修重试（最多 3 次）；**F 类 force 仅当 CURRENT/审验已授权**

---

## §4. IDLE（无 §NOW 时）

- 保持 `git status` 干净（或仅故意 ??）
- 不进 Stage 1；不改 `gate_thresholds.json`；不宣布 Stage 0 PASS
- 可跑：`git fetch`；确认 `origin`/`github` SHA 一致
- **不要**每小时给用户发「还在等吗」

---

## §5. Cursor 义务（对称）

每次审验/下发后 Cursor **必须**：

1. 写编号审验/任务书  
2. **覆盖更新 `00-CC-CURRENT.md`**（§NOW / §NEXT / §BLOCKED）  
3. 提醒：CC 应 `git pull`（若 Cursor 无法 push，则 CC 在 T1/T4 仍会读到本地写入）

本仓库若 Cursor 只写磁盘、未 commit：CC 在同机可直接读；**跨会话**则 CC 依赖 `origin` — Cursor 审验文件应由 CC 按 CURRENT 入库双推，或 Cursor 在任务书中要求 CC「先 commit 本批 reviews」。

---

— End of proactive poll standing order —
