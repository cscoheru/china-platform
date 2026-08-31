# 627 — M1-b：T2+T3 observation SUCCESS（架构师任务书）

> **类型**: Architect 签发（不写实现 / 不 commit 实现）
> **日期**: 2026-08-31
> **依据**: `docs/55` §T2–T3；`docs/54` M1；用户同意对齐队列并签 M1-b
> **前置**: M1-a（T0+T1）本地闭环 — `pytest tests/test_nbs_monthly_connector.py tests/test_m1_reference_seed.py` → **15 passed**（含 registry CSV 闸修）
> **禁止**: 宣布 Gate / O1 / M1 PASS；首页 HTML；PARTIAL 当完成；江苏页显示湖北数

---

## 0. 一句话

把 `ProvincialYearbookConnector.ingest()` 从「占位 UUID → PARTIAL」改成 **T1 真 FK → SUCCESS**，并用 `tests/test_m1_first_series.py` 锁死。

---

## 1. 锁定输入

| 项 | 值 |
|---|---|
| 文件 | `spikes/02-provincial-yearbook/hubei_2026_06.xlsx` |
| SHA-256 | `c5cf5abeb4fdf97af52567f0640470d631bc9ac329dcc98f14e5d40bf6a5cac7` |
| registry | `tjj.hubei.gov.cn` / **`PROVINCIAL_BULLETIN`**（不是 YEARBOOK） |
| 验收指标 | `gdp_cumulative_h1`（源名含「地区生产总值」） |
| T1 UUID | `scripts/seed_m1_reference_data.py`：`a1000000-…001` 省 / `…002` geo_code / `…010` GDP / `…011` GDP MV / `…0601` 2026H1 period / `…030` source_doc |

CLI：`python -m china_platform.connectors.provincial_yearbook --from-local-sample`（无 HTTP）。

---

## 2. T2 — 连接器改动

**文件：** `backend/src/china_platform/connectors/provincial_yearbook.py`（必要时 `__init__.py` / CLI）。

**必做：**

1. `_resolve_source_registry`：category=`PROVINCIAL_BULLETIN`；错误文案勿再写 YEARBOOK。
2. 删除 `uuid.UUID(int=0)` 占位；解析 T1 UUID（硬编码常量 OK，与 seed 脚本一致；或 DB lookup by short_code/name）。
3. **ingest 只写入已有 FK 的行**：至少 GDP；可选 IAV。禁止把整表 21 行全插导致未种子指标 FK 失败 → **PARTIAL**。
4. 写 `source_location`（sheet + 行号；与 `source_document` 复合 FK）。`source_id` 优先复用 T1 `HUBEI_SOURCE_DOC_ID`（同 SHA），避免同哈希多文档；若新建文档，SHA 必须 = 文件字节。
5. `lineage.source_file_sha256` = 文件字节；`caveat_text` 非空（季度 vs 半年）。
6. `ingestion_run.status=SUCCESS` 且 `records_inserted≥1`。**PARTIAL / FAILED 不算交付。**

**明确不做：** 前端、API、dbt、扩省、改 migration、改 docs/45/50、首页抓取。

---

## 3. T3 — pytest 闸

**新建：** `tests/test_m1_first_series.py`（用例名按 docs/55 §T3 七条）。

| # | 断言 |
|---|---|
| 1 | 指定 xlsx SHA == registry 该行 |
| 2 | `ingestion_run.status == SUCCESS`（PARTIAL 即失败） |
| 3 | GDP observation ≥1；`value IS NOT NULL`；`missing_reason IS NULL` |
| 4 | `observation.source_id → source_document.file_hash_sha256` == 文件 |
| 5 | `calendar_period` / `period_start` 是统计期，不是 `extracted_at` |
| 6 | GDP 行 `caveat_text` 非空 |
| 7 | 该批 `source_document.url` 不得仅为 `https://tjj.hubei.gov.cn/` 首页 |

**验收命令：**

```bash
# 先确保种子与 registry
python scripts/import_registry_csv.py
python scripts/seed_m1_reference_data.py
PYTHONPATH=backend/src python -m pytest \
  tests/test_m1_first_series.py tests/test_m1_reference_seed.py -q
```

exit 0 才可写回执。

---

## 4. 回执要求

回执文件：`627-stage0-cc-m1-b-t2-t3-receipt-20260831.md`（或次日日期）。

须含：

- `ingestion_run` id + status=SUCCESS + inserted 数
- 一条 GDP observation id + value + unit + caveat 摘要
- pytest 一行输出
- 指定表 SHA 前 16
- 声明：未宣布 Gate/O1/M1 PASS；未取首页

双推后 POLL。若仍 PARTIAL → **停**，不进 T4。

---

## 5. Cursor 审验点（下轮）

- 无 `UUID(int=0)` 残留于 observation INSERT 路径
- SUCCESS 非手改 status
- 一跳 SHA = 文件字节
- 测试失败若 PARTIAL
- 未把江苏页绑湖北数

— End 627 —
