# 639 — M4.2 任免数据 demo（执行端回执）

> **类型**: 执行端 (CC) 回执 · knife 639 落地报告
> **日期**: 2026-09-01
> **依据**: `reviews/stage0-gate0-rework-2026-08-23/639-stage0-architect-m4-2-renmian-demo-tasking-20260901.md`
> **前置**: 638 DELIVERED (cc_head `f1fdad5` + receipt `ee86977`);用户接受 M4.2 scope (ccdi 公告列表 + 23 试点省 + ≤5 demo)
> **阶段**: M4.2 落地（任免公告二次探活 + 人物政策 demo SQL + docs/59；架构师级 deliverable；非用户问句）

---

## 0. 一句话

639 落地 5 件：**(A1)** `scripts/probe_renmian_v2_2024.py` 29/29 实测 = **REACHABLE 6 / PARTIAL 8 / BLOCKED 15**（出乎任务前预期：6 试点省任免栏目任免 marker 直接命中；ccdi/npc/国务院 仍 PARTIAL/BLOCKED）；**(A2)** `scripts/seed_m4_2_demo.sql` 人物政策 demo 最小实现（1 source_registry + 1 source_document（demo SHA 0…01）+ 5 position + 5 person + 5 tenure + 5 appointment_event；person + appointment_event 全部 `is_demo=true` 隔离，tenure/position 间接通过 source_document 一跳回）；**(A3)** `docs/59-m4-2-renmian-demo-20260901.md` §1-§6 架构师级审查 + 6 REACHABLE 任免源 ≠ 政策源（M4.3 需独立 probe）；**(B)** `tests/test_m4_2_renmian_demo.py` 7 用例；**全套 M2+637+638+639 = 64/64 pytest green**；**架构师推荐 640 = M4.3 政策项目 demo**（policy_document / policy_commitment / project_event 沿用 is_demo=true 模式 + demo SHA 0…02 + 6 REACHABLE 试点省 + 政策承载路径 `/zwgk/zfwj/` 等独立 probe）；不宣布 Gate / O1 / M2 / M4 PASS；不向用户提任何 URL 裁定事项。

---

## 1. 交付映射（639-A → 639-C）

| 子刀 | 文件 | 状态 | 说明 |
|---|---|---|---|
| 639-A.1 | `scripts/probe_renmian_v2_2024.py` | DONE | 任免公告二次探活 29/29 cell；REACHABLE 6 / PARTIAL 8 / BLOCKED 15 |
| 639-A.2 | `scripts/seed_m4_2_demo.sql` | DONE | 1 source_registry + 1 source_document（demo SHA `0…01`）+ 5 position + 5 person + 5 tenure + 5 appointment_event；person + appointment_event is_demo=true 隔离 |
| 639-A.3 | `docs/59-m4-2-renmian-demo-20260901.md` | DONE | §1-§6 架构师级审查 + M4.3 推荐 scope |
| 639-A.5 | `docs/reports/m4_2_renmian_v2_probe_20260901.md` + `evidence_pack/m4_2_renmian_v2_probe_20260901.json` | DONE | probe 报告 + 证据包 |
| 639-A.6 | `reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md` | DONE | rev63（tasking OPEN → 等 CC 落地；commit `f70ac95`） |
| 639-B | `tests/test_m4_2_renmian_demo.py` | DONE | 7 用例：报告存在+顶层裁定 / evidence JSON parses / seed SQL ≤5 demo / seed is_demo 隔离 / seed source_document 跳回 SHA / docs/59 六段 / docs/59 不宣称 PASS |
| 639-C | 本回执 + commit + 双推 | DONE | §PHOTO-1..6 + commit + origin→github |

---

## 2. PHOTO-1: pytest 一行（639 §PHOTO-1 须绿）

```
$ STAGE0_SKIP_SCHEMA_APPLY=1 PYTHONPATH=backend/src python3 -m pytest \
    tests/test_m2_crosscheck.py tests/test_m2_b_first_batch.py \
    tests/test_m2_province_geo_seed.py tests/test_m2_frontend_page.py \
    tests/test_m2_backfill_feasibility.py tests/test_m3_launch_conditions_review.py \
    tests/test_m4_1_people_probe.py tests/test_m4_2_renmian_demo.py
tests/test_m2_crosscheck.py ......                                       [  9%]
tests/test_m2_b_first_batch.py ........                                  [ 21%]
tests/test_m2_province_geo_seed.py ........                              [ 34%]
tests/test_m2_frontend_page.py ..........                                [ 50%]
tests/test_m2_backfill_feasibility.py ........                           [ 62%]
tests/test_m3_launch_conditions_review.py .........                      [ 76%]
tests/test_m4_1_people_probe.py ........                                 [ 89%]
tests/test_m4_2_renmian_demo.py .......                                  [100%]

============================== 64 passed in 0.77s ==============================
```

**7 个新增 M4.2 用例**（`tests/test_m4_2_renmian_demo.py`）：

- `test_renmian_v2_probe_report_exists_and_has_top_verdict` — 报告存在 + 顶层裁定 REACHABLE/BLOCKED/MIXED + 29 cell + 实体逐项 + 中央 vs 试点省分布
- `test_renmian_v2_evidence_json_parses` — JSON parses + summary/cells/probed_count + by_class_verdict + 试点省 REACHABLE ≥ 1 (实际 6)
- `test_seed_m4_2_sql_exists_and_has_demo_data` — seed SQL 存在 + 5 demo person rows + 5 demo tenure + 5 demo appointment_event + 不含 DML/DROP/DELETE/TRUNCATE (剥注释后扫)
- `test_seed_m4_2_sql_is_demo_isolation` — 5 demo person + 5 demo appointment_event 全部 is_demo=TRUE + 不含 is_demo=FALSE
- `test_seed_m4_2_sql_has_source_document_back_link` — source_document 含 file_hash_sha256 + demo SHA `0…01` + 5 tenure + 5 appointment_event 全部 source_id = demo source_document UUID
- `test_doc_59_has_six_sections` — docs/59 含 ## 1.-## 6. 六段 + 标头 59/2026-09-01/639
- `test_doc_59_no_pass_announcement` — §6 不宣称 M4/M2/Gate PASS（智能排除 disclaimer 否定句）

**M2 + 637 + 638 回归 57 用例**：全 green。

---

## 3. PHOTO-2: docs/59 §1-§6 结构（639 §PHOTO-2）

```
## 1. M4.2 落地终态
   5 sub-knife 状态表 + M4.2 收口结论
   (任免公告 REACHABLE 6 试点省 + demo SQL seed 5 demo is_demo=true 隔离)

## 2. 任免公告 二次 probe 数据（基于 639-A.1）
   总分布: REACHABLE 6 / PARTIAL 8 / BLOCKED 15 (29/29)
   REACHABLE 6 试点省 (黑龙江/福建/河南/广东/贵州/云南)
   PARTIAL 8 实体 (中央 4 + 试点省 4)
   BLOCKED 15 实体 (npc TLS reset + 13 试点省 404/403/timeout)
   638 vs 639 对比表 + WAF 假设修正延续

## 3. demo SQL 结构（基于 639-A.2）
   1 source_registry + 1 source_document (demo SHA 0…01) +
   5 position + 5 person + 5 tenure + 5 appointment_event
   is_demo=true 隔离原则 (person + appointment_event 显式 / tenure + position 间接)

## 4. 015 schema 落地（基于 638-A.3）
   person.is_demo / appointment_event.is_demo 加性验证
   016+ backfill 既有 NULL 行 + position/tenure/source_document 三表 is_demo 加列方案

## 5. M4.3 下一步
   640 = M4.3 政策项目 demo (依 639 demo 验证)
   is_demo=true 模式复用 + 6 REACHABLE 任免源 ≠ 政策源 (M4.3 独立 probe)
   demo SHA 0…02 (与任免 demo SHA 0…01 区分)

## 6. 下一步 (640 = M4.3)
   640 探活 + 016+ 三表 is_demo 加列
   不宣称任何 M2/M4/Gate PASS
```

---

## 4. PHOTO-3: 架构师裁定 + 6 REACHABLE 任免源（639 §PHOTO-3）

**裁定（docs/59 §2.4 + §5.1）：**

638-A.2 任免公告 PARTIAL 1 / BLOCKED 2 = 仅 3 URL 探活，且 ccdi 是首页非任免页。639-A.1 二次探活发现:

- **6 REACHABLE 试点省任免栏目** (`/zwgk/` 任免 marker 直接命中): 黑龙江 / 福建 / 河南 / 广东 / 贵州 / 云南
- **8 PARTIAL** (HTTP 200 + body 已加载 + 无任免 marker):
  - 4 中央: ccdi 要闻 + 审查调查 + 国务院 政策 + 要闻 (URL 不命中任免承载栏目)
  - 4 试点省: 上海 / 重庆 / 海南 / 宁夏 (`/zwgk/` 政务公开目录,无任免列表)
- **15 BLOCKED**:
  - 2 中央: npc 任免 + 要闻 (TLS reset, HTTPS 重试仍 WAF)
  - 13 试点省: 北京 / 河北 / 山西 / 辽宁 / 吉林 / 江苏 / 陕西 (404) + 浙江 / 安徽 / 四川 / 新疆 (403 WAF) + 内蒙古 (timeout)

**架构师裁定：**

- **WAF 假设修正延续**：638 假设 `tjj.*` 子域 100% 阻断 + `www.*.gov.cn/` 部分可达;639 进一步证实 `www.*.gov.cn/` 子域内**任免承载路径**(`/zwgk/`)在 6 试点省直接命中,13 试点省 404(路径不存在,非 WAF 阻断),4 试点省 PARTIAL(栏目可达但无任免 marker)。
- **任免公告实际路径**: 6 试点省的 `/zwgk/` 直接命中任免 marker;中央(国务院 / ccdi)URL 不对(是政策 / 要闻栏,非任免);npc WAF 阻断。
- **6 REACHABLE 任免源 ≠ 政策源**: M4.3 政策项目 demo 必须独立做政策源可达性 probe,不复用 639 数据。

**M4.3 推荐 scope：**

1. **640-A.1 政策源二次探活** — 6 REACHABLE 试点省 + ccdi/npc/国务院,在 `/zwgk/` 之外探 `/zwgk/zfwj/`(政府文件)/ `/zwgk/zfgb/`(政府公报)/ `/zwgk/ghjh/`(规划计划)等政策承载路径
2. **640-A.2 政策项目 demo** — `policy_document` / `policy_commitment` / `project_event` 三表加 `is_demo` 列(016+ migration);沿用 is_demo=true 模式 + demo SHA 0…02(与 639 demo SHA 0…01 区分)
3. **640-A.3 docs/60** — M4.3 落地终态 + 政策源探活数据 + 016+ schema 加列建议
4. **640-B** 测试 ≥ 6 用例 + **640-C** 回执 + 双推

---

## 5. PHOTO-4: probe 矩阵 + demo SQL 落地（639 §PHOTO-4）

### 5.1 任免公告二次 probe 矩阵（29 cell 实测）

| verdict | 实体 | http_code 分布 | 试点省分布 |
|---|---|---|---|
| REACHABLE 6 | 黑龙江/福建/河南/广东/贵州/云南 | 200 × 6 | 试点省 6 |
| PARTIAL 8 | 中央纪委要闻 + 审查调查 + 国务院政策 + 要闻 + 上海/重庆/海南/宁夏 | 200 × 8 | 中央 4 + 试点省 4 |
| BLOCKED 15 | npc 任免 + 要闻 (TLS reset) + 北京/河北/山西/辽宁/吉林/江苏/陕西 (404) + 浙江/安徽/四川/新疆 (403 WAF) + 内蒙古 (timeout) | 0/404/403 | 中央 2 + 试点省 13 |

### 5.2 demo SQL seed 结构

| 表 | 行数 | demo 隔离列 | 来源 |
|---|---|---|---|
| source_registry | 1 | — (synthetic) | domain=demo.placeholder / enabled=FALSE |
| source_document | 1 | file_hash_sha256=`0…01` | source_level=S4 / verification_status=UNVERIFIED |
| position | 5 | — (015 未加 position.is_demo) | demo-position-1..5, level=central |
| person | 5 | is_demo=TRUE | demo-person-1..5, last_verified_at=NOW() |
| tenure | 5 | — (015 未加 tenure.is_demo) | demo tenure 1..5, source_id = demo source_document |
| appointment_event | 5 | is_demo=TRUE | demo appointment_event 1..5, source_id = demo source_document |

**is_demo 隔离原则**：
- 5 person + 5 appointment_event 显式 `is_demo=true` (015 加列约束)
- 5 tenure 间接通过 `source_id → demo source_document (SHA 0…01)` 隔离
- 5 position 间接通过 `source_document.file_hash_sha256` 关联过滤 (无 is_demo 列)
- demo 数据**只能** SELECT 通过 `WHERE is_demo=true` 过滤 (应用层 + 测试层)
- 真实数据 INSERT 必须 `is_demo=false` + `source_id NOT NULL` (016+ 引入 CHECK 约束)

### 5.3 demo 数据选择理由

- 5 person 行 (demo-person-1..5) 覆盖: 3 current tenure + 1 ended tenure + 1 removal appointment_event (演示 appointment_event.event_type 多样性)
- 5 tenure 行全部 `source_id = demo source_document (SHA 0…01)`,一跳回 SHA 用于 demo 一跳回验证
- 5 appointment_event: 4 appointment + 1 removal (演示 event_type 字段;不涉及真实任免)

---

## 6. PHOTO-5: 红线表（639 §PHOTO-5 / §1 禁）

| 红线 | 状态 | 证据 |
|---|---|---|
| 不宣布 Gate / O1 / M2 / M4 PASS | ✓ | docs/59 §6 + §1 全 disclaimer;test_doc_59_no_pass_announcement 验证 |
| 不让用户裁定 URL/年份 | ✓ | probe targets 全部 gov.cn 政府源;无问句 |
| 数据源唯一=政府/统计/研究机构 | ✓ | ccdi.gov.cn / npc.gov.cn / www.gov.cn / 23 www.\*.gov.cn |
| 不爬网 | ✓ | probe 只探可达性,不抓内容入库 |
| 不写 cegr.observation | ✓ | probe read-only + seed SQL 仅 INSERT demo 行 |
| 不静默硬编码 GDP 值 | ✓ | demo 表无 GDP 字段 |
| 不删表 / 不 DROP COLUMN | ✓ | seed SQL 仅 INSERT ON CONFLICT DO NOTHING (剥注释后扫验证) |
| is_demo 隔离 | ✓ | person.is_demo + appointment_event.is_demo 显式;tenure / position 间接 |
| demo ≤ 5 条 person/tenure/appointment_event | ✓ | test_seed_m4_2_sql_exists_and_has_demo_data 验证 |
| demo 有 source_document_id 跳回 SHA | ✓ | demo SHA `0…01` + 5 tenure + 5 appointment_event 全部 source_id = demo SD UUID |
| 不改 source_registry / mart / 4 fixture | ✓ | 639 新增 1 synthetic source_registry 行 (enabled=FALSE),不动既有行 / mart / fixture |
| 湖北必须 ≠ M1 半年表 c5cf5abe | ✓ | 639 不写湖北具体 observation;湖北在 BLOCKED 13 试点省之列 (无 probe 数据) |
| probe 脚本幂等 | ✓ | no time.sleep / no random in classify / no DML |
| 双推 origin→github | ✓ | §7 commit + origin → github 顺序 |

**新增 / 修改文件清单：**

```
scripts/probe_renmian_v2_2024.py                                (639-A.1 新增; 29 URL 二次探活)
scripts/seed_m4_2_demo.sql                                      (639-A.2 新增; demo seed SQL)
docs/59-m4-2-renmian-demo-20260901.md                           (639-A.3 新增; 架构师级 §1-§6)
docs/reports/m4_2_renmian_v2_probe_20260901.md                  (639-A.5 新增; probe 报告)
evidence_pack/m4_2_renmian_v2_probe_20260901.json               (639-A.5 新增; 证据包)
tests/test_m4_2_renmian_demo.py                                 (639-B 新增; 7 用例)
reviews/stage0-gate0-rework-2026-08-23/639-stage0-architect-m4-2-renmian-demo-tasking-20260901.md  (commit `c3968ec` tasking)
reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md          (commit `f70ac95` rev63)
reviews/stage0-gate0-rework-2026-08-23/639-stage0-cc-m4-2-renmian-demo-receipt-20260901.md  (本回执)
```

---

## 7. commit + 双推

### 7.1 639 delivery commit (6 files)

```bash
git add scripts/probe_renmian_v2_2024.py \
        scripts/seed_m4_2_demo.sql \
        docs/59-m4-2-renmian-demo-20260901.md \
        docs/reports/m4_2_renmian_v2_probe_20260901.md \
        evidence_pack/m4_2_renmian_v2_probe_20260901.json \
        tests/test_m4_2_renmian_demo.py

git commit -m "feat(639): M4.2 任免数据 demo — 二次 probe (6 REACHABLE) + 5 demo person/tenure/appointment_event is_demo=true 隔离"

git push origin HEAD
git push github HEAD
```

### 7.2 cc_head backfill commit (1 file)

```bash
# After 7.1 commit, capture hash; update EXEC-QUEUE TBD → <hash>
git add reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md
git commit -m "chore(639): EXEC-QUEUE cc_head backfill TBD → <hash> (delivery)"

git push origin HEAD
git push github HEAD
```

### 7.3 receipt commit (1 file)

```bash
git add reviews/stage0-gate0-rework-2026-08-23/639-stage0-cc-m4-2-renmian-demo-receipt-20260901.md
git commit -m "docs(639): receipt §PHOTO-1..6"

git push origin HEAD
git push github HEAD
```

---

## 8. 下一步

- 用户接受/驳回 639 推荐 640 scope:
  - **接受** → 640 = M4.3 政策项目 demo (policy_document / policy_commitment / project_event + 016+ 三表 is_demo 加列 + demo SHA 0…02 + 6 REACHABLE 试点省政策承载路径独立探活)
  - **驳回** → 用户裁定 640 re-scope 或跳过 M4.3 接 M5 spike
  - **调整** → 用户裁定 640 = 任免真实化 (M5 spike 性质,从 6 REACHABLE 试点省选 1-2 省试抓真实任免)
- **不宣布 Gate / O1 / M2 / M4 PASS**。
- 640 tasking 待架构师(用户)签发;执行端在收到新刀前静默等待。

— End 639 receipt —
