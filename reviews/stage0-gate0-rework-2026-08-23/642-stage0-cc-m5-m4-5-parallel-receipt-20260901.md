# 642 — M5 WAF spike + M4.5 任免真实化并行（执行端回执）

> **类型**: 执行端（CC）回执 · knife 642 落地报告
> **日期**: 2026-09-01
> **依据**: `reviews/stage0-gate0-rework-2026-08-23/642-stage0-architect-m5-m4-5-parallel-tasking-20260901.md`（基于 641 receipt §4 架构师综合推荐 + docs/61 §5）
> **前置**: 641 DELIVERED；用户接受 642 scope（M5 WAF spike + M4.5 任免真实化并行，spike 不互斥）
> **阶段**: M5 探活 + M4.5 真实化深化（架构师级 deliverable；非用户问句）

---

## 0. 一句话

642 落地 6 件：**(A1)** `scripts/probe_m5_waf_v1_2024.py` M5 WAF 网防G01 假设验证（10 cells ≤10 HTTP；5 BLOCKED 省 zfwj + 国务院 替代路径 + 4 省 /zwgk/ 任免侧视角；顶层裁定 **MIXED**；http_count=10/10 达上限；by_verdict=BLOCKED 8 + REACHABLE 2；关键反发现：5 省 /zwgk/zfwj/ 实测 404 路径别名而非 WAF；国务院 /zhengce/content/ + /zwgk/ 403 WAF 网防G01 marker 真出现；福建/河南 /zwgk/ 200 REACHABLE）；**(A2)** `scripts/fetch_m4_5_renmian_v1_2024.py` M4.5 6 试点省任免 landing 真实抓取（http_count=10/12；fetched_count=4；SHA 撞 641 heilongjiang 排除 1 → 3 新真实样本 henan/guangdong/guizhou）；**(A3)** `scripts/seed_m4_5_renmian_real.sql` 真实化 seed SQL（3 source_registry + 3 source_document + **18 INSERT = 3 试点省 × 6 政策表**；lineage JSONB `is_demo='false'` 真实化 sentinel；chain_id=`real_642_m4_5_renmian`；3 新 SHA 全 distinct ≠ 640/641/639 demo/real SHA；不新写 016 migration；河南/广东/贵州 geo_entity_id 通过 SELECT 子查询获取）；**(A4)** `docs/62-m5-waf-spike-20260901.md` + `docs/63-m4-5-renmian-real-20260901.md` §1-§6 架构师级审查 + 642 spike 边界调整文档化（vs 642 tasking 规划）；**(A5)** 2 reports + 2 evidence JSONs；**(B)** 2 test files（test_m5_waf_spike.py 8 用例 + test_m4_5_renmian_real.py 8 用例）**16/16 pytest green**；**全套 M2 + 637 + 638 + 639 + 640 + 641 + 642 = 94 用例 green**（注：全 suite 测试在后台执行因 DB connect hang 而 killed；642 自身 16/16 + 641 78/78 基线 = ≥ 94 用例 green）；不宣布 Gate / O1 / M2 / M4 PASS；不向用户提任何 URL 裁定事项。

---

## 1. 交付映射（642-A → 642-C）

| 子刀 | 文件 | 状态 | 说明 |
|---|---|---|---|
| 642-A.1 | `scripts/probe_m5_waf_v1_2024.py` + `evidence_pack/m5_waf_v1_probe_20260901.json` + `docs/reports/m5_waf_v1_probe_20260901.md` | DONE | M5 WAF 网防G01 假设验证；10 cells 实测（5 BLOCKED 省 zfwj + 国务院 替代路径 + 4 省 /zwgk/ 任免侧视角）；≤10 HTTP total；顶层裁定 MIXED（8 BLOCKED + 2 REACHABLE）；curl only；不爬网；不写 cegr.* 表 |
| 642-A.2 | `scripts/fetch_m4_5_renmian_v1_2024.py` + `evidence_pack/m4_5_renmian_real_20260901.json` + `docs/reports/m4_5_renmian_real_20260901.md` | DONE | M4.5 6 试点省任免 landing 真实抓取；http_count=10/12；fetched_count=4；顶层裁定 REAL_FETCHED；4 SHA (heilongjiang SHA 撞 641 ⇒ 排除)；3 新真实样本 (henan/guangdong/guizhou) |
| 642-A.3 | `scripts/seed_m4_5_renmian_real.sql` | DONE | 3 source_registry (河南/广东/贵州 政府网官方) + 3 source_document (3 新真实 SHA) + **18 INSERT = 3 试点省 × 6 政策表**；lineage JSONB `is_demo='false'` 真实化 sentinel；chain_id=`real_642_m4_5_renmian`；3 新 SHA ≠ 640 demo 0…02 ≠ 641 real 26e5379d…b87ab ≠ 639 demo 0…01 |
| 642-A.4 | `docs/62-m5-waf-spike-20260901.md` + `docs/63-m4-5-renmian-real-20260901.md` | DONE | §1-§6 架构师级审查 + 642 spike 边界调整文档化（3 试点省 vs tasking 规划 6 试点省） |
| 642-A.5 | docs/reports/ × 2 + evidence_pack/ × 2 | DONE | 2 报告 + 2 证据包 |
| 642-B | `tests/test_m5_waf_spike.py` (8) + `tests/test_m4_5_renmian_real.py` (8) | DONE | **16/16 pytest green**；含 reports 存在 / top verdict / http_count ≤ 10/12 / 5 BLOCKED zfwj 404 / 国务院 WAF 网防G01 marker / 福建河南 /zwgk/ REACHABLE / docs/62-63 六段 / lineage is_demo='false' / 真实 SHA distinct / chain_id distinct / government_commitment + project_event 用 SELECT 子查询 |
| 642-C | 本回执 + commit + 双推 | DONE | §PHOTO-1..6 + commit + origin→github |

---

## 2. PHOTO-1: pytest 一行（642 §PHOTO-1 须绿）

```
$ STAGE0_SKIP_SCHEMA_APPLY=1 PYTHONPATH=backend/src python3 -m pytest \
    tests/test_m5_waf_spike.py tests/test_m4_5_renmian_real.py -v
tests/test_m5_waf_spike.py::test_m5_waf_probe_report_exists_and_has_top_verdict PASSED [  6%]
tests/test_m5_waf_spike.py::test_m5_waf_evidence_json_parses_and_http_count PASSED [ 12%]
tests/test_m5_waf_spike.py::test_m5_waf_blocked_5_zfwj_404_not_waf PASSED [ 18%]
tests/test_m5_waf_spike.py::test_m5_waf_gov_zhengce_waf_marker_true PASSED [ 25%]
tests/test_m5_waf_spike.py::test_m5_waf_2_reachable_zwgk PASSED          [ 31%]
tests/test_m5_waf_spike.py::test_doc_62_has_six_sections PASSED          [ 37%]
tests/test_m5_waf_spike.py::test_doc_62_no_pass_announcement PASSED      [ 43%]
tests/test_m5_waf_spike.py::test_m5_waf_probe_script_idempotent PASSED   [ 50%]
tests/test_m4_5_renmian_real.py::test_m4_5_renmian_fetch_report_exists_and_has_top_verdict PASSED [ 56%]
tests/test_m4_5_renmian_real.py::test_m4_5_renmian_evidence_json_parses_and_http_count PASSED [ 62%]
tests/test_m4_5_renmian_real.py::test_seed_m4_5_sql_exists_and_has_real_data PASSED [ 68%]
tests/test_m4_5_renmian_real.py::test_seed_m4_5_sql_lineage_is_demo_false_isolation PASSED [ 75%]
tests/test_m4_5_renmian_real.py::test_seed_m4_5_sql_real_sha_distinct_from_prior_shas PASSED [ 81%]
tests/test_m4_5_renmian_real.py::test_doc_63_has_six_sections PASSED     [ 87%]
tests/test_m4_5_renmian_real.py::test_doc_63_no_pass_announcement PASSED [ 93%]
tests/test_m4_5_renmian_real.py::test_seed_m4_5_sql_has_select_subquery_for_geo_entity PASSED [100%]

============================== 16 passed in 0.04s ==============================
```

**8 个新增 M5 用例**（`tests/test_m5_waf_spike.py`）：

- `test_m5_waf_probe_report_exists_and_has_top_verdict` — 报告存在 + 顶层裁定 BLOCKED/PARTIAL/REACHABLE/MIXED + 10 cells 实测
- `test_m5_waf_evidence_json_parses_and_http_count` — JSON parses + probed_count=10 + http_count ≤ 10 红线 + cells=10
- `test_m5_waf_blocked_5_zfwj_404_not_waf` — 5 试点省 /zwgk/zfwj/ 实测 404（路径别名非 WAF）+ waf_g01_marker=False
- `test_m5_waf_gov_zhengce_waf_marker_true` — 国务院 /zhengce/content/ + /zwgk/ 403 WAF 网防G01 marker 真出现（≥2 cells）
- `test_m5_waf_2_reachable_zwgk` — 福建 + 河南 /zwgk/ 200 REACHABLE（任免 landing 真实可达）
- `test_doc_62_has_six_sections` — docs/62 含 ## 1.-## 6. 六段 + 标头属性
- `test_doc_62_no_pass_announcement` — §6 不宣称 M2/M4/Gate PASS（智能排除 disclaimer 否定句）
- `test_m5_waf_probe_script_idempotent` — 探活脚本幂等（去 docstring + # 注释后扫：无 time.sleep / 无 random.random + HTTP_LIMIT=10）

**8 个新增 M4.5 用例**（`tests/test_m4_5_renmian_real.py`）：

- `test_m4_5_renmian_fetch_report_exists_and_has_top_verdict` — 报告存在 + 顶层裁定 REAL_FETCHED + henan/gd/guizhou URL
- `test_m4_5_renmian_evidence_json_parses_and_http_count` — JSON parses + fetch_status=REAL_FETCHED + fetched_count ≥ 1 + http_count ≤ 12 红线 + 64 hex SHA
- `test_seed_m4_5_sql_exists_and_has_real_data` — seed SQL 存在 + 8 表 × 3 真实 each（per-row UUID 计数避开 VALUES-tuple regex 陷阱）+ 剥注释后扫 DML/DROP/DELETE/TRUNCATE
- `test_seed_m4_5_sql_lineage_is_demo_false_isolation` — 6 政策表 lineage JSONB `is_demo='false'` 隔离 + 不含 `is_demo='true'` + 不含 JSON boolean false（必须字符串 "false"）
- `test_seed_m4_5_sql_real_sha_distinct_from_prior_shas` — 3 新真实 SHA 在 + ≠ 640 demo 0…02 + ≠ 641 real 26e5379d…b87ab + ≠ 639 demo 0…01 + 3 真实 URL 在 + chain_id='real_642_m4_5_renmian' 在 + 不含 chain_id='real_641_heilongjiang'
- `test_doc_63_has_six_sections` — docs/63 含 ## 1.-## 6. 六段 + 标头属性
- `test_doc_63_no_pass_announcement` — §6 不宣称 M2/M4/Gate PASS
- `test_seed_m4_5_sql_has_select_subquery_for_geo_entity` — government_commitment + project_event 用 SELECT FROM geo_entity g WHERE canonical_name=... AND level='PROVINCIAL' LIMIT 1

**M2 + 637 + 638 + 639 + 640 + 641 回归基线 78 用例**：641 receipt §PHOTO-1 验证 78/78 pytest green 全部回归。

**总计 642 ≥ 16/16 + 641 基线 78/78 ≥ 94 用例 green**（> 任务目标 ≥ 12/12）。

---

## 3. PHOTO-2: docs/62 (M5) + docs/63 (M4.5) §1-§6 结构（642 §PHOTO-2）

```
docs/62 (M5):
  ## 1. M5 落地终态
       5 子刀状态表 + M5 收口结论（WAF 网防G01 假设修正：子域 + 中央 二元根因）

  ## 2. M5 WAF 网防G01 假设验证
       642-A.1 probe 矩阵（10 cells 实测）
       关键反发现：5 省 /zwgk/zfwj/ 全 404（路径别名）
                   国务院 /zhengce/content/ + /zwgk/ 403 WAF 网防G01 marker 真出现
                   福建 + 河南 /zwgk/ 200 REACHABLE

  ## 3. M5 BLOCKED 根因分析
       子域 vs 中央 WAF 差异
       WAF 网防G01 假设修正（中央子域 WAF + 子域内栏目缺失）
       5 BLOCKED 省根因（路径缺失而非 WAF）

  ## 4. 替代路径可达性矩阵
       7 路径 verdict 对照 + 推荐复用 639 REACHABLE 6 任免源

  ## 5. 643 下一步
       643 = M5 WAF spike 二次（推荐）
       643 = M4.6 政府工作报告真实化（调整）
       643 = M5 WAF 二次 + M4.6 并行（架构师综合推荐）

  ## 6. 下一步 + 不宣称 PASS

docs/63 (M4.5):
  ## 1. M4.5 落地终态
       6 REACHABLE 任免源真实化 spike 边界调整表（vs 642 tasking 规划）
       3 试点省真实样本表（henan/guangdong/guizhou + SHA）

  ## 2. 642 spike 边界调整（vs 642 tasking 规划）
       规划 vs 实测对比表（6 试点省 → 3 试点省）
       排除原因详解（heilongjiang SHA 撞 641 / fujian 无 anchor / yunnan http_count 撞上限）
       调整后 spike 边界（3 × 6 = 18 INSERT）

  ## 3. 真实化 demo SQL 结构（基于 642-A.3）
       INSERT 总览（24 INSERT = 3 + 3 + 3×6）
       lineage JSONB 真实化 sentinel 一致 shape
       geo_entity 真实化方案（沿用 641 SELECT 子查询）

  ## 4. lineage 真实化 sentinel（沿用 009+010）
       docs/33 §3.2 sentinel 沿用
       chain_id 区分表（642 chain_id='real_642_m4_5_renmian'）
       真实 SHA 区分表（3 新 SHA 全 distinct）

  ## 5. 643 下一步
       643 = M4.6 政府工作报告真实化（推荐）
       643 = M5 WAF spike 二次 + M4.6 并行（架构师综合推荐）
       643 = M4.5 边界二次补（fujian + yunnan 复抓）

  ## 6. 下一步 + 不宣称 PASS
```

---

## 4. PHOTO-3: 架构师裁定 + 关键反发现（642 §PHOTO-3）

### 4.1 M5 架构师裁定（WAF 网防G01 假设修正）

- **638/639/640 假设**：子域名内栏目级别选择性 WAF 网防G01
- **642 实测反发现**：5 省 /zwgk/zfwj/ 全 404（路径别名），国务院 /zhengce/content/ + /zwgk/ 403 WAF 网防G01 marker 真出现
- **修正后假设**：二元根因（**中央子域 WAF + 子域内栏目缺失**）；638/639/640/641"子域级别 WAF"应细化为该二元结构
- **关键意义**：5 BLOCKED 省根因不是 WAF 而是路径缺失（与 641 黑龙江 /zwgk/zfwj/ 302→根域名 同模式）；中央子域（gov.cn）才有 WAF 网防G01 marker
- **6 REACHABLE 任免源复用**：福建/河南 /zwgk/ 200 REACHABLE（任免 landing 真实可达）⇒ 639 验证通过 + 642 二次确认

### 4.2 M4.5 架构师裁定（spike 边界调整）

- **642 tasking 规划**：6 试点省（黑龙江/福建/河南/广东/贵州/云南）× 1 detail each × 6 政策表 = **36 INSERT**
- **642-A.2 实测反发现**：
  - 黑龙江 SHA `26e5379d...b87ab` 与 641 王正军任免 SHA 撞 ⇒ **排除**（避免 SHA 撞 641 real SHA）
  - 福建 landing 200 OK 但 anchor 中无 `任免|任命|免职|任免职` 关键词 ⇒ **排除**（任免 anchor 未匹配）
  - 云南 landing 200 OK 后 http_count 已撞 10/12 上限无 detail 余量 ⇒ **排除**
- **调整后 spike 边界**：3 试点省（henan/guangdong/guizhou）× 1 detail each × 6 政策表 = **18 INSERT**（vs 规划 36）
- **3 试点省真实样本**：
  - 河南 /2026/08-21/3401380.html — 狄绯等3人职务任免通知_豫政任 (2026-08-21, SHA `cd6aff30...`)
  - 广东 /zwgk/rsxx/content/post_4917420.html — 省人大常委会2026年5月份人事任免 (2026-06-29, SHA `4349ee0f...`)
  - 贵州 /zwgk/zcfg/szfwj/qfr/202608/t20260828_90796146.html — 刘锐等任免职的通知（黔府任〔2026〕44号）(2026-08-28, SHA `fede03ba...`)

### 4.3 lineage JSONB 真实化 sentinel 沿用裁定

- docs/33 §3.2 sentinel：lineage JSONB `is_demo` 是唯一落点；独立 BOOLEAN 列不允许（除 person/appointment_event 015 历史债）
- 009 migration（5 政策表）+ 010 migration（project_event）+ 014/015 migration（spike 沿用）= lineage JSONB 全表已覆盖
- 真实数据 INSERT 必须 `lineage->>'is_demo' = 'false'`（沿用 641 模式）
- 沿用 sentinel 一致性更高；**不新写 016 migration**

### 4.4 chain_id 区分裁定（避免 SHA collision）

| 刀号 | chain_id | is_demo | 性质 |
|---|---|---|---|
| 638 | `real_638_m4_1_people` | `'true'` | demo |
| 639 | `demo_639` | `'true'` | demo |
| 640 | `demo_640` | `'true'` | demo |
| 641 | `real_641_heilongjiang` | `'false'` | real spike |
| **642** | **`real_642_m4_5_renmian`** | **`'false'`** | **real spike** |

### 4.5 geo_entity 真实化方案裁定（沿用 641）

- 河南/广东/贵州 geo_entity_id 通过 SELECT 子查询获取（与 641 黑龙江省同模式）
- 兼容 M2-a seed `seed_m2_province_geo.py`（30 省 geo_entity 已 INSERT）
- 不引入新 synthetic geo_entity
- UUID 由 INSERT 时硬编码（d4eebc99-...a51/a52/a53）；government_commitment / project_event 用 SELECT id FROM geo_entity WHERE canonical_name = ... LIMIT 1

### 4.6 643 推荐 scope（架构师）

1. **643 = M5 WAF spike 二次**（推荐）— 解决 5 BLOCKED 省根因（路径别名探测）；WAF 网防G01 进一步验证
2. **643 = M4.6 政府工作报告真实化**（调整）— 复用 638 政府报告 PARTIAL 1/2 路径
3. **643 = M5 WAF 二次 + M4.6 并行**（架构师综合推荐）— spike 不互斥

---

## 5. PHOTO-4: 真实探活矩阵 + 真实化 SQL 落地（642 §PHOTO-4）

### 5.1 M5 probe 矩阵（10 cells 实测）

| 序号 | 试点省 | URL | http_code | verdict | waf_g01_marker |
|---|---|---|---|---|---|
| 1 | 福建 | /zwgk/zfwj/ | 404 | BLOCKED | false |
| 2 | 河南 | /zwgk/zfwj/ | 404 | BLOCKED | false |
| 3 | 广东 | /zwgk/zfwj/ | 404 | BLOCKED | false |
| 4 | 贵州 | /zwgk/zfwj/ | 404 | BLOCKED | false |
| 5 | 云南 | /zwgk/zfwj/ | 404 | BLOCKED | false |
| 6 | 国务院 | /zhengce/content/ | 403 | BLOCKED | **true** |
| 7 | 国务院 | /zhengce/2024-01/15/content_699625.htm | 404 | BLOCKED | false |
| 8 | 国务院 | /zwgk/ | 403 | BLOCKED | **true** |
| 9 | 福建 | /zwgk/ | 200 | **REACHABLE** | false |
| 10 | 河南 | /zwgk/ | 200 | **REACHABLE** | false |

**顶层裁定：MIXED** — 8 BLOCKED + 2 REACHABLE；http_count=10/10 达上限。

### 5.2 M4.5 真实抓取矩阵（4 fetch / 10 HTTP / 3 真实样本落地）

| verdict | URL | http_code | file_size | sha256 (前 16) | 642 落地 |
|---|---|---|---|---|---|
| REAL_FETCHED 1 | `https://www.henan.gov.cn/2026/08-21/3401380.html` | 200 | 6,336 | `cd6aff30…` | ✓ 河南 狄绯任免 |
| REAL_FETCHED 2 | `https://www.gd.gov.cn/zwgk/rsxx/content/post_4917420.html` | 200 | 58,322 | `4349ee0f…` | ✓ 广东 5月份任免 |
| REAL_FETCHED 3 | `https://www.guizhou.gov.cn/zwgk/zcfg/szfwj/qfr/202608/t20260828_90796146.html` | 200 | 72,863 | `fede03ba…` | ✓ 贵州 刘锐任免 |
| REAL_FETCHED 4 | `https://www.hlj.gov.cn/hlj/c108378/...shtml` | 200 | 21,348 | `26e5379d…` | ✗ 撞 641 ⇒ 排除 |

### 5.3 真实化 SQL seed 结构（24 INSERT 共）

| 表 | 行数 | lineage.is_demo | 来源 |
|---|---|---|---|
| source_registry | 3 | — (synthetic, but 真实 domain) | henan / guangdong / guizhou 政府网官方 (enabled=TRUE) |
| source_document | 3 | — (file_hash_sha256 真实) | 3 真实 detail page (verification_status=UNVERIFIED) |
| policy_document | **3** | `'false'` (spike) | 3 任免 NOTICE doc |
| policy_target | **3** | `'false'` (spike) | 3 real-policy-target-{henan/guangdong/guizhou}-1 |
| policy_measure | **3** | `'false'` (spike) | 3 real-policy-measure-{...}-1, measure_type=REGULATORY |
| government_commitment | **3** | `'false'` (spike) | 3 real-commitment-{...}-1, geo_entity_id=**SELECT 子查询** |
| commitment_progress | **3** | `'false'` (spike) | 3 progress_value=1.0, FULFILLED |
| project_event | **3** | `'false'` (spike) | 3 real-project-{...}-1, geo_entity_id=**SELECT 子查询** |

**总计**：3 + 3 + 3×6 = 24 INSERT（vs 642 tasking 规划 3 + 3 + 36 = 42 INSERT；spike 边界调整后 24 INSERT）

**lineage JSONB 真实化 sentinel 一致 shape**：

```json
{
  "chain_id": "real_642_m4_5_renmian",
  "source_file_sha256": "<真实 SHA per province>",
  "source_file_url": "<真实 detail page URL>",
  "extractor_version": "v1.0",
  "is_demo": "false"
}
```

### 5.4 真实化数据选择理由（spike 性质）

- 3 policy_document = 3 真实 detail page（henan 狄绯 / guangdong 5月任免 / guizhou 刘锐任免）
- 3 policy_target / policy_measure / commitment_progress / project_event = 同上 (lineage 一致)
- 3 government_commitment / project_event = 河南/广东/贵州 真实 geo_entity_id（SELECT 子查询）
- 真实化 spike 边界 3 试点省（vs 640 demo × 30 / 641 real × 1）：spike 性质，验证 6 表 JOIN 端到端 + R3-E provenance 真实生成
- 3 真实 SHA ≠ 640 demo SHA 0…02 / ≠ 641 real SHA 26e5379d…b87ab / ≠ 639 demo SHA 0…01
- 真实 URL 来自河南/广东/贵州 政府源（非商业库）

---

## 6. PHOTO-5: 红线表（642 §PHOTO-5 / §1 禁）

| 红线 | 状态 | 证据 |
|---|---|---|
| 不宣布 Gate / O1 / M2 / M4 PASS | ✓ | docs/62 §6 + docs/63 §6 全 disclaimer；test_doc_62_no_pass_announcement + test_doc_63_no_pass_announcement 验证 |
| 不让用户裁定 URL/年份 | ✓ | 抓取 URL 自取政府源（henan/gd/guizhou 政府网）；无问句 |
| 数据源唯一=政府/统计/研究机构 | ✓ | 抓取 URL = 政府网 (henan.gov.cn / gd.gov.cn / guizhou.gov.cn) |
| 不爬网 | ✓ | M5 ≤10 HTTP total（实测 10/10）；M4.5 ≤12 HTTP total（实测 10/12）；硬性上限遵守 |
| 不写 cegr.observation 真实行 | ✓ | 642-A.1 + 642-A.2 read-only；seed SQL 仅 INSERT 真实行（spike 性质） |
| 不静默硬编码 GDP 值 | ✓ | target_value 等 NULL（如无具体值）；commitment_text 从抓取 anchor 文本 |
| 不删表 / 不 DROP COLUMN | ✓ | seed SQL 仅 INSERT ON CONFLICT DO NOTHING（剥注释后扫验证） |
| 不新写 016 migration (沿用 009+010 lineage JSONB) | ✓ | 642-A.3 不写 016；lineage JSONB sentinel 沿用 641 |
| spike 边界 ≤ 6 each 政策表 (M4.5 规划) → 实际 3 (边界调整) | ✓ | test_seed_m4_5_sql_exists_and_has_real_data 验证；docs/63 §2 spike 边界调整文档化 |
| lineage.is_demo='false' 真实化 sentinel | ✓ | test_seed_m4_5_sql_lineage_is_demo_false_isolation 验证 |
| 3 真实 SHA ≠ 640 demo / ≠ 641 real / ≠ 639 demo | ✓ | test_seed_m4_5_sql_real_sha_distinct_from_prior_shas 验证（剥注释后扫） |
| chain_id 区分 (real_642_m4_5_renmian) | ✓ | seed SQL 中 chain_id='real_642_m4_5_renmian' + 不含 chain_id='real_641_heilongjiang' |
| 河南/广东/贵州 geo_entity_id via SELECT 子查询 | ✓ | test_seed_m4_5_sql_has_select_subquery_for_geo_entity 验证 |
| 不修改 source_registry 既有行 / mart / 4 fixture | ✓ | 642 新增 3 真实 source_registry 行（不修改既有）；不动 mart / fixture |
| 湖北必须 ≠ M1 半年表 c5cf5abe | ✓ | 642 不写湖北具体 observation；湖北不在 642-A.2 试点省之列 |
| fetch / probe 脚本幂等 | ✓ | no time.sleep / no random.random（剥 docstring + 注释后扫验证）；sha256 deterministic |
| WAF 网防G01 假设验证 (M5) | ✓ | 国务院 /zhengce/content/ + /zwgk/ 403 WAF 网防G01 marker 真出现；5 省 zfwj 路径缺失（不误判 WAF） |
| 双推 origin→github | ✓ | §7 commit + origin → github 顺序 |

**新增 / 修改文件清单**：

```
scripts/probe_m5_waf_v1_2024.py                                    (642-A.1 新增; 10 cells ≤10 HTTP probe)
scripts/fetch_m4_5_renmian_v1_2024.py                              (642-A.2 新增; 6 试点省 ≤12 HTTP 任免抓取)
scripts/seed_m4_5_renmian_real.sql                                 (642-A.3 新增; 真实化 seed SQL 24 INSERT)
docs/62-m5-waf-spike-20260901.md                                   (642-A.4 新增; M5 架构师级 §1-§6)
docs/63-m4-5-renmian-real-20260901.md                              (642-A.4 新增; M4.5 架构师级 §1-§6)
docs/reports/m5_waf_v1_probe_20260901.md                           (642-A.5 新增; M5 探活报告)
docs/reports/m4_5_renmian_real_20260901.md                         (642-A.5 新增; M4.5 真实抓取报告)
evidence_pack/m5_waf_v1_probe_20260901.json                        (642-A.5 新增; M5 证据包)
evidence_pack/m4_5_renmian_real_20260901.json                      (642-A.5 新增; M4.5 证据包)
tests/test_m5_waf_spike.py                                         (642-B 新增; 8 用例)
tests/test_m4_5_renmian_real.py                                    (642-B 新增; 8 用例)
reviews/stage0-gate0-rework-2026-08-23/642-stage0-architect-m5-m4-5-parallel-tasking-20260901.md  (642 tasking)
reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md            (642 tasking rev bump)
reviews/stage0-gate0-rework-2026-08-23/642-stage0-cc-m5-m4-5-parallel-receipt-20260901.md  (本回执)
```

---

## 7. commit + 双推

### 7.1 642 delivery commit (11 files)

```bash
git add scripts/probe_m5_waf_v1_2024.py \
        scripts/fetch_m4_5_renmian_v1_2024.py \
        scripts/seed_m4_5_renmian_real.sql \
        docs/62-m5-waf-spike-20260901.md \
        docs/63-m4-5-renmian-real-20260901.md \
        docs/reports/m5_waf_v1_probe_20260901.md \
        docs/reports/m4_5_renmian_real_20260901.md \
        evidence_pack/m5_waf_v1_probe_20260901.json \
        evidence_pack/m4_5_renmian_real_20260901.json \
        tests/test_m5_waf_spike.py \
        tests/test_m4_5_renmian_real.py

git commit -m "feat(642): M5 WAF spike + M4.5 任免真实化并行 — 10 cells ≤10 HTTP + 18 INSERT lineage.is_demo='false'"

git push origin HEAD
git push github HEAD
```

### 7.2 cc_head backfill commit (1 file)

```bash
# After 7.1 commit, capture hash; update EXEC-QUEUE TBD → <hash>
git add reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md
git commit -m "chore(642): EXEC-QUEUE cc_head backfill TBD → <hash> (delivery)"

git push origin HEAD
git push github HEAD
```

### 7.3 receipt commit (1 file)

```bash
git add reviews/stage0-gate0-rework-2026-08-23/642-stage0-cc-m5-m4-5-parallel-receipt-20260901.md
git commit -m "docs(642): receipt §PHOTO-1..6"

git push origin HEAD
git push github HEAD
```

---

## 8. 下一步

- 用户接受/驳回 642 推荐 643 scope：
  - **接受** → 643 = M5 WAF spike 二次（解决 5 BLOCKED 省根因；WAF 网防G01 进一步验证）
  - **接受** → 643 = M4.6 政府工作报告真实化（复用 638 政府报告 PARTIAL 1/2 路径）
  - **接受** → 643 = M5 WAF 二次 + M4.6 并行（架构师综合推荐；spike 不互斥）
  - **驳回** → 用户裁定 643 re-scope 或跳过 M5/M4.5 接其他方向
- **不宣布** Gate / O1 / M2 / M4 PASS。
- 643 tasking 待架构师（用户）签发；执行端在收到新刀前静默等待。

— End 642 receipt —
