# Stage 0 Gate 0 — Cursor 审验：GitHub 同步停报（待用户裁定）

- 文件编号：`13-stage0-cursor-github-sync-hold-20260824`
- 审核日期：2026-08-24
- 审核方：Cursor（架构/质量审计）
- 对象：CC `12-stage0-cc-push-handoff-20260824.md`
- 依据：`10` §3 / `11` §5 §G（非快进停报；禁止擅自 force）

---

## §0. 判定

| 项 | 判定 |
|---|---|
| P0 pack 0/440 + commit `9d0d30e` + `origin` 同步 | ✅ **接受 CC 回执**（本地 `HEAD`=`origin/main`=`9d0d30e`） |
| CC 停推 `github`、不 force、不冒充双端同步 | ✅ **合规** |
| 双端同步完成 | ❌ **未完成**（仅 `origin`） |
| 下一步 | ⏸ **停等用户书面裁定**（§1）；CC 禁止任何 `github` push |

**U-4：** CC 回执称用户已选 **A**（关闭 E-1 门控、可继续）。本文件**不重开** U-4；若有误请用户更正。

---

## §1. 用户须书面裁定（二选一或组合）

### 1.1 凭证（必做，否则任何 github push 都会失败）

在本机终端完成其一：

```bash
gh auth login -h github.com
# 或更新 credential / PAT 后：
gh auth status -h github.com
```

### 1.2 历史分叉（三选一，**明示抄回**）

远端 [`cscoheru/china-platform`](https://github.com/cscoheru/china-platform) 仅有无关 Initial commit（`e6fe4fa`），与本地 `f475717` 根无公共祖先。

| 代号 | 动作 | 效果 |
|---|---|---|
| **F** | 授权 `git push --force-with-lease github HEAD` | 用本地 `9d0d30e` 覆盖远端脚手架 README commit |
| **X** | 用户在 GitHub 删建空仓 `cscoheru/china-platform` → CC `git push -u github main` | 无 force；需用户删仓 |
| **Y** | 暂不同步 GitHub | `origin` 为真源；GitHub 延后 |

**CC：** 未收到含 **F / X / Y** 字样的用户书面确认前，**零** `git push github`。

授权 **F** 后 CC 仅执行：

```bash
gh auth status -h github.com   # 必须成功
git push --force-with-lease github HEAD
git rev-parse HEAD
git ls-remote github HEAD      # 期望同 SHA 9d0d30e…
```

回执写入下一份 `reviews/`；成功后视为 `10` 双远程纪律恢复。

---

## §2. 工作区备注

```
?? reviews/.../12-stage0-cc-push-handoff-20260824.md
?? reviews/.../13-stage0-cursor-github-sync-hold-20260824.md  （本文件）
```

凭证 + F/X/Y 裁定后，CC 可将 `12`+`13` 随小 commit 入库并双推（若选 Y 则仅推 `origin`）。

---

## §3. 红线（重申）

- ❌ 不自行 `--force` / `--force-with-lease`
- ❌ 不冒充 github 已同步
- ❌ 不进入 Stage 1
- ❌ 不因 GitHub 阻塞回滚 `9d0d30e` 或改 pack

— End of github sync hold (2026-08-24) —
