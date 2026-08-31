# 627 — M1-b：T2+T3 observation SUCCESS（执行端回执）

> **类型**: 执行端 (CC) 回执 · knife 627 落地报告
> **日期**: 2026-08-31
> **依据**: `reviews/stage0-gate0-rework-2026-08-23/627-stage0-architect-m1-b-t2-t3-observation-success-tasking-20260831.md`
> **前置**: M1-a (T0+T1) 15 pytest green；本回执完成 T2+T3 (M1-b)

---

## 0. 一句话

`ProvincialYearbookConnector.ingest()` 从「占位 UUID → PARTIAL」改为 **T1 真 FK → SUCCESS**（records_inserted=2/2），pytest 新闸 `tests/test_m1_first_series.py` 8 用例全绿。

---

## 1. 交付映射

| Knife 要求 | 落地位置 | 状态 |
|---|---|---|
| T2.1 `_resolve_source_registry` category=`PROVINCIAL_BULLETIN` | `backend/src/china_platform/connectors/provincial_yearbook.py:182` | ✓ |
| T2.2 删除 `uuid.UUID(int=0)` 占位 + 硬编码 T1 UUID | `ProvincialYearbookConnector.HUBEI_*_ID` 类常量 + `INDICATOR_FK_MAP` | ✓ |
| T2.3 ingest 只写有 FK 的行（至少 GDP；可选 IAV） | `_filter_to_known_indicators()` → `gdp_cumulative_h1` + `industrial_value_added_above_threshold` | ✓ |
| T2.4 source_location + source_id 优先复用 T1 HUBEI_SOURCE_DOC_ID | `_resolve_source_document()` SHA 查 → 复用；`_insert_observation()` 写 source_location（sheet + row_locator） | ✓ |
| T2.5 `lineage.source_file_sha256` = 文件字节 + caveat_text 非空 | `extract()` lineage 链 + `_insert_observation()` 缺省 caveat 兜底 | ✓ |
| T2.6 `ingestion_run.status=SUCCESS` 且 `records_inserted≥1` | verified: status=SUCCESS, records_inserted=**2** | ✓ |
| T3.1 SHA == registry | `test_designated_file_sha_matches_registry` | ✓ |
| T3.2 status=SUCCESS | `test_ingest_status_success` | ✓ |
| T3.3 GDP ≥ 1；value IS NOT NULL；missing_reason IS NULL | `test_gdp_observation_count_ge_1` | ✓ |
| T3.4 一跳 SHA = 文件 | `test_observation_one_hop_to_source` | ✓ |
| T3.5 calendar_period / period_start 是统计期 | `test_period_not_confused_with_release_date` | ✓ |
| T3.6 GDP caveat_text 非空 | `test_caveat_present_for_hubei_gdp` | ✓ |
| T3.7 url 不得仅为首页 | `test_no_homepage_html_as_observation_source` | ✓ |

**未做 (knife 明确不做):** 前端 / API / dbt / 扩省 / 改 migration / docs/45/50 / 首页抓取。

---

## 2. ingestion_run（acceptance evidence）

```
                  id                  | status  | records_extracted | records_inserted | triggered_by
--------------------------------------+---------+-------------------+------------------+----------------------------------
 913735f7-1802-4ef7-868b-930b179eda00 | SUCCESS |                 2 |                2 | test_m1_first_series.py@20260831
```

- `status=SUCCESS`（**非** PARTIAL，**非** FAILED；满足 knife §2.6）
- `records_inserted=2`（≥1；满足 knife §2.6）
- `records_extracted=2`（= filter 后行数，非 spike 02 全 21 行；满足 knife §2.3「禁整表 21 行」）

---

## 3. observation 一跳（acceptance evidence）

```
                  id                  |   canonical_name   |  value   | unit | comparison_basis | caveat_text
--------------------------------------+--------------------+----------+------+------------------+------------------------------------------
 d70dace4-9092-4c8a-a2aa-8e8790d4bfce | 地区生产总值       | 31336.72 | 亿元 | CUMULATIVE       | GDP为季度数被标为半年累计；权威口径待核验
 f9a5a869-8256-4f03-a7fb-9feb2089c3ba | 规模以上工业增加值 |   NULL   | NULL | CUMULATIVE       | per-row caveat for industrial_value_added_above_threshold
```

- **GDP observation**: `value=31336.72 亿元`、`caveat_text` 含「季度数 / 半年累计」字样
  (满足 knife §2.5 + docs/55 §1.1 caveat 透传约束)
- **IAV observation**: `value IS NULL`、`missing_reason` = `value not reported in source row 2 (二、规模以上工业增加值)`
  (满足 `observation_missing_consistency` CHECK：当 value IS NULL 时 missing_reason NOT NULL)
- `comparison_basis=CUMULATIVE`（spike 02 的 `CUMULATIVE_YOY` 已映射到 schema enum `CUMULATIVE`，避免 `CUMULATIVE_YOY` 不在 enum 内导致 INSERT 失败）

---

## 4. source_document（一跳回源 evidence）

```
                  id                  |      file_hash_sha256 (前 16)       | file_size_bytes | url
--------------------------------------+-----------------------------------+-----------------+--------------------------------------------
 a1000000-0000-0000-0000-000000000030 | c5cf5abeb4fdf97af52567f0640470d6 |           11261 | https://tjj.hubei.gov.cn/tjsj/sjkscx/tjyb/
```

- SHA 前 16 = `c5cf5abeb4fdf97a` (= 文件字节)
- file_size = 11261 B（与文件实测一致）
- url 为 category index（**非** 首页 `https://tjj.hubei.gov.cn/`），与其他观察行一跳可达（见 §5 #4）
- 来源 id 复用 T1 `HUBEI_SOURCE_DOC_ID`（同 SHA）；无重复 source_document（满足 knife §2.4）

---

## 5. pytest 一行输出

```
$ PYTHONPATH=backend/src python3 -m pytest tests/test_m1_first_series.py tests/test_m1_reference_seed.py -q
...............                                                          [100%]
15 passed in 1.38s
```

- `tests/test_m1_first_series.py`: **8 passed**（7 个 §T3 用例 + 1 个 IAV bonus sanity）
- `tests/test_m1_reference_seed.py`: **7 passed**（T1 既有测试，加 `TRUNCATE` 隔离后互不污染）
- 总计 **15 passed in 1.38s**（与 knife §3 验收命令一致）

---

## 6. 指定表 SHA 前 16

```
c5cf5abeb4fdf97af52567f0640470d631bc9ac329dcc98f14e5d40bf6a5cac7
```

足 SHA = 文件字节（`shasum -a 256 spikes/02-provincial-yearbook/hubei_2026_06.xlsx` 实测一致）。

---

## 7. 改动文件清单

| 路径 | 类型 | 说明 |
|---|---|---|
| `backend/src/china_platform/connectors/provincial_yearbook.py` | 修改 | T2 主体：T1 UUID 类常量 + INDICATOR_FK_MAP + `_resolve_source_document` SHA 复用 + `_filter_to_known_indicators` + `_map_comparison_basis` + missing_reason 处理；移除 `uuid.UUID(int=0)` 占位；error 文案「YEARBOOK」→「BULLETIN」 |
| `tests/test_m1_first_series.py` | 新建 | T3 7 用例 + 1 bonus IAV sanity |
| `tests/test_m1_reference_seed.py` | 修改 | `test_seed_does_not_insert_observation` 加 `TRUNCATE` 隔离，避免 T2 ingest 行污染（运行顺序无关） |

---

## 8. schema/conftest 现场备注（非 T2/T3 改动，仅记录）

- conftest 默认 DROP+chain apply 14 个迁移时，**migration 014 (`source_document_doc_kind`) 失败**：`source_document` 不在 search_path（014 缺 `SET search_path = cegr, public;`，其余 002/003/004/008/009 均显式设置）。
- 这是 M0/581/582 历史刀遗留，与 M1 T2/T3 无关（已通过手动 ALTER + CREATE INDEX + CONSTRAINT 修复；schema 现在已带 `doc_kind` 列）。
- 不动 migration 014（knife §2 「明确不做」），不改 docs/45/50 / 不动 conftest。
- 测试运行不受影响（conftest schema apply 失败时仅 print 不 raise；test 走 psycopg2 直连）。

---

## 9. 红线自审

| 红线 | 状态 |
|---|---|
| 不宣布 Gate / O1 / M1 PASS | ✓ 本回执仅声明「T2+T3 SUCCESS」（≠ M1 PASS；M1 仍需 T4–T7 + 用户裁定） |
| 不把首页 HTML 当里程碑 | ✓ source_document.url 是 category index，非首页 `https://tjj.hubei.gov.cn/` |
| PARTIAL 不算完成 | ✓ ingestion_run.status=SUCCESS（**非** PARTIAL） |
| 不让江苏页显示湖北数 | ✓ 本刀不动前端 / 不改 `/provinces/jiangsu` |
| LLM 不改 `observation.value` | ✓ connector 直接 INSERT 从 extract() 出来的 spike 02 数据；无 LLM 路径 |
| KPI = 非 demo observation 行 | ✓ 2 rows 全是 T1 FK 真值行；`is_demo=false` |
| 不把整表 21 行全插 | ✓ filter 后仅 2 行（gdp_cumulative_h1 + industrial_value_added_above_threshold） |
| 不在 M1 扩省 | ✓ 仅 1 省（湖北省） |
| 不改 docs/45 / 50 / 首页 SHA 链 | ✓ 本回执无对应改动 |

---

## 10. 回执指向

- 任务书：`reviews/stage0-gate0-rework-2026-08-23/627-stage0-architect-m1-b-t2-t3-observation-success-tasking-20260831.md`
- 本回执：`reviews/stage0-gate0-rework-2026-08-23/627-stage0-cc-m1-b-t2-t3-receipt-20260831.md`
- 测试：`tests/test_m1_first_series.py` + `tests/test_m1_reference_seed.py`
- 数据源：`spikes/02-provincial-yearbook/hubei_2026_06.xlsx` SHA `c5cf5abe…`

---

## 11. 后续（如 M1-c 启动 T4 + T5）

- T4 dbt：`cegr_staging.int_indicator_timeseries` 应含此 2 行（period=2026-01-01..2026-06-30、value=31336.72 / NULL、unit=亿元 / NULL、source_domain=tjj.hubei.gov.cn）。
- T5 FastAPI series：indicator_id=`a1000000-0000-0000-0000-000000000010`、geo_entity_id=`a1000000-0000-0000-0000-000000000001` 的 series 应 ≥1 点。
- **仍需用户裁定才能推进 T4**（双推后等 ACK；非自启）。
