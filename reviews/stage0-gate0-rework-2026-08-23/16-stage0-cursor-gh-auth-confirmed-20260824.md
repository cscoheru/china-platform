# Stage 0 — 用户凭证确认 + CC 待 GitHub 方案裁定

- 文件编号：`16-stage0-cursor-gh-auth-confirmed-20260824`
- 下发方：Cursor
- 日期：2026-08-24
- 触发：用户在 Cursor 会话反馈 GitHub「Your device is now connected.」

---

## §0. 凭证判定

| 项 | 结果 |
|---|---|
| 用户反馈 | Device connected（浏览器授权完成） |
| `gh auth status`（本机独立复验） | ✅ Logged in as **cscoheru**（keyring）；HTTPS；scopes 含 `repo` |
| GitHub 同步方案 F/X/Y | ⏸ **尚未裁定** |

**CC：** 凭证阻塞 **解除**。仍 **禁止** `git push github`，直到本文件 §1 出现用户书面 **F / X / Y**（或后续 `17+` 写入裁定）。

---

## §1. 用户请在 Cursor 本会话回复一行

远端仍是无关 Initial commit，普通 push 会非快进。请选：

| 代号 | 含义 |
|---|---|
| **F** | 授权 `git push --force-with-lease github HEAD`（覆盖脚手架 README） |
| **X** | 你先删建空仓 → CC 再 `git push -u github main` |
| **Y** | 暂不同步 GitHub |

示例：`GitHub = F`

---

## §2. 若用户裁定 F — CC 立即执行

```bash
gh auth status -h github.com          # 必须仍 Logged in
cd "/Users/kjonekong/projects/china platform"
git status -sb
git push --force-with-lease github HEAD
git ls-remote github HEAD             # 期望与本地 HEAD 同 SHA
git push origin HEAD                  # 若有未推 reviews，先 commit 再双推
```

回执写入 `reviews/.../17-stage0-cc-github-sync-receipt-YYYYMMDD.md`，含两侧 SHA；然后 **STOP** 等 Cursor 审验。

若 `--force-with-lease` 因网络超时失败：重试最多 2 次；仍失败则回执记网络错误，**不**改用裸 `--force`，不停改业务。

---

## §3. CC 并行可做（不等 F）

按 `14` §5：将 `12`–`16` 等未入库 reviews commit 并 `git push origin HEAD`（github 仍跳过直至 §1）。

---

— End —
