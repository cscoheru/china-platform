# CC 硬唤醒 — S1.7 交卷死锁（假死，非真跑）

- 文件编号：`59-stage0-cursor-cc-wakeup-s17-commit-deadlock-20260825`
- 日期：2026-08-25
- 效力：覆盖「Committing S1.7 + receipt 57」长挂；**立即**执行 §NOW

---

## §0. 运行时证据（Cursor 复验 2026-08-25 ~10:21）

| 检查 | 结果 |
|---|---|
| UI | 「Committing…」已 **≥27 分钟**；子步骤 verify+commit+dual-push+receipt 未勾 |
| `ps` | **无** `pytest` / `tesseract` / `pdftoppm` / `git push` / `git commit` |
| `origin/main` | 无 S1.7 实现 commit；无 `57` |
| 工作区 | `scanned_pdf_ocr.py` + `test_scanned_pdf_ocr_connector.py` 仍为 `??` |
| pack | 仍 **451**（规划态）；**未** rebuild |
| `.git/index.lock` | 无 |

**判定：会话假死 / 单工具调用打包过大。不是「还在 OCR」。继续等 = 无效。**

---

## §1. 用户侧（一句话）

在卡死的 CC 终端按 **Esc / 取消当前工具**，然后粘贴 §2。

---

## §2. CC §NOW（拆步交卷；禁止再「一条龙 30 分钟」）

```bash
git fetch origin && git pull --ff-only origin main
git status
```

然后 **严格按序，每步单独工具调用，单步超时上限 5 分钟**：

1. **只测新文件**（禁止此刻再跑全集 8+ 分钟）：
   `python3 -m pytest tests/test_scanned_pdf_ocr_connector.py -q --timeout=120`
   （若无 pytest-timeout 插件：去掉 `--timeout`；单文件失败再修，勿挂全集）
2. **pack**：`python3 scripts/build_evidence_pack.py`
3. **写回执** `reviews/.../57-stage0-cc-s17-impl-receipt-20260825.md`（附单测输出；全集可标「本轮跳过，防死锁；下轮补」）
4. **commit（仅 origin 所需文件）**：
   ```bash
   git add backend/src/china_platform/connectors/scanned_pdf_ocr.py \
           tests/test_scanned_pdf_ocr_connector.py \
           evidence_pack/manifest.json \
           reviews/stage0-gate0-rework-2026-08-23/57-stage0-cc-s17-impl-receipt-20260825.md
   git commit -m "feat(s1.7): scanned PDF OCR connector (Shaanxi research track)"
   ```
5. **`git push origin HEAD`** — 成功即交卷完成  
6. **`git push github HEAD`** — 失败/超时 **30s 即停**；回执写 github-hold；**禁止**重试超过 2 次

### 禁止

- ❌ 再把「pytest 全集 + pack + commit + dual-push + 写回执」塞进 **一个** 工具调用  
- ❌ 空等 github 443  
- ❌ Cursor 代 commit（`37`）

---

## §3. 与 `58` 关系

`58` 假设 H1/H2 部分过时：**当前无验证进程** → 主因是 **H3/会话假死**。本文件优先。

— End wakeup —
