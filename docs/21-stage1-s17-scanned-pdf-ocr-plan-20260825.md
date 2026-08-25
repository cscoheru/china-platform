# 21 — Stage 1 / S1.7 扫描 PDF OCR 连接器规划

> **规划 only**；CC 拥有最终版（per Cursor 37 §META architect-only rule）。
> **研究轨，非 Gate 1 代表性**（per Cursor 53 §NOW 红线 2）。

---

## §0. TL;DR

| 项 | 决策 |
|---|---|
| 范围 | **单样本试点**：`spikes/04-scanned-pdf/data/shaanxi_fiscal_regulation_flk.pdf`（陕西研究轨，U-1/U-2/U-3） |
| 退化样本 | 1909 numeric-table track（**仅供 OCR 压力管线验证**；不接受作为 Gate 1 代表性） |
| 复用 | spike 04：`compute_sha256`, `extract_04_shaanxi_text.run()`（默认）/ `extract_04_scanned_pdf.extract()`（退化）, `ocr_text_layout`（布局感知分栏） |
| extraction_method | `PDF_OCR`（已在 `schema/01-core.sql` enum line 55 — Cursor 49 §1 备注；无新 enum 迁移） |
| 默认 REGISTRY_CATEGORY | `SCANNED_PDF_RESEARCH`（matches `source_registry/registry.csv` wb.flk.npc.gov.cn 行） |
| DEFAULT_REGISTRY_DOMAIN | `wb.flk.npc.gov.cn` |
| needs_review 语义传播 | per-cell 1909 / per-page Shaanxi → **写入 `observation.caveat_text` + `notes`**，**不**改 `observation.status`（保持 PRELIMINARY） |
| OCR confidence 字段 | `obs.confidence NUMERIC` 0-1（已存在 observation 列；tesseract conf 0-100 → /100.0 规整） |
| 默认采样 | Shaanxi 4 页 PDF；page-level `needs_review` per Han agreement < 90% |
| 红线 | 单样本；不批量历史扫描 PDF；不降 gate_thresholds.json；不把 BLOCKED-as-PASS；陕西 ≠ 统计表代表性；不擅自 `pdftotext -bbox` 当 truth 输入 |
| 下一刀 | Cursor 53 → `54-stage0-cursor-s17-plan-audit-*.md` → S1.7 实施 tasking |

---

## §1. 目录与所有权

### §1.1 文件树（增量）

```
china-platform/
├── backend/src/china_platform/connectors/
│   └── scanned_pdf_ocr.py              # NEW (CC owns)
├── tests/
│   └── test_scanned_pdf_ocr_connector.py  # NEW (CC owns; ≥4 per Cursor 50 pattern)
├── docs/
│   ├── 21-stage1-s17-scanned-pdf-ocr-plan-20260825.md   # THIS FILE (CC owns)
└── reviews/
    └── 54-stage0-cc-s17-plan-receipt-20260825.md       # NEW (CC owns)

# 复用（no copy-paste；sys.path shim）
spikes/04-scanned-pdf/
├── extract_04_shaanxi_text.py          # DEFAULT (Chinese-text research track)
├── extract_04_scanned_pdf.py           # FALLBACK (1909 numeric-table track)
├── ocr_text_layout.py                  # 布局感知分栏
├── gate_thresholds.json                # IMMUTABLE（per B-3/B-6；不动）
├── provenance.json                     # source-of-truth SHA-256 + 元数据
├── build_truth_shaanxi_flk.py          # pdftotext -bbox truth builder
└── truth_shaanxi_flk.json              # accepted embedded-layer hash
```

### §1.2 所有权（per Cursor 37 §META）

| 文件 / 决策 | CC | Cursor |
|---|---|---|
| `docs/21-stage1-s17-...-plan-20260825.md` 正文 | ✅ 起草 | ❌ 不改 |
| `backend/.../connectors/scanned_pdf_ocr.py` | ✅ 实现 | ❌ |
| `tests/test_scanned_pdf_ocr_connector.py` | ✅ ≥4 | ❌ |
| `gate_thresholds.json` 修改 | ❌ 严禁 | 严禁；变更须用户书面批准 |
| 1909 → 改代表性中国样本 | ❌ | ❌；user decision required per gate_thresholds.json |
| `provenance.json` 修改 | ❌ | ❌ |
| `extract_04_*.py` 修改 | ❌（**只读复用**）| ❌（spike standalone discipline）|
| migration 004（obs.period_*/lineage/caveat） | ✅ 已实施 | – |
| 假设 OCR confidence 映射 / needs_review 字段决策 | ✅ 提议；Cursor 53 §NOW step 4 | ✅ 审验 |

---

## §2. 类与责任

### §2.1 ScannedPdfOcrConnector

```python
class ScannedPdfOcrConnector:
    """Stage 1 / S1.7 — Scanned PDF OCR 连接器（研究轨；非 Gate 1 代表性）.

    Single-sample pilot: 陕西财政预算管理条例 PDF (spikes/04-scanned-pdf/data/).
    默认走 extract_04_shaanxi_text.run()（Chinese-text research track，已达 unchanged
    applicable thresholds — Han 93.93% / all-non-WS 90.05% / needs_review 25% per page）。

    Fallback: extract_04_scanned_pdf.extract() for the 1909 numeric-table track;
    接受 ONLY as OCR pipeline pressure test（per Stage 0 R4 用户决策）；不接受作为
    Gate 1 代表性统计样本（per gate_thresholds.json user_decision_required）。

    No HTTP. No batch historical scanning. Single-sample per Cursor 53 §NOW 红线 2.
    """

    DEFAULT_SAMPLE = SPIKE_04_DIR / "data" / "shaanxi_fiscal_regulation_flk.pdf"
    DEFAULT_REGISTRY_DOMAIN = "wb.flk.npc.gov.cn"
    DEFAULT_REGISTRY_CATEGORY = "SCANNED_PDF_RESEARCH"
    DEFAULT_SAMPLE_TITLE = "陕西省财政预算管理条例"
    DEFAULT_SAMPLE_PUBLISHER = "陕西省财政厅"
    DEFAULT_SAMPLE_URL = (
        "https://wb.flk.npc.gov.cn/dfxfg/PDF/d31411b562fc4226a7465f1c875afe67.pdf"
    )
    DEFAULT_OCR_LANG = "chi_sim"
    DEFAULT_RENDER_DPI = 300
    DEFAULT_PSM = 6
    DEFAULT_TRACK = "shaanxi_chinese_text"   # DEFAULT；"numeric_table_1909" 仅 fallback

    # methods
    def compute_sha256(self, file_path: Path) -> str
    def extract(self, file_path: Path) -> dict   # returns sha256 + observations + metadata
    def _resolve_source_registry(...)
    def _create_ingestion_run(...)
    def _create_source_document(...)
    def _finalize_ingestion_run(...)
    def _attempt_observation_insert(...)
    def ingest(self, file_path: Path, conn, ...) -> dict
```

### §2.2 三个公开方法签名

```python
def compute_sha256(self, file_path: Path) -> str:
    """SHA-256 hex digest; reuse spike 04 hashlib recipe (no copy-paste).
    必须与 provenance.json["file_hash_sha256"] 完全一致 — 验证 local origin.
    """

def extract(self, file_path: Path) -> dict:
    """Parse scanned PDF; return dict {sha256, observations, lineage, metadata}.

    Branch by DEFAULT_TRACK:
      * "shaanxi_chinese_text" → 调用 extract_04_shaanxi_text.run()，返回 per-page
        observations（每页一条 observation？or 段级？**impl tasking 决策点**）；needs_review
        来源：page-level Han agreement < 90%（per spike 04 README）；caveat_text 来源：page
        Han agreement 数值 + 偏差清单。
      * "numeric_table_1909" → 调用 extract_04_scanned_pdf.extract()，返回 per-cell
        observations（30 rows × 15 cols = 450 obs）；needs_review 来源：value NULL OR
        ocr_confidence < 60 OR identity_mismatch_excess / gs_sum；caveat_text 来源：
        needs_review_reasons 列表。

    Pure file operation; no side effects on DB.
    """

def ingest(self, file_path: Path, conn, triggered_by: str, ...) -> dict:
    """End-to-end: extract → ingestion_run RUNNING → source_document (S0, VERIFIED)
    → observations best-effort (FK placeholder UUIDs → PARTIAL/FAILED in pilot,
    镜像 S1.4/S1.5/S1.6) → ingestion_run final status.

    extraction_method='PDF_OCR'（已存在 schema/01-core.sql enum line 55）.
    """
```

### §2.3 状态语义（mirror S1.4/S1.5/S1.6）

| n_extracted | n_inserted | status |
|---|---|---|
| 0 | 0 | SUCCESS（extract ran clean; 0 obs 是诚实结果）|
| >0 | = n_extracted | SUCCESS |
| >0 | = 0 | FAILED |
| >0 | 介于 | PARTIAL |

---

## §3. ingest_run 钩挂 + S1.7 特殊字段映射

### §3.1 ingestion_run → source_document → observation 链路

1. Resolve `source_registry` by `(domain='wb.flk.npc.gov.cn', category='SCANNED_PDF_RESEARCH')`
2. INSERT `ingestion_run` (status='RUNNING', triggered_by='scanned_pdf_ocr_connector')
3. Compute SHA-256; verify against `provenance.json["file_hash_sha256"]`；INSERT `source_document` (S0, VERIFIED, extraction_method='PDF_OCR')
4. `extract()` → N observation dicts in memory（含 migration 004 字段）
5. Attempt INSERT `observation` 行（FK placeholder UUIDs → PARTIAL/FAILED in pilot）
6. UPDATE `ingestion_run` final status + counts

### §3.2 S1.7 特殊字段映射表（per docs/10 §2.1–2.5 + spike 04 needs_review 语义）

| observation 列 | 数据源 | 转换规则 |
|---|---|---|
| `extraction_method` | constant | `'PDF_OCR'`（已在 enum）|
| `confidence` (NUMERIC 0-1) | `obs.ocr_confidence` from spike 04 | `/ 100.0` 规整；NULL 允许（无 tesseract word 时）|
| `notes` (TEXT) | `obs.needs_review_reasons` 列表 + `obs.needs_review` bool | JSON 字符串：`{"needs_review": true, "reasons": [...]}` |
| `caveat_text` (TEXT, **migration 004**) | per-track | Shaanxi → page Han agreement 数值："本页 Han 一致率 X.XX%，阈值 90%"；1909 → "OCR confidence < 60 or identity_mismatch" |
| `lineage` (JSONB, **migration 004**) | spike 04 lineage | `{chain_id, source_file_sha256, source_file_url, extractor_version: "spike04/1.0"}` |
| `period_start` / `period_end` / `period_label` / `period_type` (migration 004) | per-track | Shaanxi → NULL（法规发布日期 ≠ 数据周期；不漂移周期字段）；1909 → `obs.period = "{year}-12-31"` → period_start/end 可派生 |
| `value` (NUMERIC) | 1909 numeric → `obs.value`（int）| Shaanxi → NULL（法规文本无数值单元；per spike 04 README "numeric N/A not applicable"）|
| `raw_value` (TEXT) | 1909 → `obs.raw_ocr` | Shaanxi → 段级 OCR 文本（per `extract_04_shaanxi_text.run()` 输出结构，**impl tasking 决策点**）|
| `unit` (TEXT) | 1909 → `obs.unit = "1,000 dollars"` | Shaanxi → NULL（text track 无单位维度）|
| `comparison_basis` | constant | `'NEEDS_VERIFICATION'`（OCR 样本无显式同比口径）|
| `value_type` | constant | `'FACT'`（per docs/06 §3 约定）；若 Shaanxi 而后被解析为 quote/text 改为 `'DEFINITION'`（**impl 决策点**）|

### §3.3 needs_review 语义映射（spike 04 → observation.notes）

| Spike 04 needs_review 触发条件 | 写入 observation 字段 |
|---|---|
| 1909: `value is None` | `notes.needs_review=true` + reason `unparseable_ocr` |
| 1909: `conf < 60` | `notes.needs_review=true` + reason `low_ocr_confidence` |
| 1909: `identity_mismatch_excess` / `identity_mismatch_gs_sum` | `notes.needs_review=true` + reason `arithmetic_identity_qc_failed` |
| 1909: `no_ocr_words` | `notes.needs_review=true` + reason `no_ocr_words` |
| Shaanxi: page Han agreement < 90% | `notes.needs_review=true` + reason `page_han_agreement_below_90pct`；`caveat_text` 含具体百分比 |
| Shaanxi: page all-non-WS agreement < 90% | `notes.needs_review=true` + reason `all_non_whitespace_below_90pct` |

**关键决策**：needs_review 是 content-level 标注，**不是** status 列变更。
- `observation.status` 保持 `PRELIMINARY`（默认）
- 若后续人工审核通过 → 走 `observation_revision`（per docs/06 §6-4），不直接改 status
- 避免与 S1.4/S1.5/S1.6 的 PARTIAL/FAILED 语义冲突

---

## §4. docs/10 §2.1–2.5 + needs_review 语义映射

### §4.1 docs/10 §2.1 单位与数量级校验

- Shaanxi text track：无 numeric value → §2.1 N/A（per spike 04 README "numeric N/A not counted as pass"）
- 1909 numeric track：`obs.unit = "1,000 dollars"` 硬编码（per spike 04 line 71）；§2.1 校验：unit 白名单必须含 `"1,000 dollars"` 或改 unit 至 `OBSERVATION_UNIT_ALLOWLIST`

### §4.2 docs/10 §2.2 合计校验

- Shaanxi：N/A（无数值合计语义）
- 1909：spike 04 已有 arithmetic identity QC（excess = exports - imports；gs = gold + silver）；不通过的行打 `identity_mismatch_*` reason

### §4.3 docs/10 §2.3 同比反算

- N/A for both tracks（spike 04 样本为静态年份/页；无时序）
- S1.7 不实现同比；留 Stage 2 / dbt

### §4.4 docs/10 §2.4 跨来源一致性

- S1.7 范围：单样本；无跨来源对比
- 留 Stage 1 dbt / Stage 2 Gate 2

### §4.5 docs/10 §2.5 时间序列异常

- N/A for both tracks（单 PDF / 单页 / 单年）

### §4.6 needs_review 语义合并

| docs/10 测试 | S1.7 实现 |
|---|---|
| 2.1 单位与数量级校验 | 1909 单测断言 unit == "1,000 dollars"；Shaanxi 单测断言 unit is None |
| 2.2 合计校验 | 1909 单测断言 identity QC 不通过行进入 review queue（per spike 04 evaluate_04.py）|
| 2.3 同比反算 | N/A；测试 skip-as-N/A（per spike 04 README "not_applicable_non_tabular_source"）|
| 2.4 跨来源一致性 | N/A；测试 skip-as-N/A（单样本）|
| 2.5 时间序列异常 | N/A；测试 skip-as-N/A（无时序）|

---

## §5. 失败 / 重试

### §5.1 工具链缺失

| 缺失 | 处理 |
|---|---|
| tesseract / pdftotext / pdftoppm | spike 04 `require_tools()` 已 die（exit != 0）；connector 必须 **透传 die**，不静默 skip |
| chi_sim 语言包 | `tesseract --list-langs` 校验；缺则 die |
| poppler (pdftotext / pdftoppm) | OS-level dep；缺则 spike 04 die |

### §5.2 SHA-256 不匹配

```python
if sha256 != provenance["file_hash_sha256"]:
    die(f"sha256 mismatch for {pdf}: expected {expected}, got {actual}")
```

per spike 04 `verify_source()`。**不接受**"re-download"或"重新下载"等绕过路径。

### §5.3 OCR confidence 全 0 / all words 不可解析

- `obs.word_boxes` 为空 → `obs.needs_review=true` + reason `no_ocr_words`
- 不视为 connector 失败；spike 04 设计上 supports needs_review=true 行通过

### §5.4 --verify-determinism（spike 04 自检）

- spike 04 已实现 byte-identical JSON 输出（per B-07/I-01；spike 04 README "deterministic rebuild"）
- connector 复用 extract_*_*.run() 输出；**不自建 JSON 序列化**

### §5.5 FK 失败（pilot 阶段）

- 与 S1.4/S1.5/S1.6 一致：placeholder UUID(int=0) → FK violation
- ingestion_run status → PARTIAL（≥1 obs 尝试过）或 FAILED（全失败）

---

## §6. 红线

| 红线 | 出处 | 处置 |
|---|---|---|
| ❌ 不 Gate 1 PASS | Cursor 53 + docs/08 §2.3 | 仅 S1.7 单样本；Gate 1 留 W6 总评 |
| ❌ 不降 OCR 门槛 / gate_thresholds.json | gate_thresholds.json line 1 "任何低于此值的修改都必须经用户书面批准" | connector 不修改 thresholds.json；不引入可配置 `--threshold-override` |
| ❌ 不把 BLOCKED-as-PASS（1909 状态）| gate_thresholds.json status=FAILED + R4 用户决策 | 1909 track 不走 connector 默认路径；connector 不替 1909 "翻案" |
| ❌ 1909 ≠ 中国 / 陕西 ≠ 统计表代表性 | docs/15 §4a (U-1/U-2/U-3) + README 红线 8 | DEFAULT_TRACK="shaanxi_chinese_text"；DEFAULT_REGISTRY_DOMAIN="wb.flk.npc.gov.cn"（不是 archive.org）|
| ❌ 不批量历史扫描 PDF | Cursor 53 §NOW 红线 3 | 单样本；不实现 multi-PDF / range-PDF |
| ❌ 不以 pdftotext -bbox 当 truth 输入 | spike 04 README "do not use the embedded layer as OCR input" | connector 不写 "use truth as ocr_input" 路径 |
| ❌ 不擅自 --force / --force-with-lease | per `40` §POLL | 普通 `git push` |
| ❌ 不替用户下裁定 | Cursor 37 + §META | 不宣布 Gate 1 / 不表态接受 audit |
| ❌ Cursor 不写 docs/21 正文 | Cursor 37 + Cursor 53 §NOW | CC 起草；Cursor 仅审验 |
| ❌ 不复用 spike 04 网络抓取 | mirror S1.5 红线（不抓源站）| 默认走 repo 内 `spikes/04-scanned-pdf/data/shaanxi_fiscal_regulation_flk.pdf` |
| ❌ 不引入 DSO / pgvector embedding | docs/08 §2.4 | S1.7 仅 OCR 入库；embedding 留 Stage 3 |
| ❌ OCR 不是 numeric-table 统计样本 | per `docs/15 §4a` | observation.value_type='FACT' 仅适用于 1909 track；Shaanxi 改 'DEFINITION' 或 N/A（**impl 决策点**）|

---

## §7. 下一刀

1. CC：`tests/test_scanned_pdf_ocr_connector.py` ≥4（hash / extract / obs + needs_review 完整性 / ingest_run status）→ commit → dual-push → 回执 `54-stage0-cc-s17-plan-receipt-*.md`
2. 等 Cursor 写 `reviews/NN-stage0-cursor-s17-plan-audit-*.md` → 通过后下发 S1.7 实施 tasking（**含 `extraction_method` 决策、observation.raw_value 结构 for Shaanxi、value_type 选 FACT vs DEFINITION**）
3. S1.7 实施：迁移（**若** Cursor 决定加 `observation.extraction_metadata JSONB` 用于 bbox/word_boxes；否则不增列）+ connector + tests + pack + commit + dual-push + receipt
4. S1.8+：ingest_run 监控（per docs/08 §2.1 S1.8）

---

## §8. 已知遗留（impl 决策点 — Cursor 53 后 tasking 决策）

| 项 | 状态 | 留待 |
|---|---|---|
| Shaanxi observation 是 per-page 还是 per-segment？| **schema 候选** | impl tasking 决策 |
| Shaanxi observation.value_type=FACT vs DEFINITION？| **schema 候选** | impl tasking 决策 |
| 1909 track 是否真的当 fallback 保留？| 默认保留（per spike 04 standalone discipline）| impl tasking 确认 |
| `observation.extraction_metadata JSONB` 列（bbox + word_boxes + render_dpi + osd_rotation）？| **schema 候选** | impl tasking 决策（migration 005？）|
| 陕西法规发布日期（数据周期）→ period_* 字段填什么？| **默认 NULL**；per spike 04 不视作数据周期 | impl tasking 确认 |
| `observation_revision` 是否纳入 OCR revisits？| 不实现 | Stage 2 / Stage 3 |
| dbt staging for OCR observations | 不实现 | Stage 1 dbt (S1.9) |
| multi-PDF historical scan | 不实现 | 留 Cursor 53 后 tasking |

---

## §9. 引用

- docs/08 §2.1 S1.7 scope
- docs/08 §2.3 Gate 1 评审标准
- docs/08 §2.4 Stage 1 不做什么
- docs/10 §2.1–2.5 数据层测试
- docs/15 §4a U-1/U-2/U-3 (1909 + 陕西)
- docs/17 Stage 1 kickoff 协议
- docs/20 S1.6 pattern（mirror）
- spike 04 README.md（non-gating research track 边界）
- spike 04 `gate_thresholds.json`（immutable per B-3/B-6）
- spike 04 `provenance.json`（source-of-truth SHA-256）
- Cursor 53 tasking
- Cursor 50 §SCHEMA migration 004（period_*/caveat_text/lineage）
- reviews/40 dead-lock fix + §POLL 协议
- reviews/51 S1.6 receipt 模式（mirror）

— End of docs/21 plan (CC draft) —