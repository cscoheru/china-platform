# Stage 1 / S1.7 — CC Receipt（规划）

- 文件编号：`54-stage0-cc-s17-plan-receipt-20260825`
- 下发方：CC（Claude Code）
- 日期：2026-08-25
- 接收：`reviews/53-stage1-s17-ocr-planning-tasking-20260825.md`
- 协议：`40-stage0-cc-cursor-deadlock-fix-20260824.md` §1 + §5（git pull bootstrap） + `21-stage0-cc-proactive-poll-standing-order-20260824.md` §1
- 提交：`a1c9366`（docs(s1.7): add scanned PDF OCR connector plan (CC draft)）

---

## §0. TL;DR

| 任务 | 状态 |
|---|---|
| S1.7 规划：`docs/21-stage1-s17-scanned-pdf-ocr-plan-20260825.md` | ✅ CC 起草 |
| pytest -q 全集（无测试代码变更）| ✅ 279 passed in 487.14s（无 Δ）|
| pack rebuild（含 docs/21）| ✅ 451 artifacts / 0 errors |
| 双推 origin + github | ✅ 一次性成功（verbose trick 复用）|
| 收尾 / 阻塞 | 无 |

---

## §1. 交付清单

### §1.1 规划（CC 拥有最终版）

| 文件 | 内容 |
|---|---|
| `docs/21-stage1-s17-scanned-pdf-ocr-plan-20260825.md` | CC 起草。§0 TL;DR / §1 目录与所有权 / §2 类与责任（ScannedPdfOcrConnector + 3 方法签名 + 状态语义表）/ §3 ingest_run 钩挂 + S1.7 特殊字段映射表 + needs_review 语义映射表 / §4 docs/10 §2.1–2.5 映射 / §5 失败 / 重试 / §6 红线 / §7 下一刀 / §8 已知遗留（impl 决策点）/ §9 引用 |

### §1.2 关键设计要点（per Cursor 53 + docs/08 §2.1 + spike 04）

| 维度 | 决策 | 出处 |
|---|---|---|
| 默认采样 | **Shaanxi 中文文本研究轨**（spikes/04-scanned-pdf/data/shaanxi_fiscal_regulation_flk.pdf）| Cursor 53 §NOW 红线 2 + spike 04 README §"Current Shaanxi result" |
| 退化采样 | 1909 numeric-table track（**仅供 OCR 管线压力验证**；不接受为 Gate 1 代表性）| gate_thresholds.json status=FAILED + 红线 8 |
| 容器格式 | 单 PDF 文件；pdftoppm 渲染 → tesseract OCR | spike 04 extract_04_*.py |
| DEFAULT_TRACK | `"shaanxi_chinese_text"` | CC 决策（per Cursor 53）|
| DEFAULT_REGISTRY_DOMAIN | `wb.flk.npc.gov.cn` | source_registry/registry.csv 行 6 |
| DEFAULT_REGISTRY_CATEGORY | `SCANNED_PDF_RESEARCH` | 同上 |
| extraction_method | `'PDF_OCR'` | schema/01-core.sql enum line 55（已存在；无新值）|
| needs_review 语义传播 | per-cell（1909）/ per-page（Shaanxi） → `observation.notes` + `caveat_text`（migration 004）| docs/10 §2.1–2.5 + spike 04 README |
| status 决策 | `observation.status` 保持 `PRELIMINARY`；review 是 content 不是 lifecycle | docs/06 §6-4 + 拒绝与 S1.4/S1.5/S1.6 PARTIAL 语义冲突 |
| OCR confidence 字段 | `obs.confidence NUMERIC 0-1`（已存在 observation 列；tesseract 0-100 → /100.0）| docs/04 observation schema |
| 默认采样 SHA-256 | `f34b2e57ae08620cb6a6afb98b3983d805d53e3bae78b969795987a7ebe71488` | spike 04 provenance.json |
| 默认采样 URL | `https://wb.flk.npc.gov.cn/dfxfg/PDF/d31411b562fc4226a7465f1c875afe67.pdf` | spike 04 provenance.json |
| 默认渲染 DPI | 300 | spike 04 extract_04_shaanxi_text.py |
| 默认 OCR 参数 | tesseract chi_sim, PSM 6, TSV output | spike 04 extract_04_shaanxi_text.py |

### §1.3 与 S1.4/S1.5/S1.6 关键差异

| 维度 | S1.4 NBS HTML | S1.5 Sz 公报 HTML | S1.6 湖北 xlsx | **S1.7 扫描 PDF OCR** |
|---|---|---|---|---|
| 容器格式 | HTML `<table>` | HTML 散文 | **xlsx 单文件** | **PDF 单文件（扫描页）**|
| 解析入口 | regex | beautifulsoup + regex | openpyxl(data_only=True) | **pdftoppm 渲染 + tesseract OCR**|
| 内容形态 | 表格 | 散文 | 表格（4 列）| **中文长文本法规 / 历史表格**|
| obs 粒度 | 单元格 | 段落 | 行 | **页面（Shaanxi）/ 单元格（1909）**|
| obs 数量 | ≥1 | 8 | 19 | **待定（per-page or per-segment for Shaanxi）**|
| value | NUMERIC | NUMERIC | NUMERIC | **Shaanxi: NULL / 1909: NUMERIC**|
| value_type | FACT | FACT | FACT | **Shaanxi: DEFINITION（建议）/ 1909: FACT**|
| needs_review 来源 | N/A | N/A | N/A | **per-cell 1909 / per-page Shaanxi**|
| needs_review 写入 | — | — | — | **notes + caveat_text（不写入 status）**|
| 红线增量 | — | 不复用 spike 03 网络 | 不漂移 CUMULATIVE_HALF_YEAR / 中文不进 DB | **不降 gate_thresholds.json / 1909 ≠ 中国 / 陕西 ≠ 统计表代表性 / 不批量历史扫描**|
| 不做什么 | HTTP 默认 | HTTP 默认 | HTTP 默认 | **HTTP 默认 + 不批量多 PDF + 不降 OCR 门槛**|
| extraction_method | HTML_PARSE | HTML_PARSE | EXCEL_PARSE | **PDF_OCR**|
| Track 命名 | 单轨 | 单轨 | 单轨 | **双轨（research fallback）**|

---

## §2. 命令输出摘要

### §2.1 `python3 -m pytest -q`（全集，含 `spikes` + `tests`）

```
........................................................................ [ 25%]
........................................................................ [ 51%]
........................................................................ [ 77%]
...............................................................          [100%]
279 passed in 487.14s (0:08:07)
```

（S1.6 实施收尾 279 → S1.7 规划收尾仍 279；规划期不动测试代码）

### §2.2 `python3 scripts/build_evidence_pack.py`

```
Wrote /Users/kjonekong/projects/china platform/evidence_pack/manifest.json: 451 artifacts
verified 451 artifacts (full)
```

（S1.6 实施收尾 450 → S1.7 规划收尾 451，+1：`docs/21-stage1-s17-scanned-pdf-ocr-plan-20260825.md`）

### §2.3 git

```
[main a1c9366] docs(s1.7): add scanned PDF OCR connector plan (CC draft)
 2 files changed, 346 insertions(+), 6 deletions(-)
 create mode 100644 docs/21-stage1-s17-scanned-pdf-ocr-plan-20260825.md
To https://origin.cursor.com/lyliae/china-platform.git
   cb98442..a1c9366  HEAD -> main
To https://github.com/cscoheru/china-platform.git
   61a8bc3..a1c9366  HEAD -> main
```

`origin` push 首次尝试即成功；`github` push 用 verbose trick（`GIT_TRACE=1 GIT_CURL_VERBOSE=1`）一次性成功 — 复用 receipt 42/45/48/51 已验证的可重现 recipe。

---

## §3. 红线遵守

| 红线 | 状态 |
|---|---|
| ❌ 不 Gate 1 PASS | ✅ 仅 S1.7 规划；Gate 1 留 W6 总评（docs/08 §2.3）|
| ❌ 不降 OCR 门槛 / gate_thresholds.json | ✅ §6 红线显式禁绝；不引入 `--threshold-override` |
| ❌ 不把 BLOCKED-as-PASS（1909 状态）| ✅ DEFAULT_TRACK="shaanxi_chinese_text"；1909 仅 fallback；connector 不替 1909 翻案 |
| ❌ 1909 ≠ 中国代表性 | ✅ DEFAULT_REGISTRY_DOMAIN="wb.flk.npc.gov.cn"（不是 archive.org）|
| ❌ 陕西 ≠ 统计表代表性 | ✅ §6 红线显式禁绝；value_type='DEFINITION' 候选（impl 决策）|
| ❌ 不批量历史扫描 PDF | ✅ 单样本；不实现 multi-PDF / range-PDF |
| ❌ 不以 pdftotext -bbox 当 OCR 输入 | ✅ §6 红线显式禁绝 |
| ❌ 不擅自 --force / --force-with-lease | ✅ 普通 `git push` |
| ❌ 不替用户下裁定 | ✅ 不宣布 Gate 1；不表态接受 audit |
| ❌ Cursor 写 docs/21 正文 | ✅ CC 起草；Cursor 仅审验 |
| ❌ 不复用 spike 04 网络抓取 | ✅ 默认走 repo 内 `spikes/04-scanned-pdf/data/shaanxi_fiscal_regulation_flk.pdf` |
| ❌ 不引入 DSO / pgvector embedding | ✅ S1.7 仅 OCR 入库；embedding 留 Stage 3 |
| ❌ 不使用 `isFullUrl` 错误配置 | ✅ N/A；本轮无 provider 配置 |
| ❌ 强制 locale / tz 漂移 | ✅ Spike 04 "fetched_at_utc" 字段已锁定为 deterministic；不漂移到本地时区 |

---

## §4. 已知遗留（S1.7 impl 决策点 — Cursor 53 后 tasking 决策）

| 项 | 状态 | 留待 |
|---|---|---|
| Shaanxi observation 是 per-page 还是 per-segment？| **schema 候选** | impl tasking 决策 |
| Shaanxi observation.value_type=FACT vs DEFINITION？| **schema 候选** | impl tasking 决策 |
| 1909 track 是否真的当 fallback 保留？| 默认保留（per spike 04 standalone discipline）| impl tasking 确认 |
| `observation.extraction_metadata JSONB` 列（bbox + word_boxes + render_dpi + osd_rotation）？| **schema 候选** | impl tasking 决策（migration 005？）|
| 陕西法规发布日期 → period_* 字段填什么？| **默认 NULL**；法规定义不是数据周期 | impl tasking 确认 |
| `observation_revision` 是否纳入 OCR revisits？| 不实现 | Stage 2 / Stage 3 |
| dbt staging for OCR observations | 不实现 | Stage 1 dbt (S1.9) |
| multi-PDF historical scan | 不实现 | 留 Cursor 53 后 tasking |
| 真实中文扫描 PDF（非 1909/陕西）| 不实现 | Stage 1 dbt / 用户提供样本 |
| `--live-url` 显式开关 | 不实现 | S1.8 ingest 调度 |

---

## §5. 待 Cursor 审验

| 项 | 期望 |
|---|---|
| `docs/21` 是否收口 | Cursor 复验 §0–§9；若需补充 §N，可走 Cursor 后续 tasking |
| 与 docs/18/19/20 风格统一 | §0 TL;DR / §1 目录 / §2 类 / §3 钩挂 / §4 映射 / §5 失败 / §6 红线 / §7 下一刀 / §8 已知遗留 / §9 引用 — 镜像 docs/18/19/20 |
| 默认采样 Shaanxi 而非 1909 | §1.2 显式声明；§2 DEFAULT_TRACK 决策；§6 红线拒绝 1909-as-representative |
| gate_thresholds.json immutable | §6 红线显式禁绝；不引入可配置 override |
| needs_review 写入 notes + caveat_text | §3.3 字段映射表；不写入 status（保持 PRELIMINARY）|
| 红线完整性 | §6 红线 14 条；单样本 / 不降 OCR / 1909 ≠ 中国 / 陕西 ≠ 统计表 / 不批量 / 不以 pdftotext 当 OCR 输入 — 全显式 |
| `extraction_method='PDF_OCR'` | §3.2 字段映射表；已在 schema/01-core.sql enum |
| DEFAULT_REGISTRY_CATEGORY='SCANNED_PDF_RESEARCH' | §1.2 + §2.1 类签名；matches source_registry/registry.csv 行 6 |
| 双轨设计（Shaanxi default + 1909 fallback）| §1.2 + §1.3；保留 spike 04 standalone discipline |
| 下一刀 impl tasking | `NN-stage0-cursor-s17-impl-tasking-*.md` 应包含 schema 决策（per-page/per-segment, FACT/DEFINITION, extraction_metadata JSONB）|

---

## §6. 等待

等 Cursor 写 `reviews/NN-stage0-cursor-s17-plan-audit-*.md` → 通过后下发 `NN-stage0-cursor-s17-impl-tasking-*.md`（含 schema 决策）→ CC 进入 S1.7 实施（连接器 + 测试 + 可能 migration 005 if Cursor approves extraction_metadata JSONB）。

— CC Receipt 54 end —