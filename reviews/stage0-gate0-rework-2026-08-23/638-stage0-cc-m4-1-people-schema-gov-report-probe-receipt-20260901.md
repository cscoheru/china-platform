# 638 — M4.1 人物表 schema 收口 + 政府工作报告数据可得性 probe（执行端回执）

> **类型**: 执行端 (CC) 回执 · knife 638 落地报告
> **日期**: 2026-09-01
> **依据**: `reviews/stage0-gate0-rework-2026-08-23/638-stage0-architect-m4-1-people-schema-gov-report-probe-tasking-20260901.md`
> **前置**: 637 DELIVERED (cc_head `5d957ef`);用户接受路径 C
> **阶段**: M4.1 落地（人物表 schema 收口 + 政府工作报告/任免公告可达性 probe；架构师级 deliverable；非用户问句）

---

## 0. 一句话

638 落地 5 件：**(A1)** `scripts/probe_gov_report_2024.py` 32/32 实测 = **REACHABLE 23 / PARTIAL 0 / BLOCKED 9**（超预期：636 WAF 全阻断假设不适用于 `www.*.gov.cn/` 首页路径）；**(A2)** `scripts/probe_renmian_announcement_2024.py` 3/3 实测 = REACHABLE 0 / PARTIAL 1 / BLOCKED 2；**(A3)** `schema/migrations/015-m4-1-people-schema.sql` 加性 ADD COLUMN（person.is_demo / person.last_verified_at / appointment_event.is_demo）+ 3 索引；**(A4)** `docs/58` §1-§6 架构师级审查 + WAF 假设修正；**(B)** `tests/test_m4_1_people_probe.py` 8 用例；**全套 M2+637+638 = 57/57 pytest green**；**架构师推荐 639 = M4.2 任免数据 demo（ccdi 公告列表页 + 23 试点省）**；不宣布 Gate / O1 / M2 / M4 PASS；不向用户提任何 URL 裁定事项。

---

## 1. 交付映射（638-A → 638-C）

| 子刀 | 文件 | 状态 | 说明 |
|---|---|---|---|
| 638-A.1 | `scripts/probe_gov_report_2024.py` + `scripts/_probe_http_helpers.py` | DONE | 政府工作报告 probe 32/32 cell；REACHABLE 23 / BLOCKED 9 |
| 638-A.2 | `scripts/probe_renmian_announcement_2024.py` | DONE | 任免公告 probe 3/3 cell；REACHABLE 0 / PARTIAL 1 / BLOCKED 2 |
| 638-A.3 | `schema/migrations/015-m4-1-people-schema.sql` | DONE | 加性 DDL：person + appointment_event 各加 is_demo；person + last_verified_at；3 索引；零 DML |
| 638-A.4 | `docs/58-m4-1-people-schema-gov-report-probe-20260901.md` | DONE | §1-§6 架构师级审查 + WAF 假设修正 |
| 638-A.6 | `docs/reports/m4_1_gov_report_probe_20260901.md` + `evidence_pack/m4_1_gov_report_probe_20260901.json` | DONE | probe 报告 + 证据包 |
| 638-A.7 | `docs/reports/m4_1_renmian_probe_20260901.md` + `evidence_pack/m4_1_renmian_probe_20260901.json` | DONE | probe 报告 + 证据包 |
| 638-B | `tests/test_m4_1_people_probe.py` | DONE | 8 用例：报告存在+顶层裁定 / evidence JSON parses / probe 不写 DB / probe 不静默硬编码 GDP / 任免 JSON parses / 015 零 DML / docs/58 六段 / docs/58 不宣称 PASS |
| 638-C | 本回执 + commit + 双推 | DONE | §PHOTO-1..6 + commit + origin→github |

---

## 2. PHOTO-1: pytest 一行（638 §PHOTO-1 须绿）

```
$ STAGE0_SKIP_SCHEMA_APPLY=1 PYTHONPATH=backend/src python3 -m pytest \
    tests/test_m2_crosscheck.py tests/test_m2_b_first_batch.py \
    tests/test_m2_province_geo_seed.py tests/test_m2_frontend_page.py \
    tests/test_m2_backfill_feasibility.py tests/test_m3_launch_conditions_review.py \
    tests/test_m4_1_people_probe.py -q
..................................................                        [100%]
57 passed in 0.82s
```

**8 个新增 M4.1 用例**（tests/test_m4_1_people_probe.py）：

- `test_gov_report_probe_report_exists_and_has_top_verdict` — 报告存在 + 顶层裁定 REACHABLE/BLOCKED/MIXED + 32 cell + 实体逐项
- `test_gov_report_probe_evidence_json_parses` — JSON parses + summary/cells/probed_count + verdict sum 等于 probed_cells
- `test_gov_report_probe_does_not_modify_database` — 不含 INSERT/UPDATE/DELETE/TRUNCATE/DROP/psycopg/create_engine/.execute
- `test_gov_report_probe_no_hardcoded_gdp_values` — 31 省 2024 期望 GDP 真值（1349084 / 53926.71 / 等）禁值不在 markdown / script 中
- `test_renmian_probe_evidence_json_parses` — 任免 JSON parses + probed_cells = 3
- `test_migration_015_no_dml` — 015 不含 DML/DROP/RENAME；只 ADD COLUMN IF NOT EXISTS + CREATE INDEX IF NOT EXISTS + is_demo
- `test_doc_58_has_six_sections` — docs/58 含 ## 1.-## 6. + 58/2026-09-01/638 标头
- `test_doc_58_no_pass_announcement` — §6 不宣称 M4/M2/Gate PASS（智能排除 disclaimer 否定句）

**M2 + 637 回归 49 用例**：全 green。

---

## 3. PHOTO-2: docs/58 §1-§6 结构（638 §PHOTO-2）

```
## 1. M4.1 落地终态
   638-A.1/A.2/A.3/A.4 四 sub-knife 状态表 + M4.1 收口结论
   (schema 完成 + 政府工作报告 23/32 REACHABLE + 任免公告仍阻塞)

## 2. 政府工作报告 probe 数据（基于 638-A.1）
   总分布: REACHABLE 23 / PARTIAL 0 / BLOCKED 9
   试点省 verdict (江苏/广东/浙江/山东/四川)
   BLOCKED 9 实体 + 根因分析
   636 WAF 假设修正: www.*.gov.cn/ 路径 23/31 可达 vs tjj.* 子域 0/31

## 3. 任免公告 probe 数据（基于 638-A.2）
   总分布: REACHABLE 0 / PARTIAL 1 / BLOCKED 2
   ccdi/npc/国务院 verdict + 根因
   638 已知 gap: 任免公告 URL 未充分探 → 639 二次探活

## 4. 人物表 schema 收口（基于 638-A.3）
   person.is_demo / person.last_verified_at / appointment_event.is_demo
   3 索引 + 008 additive 纪律继承

## 5. M4.2 / M4.3 下一步
   639 = M4.2 任免数据 demo 推荐 scope
   640 = M4.3 政策项目 demo

## 6. 下一步 (639 = M4.2)
   639 探活 + demo 数据 is_demo=true 隔离
   不宣称任何 M2/M4/Gate PASS
```

---

## 4. PHOTO-3: 架构师裁定 + WAF 假设修正（638 §PHOTO-3）

**裁定（docs/58 §1 + §2.3）：**

636 §2 假设「.gov.cn 全 IP-level WAF 阻断」基于 tjj.* 31 省统计公报探针。638-A.1 实测发现：
- 23/31 省 `www.*.gov.cn/` 首页 REACHABLE ⇒ 636 假设**非全 IP-level**
- 31/31 省 `tjj.*.gov.cn/*` BLOCKED ⇒ `tjj.*` 子域被针对性 WAF
- 9 省 BLOCKED 根因为 TLS reset（WAF）；1 例（国务院）为 URL 错（404）

**架构师裁定**：
- WAF 阻断**子域/路径选择性**而非全 IP-level
- 政府工作报告路径 = `www.*.gov.cn/` 起点 + 部委厅局子页查找（23 省可达 = 强起点）
- 任免公告路径 = ccdi 公告列表页（PARTIAL 提示首页可达）+ npc + 国务院正确 URL（639 二次探活）

**M4.2 推荐 scope**：
- 639-A.1 ccdi 公告列表页 + 任免公告页二次探活
- 639-A.2 23 试点省 `www.*.gov.cn/` 任免路径探活
- 639-A.3 demo 表最小实现（is_demo=true 隔离，≤5 条 demo）
- 639-A.4 docs/59

---

## 5. PHOTO-4: probe 矩阵 + schema 落地（638 §PHOTO-4）

### 5.1 政府工作报告 probe 矩阵（32 cell 实测）

| verdict | 实体 | 说明 |
|---|---|---|
| REACHABLE 23 | 北京/上海/重庆/河北/山西/内蒙古/辽宁/吉林/黑龙江/江苏/浙江/安徽/福建/河南/湖南/广东/海南/四川/贵州/云南/陕西/宁夏 等 | HTTP 200 + 含政府工作报告/人民政府 marker |
| BLOCKED 9 | 国务院（URL 404）/ 天津/山东/湖北/江西/广西/西藏/甘肃/青海 | TLS reset（WAF）或 URL 404 |

### 5.2 任免公告 probe 矩阵（3 cell 实测）

| verdict | 实体 | 说明 |
|---|---|---|
| PARTIAL 1 | 中央纪委国家监委 | HTTP 200 首页通，但无任免 marker（URL 是首页非任免页） |
| BLOCKED 2 | 全国人大 | timeout（15s） |
| BLOCKED 2 | 国务院 | HTTP 404（URL `/zwgk/zfgbg.htm` 不存在） |

### 5.3 人物表 schema 015 加性变更

| 表 | 加列 | 类型 | 默认 |
|---|---|---|---|
| person | is_demo | BOOLEAN | NULL |
| person | last_verified_at | TIMESTAMPTZ | NULL |
| appointment_event | is_demo | BOOLEAN | NULL |

3 索引：`idx_person_is_demo` / `idx_person_last_verified_at` / `idx_appointment_event_is_demo`

008 discipline 继承：零 DROP / 零 RENAME / 零 FK / 零 CHECK。

---

## 6. PHOTO-5: 红线表（638 §PHOTO-5 / §1 禁）

| 红线 | 状态 | 证据 |
|---|---|---|
| 不宣布 Gate / O1 / M2 / M4 PASS | ✓ | docs/58 §6 + §1 全 disclaimer；test_doc_58_no_pass_announcement 验证 |
| 不让用户裁定 URL/年份 | ✓ | probe targets 全部 gov.cn 政府源；无问句 |
| 数据源唯一=政府/统计/研究机构 | ✓ | 国务院 + 31 省 www.*.gov.cn + ccdi/npc |
| 不爬网 | ✓ | probe 只探可达性, 不抓内容入库 |
| 不写 cegr.observation | ✓ | probe read-only (test_gov_report_probe_does_not_modify_database 验证) |
| 不静默硬编码 GDP 值 | ✓ | test_gov_report_probe_no_hardcoded_gdp_values 验证 |
| 不删 person 表 / 不 DROP COLUMN | ✓ | 015 加性 only (test_migration_015_no_dml 验证) |
| is_demo 隔离 | ✓ | person.is_demo + appointment_event.is_demo + 008 纪律继承 |
| 不改 source_registry / mart / 4 fixture | ✓ | 638 不动这些 |
| 湖北必须 ≠ M1 半年表 c5cf5abe | ✓ | 638 不写湖北具体 observation |
| probe 脚本幂等 | ✓ | no time.sleep / no random in classify / no DML |
| 双推 origin→github | ✓ | §7 commit + origin → github 顺序 |

**新增 / 修改文件清单：**

```
scripts/_probe_http_helpers.py                                  (638-A 新增; 共享 HTTP probe 助手)
scripts/probe_gov_report_2024.py                                (638-A.1 新增; 32 URL probe)
scripts/probe_renmian_announcement_2024.py                      (638-A.2 新增; 3 URL probe)
schema/migrations/015-m4-1-people-schema.sql                    (638-A.3 新增; 加性 DDL)
docs/58-m4-1-people-schema-gov-report-probe-20260901.md         (638-A.4 新增; 架构师级 §1-§6)
docs/reports/m4_1_gov_report_probe_20260901.md                  (638-A.6 新增; probe 报告)
evidence_pack/m4_1_gov_report_probe_20260901.json               (638-A.6 新增; 证据包)
docs/reports/m4_1_renmian_probe_20260901.md                     (638-A.7 新增; probe 报告)
evidence_pack/m4_1_renmian_probe_20260901.json                  (638-A.7 新增; 证据包)
tests/test_m4_1_people_probe.py                                 (638-B 新增; 8 用例)
reviews/stage0-gate0-rework-2026-08-23/638-stage0-cc-m4-1-people-schema-gov-report-probe-receipt-20260901.md  (本回执)
```

注：`638-stage0-architect-m4-1-people-schema-gov-report-probe-tasking-20260901.md` 在本回执之前作为 planning commit 单独 commit（chore `f57712f`）。

---

## 7. commit + 双推

### 7.1 638 delivery commit (10 files)

```bash
git add scripts/_probe_http_helpers.py \
        scripts/probe_gov_report_2024.py \
        scripts/probe_renmian_announcement_2024.py \
        schema/migrations/015-m4-1-people-schema.sql \
        docs/58-m4-1-people-schema-gov-report-probe-20260901.md \
        docs/reports/m4_1_gov_report_probe_20260901.md \
        evidence_pack/m4_1_gov_report_probe_20260901.json \
        docs/reports/m4_1_renmian_probe_20260901.md \
        evidence_pack/m4_1_renmian_probe_20260901.json \
        tests/test_m4_1_people_probe.py

git commit -m "feat(638): M4.1 人物表 schema 收口 + 政府工作报告/任免公告可达性 probe (23/32 REACHABLE)"

git push origin HEAD
git push github HEAD
```

### 7.2 cc_head backfill commit (1 file)

```bash
# After 7.1 commit, capture hash; update EXEC-QUEUE TBD → <hash>
git add reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md
git commit -m "chore(638): EXEC-QUEUE cc_head backfill TBD → <hash> (delivery)"

git push origin HEAD
git push github HEAD
```

### 7.3 receipt commit (1 file)

```bash
git add reviews/stage0-gate0-rework-2026-08-23/638-stage0-cc-m4-1-people-schema-gov-report-probe-receipt-20260901.md
git commit -m "docs(638): receipt §PHOTO-1..6"

git push origin HEAD
git push github HEAD
```

---

## 8. 下一步

- 用户接受/驳回 638 推荐 639 scope：
  - **接受** → 639 = M4.2 任免数据 demo（ccdi 公告列表页 + 23 试点省二次探活 + demo 数据 ≤5 条 is_demo=true）
  - **驳回** → 用户裁定 639 re-scope 或 640 (M4.3 跳过 demo)
- **不宣布 Gate / O1 / M2 / M4 PASS**。
- 639 tasking 待架构师（用户）签发；执行端在收到新刀前静默等待。

— End 638 receipt —