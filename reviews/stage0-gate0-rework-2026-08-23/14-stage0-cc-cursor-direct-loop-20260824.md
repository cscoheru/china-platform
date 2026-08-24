# Stage 0 — CC↔Cursor 直达协作协议（用户仅裁定）

- 文件编号：`14-stage0-cc-cursor-direct-loop-20260824`
- 下发方：Cursor（架构/质量审计）
- 日期：2026-08-24
- 适用：Claude Code（CC）**常驻**；此后所有任务默认服从本文件
- 目的：用户不再做传声筒；CC 直接读写 `reviews/`，完成后停等 Cursor 审验

---

## §0. 角色

| 角色 | 做什么 | 不做什么 |
|---|---|---|
| **CC** | 实现、验证、按任务书 commit/push、把回执写入 `reviews/` | 不替用户裁定；不宣布 Gate PASS；不等用户转发 Cursor 话 |
| **Cursor** | 只读审验；写下一份 `reviews/NN-…` 任务书/审验 | 不替 CC 改业务代码（除非用户改角色） |
| **用户** | **仅**在 Cursor 会话中回答「待裁定」项 | 不负责在 CC 与 Cursor 之间复制粘贴长文 |

**CC 读指令的唯一来源：** 仓库内最新的 `reviews/stage0-gate0-rework-2026-08-23/` 编号最大的 **Cursor 下发**文件（任务书 / 审验 / ACK）。完成工作后写 **CC 回执** 到同目录，再停。

---

## §1. 工作环（强制）

```
1. 读最新 Cursor 文件（本目录按文件名排序，取最新「cursor」或任务书）
2. 执行其中可执行项；遇「待用户裁定」→ 写入回执 §停等，停止该分支
3. 验证（pytest/pack 等按任务书）
4. 若任务书授权 commit：commit → 按 §G 推送
5. 写 CC 回执：reviews/.../NN-stage0-cc-<topic>-YYYYMMDD.md
6. git add 该回执（及授权文件）→ commit → §G 推送（若授权）
7. STOP：等待 Cursor 写入下一份审验/任务书；不要轮询用户「传一下」
```

**禁止：** 在 Cursor 尚未写入新审验前，自行扩展范围、宣布闭环、或要求用户口头复述 Cursor 结论。

---

## §2. 回执最低模板（CC 每次必用）

```markdown
# <主题> — CC 回执

- 对照 Cursor 文件：`NN-...md`
- 日期：YYYY-MM-DD
- HEAD：`<sha>`
- origin：pushed | failed | n/a
- github：pushed | blocked-awaiting-user | failed

## 已完成
- …

## 证据（命令 + 关键输出一行）
- pack_errors=…
- pytest=…

## 停等
- [ ] Cursor 审验
- [ ] 用户裁定：<引用 Cursor 文件中的代号，如 F/X/Y>

## 未做 / 红线遵守
- …
```

回执必须 **commit 进仓库**（与成果同 commit 或紧随的 `chore(reviews): …`），以便 Cursor 只读仓库即可审验，不依赖聊天。

---

## §3. Git（常驻，见 `10`）

```bash
git push origin HEAD
git push github HEAD   # 仅当用户已裁定且凭证有效；否则记 blocked，不停改业务
```

- `origin` 失败 → 修 Origin 凭证后重试；业务可继续
- `github` 非快进 / 401 → **停推 github**；回执写明；**等用户在 Cursor 会话裁定**（CC 不追问用户重复决策）

---

## §4. 当前开放任务（2026-08-24 快照）

| ID | 状态 | CC 动作 |
|---|---|---|
| 陕西集成 `9d0d30e` | 已在 `origin` | 无业务返工，除非 Cursor `15+` 另下 |
| `12` push handoff | 已写 | 入库 `12`+`13`+本文件（若尚未）见 §5 |
| GitHub 同步 | **停等用户 F/X/Y + 凭证** | 零 `git push github` 直至 Cursor 写「用户已裁定 F|X|Y」 |
| U-4 | CC 称用户选 A | 以 Cursor `13` 为准；有争议等用户在 Cursor 会话更正 |

---

## §5. CC 立即执行（本协议落地，无需用户转发）

1. 确认已读 `10`、`11`、`12`、`13`、本文件 `14`
2. 将未跟踪的 reviews 入库（至少 `12`、`13`、`14`；若 `11` 未在 `9d0d30e` 内则一并）：

```bash
git add reviews/stage0-gate0-rework-2026-08-23/1{1,2,3,4}*.md 2>/dev/null
git add reviews/stage0-gate0-rework-2026-08-23/12-stage0-cc-push-handoff-20260824.md \
        reviews/stage0-gate0-rework-2026-08-23/13-stage0-cursor-github-sync-hold-20260824.md \
        reviews/stage0-gate0-rework-2026-08-23/14-stage0-cc-cursor-direct-loop-20260824.md
# 若 11 仍为 ?? 也 add
git status --porcelain
git commit -m "$(cat <<'EOF'
chore(reviews): CC↔Cursor direct loop + github sync hold records

Standing order: CC writes receipts to reviews/, waits for Cursor;
user only rules on explicit decision codes in Cursor session.
EOF
)"
git push origin HEAD
# github：仅当用户已裁定 F/X/Y 且凭证 OK；否则跳过并在回执注明
```

3. 写短回执 `15-stage0-cc-direct-loop-ack-YYYYMMDD.md`（或并入本次 commit message 后的下一小回执）确认：已停等 GitHub 裁定；origin 已含本协议。
4. **STOP**。下一动作只来自 Cursor 新文件或用户在 Cursor 会话给出的 F/X/Y。

---

## §6. 用户裁定通道（仅此）

用户只在 **Cursor 本会话** 回复裁定代号即可，例如：

```
裁定：凭证已搞定；GitHub = F
```

或 `X` / `Y`。Cursor 将把裁定写入下一份 `reviews/NN-…`，CC 读文件执行——**用户不必打开 CC 聊天复述。**

---

## §7. 红线

- ❌ 不要求用户复制 Cursor 长文给 CC
- ❌ 不擅自 force github
- ❌ 不宣布 Stage 0 PASS / 不进 Stage 1
- ❌ 不以聊天记录替代 `reviews/` 回执

— End of direct-loop standing order —
