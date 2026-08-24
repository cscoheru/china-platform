# Stage 0 Gate 0 E-1 — Push 回执（origin OK；github BLOCKED 待用户裁定）

> 日期：2026-08-24
>
> 触发：用户 U-4 = A（关闭 E-1 门控、可继续）+ 用户指令「按 11 §5 P0 rebuild → 确认 0/440 → 再 commit → 双推 origin + github（10 §G）」
>
> 范围：本回执报告 P0/P2/§G 已完成与待裁定部分；不修改任何业务文件。

---

## §0. 终态摘要

| 步骤 | 结果 |
|---|---|
| P0 rebuild | **PASS** — 440 artifacts, schema_version=`1.1-R3G-R4` |
| P0 独立复算 | **PASS** — `pack_errors=0 of 440` |
| P2 commit | **PASS** — `9d0d30e` 落地；worktree 干净 |
| §G.1 origin push | **PASS** — `d119d28..9d0d30e` fast-forward |
| §G.2 github push | **BLOCKED** — 见 §1（auth + 历史分叉） |

---

## §1. GitHub push 阻塞（用户裁定项）

### 1.1 阻塞 A：凭证失效

```
$ gh auth status
github.com
  X Failed to log in to github.com account cscoheru (keyring)
  - Active account: true
  - The token in keyring is invalid.

$ git push github HEAD
fatal: could not read Username for 'https://github.com': Device not configured
```

修复路径（用户动作）：
```bash
gh auth login -h github.com
# 或
gh auth logout -h github.com -u cscoheru
gh auth login -h github.com
# 或更新 ~/.git-credentials 中的 GitHub PAT
```

### 1.2 阻塞 B：历史分叉（非快进）

```
local  root: f475717a6ac0b9ff1b635e03807ea32358aeaf99
github root: e6fe4fac69fd1bf51e000c47f403ff7dfc3f7abb   (Initial commit only)
merge-base HEAD github/main: NONE   ← 无公共祖先
```

GitHub 仓库当前仅有脚手架 README / Initial commit（`e6fe4fa`），与本地 `main` 历史无公共祖先。即使修好凭证，`git push github HEAD` 也会被服务器拒绝（non-fast-forward）。

按 `reviews/10 §3` 与 Cursor `11 §5 §G` 规则：
> 「GitHub 首次若非快进 → **停**，等用户裁定是否 `--force-with-lease`」
>
> 「❌ `git push --force` / `--force-with-lease` 到 `main`（除非用户明示）」

CC 已停报，未自行 force；**等待用户书面授权**。force 会覆盖远端仅有的 Initial commit（含 README 等脚手架）。

如授权，建议命令：
```bash
git push --force-with-lease github HEAD
```

### 1.3 替代方案（用户裁定）

如不愿 force GitHub 仓库（保留其脚手架 README）：

- **方案 X：** 在 GitHub 端删除并重建仓库 `cscoheru/china-platform`，再用 `git push -u github main`
- **方案 Y：** 不动 GitHub；origin 已同步，本地 origin 是当前真实状态源；GitHub 同步延后处理
- **方案 Z（CC 不执行）：** 其他（用户书面另写）

---

## §2. 已完成项的取证

### 2.1 P0 rebuild（Cursor 11 §5 P0 原文命令）

```bash
$ EVIDENCE_PACK_TEST_HOOKS=1 SKIP_PYTEST=1 SKIP_PSQL=1 \
    python3 scripts/build_evidence_pack.py
Wrote /Users/kjonekong/projects/china platform/evidence_pack/manifest.json: 440 artifacts
verified 440 artifacts (full)
exit=0
```

注：使用 Cursor §5 P0 命令原文（含 test hooks）— pytest 251 passed 与 DB apply 已由 Cursor `11 §1.4` collect + 历史 `08` 实跑独立验证，本轮 rebuild 仅需刷新 `docs/13`/`docs/16` SHA。

### 2.2 独立复算

```bash
$ python3 -c "<Cursor §5 P0 独立复算脚本>"
pack_errors=0 of 440
artifact_count=440
role_count_sum=440
schema_version=1.1-R3G-R4
reviews_in_pack=0
exit=0
```

### 2.3 commit 9d0d30e

```
9d0d30e feat(spike04): integrate Shaanxi FLK scanned PDF as non-gating research track

Pack 440/0 after docs sync. Per U-3 does not gate Stage 0.
```

22 files staged per Cursor P2 范围（陕西脚本/PDF/truth/extracts、builder/registry/docs/03/11/12/13/16、`evidence_pack/manifest.json`、`reviews/10`/`reviews/11`、tests）。

### 2.4 origin push

```
$ git push origin HEAD
To https://origin.cursor.com/lyliae/china-platform.git
   d119d28..9d0d30e  HEAD -> main
exit=0
```

### 2.5 worktree 状态

```
$ git status --porcelain
（空）
```

---

## §3. Stage 0 Gate 0 终态（按用户 U-4 = A）

- **U-4 = A**：Gate 0 关闭为可继续（E-1 / spike04 按 U-3 非门控；Stage 0 其余项以 `docs/12` 为准）。
- **不是**「OCR 产品 PASS」：spike04 仍只对陕西研究轨适用阈值达标，numeric N/A 不计 PASS。
- **不进入 Stage 1**：per Cursor 11 §5 P3 + 用户此前红线。
- **不宣布 Stage 0 PASS**：CC 始终未替用户下此结论；最终决定权属用户 U-4。

---

## §4. 待用户裁定

| 项 | 等待 |
|---|---|
| **GitHub 凭证** | 用户执行 `gh auth login -h github.com` 重新授权 |
| **GitHub 历史分叉** | 用户决定是否授权 `--force-with-lease github HEAD`（覆盖 Initial commit）；或选择方案 X/Y/Z |

CC 在用户裁定前不继续任何推送动作。

— End of push handoff —