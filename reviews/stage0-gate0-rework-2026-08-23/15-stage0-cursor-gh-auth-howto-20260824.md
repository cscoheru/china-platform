# Stage 0 — GitHub 凭证指引（用户本机；无 PAT 预知）

- 文件编号：`15-stage0-cursor-gh-auth-howto-20260824`
- 下发方：Cursor
- 日期：2026-08-24
- 读者：用户（本机会话操作）+ CC（只读；**勿**代用户粘贴 token）

---

## §0. 结论

**你不需要事先知道「是哪个令牌」。**  
推荐路径是浏览器 OAuth：`gh` 登录成功后会**自动**在 macOS 钥匙串里写入 GitHub token，无需你从某处复制一串 PAT。

| 方式 | 是否需要事先有 PAT | 建议 |
|---|---|---|
| **A. `gh auth login` + 浏览器** | 否 | **首选** |
| B. 个人访问令牌 (PAT) 粘贴 | 是（你在 GitHub 网站新建） | 仅当浏览器登录不可用 |

**禁止：** 把任何 token / PAT 粘贴到 Cursor 或 CC 聊天。

---

## §1. 用户本机步骤（方式 A，约 2 分钟）

在 **本机终端**（非沙箱）执行：

```bash
# 1) 若旧登录已坏，先清掉（可选）
gh auth logout -h github.com 2>/dev/null || true

# 2) 登录
gh auth login -h github.com
```

交互选项建议：

1. **Where do you use GitHub?** → `GitHub.com`
2. **Preferred protocol** → `HTTPS`
3. **Authenticate Git** → `Yes`（让 git 用同一套凭证）
4. **How to authenticate** → **`Login with a web browser`**
5. 终端会显示一次性码 → 回车后浏览器打开 → 用 **cscoheru** 账号确认
6. 完成后检查：

```bash
gh auth status -h github.com
# 期望：Logged in to github.com as cscoheru（Token: valid）
```

然后在 Cursor 本会话回复一行，例如：

```
凭证 OK（gh auth status 通过）
```

**仍须另选 GitHub 同步方案 F / X / Y**（见 `13`）。可同一条消息写：

```
凭证 OK；GitHub = F
```

---

## §2. 仅当浏览器不可用时（方式 B）

1. 浏览器打开：https://github.com/settings/tokens  
   （或 Fine-grained：https://github.com/settings/personal-access-tokens ）
2. **Generate new token**，权限至少：`repo`（私有仓）或公开仓的 `public_repo` / Contents: Read and write
3. **只在本机终端**粘贴（`gh auth login` 选 token 方式），**不要**发给任何人

```bash
gh auth login -h github.com
# 选：Paste an authentication token
```

---

## §3. CC 指令（本文件期间）

- ❌ 不运行交互式 `gh auth login` 代替用户（需浏览器/钥匙串）
- ❌ 不索取、不记录 PAT
- ✅ `github` push 保持 **blocked**，直到 Cursor 写入「用户已裁定：凭证 OK + F|X|Y」
- ✅ 可继续执行 `14` §5（reviews 入库 + `origin` push）

---

## §4. 登录成功后的下一刀（用户裁定 F 后由 CC 执行）

Cursor 将另写任务书；示意：

```bash
gh auth status -h github.com
git push --force-with-lease github HEAD   # 仅当用户书面 = F
git ls-remote github HEAD                 # 期望 = 本地 HEAD
```

— End of gh auth howto —
