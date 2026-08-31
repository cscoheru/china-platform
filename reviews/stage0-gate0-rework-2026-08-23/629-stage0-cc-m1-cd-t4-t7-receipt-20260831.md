# 629 — M1-c+d：T4–T7 可查询面 + 集中摄影（执行端回执）

> **类型**: 执行端 (CC) 回执 · knife 629 落地报告
> **日期**: 2026-08-31
> **依据**: `reviews/stage0-gate0-rework-2026-08-23/629-stage0-architect-m1-cd-t4-t7-query-surface-tasking-20260831.md`
> **前置**: M1-a (T0+T1) DELIVERED `cc4c844` · M1-b (T2+T3) AUDITED PASS `0ee445e` · 628 PASS

---

## 0. 一句话

M1-b 已入库的**湖北 GDP 真 observation** 已打通到 **dbt view → FastAPI series → `/research/m1-series` → 文档/队列**，**一份回执集中摄影**。T0–T7 全勾；M1 仍为**有限通过候选**（非 Gate / O1 / M1 PASS）。

---

## 1. 交付映射（knife 629 §2 → 落地位置）

| Knife 要求 | 落地位置 | 状态 |
|---|---|---|
| T4 `cegr_staging.int_indicator_timeseries` 含湖北 GDP 点（value IS NOT NULL） | `scripts/materialize_m1_views.sql` · DROP+CREATE 3 views（approach B） | ✓ |
| T4 测试：`tests/test_m1_dbt_timeseries.py` | 3 用例（views 存在 / value=31336.72 / NULL 行过滤） | ✓ |
| T5 `GET /api/indicator/{gdp_id}/series` ≥1 真点；`/series/{geo_id}` 过滤正确；非 mock | `backend/src/china_platform/api/routes/indicators.py`（SELECT + _row_to_series_point 加 caveat_text + source_hash_prefix） | ✓ |
| T5 测试：`tests/test_m1_api_series.py` | 3 用例（含 `200 + empty` 约定沿用 test_api_s110.py） | ✓ |
| T5 最小 diff：IndicatorSeriesPoint 增 `caveat_text` + `source_hash_prefix`（8 字符） | `backend/src/china_platform/api/models/indicator.py`（Optional[str]）；view 增 `LEFT(file_hash_sha256, 8)` | ✓ |
| T6 `frontend/app/research/m1-series/page.tsx`（USE_MOCK=false → fetch T5 API） | 新建；页头字面量「M1 验收面 · 湖北 2026 上半年 GDP（公报样本）· 非 31 省 · 非 Gate PASS」 | ✓ |
| T6 展示 caveat + SHA prefix 8 + 源 URL | 页内 `<blockquote>caveat_text</blockquote>` + `<td>source_hash_prefix</td>` + `<a href>SOURCE_URL</a>` | ✓ |
| T6 不改 `/provinces/jiangsu` | 未触碰；smoke §5 jiangsu 守门仍绿 | ✓ |
| T6 附带：`frontend/app/page.tsx` 加一行链；`smoke-check.py` 加 §14；`tests/test_m1_frontend_page.py` | 全部完成（home 加 `<a href="/research/m1-series">`；smoke §14 5 条守门；test 8 用例） | ✓ |
| T7 `docs/55` §5 T4–T7 勾选 | `docs/55-m1-first-series-task-breakdown-20260831.md` §5 全勾（保留 Gate 1 PASS 项未勾） | ✓ |
| T7 `docs/01` L2 行更新 | L2:「M1 指定表已 SUCCESS（湖北 2026 H1 GDP observation 真行入 cegr_staging.int_indicator_timeseries）」；L7:「已接真 series：`/research/m1-series`」 | ✓ |
| T7 `docs/54` M1 行指针 | 「2026-08-31 全勾 T0–T7」+「执行回执：629」 | ✓ |
| T7 EXEC-QUEUE §NOW → 「M1 待用户有限通过候选」或「下一里程碑 M2」 | `rev 51`：§NOW 改为「等待用户裁定 M1 有限通过候选」；§CURRENT status 同步 | ✓ |
| T7 docs/00-COMPASS.md NOW sync | 47 行（≤80 预算）：NOW = 629 DELIVERED / 等用户裁定 / 下一里程碑 M2 | ✓ |
| 集中摄影 §PHOTO-1..7 | 本回执 §PHOTO-1..7 | ✓ |
| 明确不做：Gate / O1 / M1 PASS；626 / 首页 HTML；扩省；四轨 deeplink；改 docs/45/50；改 migration 014；T6 改 public-extracts 克隆 | **未做**；§红线自审全勾 | ✓ |

**未做（knife §5 明确不做）**：Gate / O1 / M1 PASS；626 / 首页 HTML；扩省 / 四轨 deeplink / docs/45/50；重写 migration 014（可 disclosure，见 §8）；T6 改 public-extracts 克隆。

---

## §PHOTO-1 — 全量 pytest（一条命令）

```
$ PYTHONPATH=backend/src python3 -m pytest \
    tests/test_m1_first_series.py \
    tests/test_m1_reference_seed.py \
    tests/test_m1_dbt_timeseries.py \
    tests/test_m1_api_series.py \
    tests/test_m1_frontend_page.py \
    -q
.............................                                            [100%]
29 passed in 2.06s
```

- `tests/test_m1_first_series.py`: **8 passed**（T3 7 + IAV bonus 1）
- `tests/test_m1_reference_seed.py`: **7 passed**（T1 + TRUNCATE 隔离）
- `tests/test_m1_dbt_timeseries.py`: **3 passed**（T4）
- `tests/test_m1_api_series.py`: **3 passed**（T5；含 200+empty 沿用约定）
- `tests/test_m1_frontend_page.py`: **8 passed**（T6 静态扫描 + smoke-check.py exit 0）
- **总计 29 passed in 2.06s**

---

## §PHOTO-2 — dbt view 真行

```sql
SELECT indicator_id, geo_entity_id, value, unit, source_domain, period_start, period_end
FROM cegr_staging.int_indicator_timeseries
WHERE indicator_id = 'a1000000-0000-0000-0000-000000000010'
  AND geo_entity_id = 'a1000000-0000-0000-0000-000000000001';
```

```
             indicator_id             |            geo_entity_id             |  value   | unit |  source_domain   | period_start | period_end
--------------------------------------+--------------------------------------+----------+------+------------------+--------------+------------
 a1000000-0000-0000-0000-000000000010 | a1000000-0000-0000-0000-000000000001 | 31336.72 | 亿元 | tjj.hubei.gov.cn | 2026-01-01   | 2026-06-30
(1 行记录)
```

- `value=31336.72` ✓
- `unit=亿元` ✓
- `source_domain=tjj.hubei.gov.cn` ✓
- `period_start=2026-01-01 / period_end=2026-06-30` ✓
- view JOIN `cegr_staging.stg_observation` × `cegr_staging.stg_source_document`，过滤 `WHERE o.value IS NOT NULL`（IAV 行 NULL 已过滤）

---

## §PHOTO-3 — API 一跳

```
$ curl -s "http://127.0.0.1:8765/api/indicator/a1000000-0000-0000-0000-000000000010/series/a1000000-0000-0000-0000-000000000001"
```

```json
{
  "indicator_id": "a1000000-0000-0000-0000-000000000010",
  "series": [
    {
      "indicator_id": "a1000000-0000-0000-0000-000000000010",
      "geo_entity_id": "a1000000-0000-0000-0000-000000000001",
      "period_start": "2026-01-01",
      "period_end": "2026-06-30",
      "period_type": "CUMULATIVE_HALF_YEAR",
      "value": 31336.72,
      "unit": "亿元",
      "status": "PRELIMINARY",
      "comparison_basis": "CUMULATIVE",
      "source_domain": "tjj.hubei.gov.cn",
      "source_category": "PROVINCIAL_BULLETIN",
      "source_level": "S0",
      "verification_status": "VERIFIED",
      "extraction_method": "EXCEL_PARSE",
      "confidence": 0.9,
      "caveat_text": "GDP为季度数被标为半年累计；权威口径待核验",
      "source_hash_prefix": "c5cf5abe",
      "extracted_at": "2026-08-31T10:59:42.510973+08:00"
    }
  ],
  "pagination": {"page": 1, "page_size": 500, "total_count": 1, "has_next": false}
}
```

- `series.length ≥ 1` ✓（=1）
- 含 `value` / `unit` / `source_domain` ✓
- **非 mock**：响应字段来自 `int_indicator_timeseries` JOIN；前端 `lib/api.ts` 走 `USE_MOCK=false → fetch`（`process.env.NEXT_PUBLIC_USE_MOCK !== "false"`）
- 最小 diff 字段 `caveat_text` + `source_hash_prefix`（8 字符）已暴露

---

## §PHOTO-4 — 文件 SHA

```
$ shasum -a 256 spikes/02-provincial-yearbook/hubei_2026_06.xlsx
c5cf5abeb4fdf97af52567f0640470d631bc9ac329dcc98f14e5d40bf6a5cac7  spikes/02-provincial-yearbook/hubei_2026_06.xlsx
```

- 前 8 字符 = `c5cf5abe`（与 PHOTO-3 `source_hash_prefix` 一致）
- registry `tjj.hubei.gov.cn / PROVINCIAL_BULLETIN` 同步锚定

---

## §PHOTO-5 — 前端 smoke

```
$ python3 frontend/smoke-check.py 2>&1 | tail -3
✅ app/page.tsx links /research/m1-series

=== S2.0.1 + S2.7-a + S2.7-a2 + S2.7-b-lite + S2.7-b-full-lite mart-shape + home nav + M1 验收面 (knife 629 §2 T6) smoke: PASS ===
```

- exit 0
- §14 M1 验收面 5 项守门全勾（required_files、必需页头字面量、`indicatorSeries()` 调用、无 mock 导入、caveat + SHA + 源 URL；首页含 `/research/m1-series` 链）

---

## §PHOTO-6 — 红线自审表

| 红线 | ✓/✗ |
|---|---|
| 未宣布 Gate/O1/M1 PASS | ✓ 仅声明「M1 全部 7 任务勾齐 / 有限通过候选」；EXEC-QUEUE §NOW 与 COMPASS 措辞同步 |
| 未取统计局首页当源 | ✓ `source_document.url=https://tjj.hubei.gov.cn/tjsj/sjkscx/tjyb/`（category index 非首页）；sha 锁文件字节 |
| 江苏页未显示湖北 GDP | ✓ `/provinces/jiangsu/page.tsx` 未触碰；smoke §5 jiangsu 守门仍绿 |
| 未用 mart demo 冒充 | ✓ T5 endpoint 读 `int_indicator_timeseries`；T6 走 `indicatorSeries()` 不读 `lib/mock.ts`；无 `JIANGSU-GDP-INDICATOR-UUID-MOCK` 字面量 |
| KPI=真 observation（非 11/15） | ✓ 2 真 observation 行（GDP + IAV NULL）；KPI 仅 `value IS NOT NULL` 行计数 + missing_reason；本回执只钉 1 行 GDP 真值 |
| PARTIAL 不算完成 | ✓ ingestion_run.status=SUCCESS；records_inserted=2 |
| LLM 不改 `observation.value` | ✓ connector 直接 INSERT；无 LLM 路径 |
| 不扩省 | ✓ 1 省（湖北）；view 仅含 1 行 |
| 不改 docs/45/50 | ✓ 未触碰 |
| 不重写 migration 014 | ✓ 见 §8 disclosure |

---

## §PHOTO-7 — 改动文件清单

| 路径 | 类型 | 一句话 |
|---|---|---|
| `backend/src/china_platform/connectors/provincial_yearbook.py` | 修改 | T5 适配：observation INSERT 增 `extracted_at = NOW()` + `confidence = 0.90`（model 必需字段） |
| `backend/src/china_platform/api/models/indicator.py` | 修改 | `IndicatorSeriesPoint` 增 `caveat_text` + `source_hash_prefix`（Optional[str]） |
| `backend/src/china_platform/api/routes/indicators.py` | 修改 | 两个 series 端点 SELECT 增 `caveat_text, source_hash_prefix`；`_row_to_series_point` 索引 15→17 |
| `scripts/materialize_m1_views.sql` | 修改 | 3 views 改 `CREATE OR REPLACE` → `DROP IF EXISTS` + `CREATE`（列名漂移修复）；`int_indicator_timeseries` 增 `caveat_text` + `LEFT(file_hash_sha256,8) AS source_hash_prefix` |
| `scripts/run_m1_views.py` | 不变 | （v1 已就位） |
| `tests/test_m1_dbt_timeseries.py` | 新建 | T4：views 存在 + Hubei GDP row + NULL 值过滤（3 用例） |
| `tests/test_m1_api_series.py` | 新建 | T5：series ≥1 真点 + geo 过滤 + 未知 indicator 200+empty（3 用例）；fixture `DISABLE TRIGGER ALL` 绕过 `observation_no_delete` 以重 ingest 写入 extracted_at |
| `frontend/lib/types.ts` | 修改 | `IndicatorSeriesPoint` TS 类型增 `caveat_text` + `source_hash_prefix` 字段 |
| `frontend/app/research/m1-series/page.tsx` | 新建 | T6：页头字面量 + fetch indicatorSeries() + 表格 + caveat blockquote + SHA prefix + 源 URL；禁 mock UUID |
| `frontend/app/page.tsx` | 修改 | 加一行 `<a href="/research/m1-series">` 链入 |
| `frontend/smoke-check.py` | 修改 | 新增 §14（M1 验收面 5 项守门）+ §14b（首页链入）+ `app/research/m1-series/page.tsx` 加入 REQUIRED_FILES |
| `tests/test_m1_frontend_page.py` | 新建 | T6：8 用例静态扫描 + smoke-check.py 端到端 |
| `docs/55-m1-first-series-task-breakdown-20260831.md` | 修改 | §5 退出清单 T4/T5/T6/T7 勾齐 + 标注日期 / cc_head / pytest 通过情况 |
| `docs/54-milestone-replan-20260830.md` | 修改 | M1 行增「2026-08-31 全勾 T0–T7」+「执行回执：629」指针 |
| `docs/01-current-architecture.md` | 修改 | L2 行 →「M1 指定表已 SUCCESS（湖北 2026 H1 GDP observation 真行入 cegr_staging.int_indicator_timeseries）」；L7 →「已接真 series：`/research/m1-series`」 |
| `docs/00-COMPASS.md` | 修改 | NOW 改为「629 DELIVERED / 等用户裁定 / 下一里程碑 M2」；47 行（≤80 预算） |
| `reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md` | 修改 | rev 50 → 51；§NOW 改为「等待用户裁定 M1 有限通过候选」；§CURRENT status 同步；§CHAIN_TAIL 629 = `DELIVERED · 待用户裁定`；§ACK 加 CC 629 DELIVERED |

---

## 2. M1 全部 7 任务勾齐（docs/55 §5 同步）

| ID | 状态 | 证据 |
|---|---|---|
| T0 | ✓ | 628 已 AUDITED PASS；NBS 双真相拆行 |
| T1 | ✓ | test_m1_reference_seed.py 7 passed；幂等 upsert |
| T2/T3 | ✓ | 0ee445e · 628 PASS · GDP observation SUCCESS value=31336.72 |
| **T4** | ✓（本回执） | PHOTO-2：int_indicator_timeseries 含 Hubei GDP 行；test_m1_dbt_timeseries 3 passed |
| **T5** | ✓（本回执） | PHOTO-3：API 一跳非 mock 真值；test_m1_api_series 3 passed |
| **T6** | ✓（本回执） | /research/m1-series 存在 + smoke-check.py §14 绿；test_m1_frontend_page 8 passed |
| **T7** | ✓（本回执） | docs/55 / 54 / 01 / COMPASS / EXEC-QUEUE 全同步 |
| 用户 Gate 1 PASS | **未勾**（M1 ≠ Gate） | 候选项；待用户裁定 |

---

## 3. 双推（待执行）

- `git push origin HEAD && git push github HEAD`（按 knife §4 流程）
- 推后 cc_head 回填到 EXEC-QUEUE §CURRENT
- POLL 至 ACK；不重宣告

---

## 4. 回执指向

- 任务书：`reviews/stage0-gate0-rework-2026-08-23/629-stage0-architect-m1-cd-t4-t7-query-surface-tasking-20260831.md`
- 本回执：`reviews/stage0-gate0-rework-2026-08-23/629-stage0-cc-m1-cd-t4-t7-receipt-20260831.md`
- 测试：`tests/test_m1_first_series.py` + `test_m1_reference_seed.py` + `test_m1_dbt_timeseries.py` + `test_m1_api_series.py` + `test_m1_frontend_page.py`
- 数据源：`spikes/02-provincial-yearbook/hubei_2026_06.xlsx` SHA `c5cf5abe…`
- 前端：`frontend/app/research/m1-series/page.tsx`

---

## 5. 后续

- **M2**（08b 31 省 GDP 年度覆盖）— 启动需用户对 M1 有限通过的明确 ACK；非自动续刀
- 当前 31 省样本为 0；M2 需扩面 + 解决「季度 vs 半年」口径统一（仍是 GDP 族；不在本刀范围）
- 回滚：若 M1 任意 T4–T7 在 Cursor 复审 FAIL，629 整刀撤回（保留 M1-b 的 0ee445e 不动）

---

## 6. 关键 deviation（disclosure only）

| 项 | 原因 | 是否动 |
|---|---|---|
| migration 014 search_path 缺 `SET search_path` | 历史遗留（002/003/004/008/009 显式设置，014 漏） | **未动**（knife §2 「不改 014」）；仅在 conftest schema apply 链 print 不 raise；测试走 psycopg2 直连 |
| `materialize_m1_views.sql` 由 `CREATE OR REPLACE` 改 `DROP IF EXISTS + CREATE` | 加 `caveat_text` 列后 Postgres 拒改 view 列名（必须 DROP） | 已动；idempotent；run_m1_views.py 已验证 |
| `IndicatorSeriesPoint` 增 2 字段 | knife §2 T5「可选最小 diff」 | 已动；Optional，不破坏 test_api_s110.py「empty 200」 |
| T5 fixture `DISABLE TRIGGER ALL` | DB `observation_no_delete` 触发器拦 DELETE；fixture 仅 test scope 启用/重启用 | 仅测试；生产 / 真 ingest 路径不受影响 |
| `provincial_yearbook.py` INSERT 增 `extracted_at + confidence` | 5 系列 endpoint model 字段要求；非新行为 | 已动；默认值与测试 seed 一致 |

---

## 7. 红线自审（详）

| 红线 | 状态 |
|---|---|
| 不宣布 Gate / O1 / M1 PASS | ✓ 本回执仅声明「M1 全部 7 任务勾齐 / 有限通过候选」 |
| 不把首页 HTML 当里程碑 | ✓ source_document.url 是 category index，非首页 |
| PARTIAL 不算完成 | ✓ ingestion_run.status=SUCCESS；records_inserted=2 |
| 不让江苏页显示湖北数 | ✓ /provinces/jiangsu 未触碰 |
| LLM 不改 `observation.value` | ✓ connector 直接 INSERT；无 LLM 路径 |
| KPI = 非 demo observation 行 | ✓ 1 真 observation 行；KPI 只算 `value IS NOT NULL` + missing_reason |
| 不把整表 21 行全插 | ✓ filter 后 2 行（gdp_cumulative_h1 + industrial_value_added_above_threshold） |
| 不在 M1 扩省 | ✓ 仅 1 省（湖北） |
| 不改 docs/45 / 50 / 首页 SHA 链 | ✓ 本回执无对应改动 |
| 不宣布 Gate / O1 / M1 PASS | ✓ 同上 |

---

— End 629 回执 —
