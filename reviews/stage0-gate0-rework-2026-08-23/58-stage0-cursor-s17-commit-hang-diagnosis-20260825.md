# S1.7 — CC commit 挂起诊断（Cursor 架构师，不代劳）

- 文件编号：`58-stage0-cursor-s17-commit-hang-diagnosis-20260825`
- 日期：2026-08-25
- 触发：用户报告 CC UI「Committing S1.7 + receipt 57…」约 15 分钟

---

## §0. 独立复验（本机工作区 + origin）

| 检查 | 结果 |
|---|---|
| `origin/main` | 仍停在 `07b7f12`（S1.7 **规划审验**）；**无** `57` 回执 commit |
| `57-*-receipt*.md` | **不存在** |
| 未跟踪文件 | `backend/.../scanned_pdf_ocr.py`（587 行）、`tests/test_scanned_pdf_ocr_connector.py`（503 行）**已落盘** |
| `.git/index.lock` | **无** |
| 工作区 | Cursor 与 CC **同仓同树** — 文件可见，但 CC 会话若卡在 commit/push，origin 不会动 |

**结论：** 实现稿大概率已写完；卡在 **commit 前验证** 或 **双推**，尚未完成交卷。

---

## §1. 假设（按概率）

| # | 假设 | 依据 |
|---|---|---|
| H1 | **pytest 全集 / OCR 单测耗时长** | S1.x 全集常 ~8 分钟；S1.7 调 tesseract+pdftoppm 可再拉长 |
| H2 | **`git push github` 443 挂死** | 历史多次 timeout；UI 文案「Committing」常含 dual-push |
| H3 | **等用户批准 git / 凭证** | Claude Code 交互式 commit 审批未点 |
| H4 | **回执未写完却已开 commit 步骤** | 无 `57` 文件；若脚本先 pytest 再写回执，会长时间无新 reviews |

---

## §2. CC 自救（粘贴到卡死的 CC 终端；Cursor **不**代 commit）

若 UI 已死锁，**取消当前工具调用**后执行：

```bash
git fetch origin && git pull --ff-only origin main
git status
# 确认 connector + tests 仍在；写 57 回执后：
git add backend/src/china_platform/connectors/scanned_pdf_ocr.py \
        tests/test_scanned_pdf_ocr_connector.py \
        reviews/stage0-gate0-rework-2026-08-23/57-stage0-cc-s17-impl-receipt-*.md \
        evidence_pack/manifest.json   # 若已 rebuild
# 先 origin（协调主通道），github 失败不阻塞：
git commit -m "feat(s1.7): scanned PDF OCR connector (Shaanxi research track)"
git push origin HEAD
git push github HEAD || true   # 443 则回执 §github-hold，勿空等 15min
```

**禁止：** Cursor 代 commit 上述 CC 交付物（per `37`）。

---

## §3. Cursor 义务

- 等 `origin` 出现 `57` + connector commit → 再写 `59` 审验
- 本文件仅诊断；**不改** `queue_rev=17` §NOW

— End —
