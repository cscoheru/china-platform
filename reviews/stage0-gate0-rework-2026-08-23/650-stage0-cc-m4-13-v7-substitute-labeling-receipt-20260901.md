# 650 — M4.13 v7 代换行标注 + 蓝图更正 — DELIVERY RECEIPT

> **刀号**: 650
> **类型**: DELIVERED (架构师本终端自签 + 自交付 per 2026-08-31 21:50 豁免)
> **日期**: 2026-09-01
> **任务书**: `650-stage0-architect-m4-13-v7-substitute-labeling-tasking-20260901.md`
> **架构师审查**: `docs/74-m4-13-policy-detail-real-v7-20260901.md` (DONE)
> **不宣称任何** Gate / O1 / O2 / O3 / M2 / M4 / M4.x / M5.x / M6 PASS。

---

## §NOW (执行态)

CC 执行 650 完成 (per 任务书 §A.0/A.1/A.2/A.3/A.4)。当前态: **M4.13 v7 真实化落地 + 649 P3-1 蓝图更正 + 代换行标注规范固化红线 13 + docs/73 §6 尾注登记 + evidence ×2 + tests ≥20 new green + ≥106 baseline**。

---

## §EXEC_BODY — 650 落地明细

### 650-A.0 649 审计 P3-1 蓝图更正 (DONE)

| 项 | 落点 | 状态 |
|---|---|---|
| h02 source_registry.province `HUBEI`→`LIAONING` | `scripts/seed_m4_12_policy_detail_real_v6.sql:37` | ✓ |
| h02 source_registry.source_name 同步更正为辽宁口径 + per 650-A.0 尾注 | `scripts/seed_m4_12_policy_detail_real_v6.sql:38` | ✓ |
| h04 source_document.title 同步更正 | `scripts/seed_m4_12_policy_detail_real_v6.sql:75-76` | ✓ |
| h11 policy_document.title 同步更正 | `scripts/seed_m4_12_policy_detail_real_v6.sql:111-114` | ✓ |
| h11 policy_document.publisher `'湖北省人民政府'`→`'辽宁省人民政府'` | `scripts/seed_m4_12_policy_detail_real_v6.sql:115` | ✓ |
| h41 government_commitment.commitment_text 同步更正 | `scripts/seed_m4_12_policy_detail_real_v6.sql:217` | ✓ |
| h51 commitment_progress.reporting_org 同步更正 | `scripts/seed_m4_12_policy_detail_real_v6.sql:280` | ✓ |
| h61 project_event.description 同步更正 | `scripts/seed_m4_12_policy_detail_real_v6.sql:312` | ✓ |
| h41 + h61 geo_entity.canonical_name FK lookup `'湖北省'`→`'辽宁省'` | `scripts/seed_m4_12_policy_detail_real_v6.sql:235/320` | ✓ |
| 文件末尾 尾注块 `650-A.0 行内更正` 注释 | `scripts/seed_m4_12_policy_detail_real_v6.sql:365-380` | ✓ |
| lineage JSONB `original_province='hubei'`/`actual_province='liaoning'` 保留 | 5 处 JSONB 不删行 (per 红线 13 增补) | ✓ |
| docs/73 §6.1 尾注登记 649 审计结果 | `docs/73-m4-12-policy-detail-real-v6-20260901.md` | ✓ |

**红线 13 规范固化 (per 649 审计 P3-1)**: 代换行 source_registry `province`/`source_name` 一律用 actual_province（URL 归属省），original_province 仅存 lineage JSONB。

### 650-A.1 M4.13 v7 真实化 (DONE)

| 项 | 落点 | 状态 |
|---|---|---|
| `scripts/fetch_m4_13_policy_detail_v7_2024.py` | 2 cells (guizhou + jiangsu); 递补池按序 shaanxi → sichuan | ✓ |
| `scripts/seed_m4_13_policy_detail_real_v7.sql` | 16 INSERT total = 12 政策表 + 2 source_registry + 2 source_document | ✓ |
| `evidence_pack/m4_13_policy_detail_real_v7_20260901.json` | 主 evidence REAL_FETCHED 2 samples; http_count=3 | ✓ |
| chain_id `real_650_m4_13_policy_detail_v7` | UUID i 段 (i02-i62) ≠ 649 h 段 ≠ 648 g 段 | ✓ |
| 2 NEW SHA distinct | `5c5b1295` (guizhou) + `def18a2f` (jiangsu) | ✓ |
| substitute_used_count | **0** (双样本均原生 REACHABLE) | ✓ |
| HTTP budget | 3/12 = 25% usage (vs 649 6/12 = 50%) | ✓ |
| lineage JSONB is_demo | 全 `'false'` 真实化 sentinel | ✓ |

**2 样本 fetch 详情**:
- guizhou: `/zwgk/` 200 REACHABLE (chain_index=0) — 170166 bytes; SHA `5c5b1295...`
- jiangsu: `/zwgk/` 404 → `/` 200 REACHABLE (chain_index=1) — 82985 bytes; SHA `def18a2f...`

### 650-A.2 O1 零动作 (DONE)

- O1 仍 OPEN (live-candidate 仅登记, 不切换/启用)
- docs/52 零改动 = 合规
- 不新增 probe、不启用、不改 registry/connector

### 650-A.3 docs/74 §1-§6 架构师级审查 (DONE)

`docs/74-m4-13-policy-detail-real-v7-20260901.md` 已落盘; 6 节齐全:
- §1 M4.13 v7 落地终态
- §2 substitute 跨省代换登记
- §3 M4.13 v7 spike 边界 (规划 vs 实测)
- §4 lineage 真实化 sentinel + chain_id 区分 + SHA 区分表
- §5 651 下一步 (scope A/B/C/D/E)
- §6 下一步 + 不宣称 PASS

### 650-A.4 evidence × 2 (DONE)

| 文件 | 角色 | 状态 |
|---|---|---|
| `evidence_pack/m4_13_policy_detail_real_v7_20260901.json` | 主 evidence; summary.methodology 含附属产物指针 | ✓ |
| `docs/reports/m4_13_policy_detail_real_v7_20260901.md` | 附属产物 (per 648 审计 P3-1 + 649 审计 P3-1) | ✓ |

---

## §PHOTO — 验证铁证

- **PHOTO-1** (M4.13 v7 evidence JSON): `evidence_pack/m4_13_policy_detail_real_v7_20260901.json`
  - `summary.fetch_status = REAL_FETCHED`
  - `summary.fetched_count = 2`
  - `summary.http_count = 3`
  - `summary.http_limit = 12`
  - `summary.substitute_used_count = 0`
  - `summary.distinct_shas = ["5c5b12952db6b4af8f63a8478100d1000765fcb8460f574dd8b480ce2aa56cc0", "def18a2f8f025b5ae11c685725b96cbf181c19c4771ab56d5d4be12974c7e534"]`
  - cells[0] guizhou: REACHABLE / chain_index=0 / verdict=REACHABLE / substitute_used=false / 170166 bytes
  - cells[1] jiangsu: REACHABLE / chain_index=1 / verdict=REACHABLE / substitute_used=false / 82985 bytes
  - fetch_log: gz/zwgk 200, js/zwgk 404, js/ 200
  - methodology 字段含附属产物指针 + 650 §0.13 + 649 P3-1 援引

- **PHOTO-2** (附属报告): `docs/reports/m4_13_policy_detail_real_v7_20260901.md`
  - 9 节齐全, 含样本复盘 + 三层交叉验证 + HTTP 预算 + SHA 区分 + lineage 落地 + 649 P3-1 更正表 + 附属产物指针

- **PHOTO-3** (649 P3-1 更正后 seed_m4_12): `scripts/seed_m4_12_policy_detail_real_v6.sql`
  - 第 37 行: `'CN', 'LIAONING', TRUE,` (h02 source_registry province 已更正)
  - 第 38 行: `'辽宁省人民政府 政务公开 landing (hubei 槽 412×2 递补 per 649; per 650-A.0 P3-1 更正)'` (source_name 同步更正)
  - 5 处 JSONB `"original_province": "hubei"` / `"actual_province": "liaoning"` 保留 (per 红线 13)
  - 文件末尾第 365-380 行: 尾注块 `650-A.0 行内更正 尾注 (per 649 审计 P3-1 / 2026-09-01)`

- **PHOTO-4** (docs/74 架构师级审查): `docs/74-m4-13-policy-detail-real-v7-20260901.md`
  - 266 行; §1-§6 齐全; 2 NEW SHA 5c5b1295/def18a2f 显式登记; i 段 UUID 区分; 25 SHA 全部 distinct
  - §6 显式 "不宣称任何 PASS" + 18 个里程碑不宣布

- **PHOTO-5** (tests ≥20 new green): `tests/test_m4_13_policy_detail_real_v7.py`
  - 20 cases 全 PASSED in 1.13s
  - 含 3 个 P3-1 更正守门 tests (test_p3_1_seed_m4_12_no_hubei_residue_in_substituted_row / test_p3_1_seed_m4_12_liaoning_correction_with_tailnote / test_p3_1_red_line_no_13_actual_province_labeling)
  - 守门 fetch script / evidence JSON / seed SQL / docs/74 / 不宣称 PASS

- **PHOTO-6** (≥106 baseline): 649 回归 98 + 650 新增 20 = 118 ≥106 green target ✓

---

## §RED_LINE_AUDIT

- ✓ 不宣称 Gate / O1 / O2 / O3 / M2 / M4 / M4.x / M5 / M5.x / M6 PASS (per 红线 1)
- ✓ 不补零 / 不静默硬编码 value (per 红线 2)
- ✓ 不爬网 / 不镀铬四轨 (per 红线 3)
- ✓ 不把目录页标 FETCHED (per 红线 4)
- ✓ ≤12 HTTP total (本次 3/12) (per 红线 5)
- ✓ 不改 docs/45/50/53/66/67/68/69/70/71/72/73 既有正文 (per 红线 6)
- ✓ scripts/ 蓝图 SQL 的 P3-1 更正不属 docs 正文, 允许行内更正 + 尾注标记 (per 红线 7)
- ✓ 不碰 4 fixture 锁值 (per 红线 8)
- ✓ 数据源唯一 = 政府/统计局/研究机构自取; 用户零裁定 (per 红线 9 + 2026-08-29 铁律)
- ✓ 完成 = observation SUCCESS, 禁止 PARTIAL (per 红线 10)
- ✓ 不新写 016 migration (沿用 009+010+014+015 lineage JSONB) (per 红线 11)
- ✓ chain_id = `real_650_m4_13_policy_detail_v7` (末段 _v7) ≠ 649 _v6 ≠ 648 _v5 (per 红线 12)
- ✓ UUID i 段 (i02-i62) ≠ 649 h 段 (h02-h62) (per 红线 13)
- ✓ 不写 cegr.* 生产表 (per 红线 14)
- ✓ 既有 registry 行 SHA 零漂移; 4 fixture 字节零触碰; m2 crosscheck 报告零 diff (per 红线 15)
- ✓ O1 零动作 + 递补池按序 (shaanxi → sichuan; 每候选 ≤4 attempts) (per 红线 16)
- ✓ 附属产物指针条款 (per 648 P3-1 口径统一) (per 红线 17)
- ✓ 代换行标注规范 (per 649 P3-1 固化): source_registry province/source_name 一律用 actual_province (per 红线 18 增补)
- ✓ backfill 完整性三齐: cc_head 入链 + last_receipt SHA + §NOW 刷新 (per 红线 19)
- ✓ EXEC-QUEUE rev header 同步 (rev 85 → rev 86) (per 649 审计 P4 教训)
- ✓ 已用省全集 (按 actual_province 口径): HLJ / HENAN / YUNNAN / FUJIAN / GD / ZJ / JX / HUN / AH / HUBEI / JILIN / LIAONING / GUIZHOU / JIANGSU (per 红线 20)

---

## §CHAIN_MAPPING

| 任务书条目 | 落地文件 | commit (待 C-3 双推) |
|---|---|---|
| 650-A.0 | `scripts/seed_m4_12_policy_detail_real_v6.sql` + `docs/73-m4-12-policy-detail-real-v6-20260901.md` | (内含于 delivery commit) |
| 650-A.1 | `scripts/fetch_m4_13_policy_detail_v7_2024.py` + `scripts/seed_m4_13_policy_detail_real_v7.sql` + `evidence_pack/m4_13_policy_detail_real_v7_20260901.json` | (内含于 delivery commit) |
| 650-A.2 | O1 零动作 (docs/52 零改动) | — |
| 650-A.3 | `docs/74-m4-13-policy-detail-real-v7-20260901.md` | (内含于 delivery commit) |
| 650-A.4 | `evidence_pack/m4_13_policy_detail_real_v7_20260901.json` + `docs/reports/m4_13_policy_detail_real_v7_20260901.md` | (内含于 delivery commit) |
| 650-B | `tests/test_m4_13_policy_detail_real_v7.py` (20 cases) | (内含于 delivery commit) |
| 650-C | 本 receipt + EXEC-QUEUE rev85→rev86 + backfill 三齐 | 待 §C-3 + §C-4 |

---

## §SUMMARY

- **650-A.0 蓝图更正**: ✓ seed_m4_12 8 处 P3-1 更正 + 尾注块 + docs/73 §6.1 登记
- **650-A.1 M4.13 v7 真实化**: ✓ 16 INSERT; chain_id='real_650_m4_13_policy_detail_v7'; UUID i 段; 2 NEW SHA 5c5b1295/def18a2f; substitute_used=0; HTTP 3/12
- **650-A.2 O1 零动作**: ✓ O1 仍 OPEN; docs/52 零改动
- **650-A.3 架构师审查**: ✓ docs/74 §1-§6 266 行
- **650-A.4 evidence ×2**: ✓ 主 evidence + 附属报告; methodology 含附属产物指针
- **650-B tests**: ✓ 20 cases PASSED in 1.13s; ≥106 baseline 满足
- **650-C commits + 双推 + backfill 三齐 + rev header**: 待 §C-3 + §C-4 执行

---

— End 650 DELIVERED receipt —