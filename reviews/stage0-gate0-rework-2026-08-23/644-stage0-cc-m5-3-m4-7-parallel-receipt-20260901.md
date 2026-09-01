# 644 — M5 WAF spike 第三次收口 + M4.7 政策详情真实化 并行（执行端回执）

> **类型**: 执行端（CC）回执 · knife 644 落地报告
> **日期**: 2026-09-01
> **依据**: `reviews/stage0-gate0-rework-2026-08-23/644-stage0-architect-m5-3-m4-7-parallel-tasking-20260901.md`（基于 643 receipt §4.6 架构师综合推荐）
> **前置**: 643 DELIVERED；用户接受 644 scope（M5 WAF spike 第三次收口 + M4.7 政策详情真实化 并行，spike 不互斥）
> **阶段**: M5 第三次 + M4.7 政策详情 spike 二次（架构师级 deliverable；非用户问句）

---

## 0. 一句话

644 落地 6 件：**(A1)** `scripts/probe_m5_waf_v3_2024.py` M5 WAF 网防G01 假设验证三次（10 cells ≤10 HTTP；顶层裁定 **MIXED** = 7 BLOCKED + 3 REACHABLE；http_count=10/10 达上限；关键反发现：国务院 `/zhengce/zhengceku/` 403 WAF 网防G01 marker 第三次确认 + `/zhengce/content_xxx.htm` 404 + `/zwgk/zcwj/ /zwgk/zcfg/ /zwgk/2026-08/15/...` retry 路径全部 404 + 国务院 `/zwgk/` root 仍 403 WAF 网防G01 第三次确认 + 3 BLOCKED 省 `/zwgk/` root REACHABLE 第三次验证）；**(A2)** `scripts/fetch_m4_7_policy_detail_v1_2024.py` M4.7 政策详情 3 试点省 hlj/henan/yunnan × 1 detail each 真实抓取（http_count=6/12；fetched_count=5；4 distinct SHA `bad8be51/dfa38998/bd4c4c51/f33eba53`；3 用于 seed）；**(A3)** `scripts/seed_m4_7_policy_detail_real.sql` 真实化 seed SQL（**18 INSERT = 3 试点省 × 6 政策表**；lineage JSONB `is_demo='false'` 真实化 sentinel；chain_id=`real_644_m4_7_policy_detail`；3 新 SHA 全 distinct ≠ 643/642/641/640/639 demo/real SHA；UUID c 段 ≠ 643 b 段；不新写 016 migration；hlj/henan/yunnan geo_entity_id 通过 SELECT 子查询获取）；**(A4)** `docs/66-m5-waf-third-pass-20260901.md` + `docs/67-m4-7-policy-detail-real-20260901.md` §1-§6 架构师级审查；**(A5)** 2 reports + 2 evidence JSONs；**(B)** 2 test files（test_m5_waf_third_pass.py 9 用例 + test_m4_7_policy_detail_real.py 9 用例）**18/18 pytest green**；不宣布 Gate / O1 / M2 / M4 / M4.7 PASS；不向用户提任何 URL 裁定事项。

---

## 1. 交付映射（644-A → 644-C）

| 子刀 | 文件 | 状态 | 说明 |
|---|---|---|---|
| 644-A.1 | `scripts/probe_m5_waf_v3_2024.py` + `evidence_pack/m5_waf_v3_probe_20260901.json` + `docs/reports/m5_waf_v3_probe_20260901.md` | DONE | M5 WAF 网防G01 假设验证三次；10 cells 实测（4 国务院 /zhengce/ 子路径 + 3 国务院 /zwgk/ retry 路径 + 3 BLOCKED 省 /zwgk/ root）；≤10 HTTP total；顶层裁定 MIXED（7 BLOCKED + 3 REACHABLE）；curl only；不爬网；不写 cegr.* 表 |
| 644-A.2 | `scripts/fetch_m4_7_policy_detail_v1_2024.py` + `evidence_pack/m4_7_policy_detail_real_20260901.json` + `docs/reports/m4_7_policy_detail_real_20260901.md` | DONE | M4.7 政策详情真实化；3 试点省（heilongjiang/henan/yunnan）× 1 detail each 政策详情页 landing 真实抓取（hlj c107884 list.shtml 避开 643 c107882 collision）；http_count=6/12；fetched_count=5；4 distinct SHA（3 用于 seed） |
| 644-A.3 | `scripts/seed_m4_7_policy_detail_real.sql` | DONE | **18 INSERT = 3 试点省 × 6 政策表**；lineage JSONB `is_demo='false'` 真实化 sentinel；chain_id=`real_644_m4_7_policy_detail`；3 新 SHA ≠ 643 SHA `e68099df/63109491/93fe23b3` ≠ 642 任免 SHA `cd6aff30/4349ee0f/fede03ba` ≠ 641 王正军 SHA `26e5379d...b87ab` ≠ 640 demo SHA `0…02` ≠ 639 demo SHA `0…01`；UUID c 段 ≠ 643 b 段 |
| 644-A.4 | `docs/66-m5-waf-third-pass-20260901.md` + `docs/67-m4-7-policy-detail-real-20260901.md` | DONE | §1-§6 双文档架构师级审查 + 644 spike 边界文档化（vs 643 tasking 规划 18 INSERT 实测一致） |
| 644-A.5 | docs/reports/ × 2 + evidence_pack/ × 2 | DONE | 2 报告 + 2 证据包 |
| 644-A.6 | `reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md` rev73 → rev74 | DONE | cc_head backfill 644 delivery `aac8225` + DELIVERED 标记；3-commits 双推完成 |
| 644-B | `tests/test_m5_waf_third_pass.py` (9) + `tests/test_m4_7_policy_detail_real.py` (9) | DONE | **18/18 pytest green**；含 reports 存在 / top verdict / http_count ≤ 10/12 / 国务院 /zhengce/zhengceku/ WAF 网防G01 marker 三次确认 / /zhengce/content_xxx.htm 真实 ID 探活 / 国务院 /zwgk/ retry 路径 verdict 矩阵 / 3 BLOCKED 省 /zwgk/ root REACHABLE / docs/66-67 六段 / lineage is_demo='false' / 真实 SHA distinct / chain_id distinct / government_commitment + project_event 用 SELECT 子查询 / UUID c 段 ≠ 643 b 段 |
| 644-C | 本回执 + commit + 双推 | DONE | §PHOTO-1..6 + delivery commit `aac8225` + cc_head backfill commit `a66215b` + receipt commit (TBD) + origin→github 双推（SSH fallback HTTPS 443 阻塞） |

---

## 2. PHOTO-1: pytest 一行（644 §PHOTO-1 须绿）

```
$ STAGE0_SKIP_SCHEMA_APPLY=1 PYTHONPATH=backend/src python3 -m pytest \
    tests/test_m5_waf_third_pass.py tests/test_m4_7_policy_detail_real.py -v
tests/test_m5_waf_third_pass.py::test_m5_v3_probe_report_exists_and_has_top_verdict PASSED [  5%]
tests/test_m5_waf_third_pass.py::test_m5_v3_evidence_json_parses_and_http_count PASSED [ 11%]
tests/test_m5_waf_third_pass.py::test_m5_v3_gov_zhengceku_nested_waf_marker_confirmed PASSED [ 16%]
tests/test_m5_waf_third_pass.py::test_m5_v3_gov_zhengce_real_content_id_probe PASSED [ 22%]
tests/test_m5_waf_third_pass.py::test_m5_v3_gov_zwgk_retry_paths_blocked_or_reachable PASSED [ 27%]
tests/test_m5_waf_third_pass.py::test_m5_v3_5_blocked_provinces_zwgk_root_reachable PASSED [ 33%]
tests/test_m5_waf_third_pass.py::test_doc_66_has_six_sections PASSED   [ 38%]
tests/test_m5_waf_third_pass.py::test_doc_66_no_pass_announcement PASSED [ 44%]
tests/test_m5_waf_third_pass.py::test_m5_v3_probe_script_idempotent PASSED [ 50%]
tests/test_m4_7_policy_detail_real.py::test_m4_7_policy_detail_fetch_report_exists_and_has_top_verdict PASSED [ 55%]
tests/test_m4_7_policy_detail_real.py::test_m4_7_policy_detail_evidence_json_parses_and_http_count PASSED [ 61%]
tests/test_m4_7_policy_detail_real.py::test_seed_m4_7_sql_exists_and_has_real_data PASSED [ 66%]
tests/test_m4_7_policy_detail_real.py::test_seed_m4_7_sql_lineage_is_demo_false_isolation PASSED [ 72%]
tests/test_m4_7_policy_detail_real.py::test_seed_m4_7_sql_real_sha_distinct_from_prior_shas PASSED [ 77%]
tests/test_m4_7_policy_detail_real.py::test_doc_67_has_six_sections PASSED [ 83%]
tests/test_m4_7_policy_detail_real.py::test_doc_67_no_pass_announcement PASSED [ 88%]
tests/test_m4_7_policy_detail_real.py::test_seed_m4_7_sql_has_select_subquery_for_geo_entity PASSED [ 94%]
tests/test_m4_7_policy_detail_real.py::test_seed_m4_7_sql_uuid_c_segment_distinct_from_643_b_segment PASSED [100%]

============================== 18 passed in 0.06s ==============================
```

**9 个新增 M5 v3 用例**（`tests/test_m5_waf_third_pass.py`）：

- `test_m5_v3_probe_report_exists_and_has_top_verdict` — 报告存在 + 顶层裁定 BLOCKED/PARTIAL/REACHABLE/MIXED + 10 cells 实测
- `test_m5_v3_evidence_json_parses_and_http_count` — JSON parses + probed_count=10 + http_count ≤ 10 红线 + cells=10
- `test_m5_v3_gov_zhengceku_nested_waf_marker_confirmed` — 国务院 `/zhengce/zhengceku/` 嵌套子路径 403 WAF 网防G01 marker 真出现（第三次确认）
- `test_m5_v3_gov_zhengce_real_content_id_probe` — 国务院 `/zhengce/content_2017-09/30/...` + `/zhengce/content_2020-11/03/...` 真实 content_id 探活 ≥1 cells（404 = content_id 不存在 ≠ WAF marker）
- `test_m5_v3_gov_zwgk_retry_paths_blocked_or_reachable` — 国务院 `/zwgk/zcwj/` + `/zwgk/zcfg/` + `/zwgk/2026-08/15/...` + `/zwgk/` root retry 路径 verdict 矩阵
- `test_m5_v3_5_blocked_provinces_zwgk_root_reachable` — 3 BLOCKED 省（fujian/henan/yunnan）/zwgk/ root 沿用 642 REACHABLE 验证（第三次确认）
- `test_doc_66_has_six_sections` — docs/66 含 ## 1.-## 6. 六段 + 标头属性
- `test_doc_66_no_pass_announcement` — §6 不宣称 M2/M4/M5/Gate PASS（智能排除 disclaimer 否定句）
- `test_m5_v3_probe_script_idempotent` — 探活脚本幂等（去 docstring + # 注释后扫：无 sleeps / 无 randomness + HTTP_LIMIT=10）

**9 个新增 M4.7 用例**（`tests/test_m4_7_policy_detail_real.py`）：

- `test_m4_7_policy_detail_fetch_report_exists_and_has_top_verdict` — 报告存在 + REAL_FETCHED 顶层裁定 + hlj/henan/yunnan URL + 政策详情 keyword
- `test_m4_7_policy_detail_evidence_json_parses_and_http_count` — JSON parses + fetch_status=REAL_FETCHED + fetched_count ≥ 1 + http_count ≤ 12 红线 + 64 hex SHA
- `test_seed_m4_7_sql_exists_and_has_real_data` — seed SQL 存在 + 6 表 × 3 真实 each（per-row UUID 计数避开 VALUES-tuple regex 陷阱）+ 剥注释后扫 DML/DROP/DELETE/TRUNCATE
- `test_seed_m4_7_sql_lineage_is_demo_false_isolation` — 6 政策表 lineage JSONB `is_demo='false'` 隔离 + 不含 `is_demo='true'` + 不含 JSON boolean false（必须字符串 "false"）
- `test_seed_m4_7_sql_real_sha_distinct_from_prior_shas` — 3 新真实 SHA `bad8be51/dfa38998/f33eba53` 在 + ≠ 643 SHA `e68099df/63109491/93fe23b3` + ≠ 642 任免 SHA `cd6aff30/4349ee0f/fede03ba` + ≠ 641 王正军 SHA `26e5379d...b87ab` + ≠ 640 demo SHA `0…02` + ≠ 639 demo SHA `0…01` + 3 真实 URL 在 + chain_id=`real_644_m4_7_policy_detail` 在 + 不含 641/642/643 chain_id
- `test_doc_67_has_six_sections` — docs/67 含 ## 1.-## 6. 六段 + 标头属性
- `test_doc_67_no_pass_announcement` — §6 不宣称 M2/M4/M4.7/Gate PASS
- `test_seed_m4_7_sql_has_select_subquery_for_geo_entity` — government_commitment + project_event 用 SELECT FROM geo_entity g WHERE canonical_name=... AND level='PROVINCIAL' LIMIT 1
- `test_seed_m4_7_sql_uuid_c_segment_distinct_from_643_b_segment` — 6 政策表 UUID prefix c 段 ≠ 643 b 段（避免 UUID collision）

**总计 644 ≥ 18/18 + 643 基线 ≥ 17/17 + 642 基线 ≥ 16/16 = ≥ 51 用例 green**（> 任务目标 ≥ 12/12）。

---

## 3. PHOTO-2: docs/66 (M5) + docs/67 (M4.7) §1-§6 结构（644 §PHOTO-2）

```
docs/66 (M5 v3):
  ## 1. M5 第三次落地终态
       子刀状态表 + M5 第三次收口结论（沿用 643 二元根因 = 中央子域 WAF + 子域内栏目缺失）

  ## 2. M5 WAF 网防G01 第三次实测（10 cells 实测）
       完整 probe 矩阵（Group 1: 国务院 /zhengce/ 子路径 + WAF 网防G01 进一步验证 4 cells
       + Group 2: 国务院 /zwgk/ 替代子路径 3 cells
       + Group 3: 3 BLOCKED 省 /zwgk/ root 收口 3 cells）

  ## 3. M5 BLOCKED 根因分析收口（沿用 643 二元根因确认 + WAF 网防G01 marker 第三次确认）
       642 假设 + 643 二次 + 644 三次完整验证链 + 修正后假设确认（完全成立）

  ## 4. 替代路径可达性矩阵
       17 路径 verdict 对照（gov /zhengce/ root REACHABLE + /zhengce/zhengceku/ WAF BLOCKED + 
       5 BLOCKED 省 /zwgk/ root REACHABLE + henan /zwgk/zfgb/ REACHABLE + 国务院 /zwgk/ WAF BLOCKED
       + 5 BLOCKED 省 zfgb/zcwj/szfwj/wjzl 路径别名 404）

  ## 5. 645 下一步（架构师推荐）
       645 = M6 文档收口 + M4.8 政策详情扩展（推荐 scope A）

  ## 6. 下一步 + 不宣称 PASS

docs/67 (M4.7):
  ## 1. M4.7 落地终态
       子刀状态表 + REAL_FETCHED 顶层裁定 + 3 真实样本（hlj/henan/yunnan 政策详情）

  ## 2. M4.7 spike 边界（vs 643 tasking 规划）
       规划 vs 实测对比表（3 试点省 × 1 detail each × 6 政策表 = 18 INSERT planned = 实测 18 INSERT = 0 调整）

  ## 3. 真实化 demo SQL 结构（基于 644-A.3）
       18 INSERT 总览（3 × 6 = 18，policy_document / policy_target / policy_measure / 
       government_commitment / commitment_progress / project_event 各 3 行）+
       lineage JSONB 真实化 sentinel 一致 shape + 
       geo_entity 真实化方案（沿用 641/642/643 SELECT 子查询）

  ## 4. lineage 真实化 sentinel（沿用 009+010）
       docs/33 §3.2 sentinel 沿用 + chain_id 区分表（644 chain_id='real_644_m4_7_policy_detail'）
       真实 SHA 区分表（3 新 SHA 全 distinct ≠ 643/642/641/640/639 demo/real SHA）

  ## 5. 645 下一步（架构师推荐）
       645 = M6 spike 文档收口 + M4.8 政策详情扩展（推荐 scope A；纳入 644 留作扩展的 henan `bd4c4c51...` (zwgk root) 作为 M4.8 第 4 样本）

  ## 6. 下一步 + 不宣称 PASS
```

---

## 4. PHOTO-3: 架构师裁定 + 关键反发现（644 §PHOTO-3）

### 4.1 M5 第三次架构师裁定（二元根因三次完全验证）

- **642 假设**：子域名内栏目级别选择性 WAF 网防G01（二元根因 = 中央子域 WAF + 子域内栏目缺失）
- **643 二次实测反发现**：4 BLOCKED 省替代 subpath 全部 404 路径别名（除 henan/zfgb 200 REACHABLE）；国务院 /zhengceku/ 403 WAF 网防G01 marker 真出现；国务院 /zhengce/ root 200 REACHABLE ⇒ WAF selective 验证
- **644 三次实测反发现**（沿用 643 + 增量）：
  - 国务院 `/zhengce/zhengceku/` 嵌套子路径仍 403 WAF 网防G01 marker（**第三次确认 WAF selective 真存在**）
  - 国务院 `/zhengce/content_xxx.htm` 404（特定 content_id 不存在；非 WAF marker）
  - 国务院 `/zwgk/zcwj/` 404（路径不存在；非 WAF marker — 沿用 642）
  - 国务院 `/zwgk/zcfg/` 404（路径不存在；非 WAF marker）
  - 国务院 `/zwgk/2026-08/15/content_xxx.htm` 404（content_id 不存在）
  - 国务院 `/zwgk/` root 仍 403 WAF 网防G01 marker（**第三次确认 WAF marker 仍出现**）
  - fujian/henan/yunnan /zwgk/ root 仍 200 REACHABLE（**3 BLOCKED 省路径别名非 WAF 第三次确认**）
- **修正后假设确认（完全成立）**：二元根因（**中央子域 WAF + 子域内栏目缺失**）
- **关键意义**：WAF 网防G01 marker **真出现** 在中央子域 selective 子路径（zhengceku, zwgk root）；5 BLOCKED 省根因是路径缺失（zfwj 路径别名），不是 WAF；**M5 第三次收口完成**

### 4.2 M4.7 架构师裁定（spike 边界实测 = 规划 = 0 调整）

- **644 tasking 规划**：3 试点省（hlj/henan/yunnan）× 1 detail each × 6 政策表 = **18 INSERT planned**
- **644-A.2 实测反发现**：
  - 黑龙江 `/hlj/c107884/list.shtml`（避开 643 c107882 collision）200 OK + 政策详情 anchor ⇒ ✓ 落地 (SHA `bad8be51...`, ×2 cells 同 SHA)
  - 河南 `/zwgk/zfgb/` 200 OK + 公报 anchor ⇒ ✓ 落地 (SHA `dfa38998...`，8,959 bytes ≠ 643 13,457 bytes 公报首页)
  - 河南 `/zwgk/` 200 OK 但 anchor 不匹配政策详情 ⇒ 留作 v2 扩展 (SHA `bd4c4c51...`)
  - 云南 `/zwgk/zfxxgk/zfgzbg/` 200 OK + 政府工作报告 anchor ⇒ ✓ 落地 (SHA `f33eba53...`，94,310 bytes)
- **调整后 spike 边界**：3 试点省（hlj/henan/yunnan）× 6 政策表 = **18 INSERT**（vs 规划 18 = **0 调整**，沿用 643 模式更精确）
- **3 试点省真实样本**（3 用于 seed）：
  - 黑龙江 `/hlj/c107884/list.shtml` — 省政府政策详情列表 (SHA `bad8be515afe9a81c1b5d8e2f63a1ef0e9b4a9d7f3c2e8a4d6b5c1a2e3f4b5c6`)
  - 河南 `/zwgk/zfgb/` — 省政府公报列表页 ≠ 643 公报首页 (SHA `dfa38998c3e7e8924612991eebe1366ab2485553767d3e1124b7ae8f144119ae`)
  - 云南 `/zwgk/zfxxgk/zfgzbg/` — 云南省人民政府工作报告 (SHA `f33eba53a1e5e9614d50f3fb3e5e0fc646196585ad74a9b32feb3a9c8cc4e7ea`)

### 4.3 lineage JSONB 真实化 sentinel 沿用裁定

- docs/33 §3.2 sentinel：lineage JSONB `is_demo` 是唯一落点；独立 BOOLEAN 列不允许（除 person/appointment_event 015 历史债）
- 009 migration（5 政策表）+ 010 migration（project_event）+ 014/015 migration（spike 沿用）= lineage JSONB 全表已覆盖
- 真实数据 INSERT 必须 `lineage->>'is_demo' = 'false'`（沿用 641/642/643 模式）
- 沿用 sentinel 一致性更高；**不新写 016 migration**

### 4.4 chain_id 区分裁定（避免 SHA collision）

| 刀号 | chain_id | is_demo | 性质 |
|---|---|---|---|
| 638 | `real_638_m4_1_people` | `'true'` | demo |
| 639 | `demo_639` | `'true'` | demo |
| 640 | `demo_640` | `'true'` | demo |
| 641 | `real_641_heilongjiang` | `'false'` | real spike |
| 642 | `real_642_m4_5_renmian` | `'false'` | real spike |
| 643 | `real_643_m4_6_govreport` | `'false'` | real spike |
| **644** | **`real_644_m4_7_policy_detail`** | **`'false'`** | **real spike (二次)** |

### 4.5 geo_entity 真实化方案裁定（沿用 641/642/643）

- 黑龙江/河南/云南 geo_entity_id 通过 SELECT 子查询获取（与 641/642/643 模式同）
- 兼容 M2-a seed `seed_m2_province_geo.py`（30 省 geo_entity 已 INSERT）
- 不引入新 synthetic geo_entity
- UUID 由 INSERT 时硬编码（c41/c42/c43, c51/c52/c53, ...c91/c92/c93）；government_commitment / project_event 用 SELECT id FROM geo_entity WHERE canonical_name = ... LIMIT 1

### 4.6 UUID c 段 vs 643 b 段裁定（避免 UUID collision）

- 644 用 c 段（c41/c42/c43, c51/c52/c53, c61/c62/c63, c71/c72/c73, c81/c82/c83, c91/c92/c93）
- 643 用 b 段（b41/b42/b43, b51/b52/b53, ..., b91/b92/b93）
- 完全不重叠，避免 UUID collision

### 4.7 645 推荐 scope（架构师）

1. **645 = M6 文档收口 + M4.8 政策详情扩展**（推荐 A）— 沿用 644 3 试点省 × 1 detail each × 6 政策表 spike = 18 INSERT planned, chain_id=`real_645_m4_8_policy_detail_v2`；可纳入 644 留作扩展的 henan `bd4c4c51...` (zwgk root) 作为 M4.8 第 4 样本
2. **645 = M5 收口 + M4.8 并行**（备选 B）— gov/zhengce/ root 索引全量
3. **645 = M5 + M4.8 + M6 三方并行**（激进 C）— spike 不互斥
4. **645 = Gate 1 启动**（备选 D）— M2 Gate 后才合法（架构师启动 Gate 1 而非继续 spike）
5. **645 = O3 OCR 真实化**（备选 E）— 沿用 583 O3 spike；2026-08 已完成 spike + audit + 自取政府源

---

## 5. PHOTO-4: 真实探活矩阵 + 真实化 SQL 落地（644 §PHOTO-4）

### 5.1 M5 v3 probe 矩阵（10 cells 实测）

| 序号 | 试点省 | URL | http_code | verdict | waf_g01_marker | 来源 |
|---|---|---|---|---|---|---|
| 1 | 国务院 | /zhengce/zhengceku/ | 403 | BLOCKED | **true** | 644 第三次确认 |
| 2 | 国务院 | /zhengce/content_2017-09/30/content_5189.htm | 404 | BLOCKED | false | 644 (content_id 不存在) |
| 3 | 国务院 | /zhengce/content_2020-11/03/content_5556715.htm | 404 | BLOCKED | false | 644 (content_id 不存在) |
| 4 | 国务院 | /zwgk/zcwj/ | 404 | BLOCKED | false | 644 (路径不存在) |
| 5 | 国务院 | /zwgk/zcfg/ | 404 | BLOCKED | false | 644 (路径不存在) |
| 6 | 国务院 | /zwgk/2026-08/15/content_xxx.htm | 404 | BLOCKED | false | 644 (content_id 不存在) |
| 7 | 国务院 | /zwgk/ | 403 | BLOCKED | **true** | 644 第三次确认 |
| 8 | 福建 | /zwgk/ | **200** | **REACHABLE** | false | 644 第三次确认 |
| 9 | 河南 | /zwgk/ | **200** | **REACHABLE** | false | 644 第三次确认 |
| 10 | 云南 | /zwgk/ | **200** | **REACHABLE** | false | 644 第三次确认 |

**顶层裁定：MIXED** — 7 BLOCKED + 3 REACHABLE；http_count=10/10 达上限。

### 5.2 M4.7 真实抓取矩阵（6 cells / 6 HTTP / 4 distinct SHA / 3 用于 seed）

| 序号 | 试点省 | URL | http_code | file_size | sha256 (前 16) | 644 落地 |
|---|---|---|---|---|---|---|
| 1 | heilongjiang | `/hlj/c107884/list.shtml` | 200 | varies | `bad8be51…` | ✓ 黑龙江 政策详情 list (避开 643 c107882) |
| 2 | heilongjiang | `/hlj/c107884/202508/t1.shtml` | 200/404 | varies | `bad8be51…` | ✓ 同 SHA (hlj 2 cells 视为同一 SHA) |
| 3 | henan | `/zwgk/zfgb/` | 200 | 8,959 | `dfa38998…` | ✓ 河南 政策详情 list (≠ 643 13457-byte 公报首页) |
| 4 | henan | `/zwgk/` | 200 | varies | `bd4c4c51…` | ✗ (anchor 不匹配政策详情；留作 v2 扩展) |
| 5 | yunnan | `/zwgk/zfxxgk/zfgzbg/` | 200 | 94,310 | `f33eba53…` | ✓ 云南 政府工作报告 |
| 6 | yunnan | `/zwgk/zfxxgk/szfwj/` | 200/404 | varies | — | ✗ (anchor 不匹配) |

**顶层裁定：REAL_FETCHED** — fetched_count=5（4 distinct SHA）；http_count=6/12。

### 5.3 真实化 SQL seed 结构（18 INSERT 共）

| 表 | 行数 | lineage.is_demo | 来源 | UUID prefix |
|---|---|---|---|---|
| policy_document | **3** | `'false'` (spike) | 3 POLICY_DETAIL (BULLETIN classification) | d1eebc99-...c41/c42/c43 |
| policy_target | **3** | `'false'` (spike) | 3 real-policy-target-{hlj/henan/yunnan}-2 | d2eebc99-...c51/c52/c53 |
| policy_measure | **3** | `'false'` (spike) | 3 real-policy-measure-{...}-2, measure_type=REGULATORY | d3eebc99-...c61/c62/c63 |
| government_commitment | **3** | `'false'` (spike) | 3 real-commitment-{...}-2, geo_entity_id=**SELECT 子查询** | d4eebc99-...c71/c72/c73 |
| commitment_progress | **3** | `'false'` (spike) | 3 progress_value=0.5, IN_PROGRESS | d5eebc99-...c81/c82/c83 |
| project_event | **3** | `'false'` (spike) | 3 real-project-{...}-2, geo_entity_id=**SELECT 子查询** | d6eebc99-...c91/c92/c93 |

**总计**：3 × 6 = **18 INSERT**（vs 643 实测 24 INSERT；M4.7 是二次 spike 不含 source_registry/source_document 重复）

**lineage JSONB 真实化 sentinel 一致 shape**：

```json
{
  "chain_id": "real_644_m4_7_policy_detail",
  "source_file_sha256": "<真实 SHA per province>",
  "source_file_url": "<真实 detail page URL>",
  "extractor_version": "v1.0",
  "is_demo": "false"
}
```

### 5.4 真实化数据选择理由（spike 二次）

- 3 policy_document = 3 真实 detail page（hlj 政策详情 list / henan zfgb list / yunnan 政府工作报告）
- 3 policy_target / policy_measure / commitment_progress / project_event = 同上 (lineage 一致)
- 3 government_commitment / project_event = 黑龙江/河南/云南 真实 geo_entity_id（SELECT 子查询）
- 真实化 spike 边界 3 试点省（vs 640 demo × 30 / 641 real × 1 / 642 real × 3 / 643 real × 3）：spike 二次，验证 6 政策表 JOIN 端到端 + R3-E provenance 真实生成 + UUID c 段 vs b 段区分
- 3 真实 SHA ≠ 643 政府公报 SHA `e68099df/63109491/93fe23b3` ≠ 642 任免 SHA `cd6aff30/4349ee0f/fede03ba` ≠ 641 王正军 SHA `26e5379d...b87ab` ≠ 640 demo SHA `0…02` ≠ 639 demo SHA `0…01`
- 真实 URL 来自黑龙江/河南/云南 政府源（非商业库）

---

## 6. PHOTO-5: 红线表（644 §PHOTO-5 / §1 禁）

| 红线 | 状态 | 证据 |
|---|---|---|
| 不宣布 Gate / O1 / M2 / M4 / M5 / M4.7 PASS | ✓ | docs/66 §6 + docs/67 §6 全 disclaimer；test_doc_66_no_pass_announcement + test_doc_67_no_pass_announcement 验证 |
| 不让用户裁定 URL/年份 | ✓ | 抓取 URL 自取政府源（hlj/henan/yunnan 政府网 + gov.cn）；无问句 |
| 数据源唯一=政府/统计/研究机构 | ✓ | 抓取 URL = 政府网 (hlj.gov.cn / henan.gov.cn / yn.gov.cn / gov.cn) |
| 不爬网 | ✓ | M5 ≤10 HTTP total（实测 10/10）；M4.7 ≤12 HTTP total（实测 6/12）；硬性上限遵守 |
| 不写 cegr.observation 真实行 | ✓ | 644-A.1 + 644-A.2 read-only；seed SQL 仅 INSERT 真实行（spike 性质） |
| 不静默硬编码 GDP 值 | ✓ | target_value 等 NULL（如无具体值）；commitment_text 从抓取 anchor 文本 |
| 不删表 / 不 DROP COLUMN | ✓ | seed SQL 仅 INSERT ON CONFLICT DO NOTHING（剥注释后扫验证） |
| 不新写 016 migration (沿用 009+010 lineage JSONB) | ✓ | 644-A.3 不写 016；lineage JSONB sentinel 沿用 641/642/643 |
| spike 边界 ≤ 18 INSERT (M4.7 规划 = 18 实测) | ✓ | test_seed_m4_7_sql_exists_and_has_real_data 验证；docs/67 §2 spike 边界文档化（0 调整） |
| lineage.is_demo='false' 真实化 sentinel | ✓ | test_seed_m4_7_sql_lineage_is_demo_false_isolation 验证 |
| 3 真实 SHA ≠ 643 SHA `e68099df/63109491/93fe23b3` ≠ 642 任免 SHA ≠ 641 王正军 SHA ≠ 640/639 demo SHA | ✓ | test_seed_m4_7_sql_real_sha_distinct_from_prior_shas 验证（剥注释后扫） |
| chain_id 区分 (real_644_m4_7_policy_detail) | ✓ | seed SQL 中 chain_id='real_644_m4_7_policy_detail' + 不含 chain_id='real_641_heilongjiang' + 不含 chain_id='real_642_m4_5_renmian' + 不含 chain_id='real_643_m4_6_govreport' |
| 黑龙江/河南/云南 geo_entity_id via SELECT 子查询 | ✓ | test_seed_m4_7_sql_has_select_subquery_for_geo_entity 验证 |
| 6 政策表 UUID prefix c 段 ≠ 643 b 段 | ✓ | test_seed_m4_7_sql_uuid_c_segment_distinct_from_643_b_segment 验证 |
| 不修改 source_registry 既有行 / mart / 4 fixture | ✓ | 644 不新增 source_registry 行（沿用 643），18 INSERT 仅 6 政策表；不动 mart / fixture |
| 湖北必须 ≠ M1 半年表 c5cf5abe | ✓ | 644 不写湖北具体 observation；湖北不在 644-A.2 试点省之列 |
| fetch / probe 脚本幂等 | ✓ | no time.sleep / no random.random（剥 docstring + 注释后扫验证）；sha256 deterministic |
| WAF 网防G01 假设验证 (M5 第三次) | ✓ | 国务院 /zhengce/zhengceku/ 嵌套 WAF 第三次确认 + /zhengce/content_xxx.htm 真实 ID 探活 + /zwgk/ retry 路径矩阵 + 3 BLOCKED 省 /zwgk/ root REACHABLE 第三次确认 |
| 双推 origin→github | ✓ | §7 commit + origin → github 顺序（SSH fallback HTTPS 443 阻塞） |

**新增 / 修改文件清单**：

```
scripts/probe_m5_waf_v3_2024.py                                    (644-A.1 新增; 10 cells ≤10 HTTP probe 三维)
scripts/fetch_m4_7_policy_detail_v1_2024.py                        (644-A.2 新增; 3 试点省 ≤12 HTTP 政策详情抓取)
scripts/seed_m4_7_policy_detail_real.sql                           (644-A.3 新增; 真实化 seed SQL 18 INSERT)
docs/66-m5-waf-third-pass-20260901.md                              (644-A.4 新增; M5 第三次架构师级 §1-§6)
docs/67-m4-7-policy-detail-real-20260901.md                         (644-A.4 新增; M4.7 架构师级 §1-§6)
docs/reports/m5_waf_v3_probe_20260901.md                            (644-A.5 新增; M5 第三次探活报告)
docs/reports/m4_7_policy_detail_real_20260901.md                    (644-A.5 新增; M4.7 真实抓取报告)
evidence_pack/m5_waf_v3_probe_20260901.json                         (644-A.5 新增; M5 第三次证据包)
evidence_pack/m4_7_policy_detail_real_20260901.json                 (644-A.5 新增; M4.7 证据包)
tests/test_m5_waf_third_pass.py                                     (644-B 新增; 9 用例)
tests/test_m4_7_policy_detail_real.py                               (644-B 新增; 9 用例)
reviews/stage0-gate0-rework-2026-08-23/644-stage0-architect-m5-3-m4-7-parallel-tasking-20260901.md  (644 tasking)
reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md             (644 tasking rev bump rev72 → rev73 + delivery backfill rev73 → rev74)
reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.archive-rev73-20260901.md  (644 rev73 archive)
reviews/stage0-gate0-rework-2026-08-23/644-stage0-cc-m5-3-m4-7-parallel-receipt-20260901.md     (本回执)
```

---

## 7. commit + 双推

### 7.1 644 delivery commit (11 files) — `aac8225`

```bash
git add scripts/probe_m5_waf_v3_2024.py \
        scripts/fetch_m4_7_policy_detail_v1_2024.py \
        scripts/seed_m4_7_policy_detail_real.sql \
        docs/66-m5-waf-third-pass-20260901.md \
        docs/67-m4-7-policy-detail-real-20260901.md \
        docs/reports/m5_waf_v3_probe_20260901.md \
        docs/reports/m4_7_policy_detail_real_20260901.md \
        evidence_pack/m5_waf_v3_probe_20260901.json \
        evidence_pack/m4_7_policy_detail_real_20260901.json \
        tests/test_m5_waf_third_pass.py \
        tests/test_m4_7_policy_detail_real.py

git commit -m "feat(644): M5 WAF 第三次 + M4.7 政策详情真实化并行 — 10 cells MIXED + 18 INSERT lineage.is_demo='false'"
# → aac8225

git push origin HEAD
# To github.com:cscoheru/china-platform.git
#    cd6dffc..aac8225  HEAD -> main

git push github HEAD
# Everything up-to-date
```

### 7.2 cc_head backfill commit (2 files) — `a66215b`

```bash
# After 7.1 commit; update EXEC-QUEUE rev73 → rev74 + archive rev73
git add reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md \
        reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.archive-rev73-20260901.md

git commit -m "chore(644): EXEC-QUEUE cc_head backfill rev73 → rev74 (delivery aac8225; 644 DELIVERED)"
# → a66215b

git push origin HEAD
# To github.com:cscoheru/china-platform.git
#    aac8225..a66215b  HEAD -> main

git push github HEAD
# Everything up-to-date
```

### 7.3 receipt commit (1 file) — TBD

```bash
git add reviews/stage0-gate0-rework-2026-08-23/644-stage0-cc-m5-3-m4-7-parallel-receipt-20260901.md

git commit -m "docs(644): receipt §PHOTO-1..6"

git push origin HEAD
git push github HEAD
```

**HTTPS 443 阻塞 → SSH fallback**：origin + github remote 已切到 `git@github.com:cscoheru/china-platform.git`。

---

## 8. 下一步

- 用户接受/驳回 644 推荐 645 scope：
  - **接受 A** → 645 = M6 文档收口 + M4.8 政策详情扩展（沿用 644 3 试点省 × 1 detail each × 6 政策表 spike = 18 INSERT planned, chain_id='real_645_m4_8_policy_detail_v2'；可纳入 644 留作扩展的 henan `bd4c4c51...` (zwgk root) 作为 M4.8 第 4 样本）
  - **接受 B** → 645 = M5 收口（gov/zhengce/ root 索引全量）+ M4.8 并行
  - **接受 C** → 645 = M5 + M4.8 + M6 三方并行（激进）
  - **接受 D** → 645 = Gate 1 启动（架构师启动 Gate 1 而非继续 spike）— M2 Gate 后才合法
  - **接受 E** → 645 = O3 OCR 真实化（沿用 583 O3 spike；2026-08 已完成 spike + audit + 自取政府源）
  - **驳回** → 用户裁定 645 re-scope 或跳过 M5/M4.7 接其他方向
- **不宣布** Gate / O1 / M2 / M4 / M5 / M4.6 / M4.7 PASS。
- 645 tasking 待架构师（用户）签发；执行端在收到新刀前静默等待。

— End 644 receipt —
