# Stage 0 Gate 0 — CC 常驻 Git 纪律 + 双远程关联

- 文件编号：`10-stage0-cc-git-dual-remote-20260824`
- 下发方：Cursor（架构/质量审计）
- 下发日期：2026-08-24
- 适用对象：Claude Code（CC）
- 性质：**常驻指令**（此后所有 Cursor 审验/任务书默认附带本节；不替代业务任务）
- 用户要求：审验与指令须含 git；随时推送远程；关联 GitHub

---

## §0. TL;DR（CC 先看）

| 远程名 | URL | 用途 |
|---|---|---|
| `origin` | `https://origin.cursor.com/lyliae/china-platform.git` | Cursor Origin（IDE / Origin 协作） |
| `github` | `https://github.com/cscoheru/china-platform` | GitHub 公开备份与协作 |

**每个逻辑 commit 完成后，必须双推：**

```bash
git push origin HEAD
git push github HEAD
```

首次或分支未跟踪时：

```bash
git push -u origin HEAD
git push -u github HEAD
```

---

## §1. 远程基线（审计已配置，2026-08-24）

本地应满足：

```bash
git remote -v
# origin   https://origin.cursor.com/lyliae/china-platform.git (fetch/push)
# github   https://github.com/cscoheru/china-platform.git (fetch/push)
```

若缺失 `github`：

```bash
git remote add github https://github.com/cscoheru/china-platform.git
# 或已存在则：
git remote set-url github https://github.com/cscoheru/china-platform.git
```

**禁止：**

- ❌ `git remote remove origin`（除非用户明示）
- ❌ 用 GitHub URL 覆盖 `origin`（双远程并存）
- ❌ `git push --force` / `--force-with-lease` 到 `main`（除非用户明示）
- ❌ `git push` 只推一侧（必须 origin + github 都成功，或停报）

---

## §2. 标准交付闭环（每次任务结束）

```bash
# 1) 工作区干净或仅含已授权未入库草稿
git status --porcelain

# 2) 提交（仅用户/任务书授权的文件；conventional commits）
git add <paths>
git commit -m "$(cat <<'EOF'
<type>(scope): <why>

EOF
)"

# 3) 双推
git push origin HEAD
git push github HEAD

# 4) 回执（写入下一轮 Cursor 审验材料）
git log -1 --oneline
git status -sb
git rev-parse HEAD
# 期望：main...origin/main 且与 github/main 同 SHA（若 github 已跟踪）
```

回执须包含：

| 字段 | 示例 |
|---|---|
| commit | `abc1234 ...` |
| `origin` | pushed / failed + 错误摘要 |
| `github` | pushed / failed + 错误摘要 |
| dirty | empty / 列出故意 ?? |

一侧失败 → **停**；修好凭证/权限后重推；**不得**假装双端同步。

---

## §3. GitHub 空仓 / 历史分叉处理

GitHub [`cscoheru/china-platform`](https://github.com/cscoheru/china-platform) 若仅有脚手架 README、与本地历史无关：

1. **首选（用户授权后）：** `git push -u github main`  
   - 若拒绝非快进 → **停报**，请用户裁定是否允许  
     `git push --force-with-lease github main`（会覆盖远端仅有的 README commit）
2. **禁止** CC 自行 force 而不记录用户裁定

---

## §4. 凭证与工具

| 场景 | 动作 |
|---|---|
| Origin 401 | `origin auth login` 后重推 `origin` |
| GitHub 401 | `gh auth login` 或配置 credential helper 后重推 `github` |
| `gh` 不可用 | 仍可用 `git push github`（HTTPS + token/credential） |

**禁止** 在 chat / commit message / 文件中粘贴 token。

---

## §5. 与业务红线的关系

- Git 纪律 **不**授权：降低 OCR 门槛、入库 1909 代表中国、宣布 Stage 0 PASS、启动 Stage 1
- 草稿（如 `docs/16` 预审前）仍按任务书「勿 commit 直至预审通过」；**一旦**授权 commit，立即双推
- pack 变更：commit 前 `pack_errors=0`；commit 后双推

---

## §6. Cursor 审验模板增补（此后每份 `reviews/*` 任务书必含）

```markdown
## §G. Git 交付（常驻）

1. commit（conventional）
2. `git push origin HEAD && git push github HEAD`
3. 回执：`git log -1 --oneline` + 两侧 push 成功证据
4. remotes 基线见 `reviews/.../10-stage0-cc-git-dual-remote-20260824.md`
```

---

## §7. CC 立即执行（本文件落地）

1. 确认 `git remote -v` 含 `origin` + `github`
2. 将本文件随下一逻辑 commit 入库（或单独 `chore(git): document dual-remote push discipline`）
3. **双推**该 commit
4. 若 `github` 首次推送失败：按 §3 停报，等用户裁定 force

---

— End of dual-remote git standing order (2026-08-24) —
