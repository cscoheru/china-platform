# Stage 0 — 用户裁定 GitHub = F（授权 force-with-lease）

- 文件编号：`17-stage0-cursor-github-f-authorized-20260824`
- 下发方：Cursor
- 日期：2026-08-24
- 用户书面裁定（Cursor 会话）：**`f` → F**
- 前置：`16` 凭证已确认（cscoheru / keyring / repo scope）

---

## §0. 裁定生效

| 项 | 值 |
|---|---|
| 凭证 | OK（`16`） |
| 同步方案 | **F** — 允许且仅允许 `git push --force-with-lease github HEAD` |
| 裸 `--force` | ❌ 仍禁止 |
| 覆盖范围 | 远端 Initial commit / README 脚手架（`e6fe4fa` 系） |

**CC 与 Cursor 均可执行 §1；先到先得。完成后写回执并 STOP。**

---

## §1. 立即执行

```bash
gh auth status -h github.com
cd "/Users/kjonekong/projects/china platform"
LOCAL=$(git rev-parse HEAD)
echo "LOCAL=$LOCAL"
git push --force-with-lease github HEAD
REMOTE=$(git ls-remote github HEAD | awk '{print $1}')
echo "REMOTE=$REMOTE"
test "$LOCAL" = "$REMOTE" && echo SYNC_OK || echo SYNC_FAIL
```

网络超时：最多再试 2 次（间隔可自行短等）；仍失败 → 回执记错误，**不**改用裸 `--force`。

成功后：

1. 将 `12`–`17`（及未入库 reviews）commit（若尚未）→ `git push origin HEAD` → 再 `git push github HEAD`（此时应为快进）
2. 回执：`reviews/.../18-stage0-cc-github-f-receipt-YYYYMMDD.md`
3. **STOP** 等 Cursor 审验

---

## §2. 红线

- ❌ 不进 Stage 1
- ❌ 不宣布 Stage 0 PASS（U-4=A 仅关 E-1 门控，见既有口径）
- ❌ 不用裸 `--force` 绕过 lease

— End —
