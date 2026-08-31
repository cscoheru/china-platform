# 633 — M2-b：首批 ≥5 省/国 2024 GDP 表级 ingest（架构师任务书）

> **类型**: Architect 签发（不写实现）  
> **日期**: 2026-08-31  
> **依据**: `docs/56` §M2-b；`docs/08b` §1.2；632 audit PASS；用户「签 M2-b」  
> **前置**: M2-a `ee8e285` · 632 PASS · inventory 32 行基线  
> **禁止**: Gate/O1/M2 PASS；首页/目录页当 FETCHED 完成；补零；买库；江苏页绑他省

---

## 0. 一句话

把 inventory 里 **≥5 个主体**（国家 + 苏/浙/粤优先 + 湖北另取 **2024 年度**）从 PENDING/BLOCKED 推到 **定稿表字节归档 → SHA 锁 → observation SUCCESS**，coverage KPI **≥5/31**。

---

## 1. 前置 hygiene（本刀必须先做）

1. **`scripts/seed_m2_province_geo.py` `unload()`**  
   - `DELETE source_registry WHERE id = DOC_ID` → **`REGISTRY_ID`**  
   - 同步 `DELETE source_document WHERE id = DOC_ID`（或按 FK 顺序先 doc 后 reg）  
   - 回归：unload 后再 seed，`source_registry` CODE_REFERENCE 行可清可重建

2. **年期校验**  
   - inventory 中国家行 URL `…/202402/t20240228_…` 极可能是 **2023 年**公报（2024-02 发布）。  
   - 执行端必须读页面标题/正文确认统计期；若是 2023 → **换 2024 年公报或 2024 年 GDP 初步核算定稿页**；不得把 2023 值标成 2024。

---

## 2. 首批主体（锁定优先序）

| # | 主体 | geo | 说明 |
|---|---|---|---|
| 1 | 国家 | `00` | NBS **2024** 年 GDP（公报或初步核算表） |
| 2 | 江苏省 | `32` | U3 试点优先 |
| 3 | 浙江省 | `33` | U3 |
| 4 | 广东省 | `44` | U3 |
| 5 | 湖北省 | `42` | **不得**复用 M1 `hubei_2026_06.xlsx`（2026H1）；另取 **2024 年度**表 |

Fallback（仅当上表某源 TECH_BLOCKED）：上海 / 山东 / 四川 — 须在回执写明替换原因。  
合计成功 ingest 的 **geo×2024×GDP 有值行 ≥5**（国家算 1 个「省级行」外的 COVERED 或单独计；coverage 脚本须把国家与 31 省口径写清——建议 KPI 分母仍 31 省，国家另行列；**至少 5 个省级有值，或 4 省+国家且回执声明**）。

**默认验收口径（本刀）：** `coverage` 报告中 **COVERED ≥ 5**（仅计 31 省级）；国家行必须同时 SUCCESS 入库，另在 PHOTO 展示。若国家成功但省侧不足 5 → **FAIL**。

---

## 3. 交付（技术）

### A. 取数与归档（每主体）

1. 从 inventory `candidate_url` **下钻**到含 2024 年 GDP 数值的**定稿页或 xlsx/pdf 表**（禁止停在 `/tjgb/` 目录列表页）。  
2. 字节写入 `data/seed_archives/m2_2024_gdp/{geo_code}_{slug}.{ext}`（或等价路径）。  
3. `shasum -a 256` → 回填 inventory：`local_sample_path`、`file_hash_sha256`、`status=FETCHED`（或解析失败则 `BLOCKED` + `missing_reason`，**不得** FETCHED）。  
4. `asset_kind` 与真实格式一致（`HTML_TABLE` / `XLSX` / `PDF_TABLE`）。

### B. 参考数据（2024 年度）

- `calendar_period`：2024 全年（`period_start=2024-01-01`，`period_end=2024-12-31`，label 清晰）。  
- `indicator_definition`：年度地区生产总值（可新 UUID `a2000000-…` 族，或扩展 M1 指标并加 methodology **年度 vs 半年** 不得合并错期）。  
- 复用 M2-a `geo_entity`；湖北用 M1 id。

### C. Ingest

- 连接器：扩展现有 provincial/NBS 路径 **或** 新建 `scripts/ingest_m2_2024_gdp.py`（最小）；每主体 `ingestion_run.status=SUCCESS`，`records_inserted≥1`。  
- `observation.value` 非空；`missing_reason` IS NULL；`caveat_text` 必填（初步核算/最终核实/产业合计口径等）。  
- `source_document.file_hash_sha256` = 文件字节；一跳回源。  
- **PARTIAL 不算交付。**

### D. Coverage

- 重跑 `scripts/report_m2_gdp_coverage.py` → 更新 `docs/reports/m2_2024_gdp_coverage_*.md`  
- KPI：省级 COVERED **≥5/31**；BLOCKED/PENDING 诚实。

### E. 测试（新建 `tests/test_m2_b_first_batch.py`）

1. `test_unload_deletes_registry_not_doc_id` — unload 清掉 `REGISTRY_ID`  
2. `test_inventory_first_batch_fetched_or_blocked` — 5 优先主体均非「空 hash 的 FETCHED」  
3. `test_no_directory_or_homepage_fetched` — FETCHED 的 URL path 不得为 `/` 或仅 `…/tjgb/` 类目录（允许具体文章 path）  
4. `test_observation_2024_gdp_count_ge_5` — 31 省中 2024 GDP value 非空 ≥5  
5. `test_one_hop_sha` — 抽样 1 省：observation → source_document.hash == 文件  
6. `test_hubei_not_using_2026h1_sample_as_2024` — 湖北 2024 行的 source hash **≠** `c5cf5abe…`（M1 半年表）  
7. `test_m1_regression_subset` — `test_m1_reference_seed` 或 first_series 子集仍绿（或显式调用关键断言）

验收：

```bash
STAGE0_SKIP_SCHEMA_APPLY=1 PYTHONPATH=backend/src \
  python3 -m pytest tests/test_m2_b_first_batch.py tests/test_m2_province_geo_seed.py -q
```

---

## 4. 明确不做

- 不扩满 31 省（→ M2-c）  
- 不跨源核对（→ M2-d）  
- 不建 `/research/q1-2024-gdp`（→ M2-e）  
- 不改 docs/45/50；不镀铬四轨；不买库  
- 不宣布 Gate / M2 PASS  

---

## 5. 回执（一份）

`633-stage0-cc-m2-b-first-batch-receipt-YYYYMMDD.md` 须含：

| 块 | 内容 |
|---|---|
| PHOTO-1 | pytest 一行 |
| PHOTO-2 | 5+ 主体：geo、value、unit、SHA 前 16、status |
| PHOTO-3 | coverage Summary（COVERED≥5） |
| PHOTO-4 | unload 修复 diff 一行证据 |
| PHOTO-5 | 红线表（无目录 FETCHED；湖北≠c5cf5abe） |
| PHOTO-6 | 文件清单 |

双推 → POLL。

---

## 6. Cursor 审验点

- COVERED≥5；一跳 SHA；湖北非 M1 半年表  
- unload 债已清  
- 国家统计期确为 2024  
- 未宣称 M2/Gate PASS  

— End 633 —
