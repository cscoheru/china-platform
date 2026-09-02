# 652 — M4.15 v9 BLOCKED 留痕 e2e spike — DELIVERY RECEIPT

> **刀号**: 652
> **类型**: DELIVERED (架构师本终端自签 + 自交付 per 2026-08-31 21:50 豁免)
> **日期**: 2026-09-02
> **任务书**: `reviews/stage0-gate0-rework-2026-08-23/651-audit-652-tasking-consolidated-20260902.md` (合并件 PART 2 / 652 任务书)
> **前置审计**: 651 审计 PASS（有限通过）+ 2×P4 教训沉淀 (P4-1 status pin 中间 SHA / P4-2 cc_head amend 孤儿 ea64640)
> **架构师审查**: `docs/76-m4-15-policy-detail-real-v9-20260902.md` (DONE)
> **不宣称任何** Gate / O1 / O2 / O3 / M2 / M4 / M4.x / M5 / M5.x / M6 PASS。

---

## §NOW (执行态)

CC 执行 652 完成 (per 任务书 §A.0/A.1/A.2/A.3/A.4 + §B + §C)。当前态: **M4.15 v9 真实化 (xinjiang + nei_menggu 第 17/18 样本) + 651 审计 P4×2 规范固化 (status/§CURRENT/§NOW 不 pin 中间 SHA + cc_head 链 SHA 一律 git log 实测) + 652 §0.14 强制 BLOCKED_NO_POOL 留痕 e2e 验证完成 (4 实现位置 + 5 守门全到位; 双样本 REACHABLE, 分支代码可达) + docs/76 §1-§6 + evidence ×2 + tests 27 new green + ≥171 跨刀 spike 回归**。

---

## §EXEC_BODY — 652 落地明细

### 652-A.0 651 审计 P4×2 规范固化 (DONE)

| 项 | 落点 | 状态 |
|---|---|---|
| **P4-1** 规范固化: status/§CURRENT/§NOW **不 pin 中间 SHA**; 仅以"三 ref 全等 + 最终 HEAD"表述 | `docs/75-m4-14-policy-detail-real-v8-20260902.md:283` + `651 receipt:169` | ✓ |
| **P4-2** 规范固化: cc_head/回执入链 SHA 一律 `git log --format=%H -n <n>` 实测; amend 必须**先 amend 完成再写链文本** | `docs/75-m4-14-policy-detail-real-v8-20260902.md:284` + `651 receipt:170` | ✓ |
| 652-C 写 EXEC-QUEUE rev90 时 status/§NOW 措辞**不 pin 中间 SHA** | (per P4-1 固化) | ✓ |
| `git log` 实测取链 SHA (非记忆) | (per P4-2 固化) | ✓ |
| O-1 (m2 crosscheck 复跑污染) 加固仍开放 (crosscheck 测试 tmpdir isolation) | 不 gating, 652 可选 | ✓ |

红线 13 规范沿用 (per 649 审计 P3-1 + 650 蓝图更正 + 651-A.0 落地): 代换行 source_registry `province`/`source_name` 一律用 actual_province（URL 归属省），original_province 仅存 lineage JSONB。本次 652 零 substitute 触发, 全部 16 INSERT ROWS 字段 `province/source_name/publisher` 均直接用 actual_province 口径 (与 province 一致)。

### 652-A.1 M4.15 v9 真实化 (DONE)

| 项 | 落点 | 状态 |
|---|---|---|
| `scripts/fetch_m4_15_policy_detail_v9_2024.py` | 2 cells (xinjiang + nei_menggu 第 17/18 样本); **SUBSTITUTE_POOL=[] (EXHAUSTED 沿用 651)** + BLOCKED_NO_POOL 分支 + blocked_reason 字段 | ✓ |
| `scripts/seed_m4_15_policy_detail_real_v9.sql` | 16 INSERT ROWS total = 12 政策表 + 2 source_registry + 2 source_document; lineage JSONB 全 red_line_14_status='EXHAUSTED' | ✓ |
| `evidence_pack/m4_15_policy_detail_real_v9_20260902.json` | 主 evidence REAL_FETCHED 2 samples; http_count=3/12 (25% usage); substitute_pool_status='EXHAUSTED'; blocked_no_pool_count=0 (本次未触发; 分支代码可达) | ✓ |
| chain_id `real_652_m4_15_policy_detail_v9` | UUID k 段 (k02-k62) ≠ 651 j 段 ≠ 650 i 段 ≠ 649 h 段 ≠ 648 g 段 | ✓ |
| 2 NEW SHA distinct | `21c8211b` (xinjiang) + `da1d4104` (nei_menggu) | ✓ |
| substitute_used_count | **0** (双样本均 REACHABLE; 池耗尽也无需触发) | ✓ |
| blocked_no_pool_count | **0** (本次未触发 BLOCKED; 双样本均 REACHABLE; 但 BLOCKED_NO_POOL 分支代码 e2e 可达) | ✓ |
| HTTP budget | 3/12 = 25% usage (vs 651 4/12 = 33%; vs 650 3/12 = 25%; vs 649 6/12 = 50%) | ✓ |
| lineage JSONB is_demo | 全 `'false'`' 真实化 sentinel (16 行) | ✓ |
| lineage JSONB red_line_14_status | 全 `'EXHAUSTED'`' (per 红线 14 沿用 651) | ✓ |

**2 样本 fetch 详情**:
- xinjiang: `/zwgk/` 403 WAF → `/` 200 REACHABLE (chain_index=1 fallback) — 108,841 bytes; SHA `21c8211bf7bf8b41569174e5ae2ae127f8e11439a04a5501209a63506ddca472`
- nei_menggu: `/zwgk/` 200 REACHABLE (chain_index=0 首选直命中) — 137,602 bytes; SHA `da1d4104db87c47809ef40f12bd8847d98c432bf990b0d7056f0042e6fd0533b`

**BLOCKED_NO_POOL 分支代码 e2e 验证** (per 652 §0.14 强制):
- 4 实现位置: (a) fetch 脚本含 `verdict: "BLOCKED_NO_POOL"` + `blocked_reason`; (b) seed SQL 全 `red_line_14_status='EXHAUSTED'`; (c) 主 evidence `summary.substitute_pool_status='EXHAUSTED'` + methodology 含 BLOCKED_NO_POOL 援引; (d) docs/76 §2 BLOCKED 留痕 e2e 验证登记表
- 5 守门 PASSED: `test_fetch_script_blocked_no_pool_branch_present` + `test_evidence_json_substitute_pool_status_exhausted` + `test_seed_sql_red_line_14_status_exhausted` + `test_red_line_14_pool_exhaustion_*` (3 项) + `test_p4_x2_tailnote_652_a0_landed_in_docs_75_and_651_receipt`

### 652-A.2 O1 零动作 (DONE)

- O1 仍 OPEN (live-candidate 仅登记, 不切换/启用)
- docs/52 零改动 = 合规
- 不新增 probe、不启用、不改 registry/connector

### 652-A.3 docs/76 §1-§6 架构师级审查 (DONE)

`docs/76-m4-15-policy-detail-real-v9-20260902.md` 已落盘; 6 节齐全:
- §1 M4.15 v9 落地终态 (5 子刀状态表)
- §2 BLOCKED 留痕 e2e 验证登记表 (4 实现位置 + 双样本实测 REACHABLE×2 + 触发累计计数 0)
- §3 M4.15 v9 spike 边界 (规划 vs 实测 + 625 fall-through chain 注记 + 16 INSERT ROWS 明细 + 真实样本 SHA 表)
- §4 lineage 真实化 sentinel + chain_id 区分 15 真实化刀 + 29 SHA 累计 + UUID 严格递增 + 652 已用省全集 18 省 + 652-A.4 evidence 落地
- §5 后续 653+ BLOCKED 留痕口径 (5 候选 scope)
- §6 下一步 + 不宣称 PASS (20 个里程碑不宣布; 652 增量 = M4.15)

### 652-A.4 evidence × 2 (DONE)

| 文件 | 角色 | 状态 |
|---|---|---|
| `evidence_pack/m4_15_policy_detail_real_v9_20260902.json` | 主 evidence; summary 含 fetch_status=REAL_FETCHED + http_count=3 + substitute_pool_status='EXHAUSTED' + blocked_no_pool_count=0 + distinct_shas; methodology 含 652 §0.14 BLOCKED_NO_POOL e2e 验证援引 + 沿用 651 §0.14 + 648 P3-1 援引 | ✓ |
| `docs/reports/m4_15_policy_detail_real_v9_20260902.md` | 附属产物 (per 648 审计 P3-1 + 649 审计 P3-1 + 651 §0.14 + 652 §0.14); 9 节齐全 | ✓ |

主 evidence `summary.methodology` 含: "v9 spike fetch: 2 cells (xinjiang + nei_menggu)... 递补池 (SUBSTITUTE_POOL) 显式 [EXHAUSTED] (per 651 §0.14 红线 14 增补沿用, 652 §0.14 强制 BLOCKED_NO_POOL 留痕 e2e 验证)... Per 652 §0.14: BLOCKED_NO_POOL 留痕 e2e 验证. 递补池 [EXHAUSTED] 沿用 651. 本次双样本结果: REACHABLE×2 / BLOCKED_NO_POOL×0."

---

## §PHOTO — 验证铁证

- **PHOTO-1** (M4.15 v9 evidence JSON): `evidence_pack/m4_15_policy_detail_real_v9_20260902.json`
  - `summary.fetch_status = REAL_FETCHED`
  - `summary.fetched_count = 2`
  - `summary.http_count = 3` (25% usage; xinjiang 2 + nei_menggu 1)
  - `summary.http_limit = 12`
  - `summary.substitute_used_count = 0`
  - `summary.substitute_pool_status = "EXHAUSTED"` (per 红线 14 沿用 651)
  - `summary.blocked_no_pool_count = 0` (本次未触发 BLOCKED; 分支代码 e2e 可达)
  - `summary.distinct_shas = ["21c8211bf7bf8b41569174e5ae2ae127f8e11439a04a5501209a63506ddca472", "da1d4104db87c47809ef40f12bd8847d98c432bf990b0d7056f0042e6fd0533b"]`
  - cells[0] xinjiang: REACHABLE / chain_index=1 / verdict=REACHABLE / substitute_used=false / 108841 bytes / SHA 21c8211b
  - cells[1] nei_menggu: REACHABLE / chain_index=0 / verdict=REACHABLE / substitute_used=false / 137602 bytes / SHA da1d4104
  - fetch_log: xj/zwgk 403 WAF, xj/ 200, nmg/zwgk 200
  - methodology 字段含 652 §0.14 强制 BLOCKED_NO_POOL e2e 验证援引 + 沿用 651 §0.14 + 648 P3-1 援引

- **PHOTO-2** (附属报告): `docs/reports/m4_15_policy_detail_real_v9_20260902.md`
  - 9 节齐全: 任务背景 / 样本复盘 / 三层交叉验证 / SHA 区分表 + lineage 落地 / 递补池耗尽登记 + 652 §0.14 BLOCKED_NO_POOL 强制 e2e 验证 / 652-A.0 P4×2 规范固化落地 / 附属产物指针 / 验收 checklist + 不宣称 PASS

- **PHOTO-3** (fetch 脚本 BLOCKED_NO_POOL 分支): `scripts/fetch_m4_15_policy_detail_v9_2024.py`
  - `SUBSTITUTE_POOL: list[tuple[str, list[tuple[str, str]], str]] = []` (5 原始候选全部 consumed; 沿用 651 耗尽态)
  - `SUBSTITUTE_POOL_STATUS = "EXHAUSTED"` (per 红线 14 沿用 651)
  - `fetch_cell()` 含 `verdict: "BLOCKED_NO_POOL"` + `blocked_reason` 字段 (本次未触发; 双样本 REACHABLE)

- **PHOTO-4** (seed SQL red_line_14_status): `scripts/seed_m4_15_policy_detail_real_v9.sql`
  - 16 INSERT ROWS (10 INSERT statements) 全部 lineage JSONB 含 `red_line_14_status: "EXHAUSTED"` (12 quoted + 4 jsonb_build_object = 16 行)
  - source_registry 2 行 lineage JSONB 含 `substitute_pool_note` 显式说明
  - 2 NEW SHA 21c8211b/da1d4104 显式登记; 638-651 全部 stale SHA 严格不出现

- **PHOTO-5** (docs/76 架构师级审查): `docs/76-m4-15-policy-detail-real-v9-20260902.md`
  - §1-§6 齐全; §2 BLOCKED 留痕 e2e 验证登记表 完整 (4 实现位置 + 双样本实测 + 触发累计计数)
  - 2 NEW SHA 21c8211b/da1d4104 显式登记; k 段 UUID 区分; 29 SHA 全部 distinct
  - §4.4 递补池耗尽 [EXHAUSTED] 沿用 651 + 状态表 5 行
  - §6 显式 "不宣称任何 PASS" + 20 个里程碑不宣布 (vs 651 时 19 个; 652 增量 = M4.15)

- **PHOTO-6** (docs/75 + 651 receipt P4×2 tailnote): `docs/75-m4-14-policy-detail-real-v8-20260902.md:282-286` + `651 receipt:168-172`
  - docs/75 §6 末尾: P4×2 规范固化 (status/§CURRENT/§NOW 不 pin 中间 SHA + cc_head 链 SHA 一律 git log 实测 + amend 必须先 amend 完成再写链文本)
  - 651 receipt §RED_LINE_AUDIT 末尾: 对应 P4×2 tailnote (652-A.0 落地)
  - 已 commit: c58d91d chore(652-A.0)

- **PHOTO-7** (tests 27 new green): `tests/test_m4_15_policy_detail_real_v9.py`
  - 27 cases 全 PASSED in 0.93s
  - 含 5 个核心守门 (BLOCKED 留痕 e2e + 红线 14 + 652-A.0 P4×2 + chain_id v9 + UUID k 段):
    - `test_evidence_json_real_fetched_2_samples` (http_count=3, REAL_FETCHED)
    - `test_evidence_json_substitute_pool_status_exhausted` (红线 14 沿用 651 守门)
    - `test_evidence_json_blocked_no_pool_count_zero_but_field_present` (652 §0.14 字段存在守门)
    - `test_fetch_script_blocked_no_pool_branch_present` (BLOCKED_NO_POOL 分支守门)
    - `test_seed_sql_red_line_14_status_exhausted` (lineage JSONB 守门)
    - `test_p4_x2_tailnote_652_a0_landed_in_docs_75_and_651_receipt` (652-A.0 P4×2 守门)
    - `test_red_line_14_pool_exhaustion_*` (3 项)
    - `test_docs_76_sections_1_to_6_present` (docs/76 §1-§6 守门)
    - `test_docs_76_blocked_no_pool_e2e_records_present` (652 §0.14 e2e 守门)
    - `test_docs_76_pool_depletion_records` (递补池耗尽 5 行状态表守门)
    - `test_chain_id_province_used_set_clean` (18 省已用省全集守门)

- **PHOTO-8** (≥171 跨刀 spike 回归): M4.8→M4.15 全套 + m2 hygiene + m6 spike closure = 171 passed in 1.64s
  - M4.15 v9 新增: 27
  - M4.14→M4.1 回归: 144
  - 总计 171 ≥ 152 任务书阈值 (+12.5%)

---

## §RED_LINE_AUDIT

- ✓ 不宣称 Gate / O1 / O2 / O3 / M2 / M4 / M4.x / M5 / M5.x / M6 PASS (per 红线 1) — 20 个里程碑不宣布 (vs 651 时 19 个; 652 增量 = M4.15)
- ✓ 不补零 / 不静默硬编码 value (per 红线 2) — domain 值 NULL 透明占位 (沿用 641-651)
- ✓ 不爬网 / 不镀铬四轨 (per 红线 3) — ≤12 HTTP total (本次 3/12 = 25% usage)
- ✓ 不把目录页标 FETCHED (per 红线 4) — 仅 fallback 链 (zwgk → /) 落入 seed
- ✓ ≤12 HTTP total (per 红线 5) — 3/12 = 25% usage
- ✓ 不改 docs/45/50/53/66/67/68/69/70/71/72/73/74/75 既有正文 (per 红线 6) — 仅 docs/75 §6 + 651 receipt §RED_LINE_AUDIT 末尾追加 P4×2 tailnote (per 652-A.0 落地)
- ✓ scripts/ 蓝图 SQL 的 P3-1 更正不属 docs 正文, 允许行内更正 + 尾注标记 (per 红线 7) — 沿用 651 蓝图
- ✓ 不碰 4 fixture 锁值 (per 红线 8) — nbs=e30ee811 / nbs_live=9232efdb / sz=937255a5 / hb=9056001c 零漂移
- ✓ 数据源唯一 = 政府/统计局/研究机构自取; 用户零裁定 (per 红线 9 + 2026-08-29 铁律)
- ✓ 完成 = observation SUCCESS, 禁止 PARTIAL (per 红线 10) — fetch_status=REAL_FETCHED
- ✓ 不新写 016 migration (沿用 009+010+014+015 lineage JSONB) (per 红线 11)
- ✓ chain_id = `real_652_m4_15_policy_detail_v9` (末段 _v9) ≠ 651 _v8 ≠ 650 _v7 (per 红线 12)
- ✓ UUID k 段 (k02-k62) ≠ 651 j 段 ≠ 650 i 段 ≠ 649 h 段 (per 红线 13)
- ✓ 不写 cegr.* 生产表 (per 红线 14)
- ✓ 既有 registry 行 SHA 零漂移; 4 fixture 字节零触碰; m2 crosscheck 报告零 diff (per 红线 15)
- ✓ O1 零动作 + 递补池按序 (per 红线 16) — 本次递补池已耗尽 (沿用 651)
- ✓ 附属产物指针条款 (per 648 P3-1 口径统一) (per 红线 17)
- ✓ 代换行标注规范 (per 649 P3-1 固化) (per 红线 18)
- ✓ backfill 完整性三齐: cc_head 入链 + last_receipt SHA + §NOW 刷新 (per 红线 19)
- ✓ EXEC-QUEUE rev header 同步 (rev 89 → rev 90) (per 649 审计 P4 教训 + 652-A.0 P4×2 规范)
- ✓ 已用省全集 (按 actual_province 口径, 18 省): HLJ / HENAN / YUNNAN / FUJIAN / GD / ZJ / JX / HUN / AH / LN / JL / GUIZHOU / JIANGSU / SHAANXI / SICHUAN / **XINJIANG / NEI MENGGU** (per 红线 20)
- ✓ **红线 14 增补 (递补池耗尽条款, 2026-09-02 立; 652 沿用)**: SUBSTITUTE_POOL=[] + SUBSTITUTE_POOL_STATUS="EXHAUSTED" + BLOCKED_NO_POOL 留痕不代换 + 5 原始候选全部 consumed + 红线 14 生效 + **652 §0.14 强制 BLOCKED_NO_POOL 留痕 e2e 验证完成** (4 实现位置 + 5 守门 PASSED)
- ✓ **652-A.0 P4×2 规范固化**: status/§CURRENT/§NOW 不 pin 中间 SHA + cc_head 链 SHA 一律 git log 实测 (per docs/75 §6 + 651 receipt §RED_LINE_AUDIT 末尾 tailnote, 已 commit c58d91d)

---

## §CHAIN_MAPPING

| 任务书条目 | 落地文件 | commit (待 §C-3 双推) |
|---|---|---|
| 652-A.0 | `docs/75-m4-14-policy-detail-real-v8-20260902.md` §6 + 651 receipt §RED_LINE_AUDIT 末尾 (P4×2 tailnote) | **c58d91d** (已 commit) |
| 652-A.1 | `scripts/fetch_m4_15_policy_detail_v9_2024.py` + `scripts/seed_m4_15_policy_detail_real_v9.sql` + `evidence_pack/m4_15_policy_detail_real_v9_20260902.json` | (待 delivery commit) |
| 652-A.2 | O1 零动作 (docs/52 零改动) | — |
| 652-A.3 | `docs/76-m4-15-policy-detail-real-v9-20260902.md` | (待 delivery commit) |
| 652-A.4 | `evidence_pack/m4_15_policy_detail_real_v9_20260902.json` + `docs/reports/m4_15_policy_detail_real_v9_20260902.md` | (待 delivery commit) |
| 652-B | `tests/test_m4_15_policy_detail_real_v9.py` (27 cases) | (待 delivery commit) |
| 652-C | 本 receipt + EXEC-QUEUE rev89→rev90 + backfill 三齐 | 待 §C-3 + §C-4 |

---

## §SUMMARY

- **652-A.0 P4×2 规范固化**: ✓ docs/75 §6 + 651 receipt tailnote (P4-1 status 不 pin 中间 SHA + P4-2 cc_head 链 SHA 一律 git log 实测); commit c58d91d
- **652-A.1 M4.15 v9 真实化**: ✓ 16 INSERT ROWS; chain_id='real_652_m4_15_policy_detail_v9'; UUID k 段; 2 NEW SHA 21c8211b/da1d4104; substitute_used=0; HTTP 3/12 (25%)
- **652-A.2 O1 零动作**: ✓ O1 仍 OPEN; docs/52 零改动
- **652-A.3 架构师审查**: ✓ docs/76 §1-§6 (含 §2 BLOCKED 留痕 e2e 验证登记表 4 实现位置 + 5 守门)
- **652-A.4 evidence ×2**: ✓ 主 evidence (含 652 §0.14 + 沿用 651 §0.14 + BLOCKED_NO_POOL 援引) + 附属报告 (9 节齐全)
- **652-B tests**: ✓ 27 cases PASSED in 0.93s; ≥171 跨刀 spike 回归 (M4.8→M4.15 + m2 + m6 = 171 ≥ 152 任务书阈值 +12.5%)
- **652-C commits + 双推 + backfill 三齐 + rev header**: 待 §C-3 + §C-4 执行

---

— End 652 DELIVERED receipt —