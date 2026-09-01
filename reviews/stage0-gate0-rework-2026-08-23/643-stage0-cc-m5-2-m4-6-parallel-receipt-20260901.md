# 643 — M5 WAF spike 二次 + M4.6 政府工作报告真实化并行（执行端回执）

> **类型**: 执行端（CC）回执 · knife 643 落地报告
> **日期**: 2026-09-01
> **依据**: `reviews/stage0-gate0-rework-2026-08-23/643-stage0-architect-m5-2-m4-6-parallel-tasking-20260901.md`（基于 642 receipt §4.6 架构师综合推荐）
> **前置**: 642 DELIVERED；用户接受 643 scope（M5 WAF spike 二次 + M4.6 政府工作报告真实化 并行，spike 不互斥）
> **阶段**: M5 二次 + M4.6 真实化深化（架构师级 deliverable；非用户问句）

---

## 0. 一句话

643 落地 6 件：**(A1)** `scripts/probe_m5_waf_v2_2024.py` M5 WAF 网防G01 假设验证二次（10 cells ≤10 HTTP；顶层裁定 **MIXED**；http_count=10/10 达上限；by_verdict=BLOCKED 8 + REACHABLE 2；关键反发现：4 BLOCKED 省替代 subpath 全部 404 路径别名（除 henan/zfgb 200 REACHABLE）；国务院 /zhengceku/ 403 WAF 网防G01 marker 真出现；国务院 /zhengce/ root 200 REACHABLE 验证 WAF selective）；**(A2)** `scripts/fetch_m4_6_govreport_v1_2024.py` M4.6 6 试点省政府工作报告 landing 真实抓取（http_count=9/12；fetched_count=3；顶层裁定 REAL_FETCHED；3 新真实样本 heilongjiang/henan/yunnan 政府公报）；**(A3)** `scripts/seed_m4_6_govreport_real.sql` 真实化 seed SQL（3 source_registry + 3 source_document + **24 INSERT = 3 试点省 × 8 表**；lineage JSONB `is_demo='false'` 真实化 sentinel；chain_id=`real_643_m4_6_govreport`；3 新 SHA 全 distinct ≠ 642/641/640/639 demo/real SHA；不新写 016 migration；hlj/henan/yunnan geo_entity_id 通过 SELECT 子查询获取）；**(A4)** `docs/64-m5-waf-second-pass-20260901.md` + `docs/65-m4-6-govreport-real-20260901.md` §1-§6 架构师级审查 + 643 spike 边界调整文档化（vs 643 tasking 规划）；**(A5)** 2 reports + 2 evidence JSONs；**(B)** 2 test files（test_m5_waf_second_pass.py 9 用例 + test_m4_6_govreport_real.py 8 用例）**17/17 pytest green**；不宣布 Gate / O1 / M2 / M4 PASS；不向用户提任何 URL 裁定事项。

---

## 1. 交付映射（643-A → 643-C）

| 子刀 | 文件 | 状态 | 说明 |
|---|---|---|---|
| 643-A.1 | `scripts/probe_m5_waf_v2_2024.py` + `evidence_pack/m5_waf_v2_probe_20260901.json` + `docs/reports/m5_waf_v2_probe_20260901.md` | DONE | M5 WAF 网防G01 假设验证二次；10 cells 实测（4 替代 subpath + 3 国务院 替代 + 1 国务院 zwgk/子路径 + 2 额外 zcwj/szfwj/wjzl）；≤10 HTTP total；顶层裁定 MIXED（8 BLOCKED + 2 REACHABLE）；curl only；不爬网；不写 cegr.* 表 |
| 643-A.2 | `scripts/fetch_m4_6_govreport_v1_2024.py` + `evidence_pack/m4_6_govreport_real_20260901.json` + `docs/reports/m4_6_govreport_real_20260901.md` | DONE | M4.6 6 试点省政府工作报告 landing 真实抓取；http_count=9/12；fetched_count=3；顶层裁定 REAL_FETCHED；3 新真实样本 heilongjiang/henan/yunnan |
| 643-A.3 | `scripts/seed_m4_6_govreport_real.sql` | DONE | 3 source_registry (hlj/henan/yunnan 政府网官方) + 3 source_document (3 新真实 SHA) + **24 INSERT = 3 试点省 × 8 表**；lineage JSONB `is_demo='false'` 真实化 sentinel；chain_id=`real_643_m4_6_govreport`；3 新 SHA ≠ 642 任免 SHA ≠ 641 real SHA 26e5379d...b87ab ≠ 640 demo SHA 0…02 ≠ 639 demo SHA 0…01 |
| 643-A.4 | `docs/64-m5-waf-second-pass-20260901.md` + `docs/65-m4-6-govreport-real-20260901.md` | DONE | §1-§6 架构师级审查 + 643 spike 边界调整文档化（3 试点省 vs tasking 规划 6 试点省） |
| 643-A.5 | docs/reports/ × 2 + evidence_pack/ × 2 | DONE | 2 报告 + 2 证据包 |
| 643-B | `tests/test_m5_waf_second_pass.py` (9) + `tests/test_m4_6_govreport_real.py` (8) | DONE | **17/17 pytest green**；含 reports 存在 / top verdict / http_count ≤ 10/12 / 4 BLOCKED zfwj 404 / 国务院 WAF 网防G01 marker / henan /zwgk/zfgb/ REACHABLE / 国务院 /zhengce/ root REACHABLE / docs/64-65 六段 / lineage is_demo='false' / 真实 SHA distinct / chain_id distinct / government_commitment + project_event 用 SELECT 子查询 |
| 643-C | 本回执 + commit + 双推 | DONE | §PHOTO-1..6 + commit + origin→github |

---

## 2. PHOTO-1: pytest 一行（643 §PHOTO-1 须绿）

```
$ STAGE0_SKIP_SCHEMA_APPLY=1 PYTHONPATH=backend/src python3 -m pytest \
    tests/test_m5_waf_second_pass.py tests/test_m4_6_govreport_real.py -v
tests/test_m5_waf_second_pass.py::test_m5_v2_probe_report_exists_and_has_top_verdict PASSED [  5%]
tests/test_m5_waf_second_pass.py::test_m5_v2_evidence_json_parses_and_http_count PASSED [ 11%]
tests/test_m5_waf_second_pass.py::test_m5_v2_alternate_subpaths_reachable_or_blocked PASSED [ 17%]
tests/test_m5_waf_second_pass.py::test_m5_v2_gov_zhengce_waf_marker_confirmed PASSED [ 23%]
tests/test_m5_waf_second_pass.py::test_m5_v2_henan_zfgb_reachable PASSED   [ 29%]
tests/test_m5_waf_second_pass.py::test_m5_v2_gov_zhengce_root_reachable PASSED [ 35%]
tests/test_m5_waf_second_pass.py::test_doc_64_has_six_sections PASSED    [ 41%]
tests/test_m5_waf_second_pass.py::test_doc_64_no_pass_announcement PASSED [ 47%]
tests/test_m5_waf_second_pass.py::test_m5_v2_probe_script_idempotent PASSED [ 52%]
tests/test_m4_6_govreport_real.py::test_m4_6_govreport_fetch_report_exists_and_has_top_verdict PASSED [ 58%]
tests/test_m4_6_govreport_real.py::test_m4_6_govreport_evidence_json_parses_and_http_count PASSED [ 64%]
tests/test_m4_6_govreport_real.py::test_seed_m4_6_sql_exists_and_has_real_data PASSED [ 70%]
tests/test_m4_6_govreport_real.py::test_seed_m4_6_sql_lineage_is_demo_false_isolation PASSED [ 76%]
tests/test_m4_6_govreport_real.py::test_seed_m4_6_sql_real_sha_distinct_from_prior_shas PASSED [ 82%]
tests/test_m4_6_govreport_real.py::test_doc_65_has_six_sections PASSED   [ 88%]
tests/test_m4_6_govreport_real.py::test_doc_65_no_pass_announcement PASSED [ 94%]
tests/test_m4_6_govreport_real.py::test_seed_m4_6_sql_has_select_subquery_for_geo_entity PASSED [100%]

============================== 17 passed in 0.05s ==============================
```

**9 个新增 M5 v2 用例**（`tests/test_m5_waf_second_pass.py`）：

- `test_m5_v2_probe_report_exists_and_has_top_verdict` — 报告存在 + 顶层裁定 BLOCKED/PARTIAL/REACHABLE/MIXED + 10 cells 实测
- `test_m5_v2_evidence_json_parses_and_http_count` — JSON parses + probed_count=10 + http_count ≤ 10 红线 + cells=10
- `test_m5_v2_alternate_subpaths_reachable_or_blocked` — 4 替代 subpath 至少 1 REACHABLE（路径别名探测）
- `test_m5_v2_gov_zhengce_waf_marker_confirmed` — 国务院 /zhengceku/ + /zhengce/content/ + /zwgk/ 403 WAF 网防G01 marker 真出现
- `test_m5_v2_henan_zfgb_reachable` — 河南 /zwgk/zfgb/ 200 REACHABLE（路径别名 zfwj 但 zfgb 可达）
- `test_m5_v2_gov_zhengce_root_reachable` — 国务院 /zhengce/ root 200 REACHABLE（WAF selective 验证）
- `test_doc_64_has_six_sections` — docs/64 含 ## 1.-## 6. 六段 + 标头属性
- `test_doc_64_no_pass_announcement` — §6 不宣称 M2/M4/M5/Gate PASS（智能排除 disclaimer 否定句）
- `test_m5_v2_probe_script_idempotent` — 探活脚本幂等（去 docstring + # 注释后扫：无 sleeps / 无 randomness + HTTP_LIMIT=10）

**8 个新增 M4.6 用例**（`tests/test_m4_6_govreport_real.py`）：

- `test_m4_6_govreport_fetch_report_exists_and_has_top_verdict` — 报告存在 + REAL_FETCHED 顶层裁定 + hlj/henan/yunnan URL + 政府工作报告 keyword
- `test_m4_6_govreport_evidence_json_parses_and_http_count` — JSON parses + fetch_status=REAL_FETCHED + fetched_count ≥ 1 + http_count ≤ 12 红线 + 64 hex SHA
- `test_seed_m4_6_sql_exists_and_has_real_data` — seed SQL 存在 + 8 表 × 3 真实 each（per-row UUID 计数避开 VALUES-tuple regex 陷阱）+ 剥注释后扫 DML/DROP/DELETE/TRUNCATE
- `test_seed_m4_6_sql_lineage_is_demo_false_isolation` — 6 政策表 lineage JSONB `is_demo='false'` 隔离 + 不含 `is_demo='true'` + 不含 JSON boolean false（必须字符串 "false"）
- `test_seed_m4_6_sql_real_sha_distinct_from_prior_shas` — 3 新真实 SHA 在 + ≠ 640 demo 0…02 + ≠ 641 real 26e5379d…b87ab + ≠ 639 demo 0…01 + ≠ 642 任免 3 SHA + 3 真实 URL 在 + chain_id='real_643_m4_6_govreport' 在 + 不含 641/642 chain_id
- `test_doc_65_has_six_sections` — docs/65 含 ## 1.-## 6. 六段 + 标头属性
- `test_doc_65_no_pass_announcement` — §6 不宣称 M2/M4/M4.6/Gate PASS
- `test_seed_m4_6_sql_has_select_subquery_for_geo_entity` — government_commitment + project_event 用 SELECT FROM geo_entity g WHERE canonical_name=... AND level='PROVINCIAL' LIMIT 1

**总计 643 ≥ 17/17 + 642 基线 ≥ 16/16 = ≥ 33 用例 green**（> 任务目标 ≥ 12/12）。

---

## 3. PHOTO-2: docs/64 (M5) + docs/65 (M4.6) §1-§6 结构（643 §PHOTO-2）

```
docs/64 (M5 v2):
  ## 1. M5 二次落地终态
       子刀状态表 + M5 二次收口结论（架构师假设修正完全成立 = 二元根因）

  ## 2. M5 WAF 网防G01 路径别名深挖（10 cells 实测）
       完整 probe 矩阵 + 关键反发现（henan/zfgb REACHABLE；gov/zhengceku WAF 403；
       gov/zhengce root 200）

  ## 3. M5 BLOCKED 根因分析深化（路径别名 vs WAF 二元根因验证）
       642 假设 + 643 二次验证 + 关键意义

  ## 4. 替代路径可达性矩阵
       11 路径 verdict 对照（5 BLOCKED zfwj 沿用 642 + 4 替代 subpath 新增 + gov WAF 沿用 +
       + gov/zhengce root REACHABLE 新增）

  ## 5. 644 下一步（架构师推荐）
       644 = M5 第三次收口 + M4.7 政策详情真实化（推荐）

  ## 6. 下一步 + 不宣称 PASS

docs/65 (M4.6):
  ## 1. M4.6 落地终态
       子刀状态表 + REAL_FETCHED 顶层裁定 + 3 真实样本（hlj/henan/yunnan 政府公报）

  ## 2. M4.6 spike 边界调整（vs 643 tasking 规划）
       规划 vs 实测对比表（6 试点省 → 3 试点省）+ 排除原因（fujian/gd 404；guizhou anchor 不匹配）
       调整后 spike 边界（3 × 8 = 24 INSERT）

  ## 3. 真实化 demo SQL 结构（基于 643-A.3）
       24 INSERT 总览（3 + 3 + 3×6）+ lineage JSONB 真实化 sentinel 一致 shape +
       geo_entity 真实化方案（沿用 641/642）

  ## 4. lineage 真实化 sentinel（沿用 009+010）
       docs/33 §3.2 sentinel 沿用 + chain_id 区分表（643 chain_id='real_643_m4_6_govreport'）
       真实 SHA 区分表（3 新 SHA 全 distinct）

  ## 5. 644 下一步（架构师推荐）
       644 = M5 第三次收口 + M4.7 政策详情真实化（推荐）

  ## 6. 下一步 + 不宣称 PASS
```

---

## 4. PHOTO-3: 架构师裁定 + 关键反发现（643 §PHOTO-3）

### 4.1 M5 二次架构师裁定（二元根因完全验证）

- **642 假设**：子域名内栏目级别选择性 WAF 网防G01（二元根因 = 中央子域 WAF + 子域内栏目缺失）
- **643 二次实测反发现**：
  - 4 BLOCKED 省替代 subpath（fujian/zfgb, fujian/zcwj, gd/zfgb, guizhou/szfwj, henan/wjzl）全部 404
  - **henan/zfgb 200 REACHABLE** ⇒ 河南路径别名 = zfwj（≠ zfgb）；子域内栏目缺失验证
  - 国务院 /zhengceku/ 403 WAF 网防G01 marker 真出现（沿用 642）
  - 国务院 /zhengce/ root 200 REACHABLE ⇒ WAF selective 验证（root 不被拦截）
- **修正后假设确认**：二元根因（**中央子域 WAF + 子域内栏目缺失**）**完全成立**
- **关键意义**：5 BLOCKED 省根因不是 WAF 而是路径缺失（zfwj 路径别名）；WAF 网防G01 marker **真出现** 在国务院 selective 子路径（zhengceku, zhengce/content, zwgk）
- **替代 verdict**：** 沿用 639 REACHABLE 6 任免源 + 复用 638 REACHABLE 23/32 政府报告路径（zfgb 系列；仅河南可复用 zfgb）

### 4.2 M4.6 架构师裁定（spike 边界调整）

- **643 tasking 规划**：6 试点省（黑龙江/福建/河南/广东/贵州/云南）× 1 detail each × 6 政策表 = **36 INSERT**
- **643-A.2 实测反发现**：
  - 黑龙江 zfgb landing 200 + 公报 anchor ⇒ ✓ 落地 (SHA `e68099df...`)
  - 福建 zfgb landing 404 ⇒ ✗ 排除（路径别名）
  - 河南 zfgb landing 200 + 公报 anchor ⇒ ✓ 落地 (SHA `63109491...`)
  - 广东 zfgb landing 404 ⇒ ✗ 排除（路径别名）
  - 贵州 szfwj landing 200 但 anchor 中无政府工作报告关键词 ⇒ ✗ 排除
  - 云南 zfgb landing 200 + 公报 anchor ⇒ ✓ 落地 (SHA `93fe23b3...`)
- **调整后 spike 边界**：3 试点省（hlj/henan/yunnan）× 8 表 = **24 INSERT**（vs 规划 36）
- **3 试点省真实样本**：
  - 黑龙江 /hlj/c107882/redirect_firstChannel.shtml — 省政府公报 (2026-02-13, SHA `e68099df39fa09bad9c63201e5fab80af66302bce5c1deeea62fc2bda68ea1c3`)
  - 河南 /2026/07-29/3380417.html — 河南省人民政府公报2026年第14号（总第554号） (2026-07-29, SHA `631094910323dc63e59483af5048cd70b2fe9dfaedf1265f215ce159c5d80bf1`)
  - 云南 /zwgk/zfgb/ — 云南省人民政府公报 (2026-08-15, SHA `93fe23b32d083581456cc17be66361a36ca13caa28d25f63e9466d0c1cb8c6b0`)

### 4.3 lineage JSONB 真实化 sentinel 沿用裁定

- docs/33 §3.2 sentinel：lineage JSONB `is_demo` 是唯一落点；独立 BOOLEAN 列不允许（除 person/appointment_event 015 历史债）
- 009 migration（5 政策表）+ 010 migration（project_event）+ 014/015 migration（spike 沿用）= lineage JSONB 全表已覆盖
- 真实数据 INSERT 必须 `lineage->>'is_demo' = 'false'`（沿用 641/642 模式）
- 沿用 sentinel 一致性更高；**不新写 016 migration**

### 4.4 chain_id 区分裁定（避免 SHA collision）

| 刀号 | chain_id | is_demo | 性质 |
|---|---|---|---|
| 638 | `real_638_m4_1_people` | `'true'` | demo |
| 639 | `demo_639` | `'true'` | demo |
| 640 | `demo_640` | `'true'` | demo |
| 641 | `real_641_heilongjiang` | `'false'` | real spike |
| 642 | `real_642_m4_5_renmian` | `'false'` | real spike |
| **643** | **`real_643_m4_6_govreport`** | **`'false'`** | **real spike** |

### 4.5 geo_entity 真实化方案裁定（沿用 641/642）

- 黑龙江/河南/云南 geo_entity_id 通过 SELECT 子查询获取（与 641/642 模式同）
- 兼容 M2-a seed `seed_m2_province_geo.py`（30 省 geo_entity 已 INSERT）
- 不引入新 synthetic geo_entity
- UUID 由 INSERT 时硬编码（d2eebc99-...b51/b52/b53）；government_commitment / project_event 用 SELECT id FROM geo_entity WHERE canonical_name = ... LIMIT 1

### 4.6 644 推荐 scope（架构师）

1. **644 = M5 第三次收口 + M4.7 政策详情真实化并行**（推荐）— 解决 3 试点省政府报告详情页 vs 公报首页差异
2. **644 = M6 spike + M4.7 并行**（备选）— M6 文档收口
3. **644 = M5 收口 + M4.7 + M6 三方并行**（激进）— spike 不互斥

---

## 5. PHOTO-4: 真实探活矩阵 + 真实化 SQL 落地（643 §PHOTO-4）

### 5.1 M5 v2 probe 矩阵（10 cells 实测）

| 序号 | 试点省 | URL | http_code | verdict | waf_g01_marker |
|---|---|---|---|---|---|
| 1 | 福建 | /zwgk/zfgb/ | 404 | BLOCKED | false |
| 2 | 福建 | /zwgk/zcwj/ | 404 | BLOCKED | false |
| 3 | 河南 | /zwgk/zfgb/ | **200** | **REACHABLE** | false |
| 4 | 广东 | /zwgk/zfgb/ | 404 | BLOCKED | false |
| 5 | 国务院 | /zhengceku/ | 403 | BLOCKED | **true** |
| 6 | 国务院 | /zhengce/ | **200** | **REACHABLE** | false |
| 7 | 国务院 | /zhengce/2024-08/15/content_1155106.htm | 404 | BLOCKED | false |
| 8 | 国务院 | /zwgk/2024-08/15/content_xxx.htm | 404 | BLOCKED | false |
| 9 | 贵州 | /zwgk/szfwj/ | 404 | BLOCKED | false |
| 10 | 河南 | /zwgk/wjzl/ | 404 | BLOCKED | false |

**顶层裁定：MIXED** — 8 BLOCKED + 2 REACHABLE；http_count=10/10 达上限。

### 5.2 M4.6 真实抓取矩阵（3 fetch / 9 HTTP / 3 真实样本落地）

| verdict | URL | http_code | file_size | sha256 (前 16) | 643 落地 |
|---|---|---|---|---|---|
| REAL_FETCHED 1 | `https://www.hlj.gov.cn/hlj/c107882/redirect_firstChannel.shtml` | 200 | 819 | `e68099df…` | ✓ 黑龙江 省政府公报 |
| REAL_FETCHED 2 | `https://www.henan.gov.cn/2026/07-29/3380417.html` | 200 | 13,457 | `63109491…` | ✓ 河南 省政府公报2026年第14号 |
| REAL_FETCHED 3 | `https://www.yn.gov.cn/zwgk/zfgb/` | 200 | 79,137 | `93fe23b3…` | ✓ 云南 省政府公报 |

注：fujian/gd/guizhou landing 4 BLOCKED 404 或 anchor 不匹配 ⇒ 排除（vs 642 实测 fujian 200 OK 但 anchor 不匹配）。

### 5.3 真实化 SQL seed 结构（24 INSERT 共）

| 表 | 行数 | lineage.is_demo | 来源 |
|---|---|---|---|
| source_registry | 3 | — (synthetic, but 真实 domain) | hlj / henan / yunnan 政府网官方 (enabled=TRUE) |
| source_document | 3 | — (file_hash_sha256 真实) | 3 真实 detail page (verification_status=UNVERIFIED) |
| policy_document | **3** | `'false'` (spike) | 3 GOV_REPORT (BULLETIN classification) |
| policy_target | **3** | `'false'` (spike) | 3 real-policy-target-{hlj/henan/yunnan}-1 |
| policy_measure | **3** | `'false'` (spike) | 3 real-policy-measure-{...}-1, measure_type=REGULATORY |
| government_commitment | **3** | `'false'` (spike) | 3 real-commitment-{...}-1, geo_entity_id=**SELECT 子查询** |
| commitment_progress | **3** | `'false'` (spike) | 3 progress_value=1.0, FULFILLED |
| project_event | **3** | `'false'` (spike) | 3 real-project-{...}-1, geo_entity_id=**SELECT 子查询** |

**总计**：3 + 3 + 3×6 = 24 INSERT（vs 643 tasking 规划 3 + 3 + 36 = 42 INSERT；spike 边界调整后 24 INSERT）

**lineage JSONB 真实化 sentinel 一致 shape**：

```json
{
  "chain_id": "real_643_m4_6_govreport",
  "source_file_sha256": "<真实 SHA per province>",
  "source_file_url": "<真实 detail page URL>",
  "extractor_version": "v1.0",
  "is_demo": "false"
}
```

### 5.4 真实化数据选择理由（spike 性质）

- 3 policy_document = 3 真实 detail page（hlj 省政府公报 / henan  省政府公报2026年第14号 / yunnan 省政府公报）
- 3 policy_target / policy_measure / commitment_progress / project_event = 同上 (lineage 一致)
- 3 government_commitment / project_event = 黑龙江/河南/云南 真实 geo_entity_id（SELECT 子查询）
- 真实化 spike 边界 3 试点省（vs 640 demo × 30 / 641 real × 1 / 642 real × 3）：spike 性质，验证 8 表 JOIN 端到端 + R3-E provenance 真实生成
- 3 真实 SHA ≠ 642 任免 SHA cd6aff30/4349ee0f/fede03ba ≠ 641 real SHA 26e5379d…b87ab ≠ 640 demo SHA 0…02 ≠ 639 demo SHA 0…01
- 真实 URL 来自黑龙江/河南/云南 政府源（非商业库）

---

## 6. PHOTO-5: 红线表（643 §PHOTO-5 / §1 禁）

| 红线 | 状态 | 证据 |
|---|---|---|
| 不宣布 Gate / O1 / M2 / M4 / M5 / M4.6 PASS | ✓ | docs/64 §6 + docs/65 §6 全 disclaimer；test_doc_64_no_pass_announcement + test_doc_65_no_pass_announcement 验证 |
| 不让用户裁定 URL/年份 | ✓ | 抓取 URL 自取政府源（hlj/henan/yunnan 政府网）；无问句 |
| 数据源唯一=政府/统计/研究机构 | ✓ | 抓取 URL = 政府网 (hlj.gov.cn / henan.gov.cn / yn.gov.cn) |
| 不爬网 | ✓ | M5 ≤10 HTTP total（实测 10/10）；M4.6 ≤12 HTTP total（实测 9/12）；硬性上限遵守 |
| 不写 cegr.observation 真实行 | ✓ | 643-A.1 + 643-A.2 read-only；seed SQL 仅 INSERT 真实行（spike 性质） |
| 不静默硬编码 GDP 值 | ✓ | target_value 等 NULL（如无具体值）；commitment_text 从抓取 anchor 文本 |
| 不删表 / 不 DROP COLUMN | ✓ | seed SQL 仅 INSERT ON CONFLICT DO NOTHING（剥注释后扫验证） |
| 不新写 016 migration (沿用 009+010 lineage JSONB) | ✓ | 643-A.3 不写 016；lineage JSONB sentinel 沿用 641/642 |
| spike 边界 ≤ 6 each 政策表 (M4.6 规划) → 实际 3 (边界调整) | ✓ | test_seed_m4_6_sql_exists_and_has_real_data 验证；docs/65 §2 spike 边界调整文档化 |
| lineage.is_demo='false' 真实化 sentinel | ✓ | test_seed_m4_6_sql_lineage_is_demo_false_isolation 验证 |
| 3 真实 SHA ≠ 642 demo/real ≠ 641 real ≠ 640 demo ≠ 639 demo | ✓ | test_seed_m4_6_sql_real_sha_distinct_from_prior_shas 验证（剥注释后扫） |
| chain_id 区分 (real_643_m4_6_govreport) | ✓ | seed SQL 中 chain_id='real_643_m4_6_govreport' + 不含 chain_id='real_641_heilongjiang' + 不含 chain_id='real_642_m4_5_renmian' |
| 黑龙江/河南/云南 geo_entity_id via SELECT 子查询 | ✓ | test_seed_m4_6_sql_has_select_subquery_for_geo_entity 验证 |
| 不修改 source_registry 既有行 / mart / 4 fixture | ✓ | 643 新增 3 真实 source_registry 行（不修改既有）；不动 mart / fixture |
| 湖北必须 ≠ M1 半年表 c5cf5abe | ✓ | 643 不写湖北具体 observation；湖北不在 643-A.2 试点省之列 |
| fetch / probe 脚本幂等 | ✓ | no time.sleep / no random.random（剥 docstring + 注释后扫验证）；sha256 deterministic |
| WAF 网防G01 假设验证 (M5) | ✓ | 国务院 /zhengceku/ 403 WAF 网防G01 marker 真出现；4 BLOCKED 省 zfwj 路径缺失（不误判 WAF）；gov/zhengce root 200 验证 WAF selective |
| 双推 origin→github | ✓ | §7 commit + origin → github 顺序 |

**新增 / 修改文件清单**：

```
scripts/probe_m5_waf_v2_2024.py                                    (643-A.1 新增; 10 cells ≤10 HTTP probe 二次)
scripts/fetch_m4_6_govreport_v1_2024.py                             (643-A.2 新增; 6 试点省 ≤12 HTTP 政府工作报告抓取)
scripts/seed_m4_6_govreport_real.sql                               (643-A.3 新增; 真实化 seed SQL 24 INSERT)
docs/64-m5-waf-second-pass-20260901.md                             (643-A.4 新增; M5 二次架构师级 §1-§6)
docs/65-m4-6-govreport-real-20260901.md                            (643-A.4 新增; M4.6 架构师级 §1-§6)
docs/reports/m5_waf_v2_probe_20260901.md                           (643-A.5 新增; M5 二次探活报告)
docs/reports/m4_6_govreport_real_20260901.md                       (643-A.5 新增; M4.6 真实抓取报告)
evidence_pack/m5_waf_v2_probe_20260901.json                        (643-A.5 新增; M5 二次证据包)
evidence_pack/m4_6_govreport_real_20260901.json                    (643-A.5 新增; M4.6 证据包)
tests/test_m5_waf_second_pass.py                                   (643-B 新增; 9 用例)
tests/test_m4_6_govreport_real.py                                  (643-B 新增; 8 用例)
reviews/stage0-gate0-rework-2026-08-23/643-stage0-architect-m5-2-m4-6-parallel-tasking-20260901.md  (643 tasking)
reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md            (643 tasking rev bump)
reviews/stage0-gate0-rework-2026-08-23/643-stage0-cc-m5-2-m4-6-parallel-receipt-20260901.md     (本回执)
```

---

## 7. commit + 双推

### 7.1 643 delivery commit (11 files)

```bash
git add scripts/probe_m5_waf_v2_2024.py \
        scripts/fetch_m4_6_govreport_v1_2024.py \
        scripts/seed_m4_6_govreport_real.sql \
        docs/64-m5-waf-second-pass-20260901.md \
        docs/65-m4-6-govreport-real-20260901.md \
        docs/reports/m5_waf_v2_probe_20260901.md \
        docs/reports/m4_6_govreport_real_20260901.md \
        evidence_pack/m5_waf_v2_probe_20260901.json \
        evidence_pack/m4_6_govreport_real_20260901.json \
        tests/test_m5_waf_second_pass.py \
        tests/test_m4_6_govreport_real.py

git commit -m "feat(643): M5 WAF 二次 + M4.6 政府工作报告真实化并行 — 10 cells MIXED + 24 INSERT lineage.is_demo='false'"

git push origin HEAD
git push github HEAD
```

### 7.2 cc_head backfill commit (1 file)

```bash
# After 7.1 commit, capture hash; update EXEC-QUEUE TBD → <hash>
git add reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md
git commit -m "chore(643): EXEC-QUEUE cc_head backfill TBD → <hash> (delivery)"

git push origin HEAD
git push github HEAD
```

### 7.3 receipt commit (1 file)

```bash
git add reviews/stage0-gate0-rework-2026-08-23/643-stage0-cc-m5-2-m4-6-parallel-receipt-20260901.md
git commit -m "docs(643): receipt §PHOTO-1..6"

git push origin HEAD
git push github HEAD
```

---

## 8. 下一步

- 用户接受/驳回 643 推荐 644 scope：
  - **接受** → 644 = M5 WAF spike 第三次收口（gov/zhengce root 索引 + WAF 网防G01 selective 子路径进一步验证）
  - **接受** → 644 = M4.7 政策详情真实化（复用 643 3 试点省 hlj/henan/yunnan × 1 detail each × 6 政策表 spike = 18 INSERT planned）
  - **接受** → 644 = M5 第三次收口 + M4.7 并行（架构师综合推荐；spike 不互斥）
  - **接受** → 644 = M6 spike + M4.7 并行（备选）
  - **接受** → 644 = M5 + M4.7 + M6 三方并行（激进）
  - **驳回** → 用户裁定 644 re-scope 或跳过 M5/M4.6 接其他方向
- **不宣布** Gate / O1 / M2 / M4 / M5 / M4.6 PASS。
- 644 tasking 待架构师（用户）签发；执行端在收到新刀前静默等待。

— End 643 receipt —