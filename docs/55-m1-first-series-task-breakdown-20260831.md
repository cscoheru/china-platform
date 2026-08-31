# 55 — M1 第一条可查询序列：任务拆分

> 依据：`docs/54-milestone-replan-20260830.md` §5 M1；PRD 第 13 章阶段 1 切片；`docs/02` L1→L2→L5；`docs/08b` §1.2（U2）；用户 2026-08-30 U1–U5。
> 日期：2026-08-31。**单独执行文件**；不宣布 Gate / O1 PASS。
> 前置：M0 过程项已退出（见 §0）。M0.3 未改 CSV，并入本文件 **T0**。

---

## 0. M0 核对（本文件开工条件）

| ID | 完成条件 | 2026-08-31 实测 | 判定 |
|---|---|---|---|
| M0.1 | 626 停；裁定进 docs/54 §8 | U1–U5 已批；626 任务书文首 CANCELLED | 已做 |
| M0.2 | 重写 docs/01 | 七层现状已写，不再「空仓库」 | 已做 |
| M0.3 | registry SHA = 文件字节或拆行 | live `NATIONAL_BULLETIN`=`a7e4029d`/无本地；SPIKE=`dea13b8a`=`sample.html` | **T0 已做** |
| M0.4 | EXEC-QUEUE &lt; 30 KB 或归档 | 现行 46 行 / ~2 KB；archive rev46 已落 | 已做 |
| M0.5 | KPI = 覆盖率，禁 11/15 | docs/54 §8 + 队列 §CURRENT | 已做 |

**结论：** M0 **过程退出成立**。M0.3 已由 T0 拆行关闭（2026-08-31）。

---

## 1. 本阶段目标（唯一）

在 **2 周**内打通一条：

`官方表文件 → SHA=字节 → source_document → observation SUCCESS（非 PARTIAL）→ GET /api/indicator/{id}/series → 一个前端页（关 mock）`

北极星仍是 08b（2024 年 31 省 GDP）。M1 **不**覆盖 31 省；只证明管线能装 **GDP 族** 的真值，供 M2 扩面。

### 1.1 指定表（锁定，禁止换成首页 HTML）

| 项 | 值 |
|---|---|
| 文件 | `spikes/02-provincial-yearbook/hubei_2026_06.xlsx` |
| 实测 SHA-256 | `c5cf5abeb4fdf97af52567f0640470d631bc9ac329dcc98f14e5d40bf6a5cac7` |
| 与 registry | **已一致**（`tjj.hubei.gov.cn` / `PROVINCIAL_BULLETIN` / 11261 B） |
| 解析器 | `spikes/02-provincial-yearbook/extract_02_provincial_yearbook.py` |
| 目标指标 | `gdp_cumulative_h1`（源名「一、地区生产总值(上半年)」） |
| 地域 | 湖北省（`geo_entity` 新种子，不是江苏页冒充） |
| 已知 caveat | 脚注：GDP 为**季度数**，不得写成无条件「半年累计」；写入 `caveat_text` |

**禁止**用统计局首页 HTML、四轨 fixture、mart demo 行冒充本表。

**备选（仅当指定 xlsx 丢失或 xlrd/openpyxl 无法解析）：** `spikes/01-national-yearbook/sample.html` 工业增加值。备选**不是** GDP，选用必须在回执里写明「偏离 U2，M2 仍须换 GDP 表」。不要默默换。

**不选** `spikes/00-provincial-yearbook-table` 0109 年鉴 xls：解析器在，ZIP/xls 原件不在本工作树。

### 1.2 明确不做

- 31 省回补、真 HTTP 默认开启、OCR / paddle、Prefect / Grafana / MinIO
- 再锁广东/山东首页；执行 626
- 把 live SHA `a7e4029d` 铺到无对应字节的 mart 行
- 宣布 Gate 1 / O1 PASS
- 改 `/provinces/jiangsu` 去显示湖北数字（口径造假）

---

## 2. 依赖

```
T0 registry 双真相拆行          T1 参考数据种子（湖北+GDP+时期）
         \                    /
          T2 连接器 ingest SUCCESS（解析全部 observation FK）
                    |
          T3 pytest 闸（SHA / SUCCESS / 一跳回源）
                    |
          T4 dbt 视图能读到真行（stg + int_indicator_timeseries）
                    |
          T5 FastAPI series 返回真值 + source
                    |
          T6 前端 /research/m1-series（本页关 mock）
                    |
          T7 文档与队列指针
```

T0 与 T1 无互相依赖。T2 依赖 T1（以及指定表走湖北时 **不**依赖 T0）。T4 依赖库内真行。T5 读 `cegr_staging.int_indicator_timeseries`（dbt view）。T6 读 T5。

---

## 3. 任务清单

### T0 — 关闭 M0.3（NATIONAL_BULLETIN 双真相）

**完成条件：** 任一 registry 行的 `file_hash_sha256` 等于其 `local_sample_path` 文件字节；或该行 `local_sample_path` 为空且 `purpose_note` 写明「live-only，无本地样本」。NBS 单测锁文件字节，不再假设与 NATIONAL_BULLETIN 行哈希相等。

**做法（推荐拆行，保留 live 裁定 a）：**

1. `stats.gov.cn` / `NATIONAL_BULLETIN`：保留 `a7e4029d` / 180165；**清空** `local_sample_path`（不得再指向 `sample.html`）。
2. 新增一行：`category=NATIONAL_BULLETIN_SPIKE`（或等价），`local_sample_path=spikes/01-national-yearbook/sample.html`，`file_hash_sha256=dea13b8a…`，`file_size_bytes` = 文件实测。
3. `NbsMonthlyConnector` 默认改读 SPIKE 行或直接锁 `DEFAULT_SAMPLE` 的文件哈希（已是 `dea13b8a`）。
4. `tests/test_nbs_monthly_connector.py` 的 `EXPECTED_SHA` 继续锁文件；增加断言：SPIKE 行哈希 == 文件；NATIONAL_BULLETIN 行不得声称 sample.html。

**文件：**

- 修改：`source_registry/registry.csv`（会打破「前 11 行 SHA 不变」刀锁 → 回执写 **ACCEPTED disclosure**，U5/M0.3 授权）
- 修改：`backend/src/china_platform/connectors/nbs_monthly.py`
- 修改：`tests/test_nbs_monthly_connector.py`、必要时 `tests/test_auto_ingest_public_source_s52.py`（pilot 仍可指向 NATIONAL_BULLETIN live 行）
- 修改：`docs/01-current-architecture.md` §3.1 改为「已拆行」

**验收：** `shasum -a 256 spikes/01-national-yearbook/sample.html` == SPIKE 行；pytest 上述文件绿。

---

### T1 — 参考数据种子（M1.2）

**完成条件：** 指定表所需 FK 全部存在：`geo_entity`、`geo_code_version`、`indicator_definition`、`indicator_methodology_version`、`calendar_period`。同名不同口径不合并（GDP 半年累计 vs 年度 vs 单季分三条 methodology 或三条 indicator，本刀只用一条并写 caveat）。

**建议种子（稳定 UUID，写入脚本常量，测试可重复）：**

| 实体 | 建议 |
|---|---|
| geo | `湖北省` / level=PROVINCE；可选父级 `中华人民共和国` NATIONAL |
| geo_code_version | 现行国标码一行，`valid_from` 覆盖 2026-06 |
| indicator | `canonical_name=地区生产总值`，`short_code=GDP`，`unit_canonical=亿元`，`frequency` 与 period_type 一致（本表为半年/季度 caveat，**不要**标 YEARLY 假装全年） |
| methodology | `version_label=hubei-2026-06-bulletin-caveat`，`change_summary` 引用 spike 02 脚注 |
| calendar_period | 与 extract 的 `period_start` / `period_end` 对齐（上半年 / Q2，以解析器为准） |

**文件：**

- 新建：`scripts/seed_m1_reference_data.py`（幂等 upsert；DSN 默认 `cegr_test` :55440）
- 新建：`tests/test_m1_reference_seed.py`（跑种子后断言 5 类行 ≥1；GDP 与「工业增加值」不得共用 methodology）

**验收：** 脚本 exit 0 两次结果稳定；不 INSERT `observation`（那是 T2）。

---

### T2 — 连接器：observation SUCCESS（M1.1 主体）

**完成条件：** 对指定 xlsx 跑 ingest：`ingestion_run.status=SUCCESS`，`records_inserted≥1`，至少 1 条 GDP observation；`source_id` + `source_location_id` 复合 FK 成立。

**现状债：**

- `provincial_yearbook.py` 按 `(tjj.hubei.gov.cn, PROVINCIAL_YEARBOOK)` 解析 registry，**实际 category 是 `PROVINCIAL_BULLETIN`**。
- `_attempt_observation_insert` 与 NBS 一样 **FK deferred → PARTIAL**。必须删除「预期 PARTIAL」语义。

**做法：**

1. 解析 registry：`(domain=tjj.hubei.gov.cn, category=PROVINCIAL_BULLETIN)`，或兼容两 category。
2. `extract()` 复用 spike 02；筛选或优先写入 `gdp_cumulative_h1`（允许同表其它指标一并入库，但验收只钉 GDP）。
3. 用 T1 UUID 解析 FK；写 `source_location`（表定位：sheet + 行号，来自 extract）。
4. `lineage.source_file_sha256` = **文件字节**；`is_demo=false` 仅当 SHA 匹配。
5. `caveat_text` 必填（季度 vs 半年）。
6. CLI：`python -m china_platform.connectors.provincial_yearbook --from-local-sample`（无 HTTP）。

**文件：**

- 修改：`backend/src/china_platform/connectors/provincial_yearbook.py`
- 必要时小改：`backend/src/china_platform/connectors/__init__.py`

**验收：** 见 T3。T2 单独可用手跑 + SQL 目视，但退出以 T3 为准。

---

### T3 — pytest 闸

**完成条件：** 新文件全绿；指定表 SHA 锁死；SUCCESS；一跳回源。

**用例（`tests/test_m1_first_series.py`）：**

1. `test_designated_file_sha_matches_registry` — xlsx 字节 == registry 该行。
2. `test_ingest_status_success` — `ingestion_run.status == SUCCESS`（**失败若 PARTIAL**）。
3. `test_gdp_observation_count_ge_1` — GDP 行 ≥1，`value IS NOT NULL`，`missing_reason IS NULL`。
4. `test_observation_one_hop_to_source` — `observation.source_id → source_document.file_hash_sha256` == 文件。
5. `test_period_not_confused_with_release_date` — `calendar_period` / `period_start` 是统计期，不是 `extracted_at`。
6. `test_caveat_present_for_hubei_gdp` — `caveat_text` 非空。
7. `test_no_homepage_html_as_observation_source` — 该批 `source_document.url` 不得仅为 `https://tjj.hubei.gov.cn/` 首页。

**验收：** `pytest tests/test_m1_first_series.py tests/test_m1_reference_seed.py -q` exit 0。

---

### T4 — dbt 中间层能看见真行

**完成条件：** `cegr_staging.int_indicator_timeseries` 含 T2 的 GDP 点（value 非空）。

API 已 JOIN 该 view（`backend/src/china_platform/api/routes/indicators.py`）。若本地以 SQL 建 view 而非 `dbt run`，脚本必须与 `dbt/models/intermediate/int_indicator_timeseries.sql` 同构。

**文件：**

- 核对：`dbt/models/staging/stg_observation.sql`、`stg_source_document.sql`、`int_indicator_timeseries.sql`
- 新建或改：`tests/test_m1_dbt_timeseries.py`（SQL 断言 view 中 `unit` + `value` + `source_domain=tjj.hubei.gov.cn`）

**验收：** 该 pytest 绿。不在本刀引入新 mart 演示行。

---

### T5 — FastAPI series（M1.3）

**完成条件：** `GET /api/indicator/{gdp_indicator_id}/series` 与 `.../series/{hubei_geo_id}` 返回 ≥1 点；响应含 value、unit、source_domain（或等价 provenance）。不读 mock。

**文件：**

- 现有：`tests/test_api_s110.py`（可加 M1 用例，勿改「空 series 仍 200」的既有约定）
- 或：`tests/test_m1_api_series.py`（TestClient + 与 T1 相同 UUID）

**验收：** 上述测试绿。`source_id` / vintage 若模型尚未暴露，本刀在 `IndicatorSeriesPoint` **补字段**（最小 diff），禁止前端靠猜。

---

### T6 — 前端一页（M1.4）

**完成条件：** 新静态路由渲染 T5 真 series；本页 `USE_MOCK=false`（或显式 `fetch` API，不走 `lib/mock.ts`）。图表或表格可点到 source（SHA 前 8 + 文件名或 URL）。

**路由：** 新建 `frontend/app/research/m1-series/page.tsx`  
不要改 `/provinces/jiangsu` 去显示湖北。

**页头必写：**

- 「M1 验收面 · 湖北 2026 上半年 GDP（公报样本）· 非 31 省 · 非 Gate PASS」
- 展示 `caveat_text`

**环境：** 本地验收 `NEXT_PUBLIC_USE_MOCK=false` + `NEXT_PUBLIC_API_BASE`。公网 `china.3strategy.cc` 若仍 mock，首页或本页加「非 M1 验收面」。

**文件：**

- 新建：`frontend/app/research/m1-series/page.tsx`
- 修改：`frontend/app/page.tsx` 加一行链到本页（可选，一条即可，禁止四轨式镀铬）
- 修改：`frontend/smoke-check.py` 增加本页存在性 + 禁词（无 score/rank）
- 新建：`tests/test_m1_frontend_page.py`（源码含 API 路径、不含 MOCK UUID `JIANGSU-GDP-INDICATOR-UUID-MOCK`）

**验收：** `USE_MOCK=false` 下页面能列出 ≥1 个真值；smoke 绿。

---

### T7 — 文档与调度

**完成条件：** 指针一致；队列 §NOW = 下一刀 M2 或「M1 待用户裁定有限通过」。

**文件：**

- 修改：`docs/54` M1 表增加「拆分见 docs/55」
- 修改：`docs/01` L2 行改为「M1 指定表已 SUCCESS」或「进行中」（按实际）
- 修改：`reviews/…/00-EXEC-QUEUE.md` §NOW / §CURRENT
- 本文件文末勾验收清单

**验收：** 队列不再出现 PENDING 626；KPI 仍禁止 11/15。

---

## 4. 建议刀序（合刀允许，首页刀不允许）

| 刀 | 内容 | 预估 |
|---|---|---|
| M1-a | T0 + T1（并行可同一回执） | 1–2 日 |
| M1-b | T2 + T3 | 3–4 日 |
| M1-c | T4 + T5 | 2 日 |
| M1-d | T6 + T7 | 2 日 |
| 缓冲 | FK/口径/caveat 返工 | ≤3 日 |

合计对齐 docs/54「M1 ≈ 2 周」。合刀不得把 T6 做成四轨 deeplink 系列。

---

## 5. 退出清单（M1 完成 = 全勾；仍不是 Gate PASS）

- [x] T0：NATIONAL_BULLETIN 不再把 `sample.html` 标成 `a7e4029d`（2026-08-31；含 CSV 闸修后 `pytest` nbs+seed **15 passed**）
- [x] T1：种子幂等；GDP 口径不与其它指标合并（`tests/test_m1_reference_seed.py` 7 passed）
- [x] T2/T3：指定 xlsx ingest **SUCCESS**；GDP observation ≥1；一跳 SHA=文件（2026-08-31 · `0ee445e` · 628 PASS）
- [x] T4：`cegr_staging.int_indicator_timeseries` 含湖北 GDP 点（value=31336.72 / source_domain=tjj.hubei.gov.cn / SHA prefix c5cf5abe）（2026-08-31 · `tests/test_m1_dbt_timeseries.py` 3 passed）
- [x] T5：`GET /api/indicator/{gdp_id}/series[/geo]` ≥1 真点；非 mock；含 caveat_text + source_hash_prefix（2026-08-31 · `tests/test_m1_api_series.py` 3 passed）
- [x] T6：`/research/m1-series` 真值页 + 页头字面量 + caveat + SHA prefix 8 + 源 URL；首页一行链入；smoke §14 绿（2026-08-31 · `tests/test_m1_frontend_page.py` 8 passed · `smoke-check.py` §14 绿）
- [x] T7：docs/54 M1 行指针 + docs/01 L2 行 + EXEC-QUEUE §NOW + COMPASS NOW 同步（2026-08-31 · 本回执）
- [x] 用户 **M1 有限通过**（2026-08-31）；**未**宣布 Gate 1 PASS（有限通过 ≠ Gate）

回滚：T2 仍 PARTIAL → 停 T4–T6，不扩省。

---

## 6. 与其它文档

| 文档 | 关系 |
|---|---|
| docs/54 | 里程碑定义；本文是 M1 的唯一任务拆分 |
| docs/18 / docs/20 | 旧连接器计划允许 PARTIAL；**本文件作废该完成标准** |
| docs/08b | 研究问题在 M2 交卷；M1 只打通 GDP 管线 |
| docs/10 §2.1–2.6 | T3 应对齐其「可回溯」精神，不在本刀重写全文 |
| docs/45 / 50 | 不动；不是 Gate 2 |

---

## 7. 执行端 §NOW（可粘贴进队列）

M1 有限通过已裁定。下一实现见 **`docs/56` / 任务书 `631`（M2-a）**。不要宣布 Gate / M2 PASS。
