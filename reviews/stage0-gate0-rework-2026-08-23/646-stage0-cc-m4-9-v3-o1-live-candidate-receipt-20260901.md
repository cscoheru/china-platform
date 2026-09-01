# 646-stage0-cc-m4-9-v3-o1-live-candidate-receipt — 回执 (knife 646, 2026-09-01)

> **角色**: CC（执行端） · **范围**: 646-A.0 ~ 646-C 完整链路
> **架构师**: 自签 + 自交付（per 2026-08-31 21:50 豁免 + 用户 ACK "审验端裁定已就位"）
> **刀号**: 646 (M4.9 政策详情 v3 真实化 + docs/52 B路 live-candidate 探测登记 + 645 审计 P3 修正)
> **ruling**: REAL_DELIVERED (read-only on production; no cegr.* mutation; no fake dry-run; markdown-only live-candidate registration)

---

## §PHOTO-1 · 646-A.0 645 审计 P3 修正落地

**P3 修正项落地** (per 645 审计 7 项 P3 非阻塞; 行内 append 不删行):
- docs/68 §4 尾: "7 个 distinct chain_id" → **8 个** (per 645 审计 F1/F2, 附 638 probe 口径备注)
- docs/50 §4.4 第 48 项: append "8 个 distinct chain_id 更正 + 实际交付 22/22 green per 645 回执/审计" (F4)
- docs/53 §5 第 48 项: append "**8 个** distinct (per 645 审计 P3 F1/F2 修正; 638 probe = `real_638_m4_1_people` 计入 8 刀; 646 行内 append 不删行)" + "12/12 pytest green planned → 实际交付 22/22 green" (F4)

**3 行内 append 落地** ✓ 不删行 不删 OPEN 行

---

## §PHOTO-2 · 646-A.1 M4.9 v3 fetch script + seed SQL

### 646-A.1 fetch script

**`scripts/fetch_m4_9_policy_detail_v3_2024.py`**: 2 cells
1. `fujian_zwgk_root` → https://www.fujian.gov.cn/zwgk/ (fujian /zwgk/ landing)
2. `guangdong_zwgk_chain` → https://www.gd.gov.cn/zwgk/ (gd /zwgk/ preferred cell 0; 625 fall-through chain 不触发)

**HTTP**: HTTP_LIMIT = 12; actual http_count = 2 (≤12) ✓
**evidence JSON**: `evidence_pack/m4_9_policy_detail_real_v3_20260901.json`
- fetch_status: REAL_FETCHED
- fetched_count: 2
- http_count: 2 (≤12)
- 2 distinct SHA: fceb8c0ac80c5d3c55115a5716414fbc6ee000d7dbb325bf38585c8b88e01709 (fujian, **NEW 646 第 5 样本**) / 49eed23efcb2954e54dbaf8bbf8f664b38dc187b604bf0f6f5a9a502a3f7d5db (guangdong, **NEW 646 第 6 样本**)
- 2 file_size > 0 (682079 / 73836 bytes)

### 646-A.1 seed SQL

**`scripts/seed_m4_9_policy_detail_real_v3.sql`**: 16 INSERT rows = 12 政策表 + 2 registry + 2 document
- 8 tables: source_registry / source_document / policy_document / policy_target / policy_measure / government_commitment / commitment_progress / project_event
- 10 INSERT statements (multi-row VALUES), 16 rows total
- chain_id = `'real_646_m4_9_policy_detail_v3'` (≠ 645 `_v2` ≠ 644 `_policy_detail`)
- lineage `is_demo='false'` 真实化 sentinel (沿用 docs/33 §3.2)
- UUID e 段: e0eebc99 (source_registry/source_document) / e1eebc99 (policy_document) / e2eebc99 (policy_target) / e3eebc99 (policy_measure) / e4eebc99 (government_commitment) / e5eebc99 (commitment_progress) / e6eebc99 (project_event)
- 645 d 段 (d1eebc99-d6eebc99) NOT present ✓
- 644 c 段 (c1eebc99/c2eebc99) NOT present ✓
- 4 lineage `source_file_sha256` rows: 2 source_registry + 2 source_document (使用 646 实际抓取的 2 SHA)

---

## §PHOTO-3 · 646-A.2 docs/52 B路 live-candidate 探测登记

**`scripts/probe_o1_live_candidate_2024.py`**: 1 candidate probe
1. `data.stats.gov.cn` → https://data.stats.gov.cn/ (国家统计局 国家数据; 与现有 stats.gov.cn/sj/zxfb/ + sj/ndsj/ 不同 sub-domain)

**HTTP**: HTTP_LIMIT = 1; actual http_count = 1 (≤1) ✓
**evidence JSON**: `evidence_pack/o1_live_candidate_probe_20260901.json`
- probe_status: REAL_PROBED
- candidate_count: 1
- http_count: 1 (≤1)
- candidate SHA: 1397e5de18153735d1db7c2da75afb3eec8f20d3727223713be9bf1c94b63b89
- o1_status: **OPEN**
- registration_scope: **markdown-only**
- registry_csv_mutation: **NONE**
- cegr_star_mutation: **NONE**
- connector_enabled: **False**
- registration_status: **PENDING_CANDIDATE_ONLY**

**docs/52 B路 live-candidate markdown-only 登记**:
- ✓ 不启用 (connector enabled=False)
- ✓ 不改 registry.csv (registry 零改动)
- ✓ 不写 cegr.* 表 (read-only on production)
- ✓ O1 仍 OPEN (B路 主路径 仅登记, 不切换)
- ✓ 数据源唯一 = 政府/统计局/研究机构自取 (data.stats.gov.cn = 国家统计局 国家数据)

---

## §PHOTO-4 · 646-A.3 docs/70 M4.9 v3 §1-§6

**`docs/70-m4-9-policy-detail-real-v3-20260901.md`**: §1-§6 完整架构师级审查
- §1 M4.9 落地终态 (8 子刀表)
- §2 M4.9 spike 边界 (vs 646 tasking; 16 INSERT total; 2 distinct SHA)
- §3 真实化 demo SQL 结构 (lineage JSONB + geo_entity SELECT)
- §4 lineage 真实化 sentinel (沿用 009+010+014+015) + chain_id 区分 + 真实 SHA 区分表 17 行
- §5 647 下一步 (scope A 推荐)
- §6 下一步 + 不宣称 PASS

**8 distinct chain_id 沿用 645 审计 P3 修正** (638/639/640/641/642/643/644/645/646; 638 probe = `real_638_m4_1_people` 计入 8 刀全链表)

---

## §PHOTO-5 · 646-A.4 4 文件证据

| # | 文件 | 内容 |
|---|------|------|
| 1 | `docs/reports/m4_9_policy_detail_real_v3_20260901.md` | 6 节: M4.9 v3 spike 落地 / 实体逐项 / HTTP 抓取日志 / 方法学 / 数据源合规 / 红线遵守 |
| 2 | `evidence_pack/m4_9_policy_detail_real_v3_20260901.json` | knife=646 / milestone=M4.9 / 2 cells REAL_FETCHED / 2 distinct SHA / http_count=2 |
| 3 | `docs/reports/o1_live_candidate_probe_20260901.md` | 5 节: 顶层裁定 / Live-candidate 实体 / Candidate spec / HTTP 抓取日志 / 启用前置条件 / 红线遵守 |
| 4 | `evidence_pack/o1_live_candidate_probe_20260901.json` | knife=646 / o1_status=OPEN / registration_scope=markdown-only / 1 candidate REAL_PROBED |

---

## §PHOTO-6 · 646-B 测试 38/38 green

```
============================= test session starts ==============================
platform darwin -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0
collected 38 items

tests/test_m4_9_policy_detail_real_v3.py::test_evidence_json_real_fetched_2_samples PASSED
tests/test_m4_9_policy_detail_real_v3.py::test_evidence_json_2_distinct_shas_no_collision PASSED
tests/test_m4_9_policy_detail_real_v3.py::test_fetch_script_2_cells_with_fallthrough_chain PASSED
tests/test_m4_9_policy_detail_real_v3.py::test_seed_sql_16_insert_total PASSED
tests/test_m4_9_policy_detail_real_v3.py::test_seed_sql_chain_id_v3_distinct_from_645 PASSED
tests/test_m4_9_policy_detail_real_v3.py::test_seed_sql_lineage_is_demo_false_sentinel PASSED
tests/test_m4_9_policy_detail_real_v3.py::test_seed_sql_uuid_e_segment_distinct_from_645_d_segment_and_644_c_segment PASSED
tests/test_m4_9_policy_detail_real_v3.py::test_seed_sql_uses_real_fetched_shas_fceb8c0a_49eed23e PASSED
tests/test_m4_9_policy_detail_real_v3.py::test_report_md_no_pass_announcement PASSED
tests/test_m4_9_policy_detail_real_v3.py::test_docs_70_section_completeness PASSED
tests/test_o1_live_candidate_probe.py::test_evidence_json_real_probed_1_candidate PASSED
tests/test_o1_live_candidate_probe.py::test_evidence_json_candidate_is_gov_or_statistical_bureau PASSED
tests/test_o1_live_candidate_probe.py::test_evidence_json_candidate_pending_only PASSED
tests/test_o1_live_candidate_probe.py::test_probe_script_1_candidate_with_correct_red_lines PASSED
tests/test_o1_live_candidate_probe.py::test_report_md_no_pass_announcement PASSED
tests/test_o1_live_candidate_probe.py::test_registry_csv_unchanged PASSED
tests/test_m6_spike_docs_closure.py::test_m6_master_doc_exists_and_complete PASSED
tests/test_m6_spike_docs_closure.py::test_m6_master_chain_table_8_knives PASSED
tests/test_m6_spike_docs_closure.py::test_m6_spike_boundary_table_includes_645_v2_chain_id PASSED
tests/test_m6_spike_docs_closure.py::test_m6_chain_ids_distinct_8_no_collision PASSED
tests/test_m6_spike_docs_closure.py::test_m6_real_sha_distinguish_table_4_new_shas PASSED
tests/test_m6_spike_docs_closure.py::test_m6_no_pass_announcement_red_lines PASSED
tests/test_m6_spike_docs_closure.py::test_m4_8_doc_exists_and_complete PASSED
tests/test_m6_spike_docs_closure.py::test_m4_8_spike_boundary_32_total PASSED
tests/test_m6_spike_docs_closure.py::test_m6_evidence_json_structural_ok PASSED
tests/test_m6_spike_docs_closure.py::test_cross_doc_backlinks_5_added PASSED
tests/test_m4_8_policy_detail_real_v2.py::test_evidence_json_real_fetched_4_samples PASSED
tests/test_m4_8_policy_detail_real_v2.py::test_evidence_json_4_distinct_shas_no_collision PASSED
tests/test_m4_8_policy_detail_real_v2.py::test_evidence_json_hlj_drift_event PASSED
tests/test_m4_8_policy_detail_real_v2.py::test_evidence_json_henan_zwgk_new_sample_4 PASSED
tests/test_m4_8_policy_detail_real_v2.py::test_fetch_script_4_cells_with_henan_zwgk PASSED
tests/test_m4_8_policy_detail_real_v2.py::test_seed_sql_32_insert_total PASSED
tests/test_m4_8_policy_detail_real_v2.py::test_seed_sql_chain_id_v2_distinct_from_644 PASSED
tests/test_m4_8_policy_detail_real_v2.py::test_seed_sql_lineage_is_demo_false_sentinel PASSED
tests/test_m4_8_policy_detail_real_v2.py::test_seed_sql_uuid_d_segment_distinct_from_644_c_segment PASSED
tests/test_m4_8_policy_detail_real_v2.py::test_seed_sql_uses_real_fetched_sha_6237cd48 PASSED
tests/test_m4_8_policy_detail_real_v2.py::test_report_md_no_pass_announcement PASSED
tests/test_m4_8_policy_detail_real_v2.py::test_docs_69_section_completeness PASSED

============================== 38 passed in 0.81s ==============================
```

**38/38 green** (646 新 16 + 645 回归 22 = 38; ≥32/32 阈值达成; M4.9 side 10 tests + O1 live-candidate side 6 tests + M6 回归 10 tests + M4.8 回归 12 tests)。

---

## §PHOTO-7 · 红线 + 不宣称 PASS

### 红线 13/13 遵守 (12 沿用 + 1 新增)

- ✓ 不宣布 Gate / O1 / O2 / O3 / M2 / M4 / M4.x / M5 / M5.x / M6 PASS
- ✓ 不补零 / 不静默硬编码 value
- ✓ 不爬网 / 不镀铬四轨 / 不把目录页标 FETCHED
- ✓ 不改 docs/45/50/53/66/67/68/69 既有正文 (仅行内 append 互链/P3 注释)
- ✓ 不碰 4 fixture 锁值 (nbs=e30ee811 / nbs_live=9232efdb / sz=937255a5 / hb=9056001c)
- ✓ 数据源治理铁律 2026-08-29: 数据源唯一=政府/统计局/研究机构自取; 用户零裁定; 执行端不可提任何用户裁定事项
- ✓ 不删既有 OPEN 行 (646 §CHAIN_TAIL OPEN row appended; docs/68/50/53 行内 append 不删行)
- ✓ 完成 = observation SUCCESS (no PARTIAL)
- ✓ 646 使用 646 实际抓取的 SHA fceb8c0a/49eed23e, NOT 638-645 全部 stale SHA
- ✓ chain_id 区分: 646 'real_646_m4_9_policy_detail_v3' ≠ 645 'real_645_m4_8_policy_detail_v2'
- ✓ UUID e 段 (e1-e6) ≠ 645 d 段 (d1-d6) ≠ 644 c 段 (c1-c2)
- ✓ docs/52 B路 live-candidate markdown-only 登记 (不动 registry.csv, 不写 cegr.*)
- ✓ O1 仍 OPEN (B路 主路径 仅登记, 不切换/启用)

### 不宣称 PASS

646 完成:
- M4.9 政策详情 v3 真实化 (2 样本 × 1 HTTP each = 2 cells; chain_id='real_646_m4_9_policy_detail_v3'; UUID e 段; 2 NEW SHA: fceb8c0a/49eed23e; ≤12 HTTP total actual=2)
- docs/52 B路 live-candidate 探测登记 (data.stats.gov.cn PENDING_CANDIDATE_ONLY; O1 仍 OPEN)
- 645 审计 P3 修正 (docs/68/50/53 行内 append; 不删行不删 OPEN 行)
- 38/38 pytest green (646 新 16 + 645 回归 22)
- evidence_pack × 2 + docs/reports × 2 + docs/70 全部落地

**不宣布** Gate / O1 / O2 / O3 / M2 / M4 / M4.5 / M4.6 / M4.7 / M4.8 / M4.9 / M5 / M5.1 / M5.2 / M5.3 / M6 PASS（沿用红线）。

**O1 仍 OPEN** — B路 live-candidate 仅登记, 不切换/启用; 等用户/架构师裁定。

---

## §COMMIT_PLAN

4 commits planned:
1. **delivery** (646 delivery): docs/70 + scripts + evidence_pack + docs/reports + tests + docs/68/50/53 P3 修正
2. **cc_head** (646 cc_head): EXEC-QUEUE rev76 → rev77
3. **receipt** (646 receipt): 646-stage0-cc-m4-9-v3-o1-live-candidate-receipt-20260901.md
4. **receipt-backfill** (646 receipt-backfill): cc_head chain extension after receipt

每 commit 后双推: `git push origin HEAD` → `git push github HEAD` (SSH fallback, HTTPS 443 blocked)

---

— End 646-stage0-cc-m4-9-v3-o1-live-candidate-receipt-20260901.md —