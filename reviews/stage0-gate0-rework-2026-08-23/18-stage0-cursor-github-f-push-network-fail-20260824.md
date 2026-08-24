# Stage 0 — GitHub F 推送失败回执（网络；非凭证）

- 文件编号：`18-stage0-cursor-github-f-push-network-fail-20260824`
- 下发方：Cursor
- 日期：2026-08-24
- 对照：用户裁定 **F**（`17`）；凭证 OK（`16`）

---

## §0. 结果

| 项 | 结果 |
|---|---|
| 用户裁定 | **F** ✅ |
| `gh auth status` | ✅ cscoheru / repo scope |
| `git push --force-with-lease github HEAD` | ❌ **失败** |
| 错误 | `Failed to connect to github.com port 443 after 75006 ms: Couldn't connect to server` |
| 本地 HEAD | `6f663188812f20c01ecfda4966f58ad53d727d28` |
| 是否改用裸 `--force` | ❌ 否 |

**判定：** 阻塞从「凭证/授权」转为 **本机→github.com:443 网络不通**。F 授权仍然有效。

---

## §1. CC 立即执行

1. 入库 `15`–`18`（及未跟踪 reviews）→ `git push origin HEAD`
2. **网络恢复后**重试（F 仍有效，无需用户再批）：

```bash
gh auth status -h github.com
git push --force-with-lease github HEAD
# 成功后：
git ls-remote github HEAD   # == $(git rev-parse HEAD)
```

写回执 `19-stage0-cc-github-f-receipt-*.md` 后 STOP。

3. 若持续 443 超时：回执记「网络」；可提示用户检查 VPN/代理/防火墙；**不**改协议为 SSH，除非用户另裁。

---

— End —
