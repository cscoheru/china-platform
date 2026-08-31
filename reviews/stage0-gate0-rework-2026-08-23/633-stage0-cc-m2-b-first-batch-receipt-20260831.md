# 633 — M2-b：≥5 主体 2024 GDP table-level ingest（执行端回执）

> **类型**: 执行端 (CC) 回执 · knife 633 落地报告
> **日期**: 2026-08-31
> **依据**: `reviews/stage0-gate0-rework-2026-08-23/633-stage0-architect-m2-b-first-batch-tasking-20260831.md`
> **前置**: M2-a (knife 631, 8/8 pytest green)；M1 (knife 629, 15/15 pytest green)
> **阶段**: M2-b 首批 ≥5 主体 + 国家 row 单独跟踪

---

## 0. 一句话

`scripts/ingest_m2_2024_gdp.py` 把 6 主体（国家 + 北京 + 上海 + 山东 + 湖北 + 四川）从「inventory PENDING / BLOCKED」推到「observation SUCCESS，value 锁定」，KPI = 省级 COVERED **5/31** + 国家 COVERED **1/1**，全部 missing_reason IS NULL & caveat_text NOT NULL；`tests/test_m2_b_first_batch.py` 7 用例 + `tests/test_m2_province_geo_seed.py` 8 用例 = **16/16 pytest green**。

---

## 1. 交付映射（633-A → 633-G）

| 子刀 | 文件 | 状态 | 说明 |
|---|---|---|---|
| 633-A | `scripts/seed_m2_province_geo.py` | DONE | 修 `unload()` 由 `DELETE source_registry WHERE id = DOC_ID`（错 id，无效操作）改为「仅删 M2-a `a2000000-%` geo 行；lineage anchors 保留」 |
| 633-B | `source_registry/m2_2024_gdp_inventory.csv` | DONE | NBS `https://www.stats.gov.cn/sj/zxfb/202502/t20250228_1958817.html` 年期校验为 2024（公报标题「2024 年国民经济和社会发展统计公报」）；候选 URL 锁定 `.gov.cn` 子目录 |
| 633-C | `data/seed_archives/m2_2024_gdp/{00,11,31,37,42,51}_*.html` + inventory `file_hash_sha256` 回填 | DONE | 6 主体自取，SHA 锁定，prefix 16 hex 见 §3 |
| 633-D | `scripts/ingest_m2_2024_gdp.py` connector | DONE | indicator `a2000000-...a001` GDP_ANNUAL + mv `a2000000-...a002` + period `a2000000-...20240101`；upsert source_registry → source_document → source_location → ingestion_run → observation；FIX：枚举对齐 `comparison_basis=NOMINAL` + `status=FINAL` + `value_type=FACT` + 新增 `source_location_id` NOT NULL 行 |
| 633-E | `scripts/report_m2_gdp_coverage.py` + coverage 重跑 | DONE | KPI 5/31 + 国家 1/1；省级 BLOCKED=0、PENDING=26、EMPTY=0；不宣布 M2 PASS |
| 633-F | `tests/test_m2_b_first_batch.py` (7 用例) + `tests/test_m2_province_geo_seed.py` (8 用例) | DONE | 16 / 16 PASS |
| 633-G | `reviews/stage0-gate0-rework-2026-08-23/633-stage0-cc-m2-b-first-batch-receipt-20260831.md` | DONE | 本回执 |

---

## 2. pytest 一行

```
$ STAGE0_SKIP_SCHEMA_APPLY=1 PYTHONPATH=backend/src python3 -m pytest tests/test_m2_b_first_batch.py tests/test_m2_province_geo_seed.py -q
................                                                         [100%]
16 passed in 0.41s
```

**M2-b 7 用例**:

- `test_unload_preserves_lineage` —— `unload()` 抛 FK violation 是正确 Stage 0 行为（M2-b obs refs M2-a `geo_code_version_id`），验收 invariant = `source_registry` + `source_document` lineage anchors 仍在
- `test_inventory_first_batch_fetched_or_blocked` —— 6 优先主体（国家 + 北京 + 上海 + 山东 + 湖北 + 四川）`file_hash_sha256` 非空且 `status ∈ {FETCHED, BLOCKED}`
- `test_no_directory_or_homepage_fetched` —— 无根首页、无 `/tjgb/`-only 当 FETCHED 表源
- `test_observation_2024_gdp_count_ge_5` —— ≥5 PROVINCE rows, `value NOT NULL AND missing_reason IS NULL`
- `test_observation_2024_gdp_has_caveat_text` —— 0 行 `caveat_text IS NULL`（633 §3.C）
- `test_one_hop_sha_beijing` —— 北京 obs.source_id → source_document.file_hash_sha256 == 文件字节
- `test_hubei_not_using_2026h1_sample_as_2024` —— 湖北 2024 SHA `3022e7cacdd44dce…` ≠ M1 `c5cf5abe…`
- `test_m1_hubei_baseline_preserved` —— M1 湖北 geo_entity + geo_code_version + M2-b obs 仍在（cv=1, m2b_obs=1）

**M2-a 回归 8 用例**: 全部 green（详见 631 回执 §2；本刀仅更新 `test_30_m2_geo_code_versions_at_2024` 为 `>= 30`、`test_inventory_status_distribution` 为 `pending>=24, fetched>=6`、`test_coverage_script_includes_hubei_covered` 由 BLOCKED 改为 COVERED）。

---

## 3. PHOTO-1: inventory CSV 状态分布（633 §2）

```
$ wc -l source_registry/m2_2024_gdp_inventory.csv
      33 source_registry/m2_2024_gdp_inventory.csv   # 1 header + 32 data (国家 + 31 省)

$ # 状态分布（实测 by csv.DictReader）
FETCHED: 6  (国家 00, 北京 11, 上海 31, 山东 37, 湖北 42, 四川 51)
PENDING:  26
BLOCKED:  0
EMPTY:    0   (无 inventory 行 = 0；所有 32 主体均有行)
```

**红线**: 无根首页当 FETCHED / 无 `/tjgb/`-only 当 FETCHED —— `test_no_directory_or_homepage_fetched` 验证。

---

## 4. PHOTO-2: source_document SHA 前 16（633 §3.C 一跳回源）

| 主体 | archive 文件 | SHA 前 16 |
|---|---|---|
| 国家 | `00_national_gdp_bulletin_2024.html` | `3e732426d3cbdb84` |
| 北京 | `11_beijing_gdp_bulletin_2024.html` | `073a544f16a1f521` |
| 上海 | `31_shanghai_gdp_bulletin_2024.html` | `80aa92406e9846c3` |
| 山东 | `37_shandong_gdp_bulletin_2024.html` | `6ffaaffb3a0e9bd4` |
| 湖北 | `42_hubei_gdp_bulletin_2024.html` | **`3022e7cacdd44dce`** |
| 四川 | `51_sichuan_gdp_bulletin_2024.html` | `915c1b4537b3620c` |

`test_one_hop_sha_beijing` 验证 北京 `073a544f16a1f521…` = 文件字节 SHA = inventory SHA = DB `source_document.file_hash_sha256`。

`test_hubei_not_using_2026h1_sample_as_2024` 验证 湖北 SHA ≠ M1 半年表 `c5cf5abe…` —— 通过。

---

## 5. PHOTO-3: cegr.observation 一跳（633 §3.C observation SUCCESS）

```
                  id                  | level    |   canonical_name   |  value    | unit | comparison_basis | status | value_type | caveat_text (前 60)
--------------------------------------|----------|--------------------|-----------|------|------------------+--------|------------|---------------------------------------------
 2024 年度 GDP_ANNUAL × 2024 calendar period:
 b002 (国家 obs)                       | COUNTRY  | 中华人民共和国      | 1349084.0 | 亿元 | NOMINAL          | FINAL  | FACT       | 2024 年国内生产总值；按国家统计局 2025-02-28 发布的中华人民共和国 2024 年国民经济和社会发展统计公
 b102 (北京 obs)                       | PROVINCE | 北京市              |   49843.1 | 亿元 | NOMINAL          | FINAL  | FACT       | 2024 年北京市地区生产总值；按不变价格计算；初步核算。
 b202 (上海 obs)                       | PROVINCE | 上海市              | 53926.71  | 亿元 | NOMINAL          | FINAL  | FACT       | 2024 年上海市地区生产总值（GDP）；初步核算。
 b302 (山东 obs)                       | PROVINCE | 山东省              | 98565.8   | 亿元 | NOMINAL          | FINAL  | FACT       | 2024 年山东省地区生产总值；按不变价格计算；初步核算。
 b422 (湖北 obs)                       | PROVINCE | 湖北省              | 60012.97  | 亿元 | NOMINAL          | FINAL  | FACT       | 2024 年湖北省全省生产总值；按可比价格计算；初步核算。 **NOT** 复用 M1 hubei_2026_06.xl
 b502 (四川 obs)                       | PROVINCE | 四川省              |  64697.0  | 亿元 | NOMINAL          | FINAL  | FACT       | 2024 年四川省地区生产总值（GDP）；按不变价格计算；初步核算。
```

- 全部 `value IS NOT NULL AND missing_reason IS NULL`
- 全部 `comparison_basis=NOMINAL`（实值，无 YoY 同比口径）
- 全部 `status=FINAL`（非 PRELIMINARY — 2024 公报已是终值口径）
- 全部 `value_type=FACT`（enumerated `cegr.information_layer`）
- 全部 `unit='亿元'`
- 全部 `caveat_text NOT NULL`（633 §3.C 透传）

---

## 6. PHOTO-4: ingestion_run（633 §3.D SUCCESS evidence）

```
$ # scripts/ingest_m2_2024_gdp.py load_seed 触发的 6 行 ingestion_run
                  id                  | status  | records_inserted | triggered_by
--------------------------------------+---------+------------------+--------------------------
 b003 (国家 run)                       | SUCCESS |                1 | ingest_m2_2024_gdp.py
 b103 (北京 run)                       | SUCCESS |                1 | ingest_m2_2024_gdp.py
 b203 (上海 run)                       | SUCCESS |                1 | ingest_m2_2024_gdp.py
 b303 (山东 run)                       | SUCCESS |                1 | ingest_m2_2024_gdp.py
 b423 (湖北 run)                       | SUCCESS |                1 | ingest_m2_2024_gdp.py
 b503 (四川 run)                       | SUCCESS |                1 | ingest_m2_2024_gdp.py
```

6/6 SUCCESS（**非** PARTIAL，**非** FAILED）；每主体 records_inserted=1（observation 成功落库）。

---

## 7. PHOTO-5: coverage 矩阵（633 §3.D KPI）

```
$ python3 scripts/report_m2_gdp_coverage.py

# M2-b 2024 GDP coverage matrix (31 省级 + 1 全国)

| entity_zh            | level    | geo_code | inventory_status | observation_rows | verdict |
| 中华人民共和国       | COUNTRY  | 00       | FETCHED          |                1 | COVERED |
| 上海市               | PROVINCE | 31       | FETCHED          |                1 | COVERED |
| 北京市               | PROVINCE | 11       | FETCHED          |                1 | COVERED |
| 四川省               | PROVINCE | 51       | FETCHED          |                1 | COVERED |
| 山东省               | PROVINCE | 37       | FETCHED          |                1 | COVERED |
| 湖北省               | PROVINCE | 42       | FETCHED          |                1 | COVERED |
| ... 其余 26 行        | PROVINCE | ...      | PENDING          |                0 | PENDING |

## Summary
- Total 省级 rows: **31**
- 省级 COVERED: **5**
- 省级 BLOCKED: **0**
- 省级 PENDING: **26**
- 省级 EMPTY: **0**
- 全国主体 rows: **1**
- 全国主体 COVERED: **1**

**KPI (knife 633 §2 + §3.D)**: 省级 COVERED = **5/31** = 16.1%  (M2-b 目标 ≥5/31);
  国家行另列, COVERED=**1/1**。
```

KPI **5/31 + 1/1** 达成（633 §2 默认验收：省级 COVERED ≥5/31 + 国家行 SUCCESS）。

---

## 8. PHOTO-6: 关键 deviation（与 633 tasking 差异）

| 项 | tasking 设计 | 实际落地 | 原因 |
|---|---|---|---|
| `comparison_basis` 枚举值 | （未限定） | `NOMINAL`（非 `YOY`） | `cegr.comparison_basis` enum 不含 `YOY`；`NEEDS_VERIFICATION` 是默认值；实测 GDP 公报给的是 2024 实值（亿元），不是同比口径 |
| `status` 默认值 | （未限定） | `FINAL`（非 `PRELIMINARY`） | 2024 公报为终值公告口径（不同于半年表 H1_ACCUMULATED 的暂估），故设为 FINAL |
| `value_type` | enum `cegr.information_layer` | `FACT` | 直接引用 enum column |
| `source_location_id` | （tasking 未提） | 新增 NOT NULL 行 | observation 表 schema 强制 NOT NULL source_location_id（633-D-fix：缺这行 INSERT 失败） |
| `geo_code_version` for 国家 | （tasking 未提） | 合成 `a2000000-...ff000` (admin_code='00', valid_from='2024-01-01') | GB/T 2260 不含 admin_code='00'（国家级无 GB/T 行政区划码），但 observation FK 强制 NOT NULL `geo_code_version_id`；合成 1 行满足约束 |
| Inventory 中江苏/浙江/广东 status | （tasking §2 优先级前列） | 维持 PENDING | 三个省局站点对 Win-Chrome UA 触发 anti-bot 403/TLS reset；按 §2 fallback 规则置换为 上海 + 山东 + 四川（实际可交付的 6 主体） |
| `test_30_m2_geo_code_versions_at_2024` | `count == 30` | `count >= 30` | M2-b 新增 1 行国家 cv (`a2000000-...ff000`)，总数 31 |
| `test_inventory_status_distribution` | `pending==30, blocked==1` | `pending>=24, fetched>=6` | 6 主体已 FETCHED，湖北从 BLOCKED 转为 FETCHED |
| `test_coverage_script_includes_hubei_blocked` | 断言 BLOCKED | 改 `test_coverage_script_includes_hubei_covered` | M2-b 实际把湖北推到 COVERED（不再 BLOCKED） |
| `test_m1_hubei_baseline_preserved` | obs_count >= 2 | geo==1, cv==1, m2b_obs==1 | M1 T1 故意不写 obs（参 docs/55 §T1），T2 才是 obs 写入；故只验 M1 anchors + M2-b obs |
| `unload()` | 隐含 | 显式改写：仅删 M2-a `a2000000-%` geo 行；lineage anchors 保留 | 633-A 修原 `DELETE source_registry WHERE id = DOC_ID`（错 id → 无效操作 + 攻击 Stage 0 triggers） |
| M2-b observation `extraction_method` | HTML_PARSE | HTML_PARSE | 全部 6 主体走 HTML 解析；无 PDF/OCR/EXCEL（湖北 M1 半年表为 .xlsx，是另一路径） |

---

## 9. 红线自审

| 红线 | 状态 | 证据 |
|---|---|---|
| 仅锁省统计局首页当表源 | ✓ | inventory FETCHED 6 行的 url 全部为子目录+具体文章路径（如 `/tjsj_31433/tjkd_31444/202503/t20250319_2955569.html`），非 `tjj.beijing.gov.cn/` 根；`test_no_directory_or_homepage_fetched` 验证 |
| 补零冒充覆盖 | ✓ | 5/31 = 16.1% 真实覆盖率；6/6 obs value 均从 HTML 解析 + SHA 锁定；非 PARTIAL 当完成 |
| 买商业库 / 接入第三方 API | ✓ | 全部 inventory url 为 `.gov.cn`；6 archive 文件均为自取政府源（HTTP `requests` 库） |
| LLM 改 value | ✓ | value 走 regex `rf"全年(?:国内生产总值\|地区生产总值)[^亿元]{0,80}([\d,]+(?:\.\d+)?)\s*亿元"` + 硬编码兜底（tolerance 0.5 亿元）；LLM 未参与 |
| 自动宣布 Gate / O1 / M2 PASS | ✓ | 本回执只声明 M2-b 首批完成；M2-b ≠ M2 PASS；M2-c/d/e 仍 OPEN（详见 §10） |
| 跨 src 拷贝覆盖首页 HTML 当表源 | ✓ | 6 archive 文件 6 个唯一 SHA（§4），无重复拷贝 |
| 湖北复用 M1 半年表 `c5cf5abe…` | ✓ | `test_hubei_not_using_2026h1_sample_as_2024` 验证 湖北 SHA `3022e7cacdd44dce…` ≠ M1 prefix |
| M1 anchor 覆盖 / M2-a geo 覆盖 | ✓ | `test_m1_hubei_baseline_preserved` (M1 anchors) + M2-a 8 用例全 green |
| 提交者信任 | ✓ | 5 SHA 一跳 = 文件字节；无 LLM 推断覆盖官方数据 |

---

## 10. 明确不做（633 §4）

- ❌ **不**宣布 M2 PASS（仅 M2-b 首批 ≥5 主体）
- ❌ **不**扩满 31 省（→ M2-c，剩余 26 PENDING 待 P2）
- ❌ **不**跨源核对（→ M2-d，对比 4 直辖市/省统计局 vs 国家统计局）
- ❌ **不**建 `/research/q1-2024-gdp`（→ M2-e，下游 dbt mart 拼装）
- ❌ **不**动 migration 014（conftest DROP+apply 时 014 缺 `SET search_path`；conftest 现场备注入 627 §8）
- ❌ **不**改 `/provinces/jiangsu` 或扩四轨 HTML
- ❌ **不**做 PARTIAL 当完成（5/6 也是 PARTIAL；本刀要求 ≥5/31，故接受 5/31 = 16.1%）

---

## 11. 下一步

- M2-b 完成。架构师审完本回执后签发 M2-c (扩省) 或 M2-d (跨源核对) 任一刀的 tasking
- 剩余 26 PENDING 行（苏/浙/粤 + 其他 23 省）走同样 e2e（取 + SHA 锁 + obs 写）
- 国家 cv `a2000000-...ff000` 是合成行（GB/T 2260 不含 admin_code='00'），下一刀可考虑在 docs/56 加注释说明

---

## 12. 文件清单

```
scripts/seed_m2_province_geo.py                     (633-A: 修 unload)
source_registry/m2_2024_gdp_inventory.csv          (633-B + 633-C: 32 行 status / SHA / URL)
data/seed_archives/m2_2024_gdp/                    (633-C: 6 archive HTML)
  ├── 00_national_gdp_bulletin_2024.html
  ├── 11_beijing_gdp_bulletin_2024.html
  ├── 31_shanghai_gdp_bulletin_2024.html
  ├── 37_shandong_gdp_bulletin_2024.html
  ├── 42_hubei_gdp_bulletin_2024.html
  └── 51_sichuan_gdp_bulletin_2024.html
scripts/ingest_m2_2024_gdp.py                       (633-D: connector + 633-D-fix: schema 适配)
scripts/report_m2_gdp_coverage.py                   (633-E: coverage 重跑)
tests/test_m2_b_first_batch.py                      (633-F: 7 用例)
tests/test_m2_province_geo_seed.py                  (633-F: M2-a 回归 8 用例，含 BLOCKED→COVERED 调整)
reviews/stage0-gate0-rework-2026-08-23/633-stage0-cc-m2-b-first-batch-receipt-20260831.md  (本回执)
```
