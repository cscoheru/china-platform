# 640 — M4.3 政策项目 demo（执行端回执）

> **类型**: 执行端 (CC) 回执 · knife 640 落地报告
> **日期**: 2026-09-01
> **依据**: `reviews/stage0-gate0-rework-2026-08-23/640-stage0-architect-m4-3-policy-demo-tasking-20260901.md`
> **前置**: 639 DELIVERED (cc_head `1fca08e` + receipt `11778db`);用户接受 M4.3 scope (lineage JSONB sentinel + 6 REACHABLE 试点省政策承载路径独立 probe + 6 表 × 3 demo each)
> **阶段**: M4.3 落地（政策源二次探活 + 6 表 demo SQL + docs/60；架构师级 deliverable；非用户问句）

---

## 0. 一句话

640 落地 5 件：**(A1)** `scripts/probe_policy_v1_2024.py` 12/13 实测 = **REACHABLE 2 / PARTIAL 1 / BLOCKED 9**（关键反发现：6 REACHABLE 任免源（黑龙江/福建/河南/广东/贵州/云南）中仅 1 省（黑龙江）政策承载路径可达；推翻"任免源 ≈ 政策源"假设）；**(A2)** `scripts/seed_m4_3_policy_demo.sql` 政策项目 demo 最小实现（1 source_registry + 1 source_document（demo SHA 0…02，与 639 SHA 0…01 区分）+ 3 demo geo_entity（synthetic PROVINCE，不绑定真实省份）+ 3 policy_document + 3 policy_target + 3 policy_measure + 3 government_commitment + 3 commitment_progress + 3 project_event；6 表 × 3 demo 全部 `lineage->>'is_demo' = 'true'` 隔离，沿用 docs/33 §3.2 sentinel，**不新写 016 migration**）；**(A3)** `docs/60-m4-3-policy-demo-20260901.md` §1-§6 架构师级审查 + **架构师推荐 641 = M4.4 黑龙江政策真实化 spike**（单 REACHABLE 试点省，不蔓延 WAF 探活）；**(B)** `tests/test_m4_3_policy_demo.py` 7 用例；**全套 M2 + 637 + 638 + 639 + 640 = 71/71 pytest green**；不宣布 Gate / O1 / M2 / M4 PASS；不向用户提任何 URL 裁定事项。

---

## 1. 交付映射（640-A → 640-C）

| 子刀 | 文件 | 状态 | 说明 |
|---|---|---|---|
| 640-A.1 | `scripts/probe_policy_v1_2024.py` + `_probe_http_helpers.py POLICY_MARKER_RE` | DONE | 政策源二次探活 12/13 cell；REACHABLE 2 / PARTIAL 1 / BLOCKED 9 |
| 640-A.2 | `scripts/seed_m4_3_policy_demo.sql` | DONE | 1 source_registry + 1 source_document（demo SHA `0…02`）+ 3 demo geo_entity（synthetic PROVINCE）+ 3 policy_document + 3 policy_target + 3 policy_measure + 3 government_commitment + 3 commitment_progress + 3 project_event；6 政策表 × 3 demo 全部 `lineage.is_demo='true'` 隔离 |
| 640-A.3 | `docs/60-m4-3-policy-demo-20260901.md` | DONE | §1-§6 架构师级审查 + 641 推荐 |
| 640-A.5 | `docs/reports/m4_3_policy_v1_probe_20260901.md` + `evidence_pack/m4_3_policy_v1_probe_20260901.json` | DONE | probe 报告（BLOCKED 9/12 = 75% 顶层裁定）+ 证据包 |
| 640-B | `tests/test_m4_3_policy_demo.py` | DONE | 7 用例：报告存在+顶层裁定 / evidence JSON parses / seed SQL 6表×3 demo + 3 demo geo_entity / seed lineage is_demo 隔离 / seed demo SHA 0…02 区分 / docs/60 六段 / docs/60 不宣称 PASS |
| 640-C | 本回执 + commit + 双推 | DONE | §PHOTO-1..6 + commit + origin→github |

---

## 2. PHOTO-1: pytest 一行（640 §PHOTO-1 须绿）

```
$ STAGE0_SKIP_SCHEMA_APPLY=1 PYTHONPATH=backend/src python3 -m pytest \
    tests/test_m2_crosscheck.py tests/test_m2_b_first_batch.py \
    tests/test_m2_province_geo_seed.py tests/test_m2_frontend_page.py \
    tests/test_m2_backfill_feasibility.py tests/test_m3_launch_conditions_review.py \
    tests/test_m4_1_people_probe.py tests/test_m4_2_renmian_demo.py \
    tests/test_m4_3_policy_demo.py
tests/test_m2_crosscheck.py ......                                       [  8%]
tests/test_m2_b_first_batch.py ........                                  [ 19%]
tests/test_m2_province_geo_seed.py ........                              [ 30%]
tests/test_m2_frontend_page.py ..........                                [ 45%]
tests/test_m2_backfill_feasibility.py ........                           [ 56%]
tests/test_m3_launch_conditions_review.py .........                      [ 69%]
tests/test_m4_1_people_probe.py ........                                 [ 80%]
tests/test_m4_2_renmian_demo.py .......                                  [ 90%]
tests/test_m4_3_policy_demo.py .......                                   [100%]

============================== 71 passed in 1.01s ==============================
```

**7 个新增 M4.3 用例**（`tests/test_m4_3_policy_demo.py`）：

- `test_policy_v1_probe_report_exists_and_has_top_verdict` — 报告存在 + 顶层裁定 REACHABLE/BLOCKED/MIXED + 12 cell + 实体逐项 + 中央 vs 试点省分布 + 黑龙江 REACHABLE
- `test_policy_v1_evidence_json_parses` — JSON parses + summary/cells/probed_count + by_class_verdict + probed_cells == 12 + 试点省 REACHABLE ≥ 1 (实际 2)
- `test_seed_m4_3_sql_exists_and_has_demo_data` — seed SQL 存在 + 6 政策表 × 3 demo each (policy_document + policy_target + policy_measure + government_commitment + commitment_progress + project_event) + 3 demo geo_entity (synthetic PROVINCE) + 不含 DML/DROP/DELETE/TRUNCATE (剥注释后扫)
- `test_seed_m4_3_sql_lineage_is_demo_isolation` — 6 政策表每块 `INSERT INTO ... VALUES` 含 `is_demo='true'` ≥ 3 次 + 不含 `is_demo='false'`
- `test_seed_m4_3_sql_demo_sha_distinct_from_renmian` — demo SHA `0…02` 在 source_document INSERT + 639 SHA `0…01` 不在 seed SQL + 6 表 demo source_id → demo SD UUID ≥ 10 (1 policy_document + 3 + 3 + 3)
- `test_doc_60_has_six_sections` — docs/60 含 ## 1.-## 6. 六段 + 标头 60/2026-09-01/640
- `test_doc_60_no_pass_announcement` — §6 不宣称 M4/M2/Gate PASS（智能排除 disclaimer 否定句）

**M2 + 637 + 638 + 639 回归 64 用例**：全 green。

---

## 3. PHOTO-2: docs/60 §1-§6 结构（640 §PHOTO-2）

```
## 1. M4.3 落地终态
   5 sub-knife 状态表 + M4.3 收口结论 (lineage JSONB sentinel + demo SHA 0…02)

## 2. 政策源 二次 probe 数据（基于 640-A.1）
   总分布: REACHABLE 2 / PARTIAL 1 / BLOCKED 9 (12/12)
   关键反发现: 6 REACHABLE 任免源中仅 1 省 (黑龙江) 政策 REACHABLE
   REACHABLE 2: 黑龙江政策文件 (/zwgk/zfwj/) + 黑龙江政府公报 (/zwgk/zfgb/)
   PARTIAL 1: 中央纪委领导/制度 (ccdi /ldwd/) — 200 + 无政策 marker
   BLOCKED 9: 福建/河南/广东/贵州/云南 5 省 /zwgk/zfwj/ 全 404 + 国务院 /zhengce/zhengceku/ 403 WAF
   638/639 vs 640 WAF 假设修正表

## 3. demo SQL 结构（基于 640-A.2）
   1 source_registry + 1 source_document (demo SHA 0…02) +
   3 demo geo_entity (synthetic PROVINCE) +
   3 policy_document + 3 policy_target + 3 policy_measure +
   3 government_commitment + 3 commitment_progress + 3 project_event
   lineage JSONB is_demo='true' 隔离原则 (docs/33 §3.2 sentinel)
   6 政策表 × 3 demo + 3 demo geo_entity = 21 demo 行

## 4. 009+010 schema 落地（基于 638-A.3 lineage 复用）
   6 政策表 lineage JSONB 加列已完成 (009 + 010)
   demo SHA 0…02 与任免 SHA 0…01 区分
   不新写 016 migration 架构师裁定 (3 理由)

## 5. 641 下一步
   641 = M4.4 黑龙江政策真实化 spike (推荐; 单 REACHABLE 试点省)
   641 = M5 WAF spike / M4.4 任免真实化 / spike 16 migration (不推荐理由)
   沿用 lineage sentinel 基础设施

## 6. 下一步 (641 = M4.4 黑龙江政策真实化 spike)
   架构师推荐 641 scope
   不宣称任何 M2/M4/Gate PASS
```

---

## 4. PHOTO-3: 架构师裁定 + 关键反发现（640 §PHOTO-3）

**裁定（docs/60 §2.1）：**

638-A.2 任免公告 PARTIAL 1 / BLOCKED 2 = 仅 3 URL 探活。639-A.1 二次探活发现 **6 REACHABLE 试点省任免栏目** (黑龙江/福建/河南/广东/贵州/云南)。640-A.1 政策源二次探活进一步发现:

- **关键反发现（架构师裁定）**: 6 REACHABLE 任免源 (黑龙江/福建/河南/广东/贵州/云南) 中**仅 1 省** (黑龙江) 的政策承载路径 `/zwgk/zfwj/` + `/zwgk/zfgb/` 真正可达。其他 5 省 `/zwgk/zfwj/` + `/zwgk/zfgb/` **全 404 (路径不存在而非 WAF,因黑龙江同路径可达)**。
- **REACHABLE 2**: 黑龙江政策文件 (`/zwgk/zfwj/`) + 黑龙江政府公报 (`/zwgk/zfgb/`)
- **PARTIAL 1**: 中央纪委 /ldwd/ — 200 + 无政策 marker (栏目是领导/制度不是政策)
- **BLOCKED 9**:
  - 5 省 `/zwgk/zfwj/`: 福建/河南/广东/贵州/云南 (404)
  - 1 省 `/zwgk/zfgb/`: 福建 (404)
  - 2 省多路径: 河南 (zfwj 404 + ghjh 404) + 广东 (zfwj 404 + zfgb 404)
  - 1 中央: 国务院 /zhengce/zhengceku/ (403 WAF)

**架构师裁定：**

- **WAF 假设修正延续**: 638 假设 `tjj.*` 子域 100% 阻断 + `www.*.gov.cn/` 部分可达;639 证实 `www.*.gov.cn/zwgk/` 任免承载路径在 6 试点省直接命中;640 进一步修正: **任免 `/zwgk/` ≠ 政策 `/zwgk/zfwj/` `/zwgk/zfgb/` `/zwgk/ghjh/`**;子域内**栏目级别**也有选择性 WAF。
- **政策 demo 不绑定具体省份**: 反发现意味 1 省 (黑龙江) 不足以做"省-政策"映射 demo。架构师裁: demo 用 3 个 synthetic `M4.3 demo province N` geo_entity 替代真实省份(沿用 639 demo-person-1..5 合成模式);`government_commitment.geo_entity_id` + `project_event.geo_entity_id` 各指向 1 个 demo geo_entity。
- **不新写 016 migration**: docs/33 §3.2 sentinel 规定 lineage JSONB 是 is_demo 唯一落点;009+010 已在 6 政策表加 `lineage JSONB` + GIN 索引,功能等同独立 BOOLEAN 列;沿用 sentinel 一致性更高;015 偏离 sentinel 是历史债(因 person/appointment_event 表 009 不在 5+1 政策表之列)。
- **6 REACHABLE 任免源 ≠ 政策源 (架构师裁定延续)**: M4.4 任免 demo 真实化 (639 推荐未实现) 不替代 M4.4 政策真实化;两者走两条 spike 路径。

**641 推荐 scope：**

1. **641 = M4.4 黑龙江政策真实化 spike** (推荐) — 单 REACHABLE 试点省;沿用 lineage JSONB sentinel;验证 6 表 JOIN 端到端 + R3-E provenance 真实数据生成
2. 641 = M5 WAF 进一步探活 (不推荐; 不解决 5 BLOCKED 省根因)
3. 641 = M4.4 任免真实化 (调整选项; 与 640 政策 demo 无关)
4. 641 = spike 16 migration (不推荐; lineage GIN 已足够过滤,加列易回退难)

---

## 5. PHOTO-4: probe 矩阵 + demo SQL 落地（640 §PHOTO-4）

### 5.1 政策源二次 probe 矩阵（12 cell 实测）

| verdict | 实体 | http_code 分布 |
|---|---|---|
| REACHABLE 2 | 黑龙江政策文件 + 黑龙江政府公报 | 200 × 2 |
| PARTIAL 1 | 中央纪委领导/制度 (ccdi /ldwd/) | 200 × 1 |
| BLOCKED 9 | 福建政策文件 + 福建政府公报 + 河南政策文件 + 河南规划计划 + 广东政策文件 + 广东政府公报 + 贵州政策文件 + 云南政策文件 + 国务院政策库 (zhengceku) | 404 × 8 + 403 × 1 |

### 5.2 demo SQL seed 结构

| 表 | 行数 | demo 隔离 | 来源 |
|---|---|---|---|
| source_registry | 1 | — (synthetic) | domain=demo.placeholder / enabled=FALSE |
| source_document | 1 | file_hash_sha256=`0…02` | source_level=S4 / verification_status=UNVERIFIED |
| geo_entity (synthetic PROVINCE) | 3 | — (canonical_name 含 "demo") | M4.3 demo province 1/2/3 (不绑定真实省) |
| policy_document | 3 | `lineage.is_demo='true'` | REGULATION + NOTICE + PLAN (3 分类) |
| policy_target | 3 | `lineage.is_demo='true'` | demo-policy-target-1/2/3 |
| policy_measure | 3 | `lineage.is_demo='true'` | INCENTIVE + REGULATORY + INVESTMENT (3 措施类型) |
| government_commitment | 3 | `lineage.is_demo='true'` | PROPOSED + IN_PROGRESS + FULFILLED (3 status) |
| commitment_progress | 3 | `lineage.is_demo='true'` | demo progress 50% / mid-year / 100% |
| project_event | 3 | `lineage.is_demo='true'` | ANNOUNCED + IN_PROGRESS + COMPLETED (3 status) |

**lineage JSONB 隔离原则（docs/33 §3.2 sentinel）**:
- 6 政策表 × 3 demo 全部显式 `lineage->>'is_demo' = 'true'` (JSONB sentinel)
- demo 数据**只能** SELECT 通过 `WHERE lineage->>'is_demo' = 'true'` 过滤
- 真实数据 INSERT 必须 `lineage->>'is_demo' = 'false'` 或 NULL
- 009+010 已建 `idx_*_lineage_gin` GIN 索引(jsonb_path_ops),快速过滤

### 5.3 demo 数据选择理由

- 3 policy_document 覆盖 REGULATION/NOTICE/PLAN 三类,演示 `classification` 枚举 + `doc_type` 多样性
- 3 policy_target 全部 `target_year` 2024/2025/2026 递增,演示 `target_value` 数值差异
- 3 policy_measure 覆盖 INCENTIVE/REGULATORY/INVESTMENT 三类措施类型
- 3 government_commitment 覆盖 PROPOSED/IN_PROGRESS/FULFILLED 三种状态
- 3 commitment_progress 演示 `progress_value` 0.5 / 1.0 / 3.0 三个层级(50% / mid-year / 100% 履行)
- 3 project_event 覆盖 ANNOUNCED/IN_PROGRESS/COMPLETED 三种状态 + INFRASTRUCTURE/ENERGY/MANUFACTURING 三种 project_type

---

## 6. PHOTO-5: 红线表（640 §PHOTO-5 / §1 禁）

| 红线 | 状态 | 证据 |
|---|---|---|
| 不宣布 Gate / O1 / M2 / M4 PASS | ✓ | docs/60 §6 + §1 全 disclaimer;test_doc_60_no_pass_announcement 验证 |
| 不让用户裁定 URL/年份 | ✓ | probe targets 全部 gov.cn 政府源;无问句 |
| 数据源唯一=政府/统计/研究机构 | ✓ | ccdi.gov.cn / www.gov.cn / 6 www.\*.gov.cn 政策承载路径 |
| 不爬网 | ✓ | probe 只探可达性,不抓内容入库 |
| 不写 cegr.observation | ✓ | probe read-only + seed SQL 仅 INSERT demo 行 |
| 不静默硬编码 GDP 值 | ✓ | demo 表无 GDP 字段;`target_value=1.0/2.0/3.0 百分比` 为 demo 数值 |
| 不删表 / 不 DROP COLUMN | ✓ | seed SQL 仅 INSERT ON CONFLICT DO NOTHING (剥注释后扫验证) |
| lineage JSONB is_demo 隔离 | ✓ | 6 政策表 × 3 demo 全部 `lineage.is_demo='true'` (line 47-58 of policy_document 等) |
| demo ≤ 3 条 each 政策表 | ✓ | test_seed_m4_3_sql_exists_and_has_demo_data 验证 |
| demo 有 source_document_id 跳回 SHA 0…02 | ✓ | demo SHA `0…02` + 6 表 demo source_id → demo SD UUID ≥ 10 |
| 不改 source_registry / mart / 4 fixture | ✓ | 640 新增 1 synthetic source_registry 行 (enabled=FALSE),不动既有行 / mart / fixture |
| 湖北必须 ≠ M1 半年表 c5cf5abe | ✓ | 640 不写湖北具体 observation;湖北在 639 BLOCKED 13 试点省之列 (无 probe 数据) |
| 不新写 016 migration (沿用 009+010 lineage JSONB) | ✓ | 640-A.2 不写 016;test_seed_m4_3_sql_lineage_is_demo_isolation 验证 lineage JSONB sentinel |
| demo SHA 0…02 与 639 SHA 0…01 区分 | ✓ | test_seed_m4_3_sql_demo_sha_distinct_from_renmian 验证 (0…02 在;0…01 不在) |
| probe 脚本幂等 | ✓ | no time.sleep / no random in classify / no DML |
| 双推 origin→github | ✓ | §7 commit + origin → github 顺序 |

**新增 / 修改文件清单：**

```
scripts/_probe_http_helpers.py                                       (640-A.1 修改; 加 POLICY_MARKER_RE)
scripts/probe_policy_v1_2024.py                                      (640-A.1 新增; 12 URL 政策源探活)
scripts/seed_m4_3_policy_demo.sql                                    (640-A.2 新增; demo seed SQL 21 行)
docs/60-m4-3-policy-demo-20260901.md                                 (640-A.3 新增; 架构师级 §1-§6)
docs/reports/m4_3_policy_v1_probe_20260901.md                        (640-A.5 新增; probe 报告)
evidence_pack/m4_3_policy_v1_probe_20260901.json                     (640-A.5 新增; 证据包)
tests/test_m4_3_policy_demo.py                                        (640-B 新增; 7 用例)
reviews/stage0-gate0-rework-2026-08-23/640-stage0-architect-m4-3-policy-demo-tasking-20260901.md  (commit `b09a511` tasking)
reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md              (commit `b09a511` rev65)
reviews/stage0-gate0-rework-2026-08-23/640-stage0-cc-m4-3-policy-demo-receipt-20260901.md  (本回执)
```

---

## 7. commit + 双推

### 7.1 640 delivery commit (7 files)

```bash
git add scripts/_probe_http_helpers.py \
        scripts/probe_policy_v1_2024.py \
        scripts/seed_m4_3_policy_demo.sql \
        docs/60-m4-3-policy-demo-20260901.md \
        docs/reports/m4_3_policy_v1_probe_20260901.md \
        evidence_pack/m4_3_policy_v1_probe_20260901.json \
        tests/test_m4_3_policy_demo.py

git commit -m "feat(640): M4.3 政策项目 demo — 二次 probe (REACHABLE 2 = 黑龙江 zfwj/zfgb) + 3 demo each × 6 政策表 lineage.is_demo='true' 隔离"

git push origin HEAD
git push github HEAD
```

### 7.2 cc_head backfill commit (1 file)

```bash
# After 7.1 commit, capture hash; update EXEC-QUEUE TBD → <hash>
git add reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md
git commit -m "chore(640): EXEC-QUEUE cc_head backfill TBD → <hash> (delivery)"

git push origin HEAD
git push github HEAD
```

### 7.3 receipt commit (1 file)

```bash
git add reviews/stage0-gate0-rework-2026-08-23/640-stage0-cc-m4-3-policy-demo-receipt-20260901.md
git commit -m "docs(640): receipt §PHOTO-1..6"

git push origin HEAD
git push github HEAD
```

---

## 8. 下一步

- 用户接受/驳回 640 推荐 641 scope:
  - **接受** → 641 = M4.4 黑龙江政策真实化 spike (单 REACHABLE 试点省;沿用 lineage JSONB sentinel;验证 6 表 JOIN 端到端)
  - **驳回** → 用户裁定 641 re-scope 或跳过 M4.4 接 M5 WAF spike
  - **调整** → 用户裁定 641 = 任免真实化 (复用 639 6 REACHABLE 任免源,跨 6 省)
- **不宣布 Gate / O1 / M2 / M4 PASS**。
- 641 tasking 待架构师(用户)签发;执行端在收到新刀前静默等待。

— End 640 receipt —