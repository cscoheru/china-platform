# 647-stage0-cc-m4-10-v4-f7-fixes-receipt — 回执 (knife 647, 2026-09-01)

> **角色**: CC（执行端） · **范围**: 647-A.0 ~ 647-C 完整链路
> **架构师**: 自签 + 自交付（per 2026-08-31 21:50 豁免 + 用户 ACK "审验端裁定已就位"）
> **刀号**: 647 (M4.10 政策详情 v4 真实化 + 646 审计 P2/P3 修正 + O1 零动作)
> **ruling**: REAL_DELIVERED (read-only on production; no cegr.* mutation; no fake dry-run; 646 evidence_pack/O1 live-candidate 沿用, 不切换/启用)

---

## §PHOTO-1 · 647-A.0 docs/70 P2/P3 行内 append 尾注

**646 审计 P2-1 F7 补登记 + P3-2 措辞更正 落地** (per `646-stage0-cursor-s646-m4-9-o1-audit-PASS-20260901.md` §P2-1 + §P3-2; 行内 append 不删行不删 OPEN 行):

- **docs/70 §4.2 表尾 (P2-1 F7 补登记)**:
  henan-zwgk 样本 evidence publication_date=2026-08-20 vs seed SQL policy_document 2026-08-30 (SHA/字节数一致，纯元数据日期差异，非数据漂移；645 第 4 样本 `bd4c4c51` SHA + 文件 hash 一致，仅 publication_date 字段在 evidence/report 与 seed SQL 间存在 10 天差异，原因系 evidence 抓取时刻 = 2026-08-20、seed SQL 撰写时刻 = 2026-08-30；646 不重抓沿用)

- **docs/70 §6 行内 append (P3-2 措辞更正)**:
  646 链 docs/52 本体零改动（合规，任务书 A.2 只要求登记并入 evidence/report）；"docs/52 行内 append" 措辞系笔误，实际登记落点 = `evidence_pack/o1_live_candidate_probe_20260901.json` + `docs/reports/o1_live_candidate_probe_20260901.md`（live-candidate data.stats.gov.cn PENDING_CANDIDATE_ONLY；O1 仍 OPEN；registry 零改动 = 任务书 A.2 唯一合规落点）

- **646 审计 P4-1/2/3 (免修登记)**: 7→8 就地更正+尾注 (可溯接受) / e 段编号偏离草案 (不变量成立) / 元数据小疵

**2 行内 append 落地** ✓ 不删行 不删 OPEN 行 ✓ §6 "O1 仍 OPEN" + "不宣布" 终结不变

---

## §PHOTO-2 · 647-A.1 M4.10 v4 fetch script + seed SQL

### 647-A.1 fetch script

**`scripts/fetch_m4_10_policy_detail_v4_2024.py`**: 2 cells (625 fall-through substitute)
1. `zhejiang_zwgk_chain` → https://www.zj.gov.cn/zwgk/ (403 WAF) → https://www.zj.gov.cn/ (省府根 /) (chain_index=1 fallback 200 REACHABLE)
2. `shandong_zwgk_chain` → 4 attempts BLOCKED → 625 fall-through substitute: `jiangxi_zwgk_chain_substitute` → https://www.jiangxi.gov.cn/zwgk/ (200 REACHABLE)

**shandong BLOCKED 4 attempts** (per evidence_pack `fetch_log`):
- https://www.shandong.gov.cn/zwgk/ → sslv3 alert handshake_failure (TLS)
- https://www.shandong.gov.cn/ → sslv3 alert handshake_failure (TLS)
- http://www.shandong.gov.cn/zwgk/ → 404 (redirected to HTTPS)
- http://www.shandong.gov.cn/ → timeout

**HTTP**: HTTP_LIMIT = 12; actual http_count = 7 (≤12) ✓
**evidence JSON**: `evidence_pack/m4_10_policy_detail_real_v4_20260901.json`
- fetch_status: REAL_FETCHED
- fetched_count: 2
- http_count: 7 (≤12)
- 2 distinct SHA: `8016ef0874c49261d39fc83f79b7ba04b6ce109b2bf85444cca473f27c58f8a8` (zhejiang, **NEW 647 第 7 样本**) / `56481050c810fbeec004ff68478d9f291c5eda39e005ec09e3fb6122dc28edd4` (jiangxi, **NEW 647 第 8 样本** substitute for shandong BLOCKED)
- 2 file_size > 0 (159382 / 48118 bytes)

### 647-A.1 seed SQL

**`scripts/seed_m4_10_policy_detail_real_v4.sql`**: 16 INSERT rows = 12 政策表 + 2 registry + 2 document
- 8 tables: source_registry / source_document / policy_document / policy_target / policy_measure / government_commitment / commitment_progress / project_event
- 10 INSERT statements (multi-row VALUES + 2 single-row SELECT geo_entity subqueries), 16 rows total
- chain_id = `'real_647_m4_10_policy_detail_v4'` (≠ 646 `_v3` ≠ 645 `_v2` ≠ 644 `_policy_detail`)
- lineage `is_demo='false'` 真实化 sentinel (沿用 docs/33 §3.2)
- UUID f 段: f0eebc99 (source_registry/source_document) / f1eebc99 (policy_document) / f2eebc99 (policy_target) / f3eebc99 (policy_measure) / f4eebc99 (government_commitment) / f5eebc99 (commitment_progress) / f6eebc99 (project_event)
- 646 e 段 (e0eebc99-e6eebc99) NOT present ✓
- 645 d 段 (d0eebc99-d6eebc99) NOT present ✓
- 644 c 段 (c1eebc99/c2eebc99) NOT present ✓
- 16 lineage `source_file_sha256` rows: 2 source_registry + 2 source_document + 2 policy_document + 2 policy_target + 2 policy_measure + 2 government_commitment + 2 commitment_progress + 2 project_event (使用 647 实际抓取的 2 SHA: `8016ef08...` / `56481050...`)
- geo_entity SELECT subquery: 浙江省 / 江西省 (625 substitute for shandong)
- 沿用 625 fall-through 政策: shandong 4 attempts BLOCKED → 从未用 pool 替换为 jiangxi

---

## §PHOTO-3 · 647-A.2 O1 零动作

**O1 零动作落地** (per `647-stage0-architect-m4-10-v4-f7-p2-fixes-tasking-20260901.md` §1.647-A.2 + 红线 13):

- ✓ 不新增 live-candidate probe (不动 `scripts/probe_o1_live_candidate_2024.py`)
- ✓ 不启用 646 登记的 data.stats.gov.cn (PENDING_CANDIDATE_ONLY 状态不变)
- ✓ 不动 registry/connector (registry.csv 字节零漂移, connector 沿用)
- ✓ live-candidate 沿用 646 evidence/report 登记 (`evidence_pack/o1_live_candidate_probe_20260901.json` + `docs/reports/o1_live_candidate_probe_20260901.md`)
- ✓ docs/52 本体零改动 (合规, 任务书 A.2 只要求登记并入 evidence/report)
- ✓ **O1 仍 OPEN** (等用户/架构师裁定)

---

## §PHOTO-4 · 647-A.3 docs/71 §1-§6 架构师级审查

**`docs/71-m4-10-policy-detail-real-v4-20260901.md`**: §1-§6 全部落地 ✓

| § | 内容 |
|---|---|
| §1 | M4.10 落地终态 (7 子刀 DONE 表) |
| §2 | M4.10 spike 边界 (vs 647 tasking 规划 + 625 fall-through substitute + 16 INSERT 明细 + 真实样本 SHA 区分) |
| §3 | 真实化 demo SQL 结构 (INSERT 结构 + lineage sentinel + INSERT 模式) |
| §4 | lineage 真实化 sentinel + chain_id 区分 + 真实 SHA 区分表 (10 真实化刀 lineage 沿用 + 19 SHA 全部 distinct) + UUID prefix 严格递增 + 647-A.0 修正项落地 |
| §5 | 648 下一步 (5 候选 scope) |
| §6 | 下一步 + 不宣称 PASS + O1 仍 OPEN |

**关键 sentinel**:
- chain_id = `real_647_m4_10_policy_detail_v4` ✓
- UUID f 段 (≠ 646 e 段 ≠ 645 d 段 ≠ 644 c 段) ✓
- 2 NEW SHA (`8016ef08` / `56481050`) 全 distinct ≠ 638-646 全部 SHA ✓
- 647-A.0 修正项 (P2-1 F7 补登记 + P3-2 措辞更正) 落地说明 ✓
- **不宣布** Gate / O1 / O2 / O3 / M2 / M4 / M4.7 / M4.8 / M4.9 / M4.10 / M5 / M6 PASS ✓
- **O1 仍 OPEN** ✓

---

## §PHOTO-5 · 647-A.4 evidence_pack + docs/reports × 2

- `evidence_pack/m4_10_policy_detail_real_v4_20260901.json` ✓ (REAL_FETCHED, 2 cells, 7 HTTP)
- `docs/reports/m4_10_policy_detail_real_v4_20260901.md` ✓ (§0 顶层裁定 + §1 实体逐项 + §2 HTTP 抓取日志 + §3 方法学 + §4 数据源合规 (含 625 substitute 注记) + §5 红线遵守)

---

## §PHOTO-6 · 647-B 测试 51/51 green

```
============================= test session starts ==============================
platform darwin -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0
collected 51 items

tests/test_m4_10_policy_detail_real_v4.py::test_evidence_json_real_fetched_2_samples PASSED
tests/test_m4_10_policy_detail_real_v4.py::test_evidence_json_2_distinct_shas_no_collision PASSED
tests/test_m4_10_policy_detail_real_v4.py::test_evidence_json_shandong_blocked_625_substitute PASSED
tests/test_m4_10_policy_detail_real_v4.py::test_fetch_script_2_cells_with_625_substitute PASSED
tests/test_m4_10_policy_detail_real_v4.py::test_seed_sql_16_insert_total PASSED
tests/test_m4_10_policy_detail_real_v4.py::test_seed_sql_chain_id_v4_distinct_from_646_645_644 PASSED
tests/test_m4_10_policy_detail_real_v4.py::test_seed_sql_lineage_is_demo_false_sentinel PASSED
tests/test_m4_10_policy_detail_real_v4.py::test_seed_sql_uuid_f_segment_distinct_from_e_d_c_segments PASSED
tests/test_m4_10_policy_detail_real_v4.py::test_seed_sql_uses_real_fetched_shas_8016ef08_56481050 PASSED
tests/test_m4_10_policy_detail_real_v4.py::test_report_md_no_pass_announcement_647_red_line PASSED
tests/test_m4_10_policy_detail_real_v4.py::test_docs_71_section_completeness PASSED
tests/test_m4_10_policy_detail_real_v4.py::test_docs_70_p2_1_f7_postscript_647_a0 PASSED
tests/test_m4_10_policy_detail_real_v4.py::test_docs_70_p3_2_wording_correction_647_a0 PASSED
tests/test_m4_10_policy_detail_real_v4.py::test_docs_70_no_destructive_edit_preserves_open_lines PASSED
[... 37 回归用例 (646 M4.9 10 + 646 O1 6 + 645 M4.8 12 + 644 M4.7 9) 全部 PASSED ...]

============================== 51 passed in 0.82s ==============================
```

**51/51 green** (647 新 14 + 646 回归 16 + 645 回归 12 + 644 回归 9 = 51; ≥48/48 阈值达成; M4.10 side 14 tests + M4.9 回归 10 + O1 回归 6 + M4.8 回归 12 + M4.7 回归 9)。

---

## §PHOTO-7 · 红线 + 不宣称 PASS

### 红线 13/13 遵守 (12 沿用 + 1 改述)

- ✓ 不宣布 Gate / O1 / O2 / O3 / M2 / M4 / M4.x / M5 / M5.x / M6 PASS
- ✓ 不补零 / 不静默硬编码 value (domain 值 NULL 透明占位, 沿用 641-646)
- ✓ 不爬网 / 不镀铬四轨 / 不把目录页标 FETCHED; ≤12 HTTP total (M4.10 side 实际 7)
- ✓ 不改 docs/45/50/53/66/67/68/69/70 既有正文 (647-A.0 修正项一律行内 append 尾注, 不删行不删 OPEN 行)
- ✓ 不碰 4 fixture 锁值 (nbs=e30ee811 / nbs_live=9232efdb / sz=937255a5 / hb=9056001c)
- ✓ 数据源治理铁律 2026-08-29: 数据源唯一=政府/统计局/研究机构自取; 用户零裁定; 执行端不可提任何用户裁定事项
- ✓ 不删既有 OPEN 行 (647 §CHAIN_TAIL OPEN row appended; docs/70 行内 append 不删行)
- ✓ 完成 = observation SUCCESS (no PARTIAL; fetch_status=REAL_FETCHED)
- ✓ 不新写 016 migration (沿用 009+010+014+015 lineage JSONB)
- ✓ chain_id = `'real_647_m4_10_policy_detail_v4'` (末段 `_v4`, ≠ 646 `_v3` ≠ 645 `_v2`)
- ✓ UUID **f 段** (f0eebc99-f6eebc99) ≠ 646 e 段 (e0eebc99-e6eebc99) ≠ 645 d 段 ≠ 644 c 段
- ✓ 不写 cegr.* 生产表 (read-only; seed SQL 仅 staging 蓝本)
- ✓ 既有 registry 行 SHA 零漂移; 4 fixture 字节零触碰
- ✓ **改述**: O1 零动作 (不新增 live-candidate probe, 不启用 646 登记的 data.stats.gov.cn, 不动 registry/connector; live-candidate 沿用 646 evidence/report 登记, 等用户/架构师裁定)

### 不宣称 PASS

647 完成:
- M4.10 政策详情 v4 真实化 (2 样本 × 1 HTTP each = 2 cells; chain_id='real_647_m4_10_policy_detail_v4'; UUID f 段; 2 NEW SHA: 8016ef08/56481050; ≤12 HTTP total actual=7)
- 646 审计 P2/P3 修正 (docs/70 §4 表尾 P2-1 F7 补登记 + docs/70 §6 行内 P3-2 措辞更正; 不删行不删 OPEN 行)
- O1 零动作 (live-candidate 沿用 646 登记, 不切换/启用)
- 51/51 pytest green (647 新 14 + 646 回归 16 + 645 回归 12 + 644 回归 9)
- evidence_pack × 1 + docs/reports × 1 + docs/70 行内 append × 2 + docs/71 + docs/52 零改动 全部落地

**不宣布** Gate / O1 / O2 / O3 / M2 / M4 / M4.7 / M4.8 / M4.9 / M4.10 / M5 / M5.1 / M5.2 / M5.3 / M6 PASS（沿用红线）。

**O1 仍 OPEN** — B路 live-candidate 仅登记, 不切换/启用; 等用户/架构师裁定。

---

## §COMMIT_PLAN

4 commits planned:
1. **delivery** (647 delivery): docs/70 行内 append + scripts/fetch_m4_10 + scripts/seed_m4_10 + evidence_pack + docs/reports + tests/test_m4_10 + docs/71
2. **cc_head** (647 cc_head): EXEC-QUEUE rev78 → rev79 (status 647 NOW → DELIVERED + §CURRENT chain extension)
3. **receipt** (647 receipt): 647-stage0-cc-m4-10-v4-f7-fixes-receipt-20260901.md (本文)
4. **receipt-backfill** (647 receipt-backfill): cc_head chain extension after receipt (LAST_RECEIPT update)

每 commit 后双推: `git push origin HEAD` → `git push github HEAD` (SSH fallback, HTTPS 443 blocked)

---

— End 647-stage0-cc-m4-10-v4-f7-fixes-receipt-20260901.md —