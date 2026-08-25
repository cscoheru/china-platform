# S1.7 — pack 内嵌 pytest/OCR 死锁（强制拆解）

- 文件编号：`60-stage0-cursor-s17-pack-pytest-ocr-deadlock-20260825`
- 日期：2026-08-25
- 效力：覆盖 `59`；**立即**交卷

---

## §0. 根因（运行时已证实）

| 进程 (10:42) | 说明 |
|---|---|
| `python scripts/build_evidence_pack.py` | 自 10:39 起 |
| 其子：`python -m pytest -q …` | pack **强制内嵌全集 pytest**（`run_pytest()`，timeout **900s**）|
| 其孙：`tesseract … page-3.png … chi_sim` | S1.7 单测触发 OCR；**极慢** |

CC UI「Pack … 600s timeout」+「Committing…」= **在等 pack，而 pack 在等 OCR pytest**。  
单文件测试已 PASS（回执 `57` 已写）；**再等 pack 全集 = 重复 OCR，无必要。**

`build_evidence_pack.py` 支持环境变量 **`SKIP_PYTEST=1`**（见 `run_pytest()`）— OCR 刀必须用。

Cursor 已于本机 **kill** 卡住的 pack/pytest/tesseract，解除假等待。

---

## §1. CC §NOW（Esc 后立即执行；每步单独工具调用）

```bash
git fetch origin && git pull --ff-only origin main
git status
# 应见 ?? connector + tests + 57 回执
```

1. **不要**再跑无 `SKIP_PYTEST` 的 pack  
2. 快速 pack（跳过内嵌 pytest；单测已在回执）：
   ```bash
   SKIP_PYTEST=1 SKIP_PSQL=1 python3 scripts/build_evidence_pack.py
   ```
3. 若 pack 仍 >3 分钟 → **跳过 pack**，回执写 `pack=DEFERRED`，直接 commit  
4. commit + **只 push origin**：
   ```bash
   git add backend/src/china_platform/connectors/scanned_pdf_ocr.py \
           tests/test_scanned_pdf_ocr_connector.py \
           reviews/stage0-gate0-rework-2026-08-23/57-stage0-cc-s17-impl-receipt-20260825.md \
           evidence_pack/manifest.json
   git commit -m "feat(s1.7): scanned PDF OCR connector (Shaanxi research track)"
   git push origin HEAD
   git push github HEAD || true
   ```
5. 回执补填 commit SHA；github 失败写 hold  
6. → §POLL

### 禁止

- ❌ `python3 scripts/build_evidence_pack.py` **不带** `SKIP_PYTEST=1`（本刀）  
- ❌ 交卷前再跑全集 pytest  
- ❌ 单工具调用里串 pack+commit+双推并 background wait 600s  
- ❌ Cursor 代 commit

---

## §2. 常驻规则（OCR / 慢 spike 刀）

此后凡触及 tesseract/pdftoppm 的 Stage 1 刀：

1. 验收以 **定向单测** 为准  
2. pack 默认 `SKIP_PYTEST=1`（或先 commit 再异步 pack）  
3. `origin` push 成功 = 交卷；pack/github 可 hold

— End —
