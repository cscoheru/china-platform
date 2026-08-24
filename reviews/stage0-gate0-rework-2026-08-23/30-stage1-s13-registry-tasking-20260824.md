# Stage 1 — S1.3 source_registry 入表 + URL 监控（dry-run）

- 文件编号：`30-stage1-s13-registry-tasking-20260824`
- 下发方：Cursor
- 日期：2026-08-24
- 前置：`29` S1.1 审验通过

---

## §0. NOW（禁止 IDLE）

| # | 任务 | 退出标准 |
|---|---|---|
| 1 | `scripts/import_registry_csv.py`（或等价） | 读 `source_registry/registry.csv` → UPSERT `source_registry` 表 6 行 |
| 2 | 测试 `tests/test_registry_import.py` | 行数=6；`declared_source_level` 与 CSV 一致；S0+UNVERIFIED 触发 CHECK 失败用例 |
| 3 | `scripts/health_check_registry.py --dry-run` | 只打印将检查的 URL；**不发 HTTP**（per docs/17） |
| 4 | pytest 全集 + pack 若动 docs/scripts | 251 pass；pack_errors=0 |
| 5 | commit 双推 + `31-stage0-cc-s13-receipt-*.md` | |

**禁止：** 真 HTTP 爬取；改 S0/S3 等级；ingest 数据。

---

## §1. 红线

- ❌ Gate 1 PASS
- ❌ 批量爬取
- ❌ 降 OCR 门槛

— End S1.3 —
