# S1.7 — 扫描 PDF OCR 连接器实现任务书

- 编号：`56-stage1-s17-ocr-impl-tasking-20260825`
- 前置：`55` 规划通过；`docs/21`

## SCHEMA / 语义裁定（Cursor）

| 决策点 | 裁定 |
|---|---|
| Shaanxi obs 粒度 | **per-page**（每页 1 条；`raw_value`=该页 OCR 文本） |
| `value_type` | **`FACT`**（enum 无 DEFINITION；禁止新 migration 改 enum） |
| 陕西语义诚实 | `value=NULL` + `missing_reason='NOT_NUMERIC_SOURCE'`；`notes` JSON 含 `research_track=true`、`not_statistical_table=true` |
| `period_*` | Shaanxi 全 **NULL**（法规≠数据周期） |
| `extraction_metadata` 列 | **不做 migration 005**；bbox/dpi 等可入 `lineage` JSONB 扩展键 |
| 1909 fallback | 代码可保留分支；**默认测试只跑陕西**；禁止改 `gate_thresholds.json`；禁止宣布 1909 PASS |

## NOW

1. `backend/src/china_platform/connectors/scanned_pdf_ocr.py` — import spike 04 Shaanxi；默认 `data/shaanxi_fiscal_regulation_flk.pdf`；`extraction_method='PDF_OCR'`
2. `tests/test_scanned_pdf_ocr_connector.py` — ≥4：hash 对 provenance、extract≥1 page、needs_review/`caveat_text` 语义、ingest_run 状态
3. 缺 tesseract/pdftoppm → **fail 透传**（不 skip-as-PASS）
4. pytest 全集 + pack → commit 双推 → 回执 **`57-stage0-cc-s17-impl-receipt-*.md`**
5. 完成后 → **§POLL**（`40` §2）

## 红线

不 Gate 1 PASS；不降 OCR 门槛；不批量；陕西≠统计表代表性；1909≠中国代表性。
